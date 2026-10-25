#!/usr/bin/env python3
"""Compose one presenter interval above its speech-matched SaaS motion, exactly 50/50."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess


def probe(path):
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    v=next(x for x in d['streams'] if x['codec_type']=='video')
    if v.get('sample_aspect_ratio','1:1') not in ['1:1','N/A']:
        raise ValueError('Normalize pixel aspect in a working copy first.')
    if any(x.get('rotation',0) for x in v.get('side_data_list',[])):
        raise ValueError('Normalize display rotation in a working copy first.')
    return {'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],
            'duration':float(v.get('duration',d['format']['duration'])),
            'frames':int(v['nb_frames']) if v.get('nb_frames','').isdigit() else None,
            'audio':any(x['codec_type']=='audio' for x in d['streams'])}


def validate_cues(path,start,duration,fps):
    if path is None:
        raise ValueError('Production composition requires --cues with verified speech timing; use --layout-test only for explicit visual QA.')
    c=json.loads(Path(path).read_text())
    if c.get('alignment')!='verified':
        raise ValueError('Cues must be checked against actual speech; draft timing is not production alignment.')
    if abs(float(c['source_start'])-start)>1/fps+.0001 or abs(float(c['duration'])-duration)>1/fps+.0001:
        raise ValueError('Cue interval does not match the selected presenter interval.')
    end=-1
    for beat in c['beats']:
        s,e=float(beat['start']),float(beat['end'])
        if not 0<=s<e<=duration+.0001 or s<end-.0001:
            raise ValueError('Beats must be ordered, non-overlapping and inside the interval.')
        if not beat.get('narration','').strip() or not beat.get('visual','').strip():
            raise ValueError('Every beat needs actual narration and its matching visual action.')
        end=e
    if not c['beats']:
        raise ValueError('Empty speech plan')
    return len(c['beats'])


def compose(a):
    inputs=[Path(a.presenter).resolve(),Path(a.motion).resolve()]
    if Path(a.output).resolve() in inputs:
        raise ValueError('Output must be distinct from both inputs.')
    if a.width%2 or a.height%4 or a.width<4 or a.height<8:
        raise ValueError('Width must be even; height must be divisible by four for equal YUV420 halves.')
    if not 0<=a.focal_x<=1 or not 0<=a.focal_y<=1:
        raise ValueError('Focal coordinates must lie in [0,1].')
    p,m=probe(a.presenter),probe(a.motion)
    rate=Fraction(a.fps or p['fps']);fps=float(rate)
    start=round(a.start*fps)/fps
    duration=p['duration']-start if a.duration is None else a.duration
    n=int(duration*fps+1e-4);duration=n/fps
    if start<0 or n<1 or start+duration>p['duration']+1/fps:
        raise ValueError('Invalid presenter interval.')
    if m['duration']+1e-4<duration:
        raise ValueError('Motion is shorter than the selected interval; render the correct duration instead of silently looping it.')
    beats=0 if a.layout_test else validate_cues(a.cues,start,duration,fps)
    w,h=a.width,a.height//2
    aspect=m['width']/m['height']
    if abs(aspect-w/h)>0.005 and a.motion_fit=='strict':
        raise ValueError('Re-layout motion for the lower panel aspect ratio, or explicitly request --motion-fit contain. Never stretch UI/text.')
    rate_text=f'{rate.numerator}/{rate.denominator}'
    x=f"max(0,min(iw-ow,iw*{a.focal_x}-ow/2))"
    y=f"max(0,min(ih-oh,ih*{a.focal_y}-oh/2))"
    top=f"[0:v]setpts=PTS-STARTPTS,fps={rate_text},scale={w}:{h}:force_original_aspect_ratio=increase:force_divisible_by=2,crop={w}:{h}:'{x}':'{y}',setsar=1[top]"
    bottom=f'[1:v]trim=duration={duration},setpts=PTS-STARTPTS,fps={rate_text},scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0xf5f5f7,setsar=1[bottom]'
    graph=top+';'+bottom+';[top][bottom]vstack=inputs=2[v]'
    if p['audio']:
        graph+=f';[0:a]atrim=duration={duration},asetpts=PTS-STARTPTS[a]'
    cmd=['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(a.presenter),'-i',str(a.motion),
         '-filter_complex',graph,'-map','[v]']
    if p['audio']:
        cmd+=['-map','[a]','-c:a','aac','-b:a','192k']
    else:
        cmd+=['-an']
    cmd+=['-t',str(duration),'-r',rate_text,'-c:v','libx264','-crf','17','-preset','fast',
          '-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)]
    subprocess.run(cmd,check=True)
    out=probe(a.output)
    if (out['width'],out['height'])!=(w,2*h) or out['frames']!=n or out['audio']!=p['audio']:
        raise RuntimeError('Output dimensions/frame count/audio verification failed.')
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(a.output),'-f','null','-'],check=True)
    report={'output':str(a.output),'mode':'layout QA only' if a.layout_test else 'speech-planned interval',
            'source_start':start,'duration':duration,'fps':rate_text,'frames':n,
            'top_rect':[0,0,w,h],'bottom_rect':[0,h,w,h],
            'cue_beats':beats,'audio':'AAC from the trimmed presenter; original timing retained' if p['audio'] else 'none',
            'limitation':'This composer does not transcribe speech, author motion or independently validate semantic alignment.'}
    Path(str(a.output)+'.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--presenter',required=True,type=Path)
    p.add_argument('--motion',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--start',type=float,default=0)
    p.add_argument('--duration',type=float)
    p.add_argument('--width',type=int,default=1080)
    p.add_argument('--height',type=int,default=1920)
    p.add_argument('--fps',help='Output CFR; defaults to presenter average rate. Normalize VFR explicitly before production.')
    p.add_argument('--focal-x',type=float,default=.5)
    p.add_argument('--focal-y',type=float,default=.35)
    p.add_argument('--motion-fit',choices=['strict','contain'],default='strict')
    p.add_argument('--cues',type=Path)
    p.add_argument('--layout-test',action='store_true',help='Explicit QA-only bypass of the speech plan. Never label this speech-synced.')
    compose(p.parse_args())


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Frame-exact 50/50 compositor; pass a designed lower-panel video and measured head track."""
import argparse,json,subprocess,math
from pathlib import Path
import numpy as np
from PIL import Image

def probe(p):
 d=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(p)]));s=next(x for x in d['streams'] if x['codec_type']=='video')
 a,b=map(int,s['avg_frame_rate'].split('/'));fps=a/b
 if s.get('r_frame_rate')!=s['avg_frame_rate']:raise ValueError('CFR source/panel required')
 return s,fps

def geometry(W,H,SW,SH,x,y,scale):
 # Mapping output pixel coordinates to original source coordinates.
 return (1/scale,0,x-W/(2*scale),0,1/scale,y-H/(2*scale))

def reframe(frame,W,H,x,y,scale):
 SW,SH=frame.size;aff=list(geometry(W,H,SW,SH,x,y,scale))
 # Reflect only required out-of-bounds region, retaining exact head centering.
 xlo=aff[2];ylo=aff[5];xhi=xlo+W/scale;yhi=ylo+H/scale
 pl=max(0,math.ceil(-xlo)+2);pt=max(0,math.ceil(-ylo)+2);pr=max(0,math.ceil(xhi-SW)+2);pb=max(0,math.ceil(yhi-SH)+2)
 if any((pl,pt,pr,pb)):
  frame=Image.fromarray(np.pad(np.asarray(frame),((pt,pb),(pl,pr),(0,0)),mode='reflect'));aff[2]+=pl;aff[5]+=pt
 return frame.transform((W,H),Image.Transform.AFFINE,tuple(aff),Image.Resampling.BICUBIC)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('config',type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();c=json.loads(a.config.read_text())
 def path(k):
  p=Path(c[k]);return p if p.is_absolute() else a.config.parent/p
 source,panel=path('source'),path('panel');v,fps=probe(source);pv,pfps=probe(panel);W,H=v['width'],v['height'];half=H//2
 if W%2 or H%4:raise ValueError('Need even width and height divisible by four for two yuv420 halves')
 if (pv['width'],pv['height'])!=(W,half) or abs(fps-pfps)>1e-6:raise ValueError('Panel dimensions/FPS must match source half')
 total=int(v.get('nb_frames',0));pn=int(pv.get('nb_frames',0))
 if not total or not pn:raise ValueError('Need frame counts in source/panel metadata')
 start=round(c['start']*fps);end=round(c['end']*fps)
 if not 0<=start<end<=total or pn<end-start:raise ValueError('Invalid interval or short panel')
 track=c['head_track'];ts=[p['time'] for p in track]
 if not ts or ts!=sorted(set(ts)) or ts[0]>start/fps or ts[-1]<(end-1)/fps:raise ValueError('Measured head track must cover interval with unique ordered timestamps')
 if any(not (0<=p['x']<W and 0<=p['y']<H) for p in track):raise ValueError('Head coordinates outside source')
 scale=c.get('scale',max(W/v['width'],half/v['height']))
 if not math.isfinite(scale) or scale<=0:raise ValueError('Bad scale')
 def reader(p):return subprocess.Popen(['ffmpeg','-v','error','-i',str(p),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
 src=reader(source);pan=reader(panel);a.output.parent.mkdir(parents=True,exist_ok=True);temp=a.output.with_name(a.output.stem+'-silent.mp4')
 enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',v['avg_frame_rate'],'-i','pipe:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
 try:
  for i in range(total):
   data=src.stdout.read(W*H*3)
   if len(data)!=W*H*3:raise ValueError('Source ended early')
   if start<=i<end:
    lower=pan.stdout.read(W*half*3)
    if len(lower)!=W*half*3:raise ValueError('Panel ended early')
    t=i/fps;x=float(np.interp(t,ts,[p['x'] for p in track]));y=float(np.interp(t,ts,[p['y'] for p in track]))
    frame=Image.frombytes('RGB',(W,H),data);out=Image.new('RGB',(W,H));out.paste(reframe(frame,W,half,x,y,scale),(0,0));out.paste(Image.frombytes('RGB',(W,half),lower),(0,half));data=out.tobytes()
   enc.stdin.write(data)
  enc.stdin.close()
  if enc.wait()!=0:raise RuntimeError('Encoder failed')
 finally:
  for proc in (src,pan):proc.stdout.close();proc.terminate();proc.wait()
  if enc.poll() is None:enc.terminate();enc.wait()
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-i',str(source),'-map','0:v:0','-map','1:a?','-c','copy','-movflags','+faststart',str(a.output)],check=True);temp.unlink()
 report={'interval_frames':[start,end],'end_exclusive':True,'source_frames':total,'fps':fps,'size':[W,H],'split_y':half,'head_target':[W/2,H/4],'scale':scale,'head_track':track,'new_subtitles':False,'panel_audio_used':False,'source_audio':'stream copied; optional if absent','outside_interval':'source frames unchanged before video encoding'}
 a.output.with_suffix('.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report))
if __name__=='__main__':main()

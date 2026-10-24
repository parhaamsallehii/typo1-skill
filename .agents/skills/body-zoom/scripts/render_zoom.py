#!/usr/bin/env python3
"""Render the shared virtual camera on a planar complete composition."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from body_zoom import BodyZoom


def linear(rgb):
    return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)


def srgb(rgb):
    return np.where(rgb<=.0031308,rgb*12.92,1.055*np.maximum(rgb,0)**(1/2.4)-.055)


def render_frame(scene_at,rig,t,width,height,fps):
    """scene_at(t) returns the complete RGBA scene at each shutter subframe.

    This is the coplanar z=0 camera projection, not a depth/parallax renderer.
    Evaluate all existing foreground animation inside scene_at before this pass.
    """
    yy,xx=np.mgrid[:height,:width].astype(float)
    cx,cy=(width-1)/2,(height-1)/2
    lo=rig.scale(t);hi=rig.scale(t+.5/fps)
    movement=abs(hi-lo)*math.hypot(width,height)/2
    count=min(128,max(16,math.ceil(movement/.5)))
    accum=np.zeros((height,width,4),float)
    for u in rig.shutter_times(t,fps,count):
        frame=scene_at(u).convert('RGBA')
        if frame.size!=(width,height):
            raise ValueError('scene_at must return final composition dimensions')
        rgba=np.asarray(frame,dtype=float)/255
        a=rgba[...,3:4]
        premul=np.concatenate([linear(rgba[...,:3])*a,a],axis=-1)
        scale=rig.scale(u)
        sx=(xx-cx)/scale+cx;sy=(yy-cy)/scale+cy
        # A single transform applies to the entire scene, including all overlays.
        accum+=np.stack([map_coordinates(premul[...,j],[sy,sx],order=1,mode='nearest')
                         for j in range(4)],axis=-1)
    accum/=count
    alpha=accum[...,3:4]
    rgb=np.divide(accum[...,:3],alpha,out=np.zeros_like(accum[...,:3]),where=alpha>1e-12)
    out=np.concatenate([srgb(np.clip(rgb,0,1)),alpha],axis=-1)
    return Image.fromarray(np.uint8(np.clip(out,0,1)*255),'RGBA'),count


def probe(path):
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
        '-show_format','-of','json',str(path)]))
    v=next(s for s in d['streams'] if s['codec_type']=='video')
    return d,v


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--start',type=float,required=True)
    p.add_argument('--end',type=float,required=True)
    p.add_argument('--travel',type=float,default=200)
    p.add_argument('--width',type=int)
    a=p.parse_args()
    if a.input.resolve()==a.out.resolve():
        p.error('Output must differ from source')
    meta,v=probe(a.input)
    if int(v.get('disposition',{}).get('attached_pic',0)):
        p.error('Input must be a video')
    fps=eval_fraction(v['avg_frame_rate'])
    duration=float(meta['format']['duration'])
    if a.end > duration+1e-7:
        p.error('Requested range exceeds source duration')
    w=a.width or v['width'];h=round(v['height']*w/v['width'])
    if w<=0 or w%2 or h%2:
        p.error('Use positive even output dimensions for H.264')
    rig=BodyZoom(a.start,a.end,w,a.travel)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(a.input),'-vf',f'scale={w}:{h}',
        '-f','rawvideo','-pix_fmt','rgba','-'],stdout=subprocess.PIPE)
    command=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{w}x{h}',
        '-r',str(fps),'-i','-','-i',str(a.input),'-map','0:v','-map','1:a?',
        '-t',str(duration),'-c:v','libx264','-crf','18','-preset','fast',
        '-pix_fmt','yuv420p','-c:a','copy',str(a.out)]
    enc=subprocess.Popen(command,stdin=subprocess.PIPE)
    counts=set();n=0
    try:
        while True:
            raw=dec.stdout.read(w*h*4)
            if not raw:break
            if len(raw)!=w*h*4:raise RuntimeError('Incomplete decoded frame')
            frame=Image.frombytes('RGBA',(w,h),raw)
            # Flattened-input route holds source at its decoded frame during the
            # shutter; only camera motion gets new blur. Use scene_at integration
            # for genuine subframe foreground/video evaluation in an editable scene.
            out,count=render_frame(lambda u:frame,rig,n/fps,w,h,fps)
            counts.add(count);enc.stdin.write(out.tobytes());n+=1
    finally:
        dec.stdout.close();enc.stdin.close()
        dr,er=dec.wait(),enc.wait()
    if dr or er:raise RuntimeError('FFmpeg render failed; use a compatible audio container/codec')
    check,cv=probe(a.out)
    if (cv['width'],cv['height'])!=(w,h):raise RuntimeError('Output dimensions invalid')
    subprocess.run(['ffmpeg','-v','error','-i',str(a.out),'-f','null','-'],check=True)
    report=dict(rig=rig.plan(),frames=n,fps=fps,size=[w,h],sample_counts=sorted(counts),
        native_after_effects=False,route='coplanar virtual camera; frame-held source within shutter',
        audio='stream copied',output=str(a.out))
    a.out.with_suffix('.zoom.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(out=str(a.out),frames=n,samples=sorted(counts))))


def eval_fraction(s):
    n,d=map(float,s.split('/'))
    if d==0 or n<=0:raise ValueError('Cannot determine a positive source frame rate')
    return n/d


if __name__=='__main__':
    main()

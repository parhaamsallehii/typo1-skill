#!/usr/bin/env python3
"""Reference-inspired halftone circular reveal on the live supplied clip."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter


def svg_polygon(path):
    tokens=re.findall(r'[MLCZ]|-?\d+(?:\.\d+)?',path)
    i=0;points=[];last=(0,0)
    while i<len(tokens):
        cmd=tokens[i];i+=1
        if cmd in ('M','L'):
            last=(float(tokens[i]),float(tokens[i+1]));i+=2;points.append(last)
        elif cmd=='C':
            vals=list(map(float,tokens[i:i+6]));i+=6
            a=np.array(last);b=np.array(vals[:2]);c=np.array(vals[2:4]);d=np.array(vals[4:])
            for t in np.linspace(0,1,15)[1:]:
                p=(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
                points.append(tuple(p))
            last=tuple(d)
        elif cmd=='Z':
            points.append(points[0])
        else:raise ValueError(cmd)
    return points


def hand_icon(size,rotation):
    # Vector-native cursor silhouette: long index, curled fingers, thumb and cuff.
    path='M31 58 L31 20 C31 11 44 11 44 20 L44 47 L44 38 C44 29 57 30 57 38 L57 48 L57 43 C57 34 70 35 70 43 L70 53 L70 49 C70 42 83 43 83 51 L83 71 C83 85 72 95 66 100 L66 108 L34 108 L34 96 L14 72 C8 65 15 57 22 62 L31 70 Z'
    ss=4;image=Image.new('RGBA',(120*ss,120*ss))
    d=ImageDraw.Draw(image)
    pts=[(x*ss,y*ss) for x,y in svg_polygon(path)]
    d.polygon(pts,fill=(255,253,242,255))
    d.line(pts,fill=(38,35,32,255),width=3*ss,joint='curve')
    for a,b in [((44,50),(44,68)),((57,51),(57,69)),((70,55),(70,70)),((34,96),(65,99))]:
        d.line((a[0]*ss,a[1]*ss,b[0]*ss,b[1]*ss),fill=(38,35,32,255),width=2*ss)
    image=image.rotate(rotation,resample=Image.Resampling.BICUBIC,expand=True)
    bbox=image.getchannel('A').getbbox()
    image=image.crop(bbox) if bbox else image
    image.thumbnail((size,size),Image.Resampling.LANCZOS)
    return image


class DottedReveal:
    def __init__(self,width,height,duration=43/30,fps=30):
        self.w,self.h,self.duration,self.fps=width,height,duration,fps
        self.k=width/1080;self.cx=width*.5;self.cy=height*.49
        yy,xx=np.mgrid[:height,:width].astype(np.float32)
        self.dist=np.hypot(xx-self.cx,yy-self.cy)
        theta=np.arctan2(yy-self.cy,xx-self.cx)
        self.edge_wobble=(np.sin(theta*13+.3)*5+np.sin(theta*29)*2)*self.k
        pitch=20*self.k
        gx=(xx+pitch/2)%pitch-pitch/2;gy=(yy+pitch/2)%pitch-pitch/2
        self.dots=np.clip(7.2*self.k-np.hypot(gx,gy)+.5,0,1).astype(np.float32)
        self.max_radius=max(math.hypot(x-self.cx,y-self.cy) for x,y in [(0,0),(width,0),(0,height),(width,height)])+35*self.k
        size=round(92*self.k)
        self.hands=[hand_icon(size,-45),hand_icon(size,135)]

    def radius(self,t):
        u=min(1,max(0,t/self.duration))
        return 78*self.k+(self.max_radius-78*self.k)*u**.52

    def samples(self,t):
        return [t+(i+.5)/16*.5/self.fps for i in range(16)]

    def cursor(self,base,times,index):
        icon=self.hands[index];iw,ih=icon.size
        sign=-1 if index==0 else 1
        positions=[]
        for t in times:
            if t>=self.duration:continue
            r=self.radius(t)
            x=self.cx+sign*r/math.sqrt(2)
            y=self.cy-sign*r/math.sqrt(2)
            positions.append((round(x-iw/2),round(y-ih/2)))
        visible=[p for p in positions if p[0]+iw>0 and p[0]<self.w and p[1]+ih>0 and p[1]<self.h]
        if not visible:return
        left=max(0,min(p[0] for p in visible));top=max(0,min(p[1] for p in visible))
        right=min(self.w,max(p[0]+iw for p in visible));bottom=min(self.h,max(p[1]+ih for p in visible))
        accum=np.zeros((bottom-top,right-left,4),np.float32)
        for x,y in positions:
            if x+iw<=left or x>=right or y+ih<=top or y>=bottom:continue
            layer=Image.new('RGBA',(right-left,bottom-top))
            layer.alpha_composite(icon,(x-left,y-top))
            a=np.asarray(layer,dtype=np.float32)/255
            a[...,:3]*=a[...,3:4];accum+=a
        accum/=len(times)
        rgb=np.divide(accum[...,:3],accum[...,3:4],out=np.zeros_like(accum[...,:3]),where=accum[...,3:4]>1e-7)
        rgba=np.concatenate([rgb,accum[...,3:4]],axis=-1)
        base.alpha_composite(Image.fromarray(np.uint8(np.clip(rgba,0,1)*255),'RGBA'),(left,top))

    def render(self,frame,t):
        if t>=self.duration:return frame.convert('RGB')
        times=self.samples(t)
        outside=np.zeros((self.h,self.w),np.float32)
        edge=np.zeros_like(outside);outline=np.zeros_like(outside)
        for sample in times:
            if sample>=self.duration:continue
            r=self.radius(sample);delta=self.dist-r
            # A fixed dot grid is uncovered by an opening circle. Only the
            # bright dotted rim is irregular; the guide outline stays smooth.
            u=np.clip((delta+7*self.k)/(14*self.k),0,1)
            outside+=u*u*(3-2*u)
            edge+=np.exp(-((delta-self.edge_wobble)/(31*self.k))**2)
            outline+=np.exp(-(delta/(1.0*self.k))**2)
        outside/=len(times);edge/=len(times);outline/=len(times)
        original=np.asarray(frame.convert('RGB'),dtype=np.float32)/255
        blurred=np.asarray(frame.filter(ImageFilter.GaussianBlur(2.4*self.k)).convert('RGB'),dtype=np.float32)/255
        warm=np.array([1.0,.98,.90],np.float32)
        tint=blurred*.69
        luma=blurred[...,0]*.2126+blurred[...,1]*.7152+blurred[...,2]*.0722
        dot_alpha=self.dots*(.10+.24*luma+.25*edge)
        patterned=tint*(1-dot_alpha[...,None])+warm*dot_alpha[...,None]
        result=original*(1-outside[...,None])+patterned*outside[...,None]
        highlight=np.clip(edge*self.dots*.66+outline*.20,0,.92)
        result=result*(1-highlight[...,None])+warm*highlight[...,None]
        output=Image.fromarray(np.uint8(np.clip(result,0,1)*255),'RGB').convert('RGBA')
        self.cursor(output,times,0);self.cursor(output,times,1)
        return output.convert('RGB')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--width',type=int,default=1080);p.add_argument('--still',type=float)
    a=p.parse_args()
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(a.input)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    n,d=map(float,v['avg_frame_rate'].split('/'));fps=n/d
    w=a.width;h=round(v['height']*w/v['width']);duration=float(info['format']['duration'])
    effect=DottedReveal(w,h,min(43/30,duration),fps)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if a.still is not None:
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(a.still),'-i',str(a.input),'-frames:v','1','-vf',f'scale={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-'])
        effect.render(Image.frombytes('RGB',(w,h),raw),a.still).save(a.out)
        print(str(a.out));return
    decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(a.input),'-vf',f'scale={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-i',str(a.input),'-map','0:v','-map','1:a?','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(a.out)],stdin=subprocess.PIPE)
    count=0
    try:
        while True:
            raw=decoder.stdout.read(w*h*3)
            if not raw:break
            if len(raw)!=w*h*3:raise RuntimeError('Incomplete source frame')
            result=effect.render(Image.frombytes('RGB',(w,h),raw),count/fps)
            encoder.stdin.write(result.tobytes());count+=1
            if count in [1,15,30,43,60,90]:print(json.dumps({'frame':count}),flush=True)
    finally:
        decoder.stdout.close();encoder.stdin.close();dr=decoder.wait();er=encoder.wait()
    if dr or er:raise RuntimeError('FFmpeg render failed')
    subprocess.run(['ffmpeg','-v','error','-i',str(a.out),'-f','null','-'],check=True)
    print(json.dumps({'output':str(a.out),'frames':count,'fps':fps,'size':[w,h],'effect_seconds':effect.duration,'audio':'stream copied'}))


if __name__=='__main__':main()

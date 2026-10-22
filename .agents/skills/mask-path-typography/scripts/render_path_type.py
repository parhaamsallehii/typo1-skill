#!/usr/bin/env python3
"""Persian shaped-ribbon text on an arc-length path, with temporal motion blur.

Dependencies: Pillow with RAQM, numpy, scipy, fonttools, FFmpeg.
The native Deep Glow plugin and AE glyph layout are not executed by this file.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, features
from fontTools.ttLib import TTFont
from scipy.interpolate import CubicSpline
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.spatial import cKDTree

from spring import margin_at

ROOT = Path(__file__).resolve().parents[1]
FONTS = {"bahman": "Bahman.ttf", "e-bahman": "E-Bahman.ttf",
         "lifta-black": "Lifta-Black.otf", "lifta-bold": "Lifta-Bold.otf"}
PALETTE = {"red": "#B40023", "cream": "#FCF0D6"}


def rgb(h):
    return np.array([int(h[i:i+2],16)/255 for i in (1,3,5)],np.float32)


def linear(c):
    return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)


def srgb(c):
    c=np.maximum(c,0)
    return np.where(c<=.0031308,12.92*c,1.055*c**(1/2.4)-.055)


def check(text="نمونه تایپوگرافی روی مسیر نرم و فنری"):
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM is required for connected Persian shaping")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is required for video export")
    result={}
    for key,name in FONTS.items():
        p=ROOT/"assets/fonts"/name
        ft=TTFont(p); cmap=ft.getBestCmap()
        missing=[ch for ch in sorted(set(text)) if not ch.isspace()
                 and ch not in "\u200c\u200d\u200e\u200f" and ord(ch) not in cmap]
        if missing:
            raise ValueError(f"{key} lacks glyphs {missing}; do not substitute fonts silently")
        result[key]=dict(family=ft['name'].getDebugName(1),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        ft.close()
    return dict(raqm=True,ffmpeg=True,fonts=result)


class Curve:
    """C2-continuous y(x) spline, increasing x, sampled in true arc length."""
    def __init__(self, points, scale):
        p=np.asarray(points,dtype=float)*scale
        if p.ndim!=2 or p.shape[1]!=2 or len(p)<3 or not np.isfinite(p).all():
            raise ValueError("path requires at least three finite [x,y] points")
        if np.any(np.diff(p[:,0])<=0):
            raise ValueError("path points must have strictly increasing x; no corners/loops")
        self.fn=CubicSpline(p[:,0],p[:,1],bc_type='natural')
        self.x=np.linspace(p[0,0],p[-1,0],max(4097,int((p[-1,0]-p[0,0])*2)))
        self.y=self.fn(self.x)
        self.s=np.r_[0,np.cumsum(np.hypot(np.diff(self.x),np.diff(self.y)))]
        self.tree=cKDTree(np.column_stack([self.x,self.y]))
        self.scale=scale

    def at(self,s):
        x=np.interp(s,self.s,self.x)
        return x,self.fn(x)

    def arc_at_x(self,x):
        return float(np.interp(x,self.x,self.s))

    def inverse(self,w,y0,y1,shadow_dy=0):
        yy,xx=np.mgrid[y0:y1,0:w].astype(np.float32)
        yy-=shadow_dy
        _,idx=self.tree.query(np.column_stack([xx.ravel(),yy.ravel()]))
        q=self.x[idx].reshape(xx.shape)
        for _ in range(5):
            y=self.fn(q);d=self.fn(q,1);dd=self.fn(q,2)
            q-=np.clip(((q-xx)+(y-yy)*d)/(1+d*d+(y-yy)*dd),-20*self.scale,20*self.scale)
            q=np.clip(q,self.x[0],self.x[-1])
        y=self.fn(q); d=self.fn(q,1)
        n=((xx-q)*(-d)+(yy-y))/np.sqrt(1+d*d)
        s=np.interp(q,self.x,self.s)
        return s.astype(np.float32),n.astype(np.float32)


class Layer:
    def __init__(self,cfg,scene,index):
        self.cfg=cfg;self.fps=scene['fps'];self.W=scene['width'];self.H=scene['height']
        self.scale=self.W/1080; k=self.scale
        if cfg.get('motion_blur',True) is not True:
            raise ValueError("Motion blur must remain enabled on every layer")
        self.text=cfg['text'];self.font_key=cfg['font']
        font_path=ROOT/'assets/fonts'/FONTS[self.font_key]
        ft=TTFont(font_path);cmap=ft.getBestCmap();ft.close()
        missing=[ch for ch in set(self.text) if not ch.isspace() and ch not in '\u200c\u200d\u200e\u200f' and ord(ch) not in cmap]
        if missing: raise ValueError(f"Missing glyphs in {self.font_key}: {missing}")
        if '\n' in self.text: raise ValueError("Use separate layers for separate lines")
        font=ImageFont.truetype(str(font_path),round(cfg.get('font_size',110)*k),layout_engine=ImageFont.Layout.RAQM)
        bbox=font.getbbox(self.text,anchor='ls',direction='rtl',language='fa')
        pad=max(3,round(5*k));left,top,right,bottom=bbox
        mask=Image.new('L',(right-left+2*pad,bottom-top+2*pad))
        ImageDraw.Draw(mask).text((pad-left,pad-top),self.text,font=font,fill=255,anchor='ls',direction='rtl',language='fa')
        self.alpha=np.asarray(mask,dtype=np.float32)/255
        self.src_top=top-pad
        self.sw,self.sh=mask.size
        seed=int(hashlib.sha256((self.font_key+self.text+str(cfg.get('seed',7))).encode()).hexdigest()[:8],16)
        rng=np.random.default_rng(seed)
        yy,xx=np.mgrid[:self.sh,:self.sw]/k
        angle=math.pi/4
        u=xx*math.cos(angle)+yy*math.sin(angle);v=-xx*math.sin(angle)+yy*math.cos(angle)
        pitch=cfg.get('texture_pitch',4.0)
        dot_radius=cfg.get('halftone_radius',1.05)
        dots=((u+pitch/2)%pitch-pitch/2)**2+((v+pitch/2)%pitch-pitch/2)**2 < dot_radius**2
        grain=np.maximum(rng.normal(.0,.16,self.alpha.shape),0)
        texture=np.clip((grain+dots*.46)*cfg.get('texture_strength',1.25),0,.72)
        self.mix=(texture*self.alpha).astype(np.float32)
        self.curve=Curve(cfg['path'],k)
        # A curved ribbon must not fold over itself at the glyph height.
        d=self.curve.fn(self.curve.x,1);dd=self.curve.fn(self.curve.x,2)
        curvature=np.abs(dd)/(1+d*d)**1.5
        if np.max(curvature)*max(abs(self.src_top),abs(bottom+pad))>.70:
            raise ValueError("Curve too tight for this text size; make the path shallower")
        center_x=cfg.get('center_x',540)*k
        self.target=self.curve.arc_at_x(center_x)-self.sw/2+cfg.get('target_margin_offset',0)*k
        self.source=self.target+cfg.get('travel',900)*k
        self.start=cfg.get('start',0)
        # Ordinal frames 1 -> 5 contain four frame intervals.
        self.frame_span=cfg.get('arrival_frame',5)-cfg.get('start_frame',1)
        if self.frame_span<=0:raise ValueError('arrival_frame must follow start_frame')
        self.arrival=self.start+self.frame_span/self.fps
        self.exit_start=cfg.get('exit_start')
        self.exit_arrival=None
        self.exit_source=self.target+cfg.get('exit_travel',cfg.get('travel',900))*k
        if self.exit_start is not None:
            self.exit_span=cfg.get('exit_end_frame',5)-cfg.get('exit_start_frame',1)
            if self.exit_span<=0:raise ValueError('exit_end_frame must follow exit_start_frame')
            if self.exit_start<self.arrival+cfg.get('spring',{}).get('duration',1):
                raise ValueError('exit_start must follow the completed entrance spring')
            self.exit_arrival=self.exit_start+self.exit_span/self.fps
        self.profile=cfg.get('profile','spring-entry')
        self.spring=cfg.get('spring',{}).copy()
        self.spring.setdefault('max_offset',300)
        if self.spring.get('max_offset') is not None:self.spring['max_offset']*=k
        self.hand_draw_amount=cfg.get('hand_draw_amount',3.2)*k
        self.hand_draw_frequency=cfg.get('hand_draw_frequency',8.0)
        if self.hand_draw_amount<0 or self.hand_draw_frequency<=0:
            raise ValueError('hand-drawn amount/frequency must be nonnegative/positive')
        self.style=cfg.get('style','red')
        if self.style not in PALETTE:raise ValueError('style must be red or cream')
        self.base=linear(rgb(PALETTE[self.style]))
        self.pigment=self.base*.30
        self.shadow=linear(rgb(PALETTE['cream' if self.style=='red' else 'red']))
        self.shadow_dy=3*k # documented default direction, not an unspecified angle claim
        visible_x=np.linspace(0,self.W,500);visible_y=self.curve.fn(visible_x)
        # Account for normal rotation, descent, and 3 px shadow. Glow is computed on full canvas.
        margin=abs(self.src_top)+self.sh+12*k
        self.y0=max(0,int(np.min(visible_y)-margin));self.y1=min(self.H,int(np.max(visible_y)+margin))
        if self.y0>=self.y1:raise ValueError('Path lies completely outside the canvas')
        self.s,self.n=self.curve.inverse(self.W,self.y0,self.y1)
        self.ss,self.nn=self.curve.inverse(self.W,self.y0,self.y1,self.shadow_dy)
        self.cache={};self.sample_counts=[]

    def margin(self,t):
        if self.exit_start is not None and t>=self.exit_start:
            # Reverse First Margin travel: settled target -> original offscreen side.
            return margin_at(t,self.exit_start,self.exit_arrival,self.target,
                             self.exit_source,self.fps,self.profile,self.spring)
        return margin_at(t,self.start,self.arrival,self.source,self.target,self.fps,self.profile,self.spring)

    def opacity(self,t):
        if t<=self.start:return 0.0
        if t<self.arrival:return (t-self.start)/(self.arrival-self.start)
        if self.exit_start is not None and t>=self.exit_start:
            return max(0.0,1.0-(t-self.exit_start)/(self.exit_arrival-self.exit_start))
        return 1.0

    def sample(self,margin,t,shadow=False):
        s,n=(self.ss,self.nn) if shadow else (self.s,self.n)
        x=s-margin; y=n-self.src_top
        # Continuous hand-drawn contour movement in the glyph's own space.
        # The same displaced coordinates sample glyph coverage and print texture.
        if self.hand_draw_amount:
            phase=2*math.pi*self.hand_draw_frequency*t
            local_x=x/self.scale;local_y=y/self.scale
            x=x+self.hand_draw_amount*(.62*np.sin(local_x/83+local_y/41+phase)
                    +.38*np.sin(local_x/29-local_y/73-phase*1.2))
            y=y+self.hand_draw_amount*(.52*np.sin(local_x/57-local_y/69+phase*.87)
                    +.24*np.sin(local_x/31+local_y/47-phase*1.3))
        valid=(x>=0)&(x<=self.sw-1)&(y>=0)&(y<=self.sh-1)
        a=np.zeros(s.shape,np.float32);m=np.zeros_like(a)
        if valid.any():
            coords=[y[valid],x[valid]]
            a[valid]=map_coordinates(self.alpha,coords,order=1,mode='constant',cval=0,prefilter=False)
            if not shadow:m[valid]=map_coordinates(self.mix,coords,order=1,mode='constant',cval=0,prefilter=False)
        return a,m

    def exposure_times(self,t):
        # Screenshot: phase 0, angle 180. Forward exposure, NOT centered -90.
        lo=t;hi=t+.5/self.fps
        times=np.linspace(lo,hi,9)
        probes=np.array([self.margin(u) for u in times])
        alphas=np.array([self.opacity(u) for u in times])
        distance=float(np.abs(np.diff(probes)).sum())
        count=min(128,max(16,int(math.ceil(distance/.6))))
        if distance<1e-8 and np.max(np.abs(alphas))<1e-8:
            return [t],16
        if distance<1e-8 and np.max(np.abs(alphas-alphas[0]))<1e-8 and not self.hand_draw_amount:
            # Analytically identical subframes: evaluate once with identical result.
            return [t],16
        return lo+(np.arange(count)+.5)/count*(hi-lo),count

    def render(self,t):
        times,n=self.exposure_times(t);self.sample_counts.append(n)
        stable_key=round(self.margin(float(times[0])),9) if len(times)==1 else None
        if stable_key is not None and stable_key in self.cache:return self.cache[stable_key]
        ba=np.zeros(self.s.shape,np.float32);sa=np.zeros_like(ba);mi=np.zeros_like(ba);ga=np.zeros_like(ba)
        for u in times:
            opacity=self.opacity(float(u))
            if opacity<=0:continue
            margin=self.margin(float(u))
            a,m=self.sample(margin,float(u));shadow,_=self.sample(margin,float(u),True)
            # Subframe fill over opaque hard shadow, in premultiplied linear light.
            ba+=(a-m)*opacity;mi+=m*opacity
            sa+=shadow*(1-a)*opacity;ga+=a*opacity
        ba/=len(times);mi/=len(times);sa/=len(times);ga/=len(times)
        alpha=np.clip(ba+mi+sa,0,1)
        premul=ba[...,None]*self.base+mi[...,None]*self.pigment+sa[...,None]*self.shadow
        # Linear glow convolution commutes with temporal averaging. Screen is applied
        # at compositing time. This is a documented approximation to native Deep Glow.
        down=8
        full=Image.new('F',(self.W,self.H));full.paste(Image.fromarray(ga),(0,self.y0))
        small=np.asarray(full.resize((max(1,self.W//down),max(1,self.H//down)),Image.Resampling.BILINEAR))
        radius=1000*self.scale/down
        glow=sum(weight*gaussian_filter(small,sigma=max(.5,radius*f),mode='constant')
                 for f,weight in [(.012,.38),(.08,.34),(.34,.28)])*.3
        glow=np.asarray(Image.fromarray(glow.astype(np.float32)).resize((self.W,self.H),Image.Resampling.BILINEAR))
        result=(premul,alpha,glow)
        if stable_key is not None:
            if len(self.cache)>1:self.cache.clear()
            self.cache[stable_key]=result
        return result


class Renderer:
    def __init__(self,scene):
        self.scene=scene
        for key in ('width','height','fps','duration','layers'):
            if key not in scene:raise ValueError(f'Missing {key}')
        if not scene['layers']:raise ValueError('Provide at least one text layer')
        if any(scene[k]<=0 for k in ['width','height','fps','duration']):raise ValueError('Dimensions/timing must be positive')
        if scene['width']%2 or scene['height']%2:raise ValueError('Use even output dimensions')
        if scene.get('motion_blur',True) is not True:raise ValueError('Motion blur is mandatory')
        self.W=scene['width'];self.H=scene['height']
        self.bg=linear(rgb(scene.get('background','#000000')))
        self.layers=[Layer(cfg,scene,i) for i,cfg in enumerate(scene['layers'])]

    def frame(self,t):
        dest=np.empty((self.H,self.W,3),np.float32);dest[:]=self.bg
        for layer in self.layers:
            premul,a,glow=layer.render(t)
            g=np.clip(glow[...,None]*layer.base,0,1)
            dest=1-(1-dest)*(1-g) # screen, in linear light
            view=dest[layer.y0:layer.y1]
            view[:]=premul+view*(1-a[...,None])
        return Image.fromarray(np.uint8(np.clip(srgb(dest),0,1)*255+.5))

    def report(self):
        return dict(renderer='shaped-ribbon/path-arc-length',native_AE=False,
                    motion_blur=dict(enabled=True,shutter_angle=180,shutter_phase=0,min_samples=16,adaptive_limit=128,temporal_linear_premultiplied=True),
                    deep_glow=dict(native=False,radius=1000,exposure=.3,blend='screen',method='multi-scale convolution approximation'),
                    layers=[dict(text=l.text,font=l.font_key,style=l.style,start=l.start,arrival=l.arrival,
                                 exit_start=l.exit_start,exit_arrival=l.exit_arrival,
                                 hand_draw_amount=l.hand_draw_amount,halftone_radius=l.cfg.get('halftone_radius',1.05),
                                 incoming_direction='right' if l.source>l.target else 'left',
                                 target_margin=float(l.target),sample_counts=sorted(set(l.sample_counts))) for l in self.layers])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true');ap.add_argument('--scene',type=Path)
    ap.add_argument('--out',type=Path);ap.add_argument('--still',type=float,help='Output PNG at timeline seconds')
    ap.add_argument('--width',type=int,help='Preview/output width; preserve aspect ratio')
    args=ap.parse_args()
    if args.check:print(json.dumps(check(),ensure_ascii=False,indent=2));return
    if not args.scene or not args.out:ap.error('--scene and --out required')
    check('')
    scene=json.loads(args.scene.read_text())
    if args.width:
        scene['height']=round(scene['height']*args.width/scene['width']/2)*2;scene['width']=args.width
    renderer=Renderer(scene);args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.still is not None:
        if args.out.suffix.lower()!='.png':raise ValueError('Use .png for still output')
        renderer.frame(args.still).save(args.out)
    else:
        if args.out.suffix.lower()!='.mp4':raise ValueError('Bundled renderer exports opaque MP4 or PNG; no alpha codec claim')
        cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{renderer.W}x{renderer.H}',
             '-r',str(scene['fps']),'-i','-','-an','-c:v','libx264','-crf','17','-preset','fast',
             '-pix_fmt','yuv420p','-movflags','+faststart',str(args.out)]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        total=math.ceil(scene['duration']*scene['fps'])
        try:
            for f in range(total):
                p.stdin.write(renderer.frame(f/scene['fps']).tobytes())
                if f%30==0:print(f'frame {f}/{total}',flush=True)
            p.stdin.close()
            if p.wait()!=0:raise RuntimeError('FFmpeg failed')
        except BaseException:
            p.kill();p.wait();raise
    args.out.with_suffix('.render.json').write_text(json.dumps(renderer.report(),ensure_ascii=False,indent=2))
    print(args.out)


if __name__=='__main__':main()

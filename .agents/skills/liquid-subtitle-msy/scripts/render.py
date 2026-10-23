#!/usr/bin/env python3
"""Reference-style fallback; does not execute LiquidGlass.aex or Deep Glow 2."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features
from scipy.ndimage import gaussian_filter, map_coordinates
from motion import WidthTrack

ROOT = Path(__file__).resolve().parents[1]


def probe(path):
    data = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
    v = next(s for s in data['streams'] if s['codec_type']=='video')
    return v['width'], v['height']


class Renderer:
    def __init__(self, scene, width, height):
        if not features.check_feature('raqm'):
            raise RuntimeError('Pillow RAQM is required for connected Persian shaping')
        self.scene, self.w, self.h = scene, width, height
        self.k = width/1080
        self.fps = scene.get('fps',30)
        self.cues = scene['cues']
        if not self.cues:
            raise ValueError('At least one timed cue is required')
        self.font = ImageFont.truetype(str(ROOT/'assets/fonts'/scene.get('font','TRADO.TTF')),
                    max(1,round(scene.get('font_size',78)*self.k)),layout_engine=ImageFont.Layout.RAQM)
        self.cx = width/2
        self.cy = height*1356/1920
        self.ph = scene.get('pill_height',82)*self.k
        self.texts, widths = [], []
        prev_end = -math.inf
        for c in self.cues:
            if c['start'] < prev_end-1e-7 or c['end'] <= c['start']:
                raise ValueError('Cues must be ordered, non-overlapping and positive-duration')
            if c['start'] < 0 or c['end'] > scene['duration']+1e-7:
                raise ValueError('Cues must lie within scene duration')
            if not 1 <= len(c['text'].split()) <= 5:
                raise ValueError('Each cue must contain one to five words; preserve ZWNJ')
            prev_end = c['end']
            bbox = self.font.getbbox(c['text'], direction='rtl',language='fa')
            tw = max(self.font.getlength(c['text'],direction='rtl',language='fa'),bbox[2]-bbox[0])
            pw = max(130*self.k,tw+52*self.k)
            if pw > .9*width:
                raise ValueError('Cue too wide: regroup the text, do not squeeze glyphs')
            widths.append(pw)
            # A local centered glyph mask; shape and glyphs are independently composited.
            size = (math.ceil(pw+100*self.k),math.ceil(180*self.k))
            mask = Image.new('L',size)
            d = ImageDraw.Draw(mask)
            d.text(((size[0]-(bbox[2]-bbox[0]))/2-bbox[0],
                    (size[1]-(bbox[3]-bbox[1]))/2-bbox[1]),c['text'],font=self.font,
                    direction='rtl',language='fa',fill=255)
            self.texts.append(mask)
        self.widths = widths
        self.track = WidthTrack(self.cues,widths,self.fps)

    def cue_index(self,t):
        return next((i for i,c in enumerate(self.cues) if c['start'] <= t < c['end']),None)

    def pattern(self,t):
        y,x=np.mgrid[:self.h,:self.w]
        q=(np.sin((x+170*self.k*t)/(90*self.k))+1)/2
        r=np.clip(60+110*q+30*y/self.h,0,255)
        g=np.clip(35+80*(1-q)+45*y/self.h,0,255)
        b=np.clip(55+65*np.sin(y/(170*self.k)+t)**2,0,255)
        arr=np.stack([r,g,b],-1).astype('uint8')
        return Image.fromarray(arr).convert('RGBA')

    def frame(self, source, t, underlay=None):
        base=(underlay or source).convert('RGBA')
        i=self.cue_index(t)
        if i is None:
            return base
        width=self.track.at(t)
        if width < self.ph or width > self.w*.98:
            raise ValueError('Spring exceeds safe geometry; regroup cues or adjust layout explicitly')
        k=self.k
        margin=math.ceil(65*k)
        left=math.floor(self.cx-width/2)-margin
        top=math.floor(self.cy-self.ph/2)-margin
        rw=math.ceil(width)+2*margin;rh=math.ceil(self.ph)+2*margin
        yy,xx=np.mgrid[:rh,:rw]
        x=xx+left-self.cx; y=yy+top-self.cy
        radius=self.ph/2
        qx=np.abs(x)-width/2+radius
        qy=np.abs(y)-self.ph/2+radius
        dist=np.sqrt(np.maximum(qx,0)**2+np.maximum(qy,0)**2)+np.minimum(np.maximum(qx,qy),0)-radius
        alpha=np.clip(.5-dist,0,1)
        # Shape shadow is separate and soft. Its source never feeds back into refraction.
        shadow=Image.fromarray((alpha*100).astype('uint8')).filter(ImageFilter.GaussianBlur(18*k))
        sh=Image.new('RGBA',(rw,rh),(0,0,0,0));sh.putalpha(shadow)
        base.alpha_composite(sh,(left,top+round(12*k)))
        # Sample the current original presenter frame in absolute composition coordinates.
        # This keeps the video texture live even while the pill changes width or position.
        gy,gx=np.gradient(dist)
        edge=np.exp(-np.abs(dist)/(9*k))
        dx=gx*(9*k*edge)+2*k*np.sin(y/(14*k))*alpha
        dy=gy*(9*k*edge)+2*k*np.sin(x/(95*k)+t)*alpha
        sy=np.clip(yy+top+dy,0,self.h-1);sx=np.clip(xx+left+dx,0,self.w-1)
        src=np.asarray(source.convert('RGB'),dtype=float)/255
        col=np.stack([map_coordinates(src[...,j],[sy,sx+(j-1)*.4*k*edge],order=1,mode='nearest') for j in range(3)],-1)
        col=gaussian_filter(col,sigma=(.45*k,.45*k,0))*.9
        rim=np.exp(-(dist/(1.15*k))**2)
        light=np.clip(-gx*.5-gy*.75+.25,0,1)*rim
        col=np.clip(col+light[...,None]*.73+rim[...,None]*.09,0,1)
        glass=Image.fromarray(np.dstack([(col*255).astype('uint8'),(alpha*255).astype('uint8')]),'RGBA')
        base.alpha_composite(glass,(left,top))
        glyph=self.texts[i]
        ar=np.asarray(glyph,dtype=float)/255
        ty,tx=np.mgrid[:ar.shape[0],:ar.shape[1]]
        # Weak hand-drawn / fine turbulence on contours, without word transforms.
        disp=.38*k*np.sin(tx/(11*k)+t*2*math.pi*5)*np.cos(ty/(8*k)-t*6)
        ar=map_coordinates(ar,[ty+disp,tx+.28*k*np.sin(ty/(7*k)+t*7)],order=1,mode='constant')
        glyph=Image.fromarray(np.uint8(np.clip(ar,0,1)*255))
        radius=max(1,math.ceil(k))
        expanded=glyph.filter(ImageFilter.MaxFilter(radius*2+1))
        stroke=Image.blend(glyph,expanded,min(1,k/radius))
        layer=Image.new('RGBA',glyph.size,(0,0,0,0))
        def color_layer(mask,color):
            z=Image.new('RGBA',mask.size,color);z.putalpha(mask);return z
        off1=round(3.5*k/math.sqrt(2));off2=round(5*k/math.sqrt(2))
        # First hard shadow then second soft shadow, matching the declared effect order.
        layer.alpha_composite(color_layer(stroke,(0,0,0,255)),(off1,off1))
        layer.alpha_composite(color_layer(stroke.filter(ImageFilter.GaussianBlur(7*k)),(0,0,0,255)),(off2,off2))
        layer.alpha_composite(color_layer(stroke,(0,0,0,255)))
        layer.alpha_composite(color_layer(glyph,(255,255,255,255)))
        # A deliberately faint diffuse appearance approximation, not the proprietary plugin.
        glow=Image.fromarray(np.uint8(gaussian_filter(np.asarray(glyph,dtype=float),18*k)*.007))
        layer=Image.alpha_composite(color_layer(glow,(255,255,255,255)),layer)
        base.alpha_composite(layer,(round(self.cx-glyph.width/2),round(self.cy-glyph.height/2)))
        return base


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scene',type=Path,required=True)
    p.add_argument('--source',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--width',type=int)
    p.add_argument('--still',type=float)
    p.add_argument('--test-pattern',action='store_true')
    a=p.parse_args()
    scene=json.loads(a.scene.read_text())
    if not a.source and not a.test_pattern:
        p.error('Provide a clean presenter source or --test-pattern')
    sw,sh=probe(a.source) if a.source else (1080,1920)
    w=a.width or sw;h=round(sh*w/sw)
    renderer=Renderer(scene,w,h)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    decoder=None
    if a.source:
        command=['ffmpeg','-v','error','-i',str(a.source),'-vf',f'scale={w}:{h},fps={renderer.fps}',
                 '-f','rawvideo','-pix_fmt','rgb24','-']
        if a.still is not None:
            command=['ffmpeg','-v','error','-ss',str(a.still),'-i',str(a.source),'-vf',f'scale={w}:{h}',
                     '-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']
        decoder=subprocess.Popen(command,stdout=subprocess.PIPE)
    def source_frame(t):
        if decoder:
            raw=decoder.stdout.read(w*h*3)
            if len(raw)!=w*h*3:raise RuntimeError('Source ended before requested scene duration')
            return Image.frombytes('RGB',(w,h),raw).convert('RGBA')
        return renderer.pattern(t)
    fps=renderer.fps
    try:
        if a.still is not None:
            renderer.frame(source_frame(a.still),a.still).save(a.out)
        else:
            command=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}',
                     '-r',str(fps),'-i','-']
            if a.source:command+=['-i',str(a.source),'-map','0:v','-map','1:a?']
            command+=['-t',str(scene['duration']),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p']
            if a.source:command+=['-c:a','aac','-b:a','192k']
            encoder=subprocess.Popen(command+[str(a.out)],stdin=subprocess.PIPE)
            try:
                for n in range(math.ceil(scene['duration']*fps-1e-8)):
                    t=n/fps
                    encoder.stdin.write(renderer.frame(source_frame(t),t).convert('RGB').tobytes())
            finally:
                encoder.stdin.close()
                if encoder.wait():raise RuntimeError('FFmpeg encode failed')
    finally:
        if decoder:
            decoder.stdout.close();decoder.wait()
    if a.still is None:
        # A successful encoder exit alone is not proof of a playable MP4.
        if probe(a.out)!=(w,h):
            raise RuntimeError('Output geometry validation failed')
        subprocess.run(['ffmpeg','-v','error','-i',str(a.out),'-f','null','-'],check=True)
    report={'native_liquidglass':False,'native_deep_glow_2':False,'output_size':[w,h],
            'font':scene.get('font','TRADO.TTF'),'width_track':renderer.track.report(),
            'warning':'Visual approximation; does not execute .aex or proprietary Deep Glow 2'}
    a.out.with_suffix('.render.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'out':str(a.out),'size':[w,h],'native_plugins':False}))


if __name__=='__main__':
    main()

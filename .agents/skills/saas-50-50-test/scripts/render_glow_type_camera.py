#!/usr/bin/env python3
"""Five-second SaaS study: glass, pointer variants, glow typing and camera cuts.

Pillow/numpy/scipy/FFmpeg. Authored virtual-camera reconstruction, not native AE.
"""
import argparse
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/variants/glow-type-camera-v1'
W, H, WW, HH, FPS = 1080, 960, 2160, 1920, 30
CX, CY, FIELD_Y, TEXT_X = 1080., 960., 902., 760.
PUNCH, TYPE_IN, TYPE_OUT = 44/30, 48/30, 100/30
PAN_IN, PAN_OUT, MATCH_CUT = 100/30, 122/30, 111/30


def clamp(u):
    return min(1., max(0., float(u)))


def influence_ease(u, influence):
    """Zero-endpoint-speed scalar mapping: x handles I and1-I; y handles0 and1."""
    u = clamp(u)
    if u == 0 or u == 1:
        return u
    lo, hi = 0., 1.
    h = influence/100
    for _ in range(36):
        s = (lo+hi)/2
        x = 3*(1-s)**2*s*h + 3*(1-s)*s*s*(1-h) + s**3
        if x < u:
            lo = s
        else:
            hi = s
    s = (lo+hi)/2
    return 3*s*s - 2*s**3


def color(value):
    s = value.lstrip('#')
    if len(s) != 6 or any(c not in '0123456789abcdefABCDEF' for c in s):
        raise ValueError('Use a six-digit brand hue')
    return tuple(int(s[i:i+2],16) for i in (0,2,4))


@lru_cache(maxsize=20)
def font(size, bold=False):
    return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf', max(1,int(size)))


class GlassStage:
    """Code-native abstract study stage and approximate refractive glass panel."""
    def __init__(self, accent):
        self.accent = accent
        y,x = np.mgrid[0:HH,0:WW].astype(np.float32)
        u,v = x/WW,y/HH
        rgb = np.zeros((HH,WW,3),np.float32)
        rgb[:] = [8,15,36]
        rgb += np.exp(-(((u-.29)/.28)**2+((v-.28)/.38)**2))[...,None]*np.array([17,62,90])
        rgb += np.exp(-(((u-.73)/.30)**2+((v-.64)/.32)**2))[...,None]*np.array([47,25,84])
        ribbon = np.exp(-((v-(.54+.11*np.sin(u*5.5)))/.06)**2)
        rgb += ribbon[...,None]*np.array([4,18,27])
        self.world = Image.fromarray(np.clip(rgb,0,255).astype('uint8')).convert('RGBA')
        lines = Image.new('RGBA',(WW,HH))
        d=ImageDraw.Draw(lines)
        for i in range(7):
            yy=930+i*62
            d.arc((340,yy-560,1940,yy+560),193,335,fill=(*accent,10),width=2)
        self.world.alpha_composite(lines.filter(ImageFilter.GaussianBlur(2)))
        box=(650,840,1510,1130)
        shadow=Image.new('RGBA',(WW,HH))
        ImageDraw.Draw(shadow).rounded_rectangle((650,863,1510,1153),50,fill=(0,0,0,95))
        self.world.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
        patch=self.world.crop(box).filter(ImageFilter.GaussianBlur(17))
        # Slight local resampling and tint approximate glass; not an optical shader/native plugin.
        patch=patch.resize((880,302),Image.Resampling.BICUBIC).crop((10,6,870,296))
        wash=Image.new('RGBA',patch.size,(126,204,225,25));patch=Image.alpha_composite(patch,wash)
        mask=Image.new('L',patch.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,859,289),48,fill=230)
        self.world.paste(patch,box[:2],mask)
        d=ImageDraw.Draw(self.world)
        d.rounded_rectangle(box,48,outline=(219,247,255,110),width=2)
        d.rounded_rectangle((655,845,1505,1125),45,outline=(239,254,255,40),width=1)
        d.rounded_rectangle((672,866,1488,938),27,fill=(247,253,255,255),outline=(224,250,255,255),width=2)
        d.rounded_rectangle((692,883,740,923),12,fill=(*accent,255))
        d.line([(707,914),(716,893),(725,914),(721,906),(710,906)],fill=(6,35,57,255),width=3)
        d.text((688,791),'STUDY COPILOT',font=font(17,True),fill=(204,236,248,220))
        d.rounded_rectangle((1342,889,1403,916),13,fill=(197,242,250,255))
        d.ellipse((1363,896,1376,909),outline=(29,114,137,255),width=2)
        d.line((1373,906,1381,912),fill=(29,114,137,255),width=2)
        d.ellipse((1430,891,1447,908),outline=(20,42,57,255),width=2)
        d.line((1444,905,1452,913),fill=(20,42,57,255),width=3)
        # Under-glass utility marks, intentionally quiet like the reference.
        for i in range(5):
            xx=850+i*108
            d.rounded_rectangle((xx-8,1026,xx+8,1042),5,outline=(213,245,253,65),width=2)
            if i==2:
                d.line((xx,1021,xx,1048),fill=(213,245,253,80),width=2)
                d.line((xx-13,1034,xx+13,1034),fill=(213,245,253,80),width=2)
        self.world=self.world.convert('RGB')


class GlowTypeWriter:
    """Reveal a whole prefix; moving luminous head and tint trail share one progress."""
    def __init__(self,text,accent):
        self.text,self.accent=text,accent
        self.advances=[float(font(32).getlength(text[:i])) for i in range(len(text)+1)]
        self.width=self.advances[-1]

    def state(self,t):
        e=influence_ease((t-TYPE_IN)/(TYPE_OUT-TYPE_IN),75)
        head=e*self.width
        count=int(np.searchsorted(self.advances,head+1e-6,side='right')-1)
        return e,head,min(len(self.text),max(0,count))

    @lru_cache(maxsize=256)
    def glyph_sprite(self,count,scale,placeholder=False):
        text='Ask for a study plan...' if placeholder else self.text[:count]
        f=font(round(32*scale))
        w=max(4,math.ceil(f.getlength(text))+12);h=math.ceil(52*scale)
        mask=Image.new('L',(w,h));ImageDraw.Draw(mask).text((3,0),text,font=f,fill=255,anchor='lt')
        return mask

    @lru_cache(maxsize=16)
    def head_sprite(self,scale):
        w,h=math.ceil(104*scale),math.ceil(122*scale)
        mask=Image.new('L',(w,h));d=ImageDraw.Draw(mask);cx=w/2;cy=h/2
        d.rounded_rectangle((cx-2.3*scale,cy-17*scale,cx+2.3*scale,cy+17*scale),2*scale,fill=255)
        core=Image.new('RGBA',(w,h),(*self.accent,255));core.putalpha(mask)
        glow=Image.new('RGBA',(w,h),(*self.accent,255))
        glow.putalpha(mask.filter(ImageFilter.GaussianBlur(11*scale)).point(lambda a:min(255,round(a*3.8))))
        tight=Image.new('RGBA',(w,h),(*self.accent,255));tight.putalpha(mask.filter(ImageFilter.GaussianBlur(3.8*scale)))
        glow=Image.alpha_composite(glow,tight);glow=Image.alpha_composite(glow,core)
        return glow

    def draw(self,frame,t,camera):
        scale,shiftx,shifty=camera
        project=lambda x,y:(W/2+(x-CX)*scale+shiftx,H/2+(y-FIELD_Y)*scale+shifty)
        e,head,count=self.state(t)
        placeholder=t<TYPE_IN
        mask=self.glyph_sprite(count,scale,placeholder)
        px,py=project(TEXT_X,889)
        # A prefix is laid out as one shaped string; production RTL requires grapheme shaping/masks.
        a=np.asarray(mask,dtype=np.float32)/255
        ink=np.full((*a.shape,3),[26,46,63],np.float32)
        if placeholder:
            ink[:]=[133,153,165]
        elif count:
            xx=np.arange(a.shape[1],dtype=np.float32)
            distance=head*scale-xx
            tint=np.where(distance>=0,np.exp(-distance/(45*scale)),0)*.88
            ink=ink*(1-tint[None,:,None])+np.array(self.accent)*(tint[None,:,None])
        sprite=Image.fromarray(np.clip(ink,0,255).astype('uint8')).convert('RGBA');sprite.putalpha(mask)
        frame.paste(sprite,(round(px),round(py)),sprite)
        if TYPE_IN<=t<TYPE_OUT+.12:
            x,y=project(TEXT_X+head,FIELD_Y-2)
            glow=self.head_sprite(scale);frame.paste(glow,(round(x-glow.width/2),round(y-glow.height/2)),glow)


class FollowCamera:
    """Same typed progress controls the tracking camera; scale cuts remain true edits."""
    def __init__(self,writer):
        self.writer=writer
        self.end_x=TEXT_X+60+.96*writer.width
        self.anchor_start=(CX-self.end_x)*2.5

    def state(self,t):
        if t<PUNCH:
            return 1.,0.,FIELD_Y-CY
        e=self.writer.state(t)[0]
        if t<PAN_IN:
            cx=TEXT_X+60+.96*self.writer.width*e
            return 2.5,(CX-cx)*2.5,0.
        if t<PAN_OUT:
            p=influence_ease((t-PAN_IN)/(PAN_OUT-PAN_IN),100)
            scale=2.5 if t<MATCH_CUT else 1.
            # Same projected anchor and lateral direction through the scale jump.
            return scale,self.anchor_start*(1-p),0.
        return 1.,0.,0.


class ReferenceCursor:
    """Independent source-measured position fits with estimated unwrapped orientation."""
    def __init__(self,kind):
        self.kind=kind
        rows=json.loads((ASSETS/'cursor-variants.json').read_text())['entry' if kind==1 else 'exit']
        self.rows=np.array(rows,float)
        self.curve=PchipInterpolator(self.rows[:,0],self.rows[:,1:],axis=0)
        data=json.loads((ROOT/'assets/variants/white-icon-dock-v1/cursor-measurements.json').read_text())
        poly=np.array(data['polygon_centered'])
        self.sprite=Image.new('RGBA',(168*3,168*3));d=ImageDraw.Draw(self.sprite)
        pts=[tuple((p+84)*3) for p in poly];d.polygon(pts,fill='black');d.line(pts+[pts[0]],fill='white',width=5*3,joint='curve');d.polygon(pts,fill='black')
        self.sprite=self.sprite.resize((168,168),Image.Resampling.LANCZOS)

    def state(self,t):
        if self.kind==1:
            if t<.20 or t>1.60:return None
            f=6+clamp((t-.20)/1.14)*40
            x,y,a=self.curve(f)
            x=x-320.4+240;y=y-297.6+456
            return x+(CX-W/2),y+(CY-H/2),float(a),.64,clamp((1.6-t)/.12)
        if t<4.10:return None
        f=122+clamp((t-4.10)/.88)*32;x,y,a=self.curve(f)
        x=x-803+925;y=y-317.8+500
        return x+(CX-W/2),y+(FIELD_Y-H/2),float(a),.38,1.

    def draw(self,frame,t,camera):
        st=self.state(t)
        if st is None:return
        x,y,angle,size,alpha=st;scale,dx,dy=camera
        px=W/2+(x-CX)*scale+dx;py=H/2+(y-FIELD_Y)*scale+dy
        side=max(2,round(168*size*scale));sp=self.sprite.resize((side,side),Image.Resampling.LANCZOS).rotate(-angle,Image.Resampling.BICUBIC,expand=True)
        if alpha<1:sp.putalpha(sp.getchannel('A').point(lambda a:round(a*alpha)))
        frame.paste(sp,(round(px-sp.width/2),round(py-sp.height/2)),sp)


class PeripheralFocus:
    """Independent spatial focus; separate from actual temporal motion blur."""
    def __init__(self):
        y,x=np.mgrid[0:H,0:W].astype(np.float32)
        q=np.sqrt(((x-W/2)/440)**2+((y-H/2)/350)**2)
        v=np.clip((q-.72)/.62,0,1);v=v*v*(3-2*v)
        self.mask=Image.fromarray((v*190).astype('uint8'))

    def apply(self,frame,close):
        blur=frame.filter(ImageFilter.GaussianBlur(5 if not close else 9))
        return Image.composite(blur,frame,self.mask)


def build_scene(text,accent,focus=True):
    stage=GlassStage(accent);writer=GlowTypeWriter(text,accent);camera=FollowCamera(writer)
    cursors=[ReferenceCursor(1),ReferenceCursor(2)];peripheral=PeripheralFocus()
    def scene(t):
        c=camera.state(t);scale,dx,dy=c
        # Inverse virtual-camera mapping; every stage layer uses this same projection.
        coeff=(1/scale,0,CX+(-W/2-dx)/scale,0,1/scale,FIELD_Y+(-H/2-dy)/scale)
        frame=stage.world.transform((W,H),Image.Transform.AFFINE,coeff,Image.Resampling.BILINEAR).convert('RGBA')
        writer.draw(frame,t,c)
        for cursor in cursors:cursor.draw(frame,t,c)
        if focus:frame=peripheral.apply(frame,scale>1)
        return frame.convert('RGB')
    return scene,writer,camera,cursors


def render(args):
    output=args.output.resolve()
    if output.exists() or ROOT in output.parents or output.suffix.lower()!='.mp4':raise ValueError('Use a new MP4 outside skill sources')
    output.parent.mkdir(parents=True,exist_ok=True)
    scene,writer,camera,cursors=build_scene(args.text,color(args.color),not args.no_focus)
    proc=subprocess.Popen(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
    counts=[]
    try:
        for f in range(150):
            t=f/FPS;half=.5/FPS;c0=camera.state(t);c1=camera.state(t+half)
            # A hard scale edit is not a continuous zoom; never smear its two shots together.
            same_leg=not any(t<cut<=t+half for cut in [PUNCH,MATCH_CUT])
            travel=abs(c1[1]-c0[1])+abs(writer.state(t+half)[1]-writer.state(t)[1])*c0[0]
            for cursor in cursors:
                a,b=cursor.state(t),cursor.state(t+half)
                if a is not None and b is not None:travel=max(travel,math.hypot(a[0]-b[0],a[1]-b[1])*c0[0]+abs(a[2]-b[2])*math.pi/180*45)
            n=min(128,max(16,math.ceil(travel/.65)));counts.append(n)
            accum=np.zeros((H,W,3),np.float32)
            for j in range(n):
                st=t+(j+.5)/n*half
                if not same_leg:st=min(st,min(cut for cut in [PUNCH,MATCH_CUT] if t<cut<=t+half)-1e-9)
                accum+=np.asarray(scene(st),np.float32)
            proc.stdin.write(np.clip(np.rint(accum/n),0,255).astype('uint8').tobytes())
            if f%15==0:print(f'frame {f}/150, samples {n}',flush=True)
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('FFmpeg failed')
    subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]));v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==150 and (v['width'],v['height'])==(W,H) and abs(float(info['format']['duration'])-5)<.001
    assert not any(s['codec_type']=='audio' for s in info['streams'])
    report=dict(variant='glow-type-camera-v1',duration=5,fps=30,frames=150,width=W,height=H,text=args.text,color=args.color,audio=False,presenter=False,speech_sync_tested=False,status='awaiting explicit user review',native_AE_executed=False,background='authored code-native navy/cyan abstract; image generation unavailable',glass='coded approximate refractive material',graphs={'type_and_follow':[75,75],'pan_match':[100,100]},cuts={'detail_frame':44,'peak_speed_match_frame':111,'detail_time':PUNCH,'match_time':MATCH_CUT},blur={'angle':180,'phase':0,'minimum_samples':16,'adaptive_limit':128,'actual_min':min(counts),'actual_max':max(counts),'method':'subframe RGB integration; cut boundaries kept separate'},sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_suffix('.mp4.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--text',default='Build my AI study plan');p.add_argument('--color',default='#48E2FF');p.add_argument('--no-focus',action='store_true');render(p.parse_args())

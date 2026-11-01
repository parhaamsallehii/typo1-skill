#!/usr/bin/env python3
"""Reusable clean RTL ribbon-on-Bezier renderer; coded approximation of AE text paths.
Requires Pillow+RAQM, numpy, scipy, fonttools and FFmpeg/ffprobe.
All path and font sizes are in output pixels. First Margin 35 is not 35 percent.
"""
import argparse,bisect,json,math,subprocess,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageFont,ImageDraw,features
from scipy.spatial import cKDTree
from scipy.ndimage import map_coordinates
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
FONTS={'saadi':'Saadi.ttf','saadi-bold':'Saadi-Bold.ttf','saadi-ultra':'Saadi-Ultra.ttf','lifta-black':'Lifta-Black.otf','lifta-bold':'Lifta-Bold.otf'}
COLORS={'cream':'#FCF0D6','red':'#B40023'}

def key_data(c,fps):
    s=float(c['start']);arr=s+2/fps
    # Hold begins when opacity reaches 100%; requested one-second default.
    e=float(c.get('exit_start',s+4/fps+float(c.get('hold',1))))
    if e<arr:raise ValueError('Exit must follow entrance')
    travel=float(c.get('entry_margin',35));out=float(c.get('exit_margin',travel))
    if abs(travel)!=35 or abs(out)!=35:
        if not c.get('explicit_margin_override'):raise ValueError('Use +/-35 unless user explicitly overrides')
    return [(s,travel),(arr,0),(e,0),(e+2/fps,out)]

def base(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return x+(y-x)*(t-a)/(b-a)
    return keys[-1][1]

def margin(t,c,fps):
    keys=key_data(c,fps);n=bisect.bisect_right([k[0] for k in keys],t)-1
    result=base(t,keys)
    if n<0:return result
    elapsed=t-keys[n][0]
    if 0<=elapsed<1:
        sample=keys[n][0]-1/(fps*10)
        velocity=0.
        for (a,x),(b,y) in zip(keys,keys[1:]):
            if a<sample<b:velocity=(y-x)/(b-a);break
        result+=velocity*.1*math.sin(elapsed*2*math.pi*2)/math.exp(6*elapsed)
    return result

def opacity(t,c,fps):
    s=float(c['start']);e=key_data(c,fps)[2][0]
    return max(0.,min(1.,(t-s)/(4/fps),(e+3/fps-t)/(3/fps))) if t>=s else 0.

class Ribbon:
    def __init__(self,c,W,H,fps):
        self.c=c;self.fps=fps
        if c.get('motion_blur',True)!=True:raise ValueError('Layer motion blur must be on')
        if not features.check('raqm'):raise RuntimeError('Pillow must include RAQM for connected Persian')
        fontpath=ROOT/'assets/fonts'/FONTS[c.get('font','saadi-ultra')]
        f=TTFont(fontpath);cmap=f.getBestCmap();f.close()
        missing=[ch for ch in c['text'] if not ch.isspace() and ch not in '\u200c\u200d\u200e\u200f' and ord(ch) not in cmap]
        if missing:raise ValueError('Missing glyphs; do not silently substitute: '+repr(missing))
        font=ImageFont.truetype(str(fontpath),int(c.get('font_size',130)),layout_engine=ImageFont.Layout.RAQM)
        l,top,right,bottom=font.getbbox(c['text'],anchor='ls',direction='rtl',language='fa')
        pad=5
        im=Image.new('L',(right-l+2*pad,bottom-top+2*pad))
        ImageDraw.Draw(im).text((pad-l,pad-top),c['text'],font=font,anchor='ls',direction='rtl',language='fa',fill=255)
        self.alpha=np.asarray(im,dtype=np.float32)/255
        self.top=top-pad;self.sw,self.sh=im.size
        points=np.asarray(c['path'],float)
        if points.shape!=(4,2):raise ValueError('Path must be four cubic Bezier control points')
        u=np.linspace(0,1,4097)[:,None]
        curve=(1-u)**3*points[0]+3*(1-u)**2*u*points[1]+3*(1-u)*u*u*points[2]+u**3*points[3]
        delta=np.gradient(curve,axis=0);norm=np.linalg.norm(delta,axis=1)
        if np.min(norm)<1e-8:raise ValueError('Degenerate path tangent')
        tangent=delta/norm[:,None]
        self.length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
        self.target=(self.length[-1]-self.sw)/2+float(c.get('target_offset',0))
        if self.sw+70>self.length[-1]:raise ValueError('Text too long for path; shorten phrase or author a larger path; never squash glyphs')
        # Map connected, shaped text ribbon by normal coordinates. Guard endcaps
        # so out-of-path pixels do not become long stretched edge streaks.
        d=max(abs(self.top),abs(bottom+pad))+4
        x0=max(0,int(curve[:,0].min()-d));x1=min(W,int(curve[:,0].max()+d)+1)
        y0=max(0,int(curve[:,1].min()-d));y1=min(H,int(curve[:,1].max()+d)+1)
        if x1<=x0 or y1<=y0:raise ValueError('Path outside frame')
        self.box=(x0,y0,x1,y1)
        yy,xx=np.mgrid[y0:y1,x0:x1]
        coords=np.c_[xx.ravel(),yy.ravel()]
        _,idx=cKDTree(curve).query(coords)
        v=coords-curve[idx];tan=tangent[idx];normal=np.c_[-tan[:,1],tan[:,0]]
        self.s=(self.length[idx]+np.sum(v*tan,axis=1)).reshape(xx.shape).astype(np.float32)
        self.n=(np.sum(v*normal,axis=1).reshape(xx.shape)-self.top).astype(np.float32)
        self.valid=(self.n>=0)&(self.n<self.sh-1)&(self.s>=0)&(self.s<=self.length[-1])
        self.coords_y=self.n[self.valid]
        color=COLORS[c.get('color','cream')]
        self.color=np.array([int(color[i:i+2],16) for i in [1,3,5]],dtype=np.float32)/255
        self.counts=[]
    def alpha_at(self,t):
        a=np.zeros(self.s.shape,np.float32);o=opacity(t,self.c,self.fps)
        if o<=0:return a
        x=self.s[self.valid]-self.target-margin(t,self.c,self.fps)
        a[self.valid]=map_coordinates(self.alpha,[self.coords_y,x],order=1,mode='constant',cval=0,prefilter=False)*o
        return a
    def render(self,t):
        probes=[margin(t+u*.5/self.fps,self.c,self.fps) for u in np.linspace(0,1,9)]
        distance=sum(abs(b-a) for a,b in zip(probes,probes[1:]))
        count=min(128,max(16,math.ceil(distance/.5)))
        self.counts.append(count)
        # Same alpha/color for all exposure samples is analytically equivalent.
        if distance<1e-9 and opacity(t,self.c,self.fps)==opacity(t+.5/self.fps,self.c,self.fps):return self.alpha_at(t)
        result=np.zeros(self.s.shape,np.float32)
        for i in range(count):result+=self.alpha_at(t+(i+.5)/count*.5/self.fps)
        return result/count

def validate(scene):
    fps=float(scene['fps'])
    if fps<=0 or scene['width']<=0 or scene['height']<=0 or scene['duration']<=0:raise ValueError('Invalid dimensions/timing')
    layers=scene['layers']
    if len(layers)!=2:raise ValueError('Exactly two speech-matched phrases required')
    demo=scene.get('demo',False)
    if not demo and not scene.get('speech_evidence'):raise ValueError('Production requires actual timed speech evidence; a request time alone is not a transcript')
    if not demo and any(c.get('speech_verified') is not True for c in layers):raise ValueError('Verify each phrase against actual speech before render')
    if not demo and layers[1]['start']<layers[0]['start']:raise ValueError('Second phrase must follow first')
    for c in layers:key_data(c,fps)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('scene',type=Path);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();cfg=json.loads(args.scene.read_text());validate(cfg)
    W,H=int(cfg['width']),int(cfg['height']);fps=float(cfg['fps']);duration=float(cfg['duration'])
    bg=Path(cfg['background']);bg=bg if bg.is_absolute() else args.scene.parent/bg
    still=bg.suffix.lower() in ['.png','.jpg','.jpeg','.webp']
    count=round(duration*fps)
    if still:
        im=Image.open(bg).convert('RGB')
        if im.size!=(W,H):raise ValueError('Background must match output dimensions; do not stretch presenter')
        frame=np.asarray(im,dtype=np.float32)/255;reader=None
    else:
        reader=subprocess.Popen(['ffmpeg','-v','error','-i',str(bg),'-an','-vf',f'fps={fps}','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
        info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(bg)]))['streams'][0]
        if (info['width'],info['height'])!=(W,H):raise ValueError('Source dimensions must match scene')
    layers=[Ribbon(c,W,H,fps) for c in cfg['layers']]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    temp=args.output.with_name(args.output.stem+'-silent.mp4')
    writer=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
    try:
        for i in range(count):
            if reader:
                data=reader.stdout.read(W*H*3)
                if len(data)!=W*H*3:raise ValueError('Source shorter than requested duration; no freeze/loop permitted')
                frame=np.frombuffer(data,np.uint8).reshape(H,W,3).astype(np.float32)/255
            result=frame.copy()
            for layer in layers:
                a=layer.render(i/fps)[...,None];x0,y0,x1,y1=layer.box
                result[y0:y1,x0:x1]=result[y0:y1,x0:x1]*(1-a)+a*layer.color
            writer.stdin.write(np.clip(result*255+.5,0,255).astype(np.uint8).tobytes())
        writer.stdin.close()
        if writer.wait()!=0:raise RuntimeError('Encoder failed')
    finally:
        if reader:reader.stdout.close();reader.terminate();reader.wait()
        if writer.poll() is None:writer.terminate();writer.wait()
    if still:temp.replace(args.output)
    else:
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-i',str(bg),'-map','0:v:0','-map','1:a?','-c','copy','-t',str(duration),'-movflags','+faststart',str(args.output)],check=True)
        temp.unlink()
    report={'renderer':'coded shaped-ribbon approximation; not native AE glyph layout','demo':cfg.get('demo',False),'frames':count,'fps':fps,'width':W,'height':H,'duration':count/fps,'motion_blur':{'shutter_angle':180,'shutter_phase':0,'minimum_samples':16,'adaptive_limit':128,'max_used':max(max(l.counts) for l in layers)},'layers':[{'text':c['text'],'keys':key_data(c,fps),'fade_in_frames':4,'fade_out_frames':3} for c in cfg['layers']]}
    args.output.with_suffix('.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

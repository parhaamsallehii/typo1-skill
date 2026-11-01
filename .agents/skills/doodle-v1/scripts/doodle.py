#!/usr/bin/env python3
"""Reusable reference-inspired thin pencil-like strokes, independent of footage.
Author paths around the actual subject; no segmentation/transcription is claimed.
"""
import argparse,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.interpolate import CubicSpline
ROOT=Path(__file__).resolve().parents[1]

def smooth(u):
    u=max(0.,min(1.,u));return u*u*(3-2*u)

def sample_path(points,step=2.):
    p=np.asarray(points,dtype=float)
    if p.ndim!=2 or p.shape[1]!=2 or len(p)<2 or not np.isfinite(p).all():raise ValueError('Require at least two finite path points')
    dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    if np.any(np.diff(dist)<=0):raise ValueError('Remove repeated adjacent points')
    # Open interpolation with author-controlled landmarks, never close contour.
    s=np.linspace(0,dist[-1],max(16,int(dist[-1]/step)+1))
    xy=CubicSpline(dist,p,axis=0,bc_type='natural')(s) if len(p)>2 else np.c_[np.interp(s,dist,p[:,0]),np.interp(s,dist,p[:,1])]
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
    d=np.gradient(xy,axis=0);d/=np.maximum(np.linalg.norm(d,axis=1)[:,None],1e-8)
    return xy,arc,np.c_[-d[:,1],d[:,0]]

class Stroke:
    def __init__(self,c,cfg):
        self.c=c;self.fps=float(cfg['fps']);self.W=int(cfg['width']);self.H=int(cfg['height'])
        self.k=self.W/1080
        self.start=float(c.get('start',cfg.get('start',0)));self.end=float(c.get('end',cfg.get('end',cfg['duration'])))
        if self.end<=self.start:raise ValueError('Stroke end must follow start')
        self.xy,self.s,self.normal=sample_path(c['points'],max(.6,2*self.k))
        self.seed=int(c.get('seed',17));rng=np.random.default_rng(self.seed)
        self.phase=rng.uniform(0,2*math.pi,6)
        self.color=tuple(int(c.get('color','#F8F3E8').lstrip('#')[i:i+2],16) for i in (0,2,4))
        self.width=float(c.get('width',2.4*self.k));self.boil=float(c.get('boil',.65*self.k))
        if self.width<=0 or self.width>12*self.k:raise ValueError('Use thin strokes; thick cartoon outlines need explicit new variant')
        self.alpha=float(c.get('opacity',.95));self.cadence=self.fps
        if 'cadence' in c and abs(float(c['cadence'])-self.fps)>1e-6:
            raise ValueError('Use output FPS for one-frame lifetimes; rest gating is managed by Renderer')
        self.reposition=float(c.get('reposition',8*self.k))
        self.frame_cache={}
        self.move=np.asarray(c.get('travel',[0,0]),float)
        self.motion=float(c.get('travel_duration',4/self.fps))
        self.reveal=float(c.get('reveal',2/self.fps));self.fade=float(c.get('fade',2/self.fps))
        self.mode=c.get('mode','flash')
        if self.mode not in ['flash','draw','hold','sweep']:raise ValueError('mode: flash, draw, hold or sweep')
    def frame_style(self,t):
        # Lock one independent drawing to each output frame, including all shutter
        # samples. Never blend between drawings or repeat a five-pose bank.
        tick=math.floor(t*self.fps+1e-7)
        if tick in self.frame_cache:return self.frame_cache[tick]
        rng=np.random.default_rng(np.random.SeedSequence([self.seed,tick]))
        def field(spacing):
            knots=np.linspace(0,self.s[-1],max(4,int(self.s[-1]/(spacing*self.k))+2))
            vals=rng.uniform(-1,1,len(knots))
            return np.clip(CubicSpline(knots,vals,bc_type='natural')(self.s),-1.2,1.2)
        # Each drawing lives for ONE frame. Separate smooth redraw/relocation
        # from fine hand roughness, so lowering roughness does not freeze it.
        drift=self.boil*(.9*field(110)+.45*field(38))
        drift+=.12*self.k*field(14)
        tangent=np.c_[self.normal[:,1],-self.normal[:,0]]
        points=self.xy+self.normal*drift[:,None]+tangent*(.3*self.k*field(50))[:,None]
        center=self.xy.mean(axis=0)
        angle=rng.uniform(-.025,.025)
        rotation=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
        offset=rng.uniform(-self.reposition,self.reposition,2)
        points=(points-center)@rotation.T+center+offset
        pressure=np.clip(.88+.10*field(38),.72,1.02)
        rough=np.clip(.87+.11*field(12)+rng.uniform(-.04,.04,len(self.s)),.60,1)
        trim=(rng.uniform(0,.10),rng.uniform(.90,1))
        data=(points,pressure,rough,trim)
        if len(self.frame_cache)>8:self.frame_cache.clear()
        self.frame_cache[tick]=data
        return data
    def pose(self,t):
        age=t-self.start
        if age<0 or t>=self.end:return None
        points,_,_,trim=self.frame_style(t)
        points=points.copy()
        u=self.s/max(self.s[-1],1)
        if np.any(self.move):
            amount=1-smooth(age/max(self.motion,1e-6))
            points=points+amount*self.move
        alpha=self.alpha if self.mode=='flash' else min(1.,age/max(1/self.fps, self.fade),max(0.,(self.end-t)/max(self.fade,1e-6)))*self.alpha
        tip=1. if self.mode in ['hold','flash'] else smooth(age/max(self.reveal,1e-6))
        if self.mode=='sweep':
            head=(age/max(self.end-self.start,1e-6))*1.5
            visible=(u<=head)&(u>=head-.7)
        else:visible=(u<=min(tip,trim[1]))&(u>=trim[0])
        return points,alpha,visible
    def draw(self,canvas,t,ss):
        pose=self.pose(t)
        if pose is None:return
        pts,alpha,vis=pose
        draw=ImageDraw.Draw(canvas)
        _,pressure,rough,_=self.frame_style(t)
        for j in range(len(pts)-1):
            if not (vis[j] and vis[j+1]):continue
            # Subpixel AA comes from supersampling; slight pressure variation.
            width=max(1,round(self.width*ss*pressure[j]))
            a=round(255*alpha*rough[j])
            draw.line([tuple(pts[j]*ss),tuple(pts[j+1]*ss)],fill=self.color+(a,),width=width)

def check(cfg):
    if cfg['width']<=0 or cfg['height']<=0 or cfg['fps']<=0 or cfg['duration']<=0:raise ValueError('Invalid output')
    if len(cfg.get('drawings',[]))<3:raise ValueError('Provide at least three differently shaped drawings anchored to actual elements or edges')
    start=float(cfg.get('start',0));end=float(cfg.get('end',cfg['duration']))
    if start<0 or end<=start or end>cfg['duration']+1e-9:raise ValueError('Invalid effect interval')
    for drawing in cfg['drawings']:
        if not isinstance(drawing.get('target'),str) or not drawing['target'].strip():raise ValueError('Name the actual visible target or edge for each drawing')
        bounds=np.asarray(drawing.get('target_bounds',[]),float)
        if bounds.shape!=(4,) or not np.isfinite(bounds).all():raise ValueError('Supply inspected target_bounds [left,top,right,bottom]')
        left,top,right,bottom=bounds
        if not (0<=left<right<=cfg['width'] and 0<=top<bottom<=cfg['height']):raise ValueError('Target bounds must be inside the output')
        for stroke in drawing.get('strokes',[]):
            pts=np.asarray(stroke['points'],float)
            if pts.ndim!=2 or pts.shape[1]!=2:raise ValueError('Invalid target stroke points')
            dx=np.maximum(np.maximum(left-pts[:,0],pts[:,0]-right),0)
            dy=np.maximum(np.maximum(top-pts[:,1],pts[:,1]-bottom),0)
            margin=.05*cfg['width']+float(stroke.get('reposition',8*cfg['width']/1080))
            if np.any(np.hypot(dx,dy)>margin):raise ValueError('Doodle path is too far from its authored target bounds')
        if not drawing.get('strokes'):raise ValueError('Every drawing requires authored strokes')
        for c in drawing['strokes']:
            if c.get('mode','flash')!='flash':raise ValueError('Current Doodle V1 uses hard one-frame flash drawings only')
            if c.get('glow',False) or c.get('shadow',False):raise ValueError('This variant has no glow or shadow')
            if 'start' in c or 'end' in c:raise ValueError('Use the shared scene interval; strokes inherit the exact one-frame gate')

class Renderer:
    def __init__(self,cfg):
        check(cfg);self.cfg=cfg;self.W=int(cfg['width']);self.H=int(cfg['height']);self.ss=int(cfg.get('supersample',2))
        self.fps=float(cfg['fps'])
        self.first=math.ceil(float(cfg.get('start',0))*self.fps-1e-7)
        self.stop=math.ceil(float(cfg.get('end',cfg['duration']))*self.fps-1e-7)
        aligned_cfg=dict(cfg,start=self.first/self.fps,end=self.stop/self.fps)
        self.drawings=[[Stroke(c,aligned_cfg) for c in d['strokes']] for d in cfg['drawings']]
        self.strokes=[s for drawing in self.drawings for s in drawing]
        self.samples=int(cfg.get('samples',16))
        if not 16<=self.samples<=128:raise ValueError('Temporal samples must be 16..128')
    def drawing_index(self,t):
        frame=math.floor(t*self.fps+1e-7)
        if frame<self.first or frame>=self.stop:return None
        relative=frame-self.first
        # One drawing frame, one fully transparent rest frame, forever.
        if relative%2:return None
        return (relative//2)%len(self.drawings)
    def overlay(self,t):
        idx=self.drawing_index(t)
        if idx is None:return np.zeros((self.H,self.W,4),np.float32)
        # The entire flash is held only inside THIS frame. No cross-frame
        # shutter sampling, fade, trails or interpolation may fill a rest frame.
        frame=math.floor(t*self.fps+1e-7)
        sample_time=(frame+.25)/self.fps
        im=Image.new('RGBA',(self.W*self.ss,self.H*self.ss))
        for stroke in self.drawings[idx]:stroke.draw(im,sample_time,self.ss)
        im=im.resize((self.W,self.H),Image.Resampling.LANCZOS)
        a=np.asarray(im,dtype=np.float32)/255
        a[:,:,:3]*=a[:,:,3:4]
        return a

def main():
    p=argparse.ArgumentParser();p.add_argument('scene',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.scene.read_text());r=Renderer(cfg);W,H=r.W,r.H;fps=r.fps;duration=float(cfg['duration'])
    bg=cfg.get('background','#172936');reader=None;source=None
    if isinstance(bg,str) and bg.startswith('#'):
        frame=np.array(Image.new('RGB',(W,H),bg),np.float32)/255
    else:
        source=Path(bg);source=source if source.is_absolute() else a.scene.parent/source
        info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(source)]))
        video=next(s for s in info['streams'] if s['codec_type']=='video')
        if (video['width'],video['height'])!=(W,H):raise ValueError('Use actual source size; no silent stretching')
        reader=subprocess.Popen(['ffmpeg','-v','error','-i',str(source),'-an','-vf',f'fps={fps}','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    a.output.parent.mkdir(parents=True,exist_ok=True);temp=a.output.with_name(a.output.stem+'-silent.mp4')
    out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
    try:
        for i in range(round(duration*fps)):
            if reader:
                data=reader.stdout.read(W*H*3)
                if len(data)!=W*H*3:raise ValueError('Source too short; never loop or freeze silently')
                frame=np.frombuffer(data,np.uint8).reshape(H,W,3).astype(np.float32)/255
            ov=r.overlay(i/fps);result=ov[:,:,:3]+frame*(1-ov[:,:,3:4])
            out.stdin.write(np.uint8(np.clip(result*255+.5,0,255)).tobytes())
        out.stdin.close()
        if out.wait()!=0:raise RuntimeError('Encoding failed')
    finally:
        if reader:reader.stdout.close();reader.terminate();reader.wait()
        if out.poll() is None:out.terminate();out.wait()
    if source:
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-i',str(source),'-map','0:v:0','-map','1:a?','-c','copy','-t',str(duration),'-movflags','+faststart',str(a.output)],check=True);temp.unlink()
    else:temp.replace(a.output)
    report=dict(width=W,height=H,fps=fps,frames=round(duration*fps),duration=duration,strokes=len(r.strokes),shutter_angle=180,shutter_phase=0,samples=r.samples,automatic_segmentation=False,one_frame_lifetime=True,blank_frames_between=1,hard_cut_locations=True,target_anchored=True,local_roughness=.65,source_reference='Only thin animated doodle lines; no source scene recreation')
    a.output.with_suffix('.report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()

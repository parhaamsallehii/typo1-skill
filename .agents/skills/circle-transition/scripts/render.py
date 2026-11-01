#!/usr/bin/env python3
"""Single outward soft circular ring; exact supplied Bezier and shutter controls."""
import argparse,json,math,subprocess
from pathlib import Path
import numpy as np
from scipy.special import ndtr
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'references/profile.json').read_text())

def bezier(u,control=(.06,.88,.10,.95)):
    """Invert cubic X to evaluate Y; input progress is NOT the curve parameter."""
    u=float(np.clip(u,0,1))
    if u in (0.,1.):return u
    x1,y1,x2,y2=control;lo=0.;hi=1.
    for _ in range(45):
        s=(lo+hi)/2;one=1-s
        x=3*one*one*s*x1+3*one*s*s*x2+s**3
        if x<u:lo=s
        else:hi=s
    s=(lo+hi)/2;one=1-s
    return 3*one*one*s*y1+3*one*s*s*y2+s**3

class Ring:
    def __init__(self,cfg):
        self.W=int(cfg['width']);self.H=int(cfg['height']);self.fps=float(cfg['fps'])
        if min(self.W,self.H,self.fps,cfg['duration'])<=0:raise ValueError('Invalid output size/time')
        self.start=float(cfg['start']);self.duration=float(cfg.get('transition_duration',PROFILE['duration']))
        if self.start<0 or self.duration<=0 or self.start+self.duration>cfg['duration']+1e-7:raise ValueError('Transition must fit inside the real source duration')
        self.center=np.array(cfg.get('center',PROFILE['center']),float)*[self.W,self.H]
        if self.center.shape!=(2,) or not np.isfinite(self.center).all() or np.any(self.center<0) or np.any(self.center>[self.W,self.H]):raise ValueError('Center must be normalized inside frame')
        self.k=self.W/1080;self.width=float(cfg.get('stroke_width',PROFILE['stroke_width_at_1080']*self.k))
        self.sigma=float(cfg.get('feather_sigma',PROFILE['feather_sigma_at_1080']*self.k))
        if min(self.width,self.sigma)<=0:raise ValueError('Width/feather must be positive')
        corners=np.array([[0,0],[self.W,0],[0,self.H],[self.W,self.H]],float)
        self.farthest=float(np.linalg.norm(corners-self.center,axis=1).max())
        self.first=-self.width/2;self.last=self.farthest+self.width/2+5*self.sigma
        yy,xx=np.mgrid[:self.H,:self.W]
        self.distance=np.hypot(xx-self.center[0],yy-self.center[1]).astype(np.float32)
        color=cfg.get('color',PROFILE['color'])
        if color.upper()!=PROFILE['color']:raise ValueError('Current user version uses exact crimson #B40023')
        self.color=np.array([int(color[i:i+2],16) for i in (1,3,5)],np.float32)/255
        self.sample_counts=[]
    def radius(self,t):
        u=(t-self.start)/self.duration
        return self.first+(self.last-self.first)*bezier(u,PROFILE['easing'])
    def disc(self,r):
        if r<=0:return np.zeros_like(self.distance)
        # Soft radial boundary; seed fades smoothly from zero area near r=0.
        density=-math.expm1(-.5*(r/self.sigma)**2)
        return ndtr((r-self.distance)/self.sigma)*density
    def weights(self,t):
        """Exact subframe blend weights for outgoing, incoming and red ring."""
        if t>=self.start+self.duration:return None
        if t+.5/self.fps<=self.start:return None
        displacement=abs(self.radius(t+.5/self.fps)-self.radius(t))
        count=min(PROFILE['adaptive_sample_limit'],max(PROFILE['samples_per_frame'],math.ceil(displacement/1.5)))
        self.sample_counts.append(count)
        outgoing=np.zeros_like(self.distance);incoming=np.zeros_like(self.distance);red=np.zeros_like(self.distance)
        for i in range(count):
            time=t+(i+.5)/count*.5/self.fps
            if time<self.start:outgoing+=1/count;continue
            if time>=self.start+self.duration:incoming+=1/count;continue
            radius=self.radius(time);outer=max(0,radius+self.width/2);inner=max(0,radius-self.width/2)
            hole=self.disc(inner);alpha=np.clip(self.disc(outer)-hole,0,1)
            red+=alpha/count
            incoming+=hole*(1-alpha)/count
            outgoing+=(1-hole)*(1-alpha)/count
        return outgoing,incoming,red
    def composite(self,a,b,t):
        weights=self.weights(t)
        if weights is None:return b if t>=self.start+self.duration else a
        wa,wb,wr=weights
        return a*wa[:,:,None]+b*wb[:,:,None]+self.color*wr[:,:,None]

class Source:
    def __init__(self,value,folder,W,H,fps):
        self.proc=None;self.static=None;self.path=None
        if value.startswith('#'):self.static=np.asarray(Image.new('RGB',(W,H),value),np.float32)/255
        else:
            self.path=Path(value);self.path=self.path if self.path.is_absolute() else folder/self.path
            if self.path.suffix.lower() in ['.png','.jpg','.jpeg','.webp']:
                im=Image.open(self.path).convert('RGB')
                if im.size!=(W,H):raise ValueError('Still must match actual frame size')
                self.static=np.asarray(im,np.float32)/255
            else:
                info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(self.path)]))
                v=next(s for s in info['streams'] if s['codec_type']=='video');n,d=map(int,v['avg_frame_rate'].split('/'))
                if (v['width'],v['height'])!=(W,H) or abs(n/d-fps)>1e-4:raise ValueError('Preserve actual video dimensions and FPS')
                self.proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(self.path),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
        self.W=W;self.H=H
    def read(self):
        if self.static is not None:return self.static
        data=self.proc.stdout.read(self.W*self.H*3)
        if len(data)!=self.W*self.H*3:raise ValueError('Input too short; do not silently loop/freeze or retime clips')
        return np.frombuffer(data,np.uint8).reshape(self.H,self.W,3).astype(np.float32)/255
    def close(self):
        if self.proc:self.proc.stdout.close();self.proc.terminate();self.proc.wait()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('scene',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    cfg=json.loads(a.scene.read_text());ring=Ring(cfg);W,H=ring.W,ring.H;fps=ring.fps
    source=Source(cfg['background'],a.scene.parent,W,H,fps)
    target=Source(cfg['next_background'],a.scene.parent,W,H,fps) if cfg.get('next_background') else None
    a.output.parent.mkdir(parents=True,exist_ok=True);temp=a.output.with_name(a.output.stem+'-silent.mp4')
    writer=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
    frames=round(cfg['duration']*fps)
    try:
        for i in range(frames):
            before=source.read();after=target.read() if target else before
            result=ring.composite(before,after,i/fps)
            writer.stdin.write(np.uint8(np.clip(result*255+.5,0,255)).tobytes())
        writer.stdin.close()
        if writer.wait()!=0:raise RuntimeError('Encoding failed')
    finally:
        source.close()
        if target:target.close()
        if writer.poll() is None:writer.terminate();writer.wait()
    # A finished audio timeline can be specified. Otherwise preserve source A.
    audio=cfg.get('audio_source')
    if audio:
        audio=Path(audio);audio=audio if audio.is_absolute() else a.scene.parent/audio
    elif source.proc:audio=source.path
    if audio:
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-i',str(audio),'-map','0:v:0','-map','1:a?','-c','copy','-t',str(frames/fps),'-movflags','+faststart',str(a.output)],check=True);temp.unlink()
    else:temp.replace(a.output)
    report={'effect':'single expanding soft annulus only','color':PROFILE['color'],'easing':PROFILE['easing'],'start':ring.start,'transition_duration':ring.duration,'frames':frames,'fps':fps,'duration':frames/fps,'width':W,'height':H,'shutter_angle':180,'shutter_phase':0,'samples_per_frame':16,'adaptive_limit':128,'observed_samples_min':min(ring.sample_counts,default=16),'observed_samples_max':max(ring.sample_counts,default=16),'next_scene_provided':bool(target),'camera_animation_added':False,'audio':'explicit finished timeline or unchanged outgoing source','renderer':'coded temporal reconstruction; original AE project not supplied'}
    a.output.with_suffix('.report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()

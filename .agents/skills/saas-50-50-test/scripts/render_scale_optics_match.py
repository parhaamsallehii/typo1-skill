from PIL import Image,ImageFilter
import numpy as np,subprocess
from pathlib import Path
W,H=540,960;fps=30;cut=75
Y,X=np.mgrid[:H,:W].astype(np.float32);nx=(X-W/2)/(W/2);ny=(Y-H/2)/(H/2);rr=nx*nx+ny*ny

def bez(u,c):
 u=np.clip(u,0,1);lo=0.;hi=1.
 for _ in range(28):
  t=(lo+hi)/2;x=3*(1-t)**2*t*c[0]+3*(1-t)*t*t*c[2]+t**3
  if x<u:lo=t
  else:hi=t
 t=(lo+hi)/2;return 3*(1-t)**2*t*c[1]+3*(1-t)*t*t*c[3]+t**3
A=(.88,.04,.93,.10);B=(.06,.88,.10,.95)
def state(f):
 incoming=f>=cut
 p=bez((f-(cut-15))/15,A) if not incoming else bez((f-cut)/15,B)
 w=360+(250-360)*p if not incoming else 250+(190-250)*p
 h=110+(200-110)*p if not incoming else 200+(310-200)*p
 lens=(p if not incoming else 1-p)*.22
 xx=(X-W/2)*(1-lens*rr);yy=(Y-H/2)*(1-lens*rr)
 u=xx/w+.5;v=yy/h+.5
 # whole-scene warp, including background marker lines
 bg=np.empty((H,W,3),np.float32);bg[:]=[15,25,42]
 grid=((np.abs((xx+1000)%90-45)<.7)|(np.abs((yy+1000)%90-45)<.7));bg[grid]=[24,40,61]
 inside=(np.abs(xx)<w/2)&(np.abs(yy)<h/2)
 edge=np.minimum(w/2-np.abs(xx),h/2-np.abs(yy));alpha=np.clip(edge,0,1)*inside
 if not incoming:
  tex=np.empty_like(bg);tex[:]=[224,239,244]
  rows=(np.abs((v-.5)*h)<6)&(u>.12)&(u<.70);tex[rows]=[85,115,125]
  disk=((u-.84)*w)**2+((v-.5)*h)**2<22**2;tex[disk]=[30,179,169]
 else:
  angle=np.arctan2(v-.5,u-.5);rad=np.hypot(u-.5,v-.5)
  petal=np.cos(angle*6+rad*12)
  tex=np.stack([75+100*(petal+1)/2,85+120*(np.sin(rad*22)+1)/2,140+90*(np.cos(angle*3)+1)/2],axis=-1)
  q=np.clip((f-cut)/20,0,1);strength=(1-q)*.8
  bands=np.stack([(np.sin(u*12+v*8-q*12)+1)/2,(np.sin(u*12+v*8-q*12+2.1)+1)/2,(np.sin(u*12+v*8-q*12+4.2)+1)/2],axis=-1)*255
  tex=tex*(1-strength)+bands*strength
 return bg*(1-alpha[:,:,None])+tex*alpha[:,:,None]
out=Path(__file__).with_name('scale-optics-match-cut.mp4')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
for f in range(150):
 # phase-zero 180-degree exposure; sample whole-scene states, never blend across cut
 samples=16;acc=np.zeros((H,W,3),np.float32)
 for k in range(samples):acc+=state(f+(k+.5)/samples*.5)/samples
 im=Image.fromarray(np.clip(acc,0,255).astype('uint8'))
 blur=4*max(0,1-abs(f-cut)/4) # internal half-resolution: output peak8px
 if blur:im=im.filter(ImageFilter.BoxBlur(blur))
 p.stdin.write(im.tobytes())
 if f in [59,70,74,75,78,90,95]:im.resize((1080,1920)).save(out.with_name('frame-%03d.jpg'%f))
p.stdin.close();assert p.wait()==0

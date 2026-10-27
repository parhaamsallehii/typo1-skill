from PIL import Image,ImageDraw
import numpy as np,subprocess
from scipy.ndimage import map_coordinates
from pathlib import Path
W,H=540,960;Y,X=np.mgrid[:H,:W].astype(float);R=np.hypot(X-W/2,Y-H/2);tiles=[]
for i in range(9):
 im=Image.new('RGBA',(120,170),(25+15*i,55+8*i,95+9*i,255));d=ImageDraw.Draw(im)
 for j in range(5):
  x=20+j*20;d.ellipse((x-20,40-j*3,x+35,120+j*4),fill=(30+20*j,150+10*i,180-15*j,255))
 d.line((60,155,60,50),fill='white',width=3);tiles.append(im)
def ease(u,c):
 u=np.clip(u,0,1);l=0.;h=1.
 for _ in range(24):
  t=(l+h)/2;x=3*(1-t)**2*t*c[0]+3*(1-t)*t*t*c[2]+t**3
  if x<u:l=t
  else:h=t
 return 3*(1-t)**2*t*c[1]+3*(1-t)*t*t*c[3]+t**3

def plane(tile,cx,cy,rx,rz,z):
 corners=np.array([[-60,-85,0],[60,-85,0],[60,85,0],[-60,85,0]],float)
 ax=np.deg2rad(rx);az=np.deg2rad(rz)
 rotX=np.array([[1,0,0],[0,np.cos(ax),-np.sin(ax)],[0,np.sin(ax),np.cos(ax)]])
 rotZ=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]])
 v=corners@rotX.T@rotZ.T;factor=650/(650+z+v[:,2]);dst=np.column_stack((cx+v[:,0]*factor,cy+v[:,1]*factor))
 x0,y0=np.floor(dst.min(axis=0)-2).astype(int);x1,y1=np.ceil(dst.max(axis=0)+2).astype(int)
 dst-=np.array([x0,y0])
 src=[(0,0),(120,0),(120,170),(0,170)];A=[];b=[]
 for (x,y),(u,vv) in zip(dst,src):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-vv*x,-vv*y]]);b.extend([u,vv])
 coeff=np.linalg.solve(A,b)
 return tile.transform((int(x1-x0),int(y1-y0)),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC),(int(x0),int(y0))
def state(f):
 start=45;u=(f-start)/15;pose=ease(u,(.30,0,.10,1));entry=ease(u,(.06,.88,.10,.95));im=Image.new('RGBA',(W,H),'#EDF3F3')
 # main object tilts toward lower-left, and recedes along Z
 for i in range(1,9):
  col=(i-1)%3;row=(i-1)//3;cx=90+col*180;target=245+row*230
  direction=-1 if i%2 else 1
  cy=target+direction*760*(1-entry)
  if u>1:cy+=direction*(f-start-15)*.18
  tile=tiles[i]
  if 0<=u<1:
   a=np.array(tile).astype(float);phase=entry*7+i;a[:,:,:3]=np.clip(a[:,:,:3]+30*np.sin(phase+np.arange(3)*2.1),0,255);tile=Image.fromarray(a.astype('uint8'))
  im.alpha_composite(*plane(tile,cx,cy,-12*pose,-5*pose,35))
 im.alpha_composite(*plane(tiles[0],270-14*pose,480+15*pose,24*pose,9*pose,90*pose))
 a=np.array(im.convert('RGB'),dtype=float)
 # coded approximation of the automatic 15-frame center-out ripple
 if 0<=u<1:
  rad=8+300*u;env=np.exp(-((R-rad)/65)**2)*min(1,u*12)*min(1,(1-u)*5)
  delta=20*np.sin((R-rad)/23)*env*np.clip(R/70,0,1);xx=X+delta*(X-W/2)/np.maximum(R,1);yy=Y+delta*(Y-H/2)/np.maximum(R,1)
  a=np.stack([map_coordinates(a[:,:,k],[yy,xx],order=1,mode='nearest') for k in range(3)],axis=-1)
 return a
out=Path(__file__).with_name('ripple-gallery-v2.mp4');p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-vf','crop=540:600:0:180,scale=1080:1200:flags=lanczos,pad=1080:1920:0:360:color=0xEDF3F3','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
for f in range(150):
 a=np.zeros((H,W,3))
 for k in range(1 if f<45 else 16):a+=state(f+(k+.5)/(1 if f<45 else 16)*.5)/(1 if f<45 else 16)
 im=Image.fromarray(np.clip(a,0,255).astype('uint8'));p.stdin.write(im.tobytes())
 if f in [40,46,48,50,53,56,60,90,149]:im.save(out.with_name('frame-%03d.jpg'%f))
p.stdin.close();assert p.wait()==0

from PIL import Image,ImageDraw,ImageFont
import numpy as np, subprocess,json
from scipy.ndimage import gaussian_filter
from pathlib import Path
W,H=1080,1920
base=Image.new('RGB',(W,H),'#182420');d=ImageDraw.Draw(base)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def text(x,y,s,n,c):
 if 860<=y<=1080:d.text((x,y),s,font=ImageFont.truetype(font,n),fill=c)
text(100,530,'FOCUS SPACE',24,'#B6C9BD');text(100,590,'Make room',66,'#F3EDE0');text(100,675,'for deep work.',66,'#F3EDE0')
d.rounded_rectangle((85,860,995,1080),35,fill='#F0EADD');text(130,935,'Start a focus session',32,'#253A30')
d.rounded_rectangle((805,910,945,1030),25,fill='#BC8743');d.polygon([(862,944),(862,995),(900,970)],fill='#FFF8E8')
text(100,1160,'25 minutes. One clear intention.',25,'#B6C9BD')
# Fixed hollow-square field; only feathered circular matte reveals it.
mask=Image.new('L',(910,220));md=ImageDraw.Draw(mask)
for y in range(4,220,20):
 for x in range(4,910,20):md.rectangle((x,y,x+16,y+16),outline=255,width=2)
clip=Image.new('L',(910,220));ImageDraw.Draw(clip).rounded_rectangle((0,0,909,219),35,fill=255)
pattern=np.asarray(mask,dtype=np.float32)/255*np.asarray(clip)/255
Y,X=np.mgrid[:220,:910];distance=np.hypot(X-790,Y-110)
raw=np.asarray(base).copy();roi=raw[860:1080,85:995].astype(float);accent=np.array([188,135,67.])
def frame(t):
 al=np.zeros_like(pattern)
 for k in range(64):
  u=(t+(k+.5)/64*2/30-1.3)/1.15
  if 0<=u<=1:
   radius=145*(1-(1-u)**5)
   reveal=np.clip((radius-distance)/65+.5,0,1);reveal=reveal*reveal*(3-2*reveal)
   fade=1-np.clip((u-.55)/.45,0,1)**2
   al+=pattern*reveal*fade/64
 a=raw.copy()
 glow=np.clip(gaussian_filter(al,3)*1.5+gaussian_filter(al,12)*1.8,0,1)
 light=np.array([255,183,75.])
 surface=roi*(1-al[:,:,None])+accent*al[:,:,None]
 surface=255-(255-surface)*(1-glow[:,:,None]*light/255)
 a[860:1080,85:995]=np.clip(surface,0,255).astype('uint8')
 im=Image.fromarray(a);q=ImageDraw.Draw(im)
 x,y=875,970
 q.polygon([(x,y),(x+7,y+42),(x+18,y+31),(x+29,y+49),(x+37,y+44),(x+26,y+27),(x+42,y+24)],fill='#14231C',outline='white',width=2)
 return im.crop((540,490,1080,1450)).resize((1080,1920),Image.Resampling.LANCZOS)
out=Path(__file__).with_name('focus-pixel-reaction-v2.mp4')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
for i in range(150):p.stdin.write(frame(i/30).tobytes())
p.stdin.close();assert p.wait()==0
frame(1.55).save(out.with_suffix('.jpg'))

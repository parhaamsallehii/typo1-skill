#!/usr/bin/env python3
"""RTL two-line reference reconstruction. Coded approximation, not a native AE render."""
import argparse,json,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,features
from scipy.interpolate import PchipInterpolator
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'references/profile.json').read_text())

def rgb(hexcolor):return tuple(int(hexcolor[i:i+2],16) for i in (1,3,5))
def curve(block,key,t):
    xs=block['frames'];ys=block[key]
    return float(PchipInterpolator(xs,ys)(np.clip(t,xs[0],xs[-1])))
def base_property(block,key,t):
    """Base value/analytic velocity in seconds, BEFORE expression application."""
    xs=np.asarray(block['frames'],float)/30
    ys=np.asarray(block[key],float)
    if t<xs[0] or t>=xs[-1]:return (float(ys[0] if t<xs[0] else ys[-1]),0.)
    n=int(np.searchsorted(xs,t,side='right')-1)
    duration=xs[n+1]-xs[n];u=(t-xs[n])/duration
    ratio=float(block.get('arrival_velocity_ratio',.15))
    # Monotone authored Hermite base: zero outgoing speed, specified
    # incoming speed. The user supplied the spring, not the base AE graph.
    ease=(-2+ratio)*u**3+(3-ratio)*u**2
    derivative=(3*(-2+ratio)*u*u+2*(3-ratio)*u)/duration
    delta=ys[n+1]-ys[n]
    return float(ys[n]+delta*ease),float(delta*derivative)

def spring_curve(block,key,frame_age,fps):
    t=frame_age/30
    value,_=base_property(block,key,t)
    xs=np.asarray(block['frames'],float)/30
    n=int(np.searchsorted(xs,t,side='right')-1)
    if n<0:return value
    elapsed=t-xs[n]
    if elapsed<1:
        _,velocity=base_property(block,key,xs[n]-1/(fps*10))
        value+=velocity*.1*math.sin(2*math.pi*2*elapsed)/math.exp(6*elapsed)
    return value

def mix(a,b,t):return tuple(round(x+(y-x)*np.clip(t,0,1)) for x,y in zip(a,b))

def pair_masks(texts,weight,ink_height,max_width,gap):
    if not features.check('raqm'):raise RuntimeError('Pillow RAQM required for joined Persian')
    path=ROOT/'assets/fonts'/('MODAM-'+weight+'.TTF')
    f=TTFont(path);cmap=f.getBestCmap();f.close()
    for text in texts:
        missing=[c for c in text if not c.isspace() and c not in '\u200c\u200d\u200e\u200f' and ord(c) not in cmap]
        if missing:raise ValueError('Missing glyphs: '+repr(missing))
    size=200
    for _ in range(8):
        font=ImageFont.truetype(str(path),size,layout_engine=ImageFont.Layout.RAQM)
        boxes=[font.getbbox(t,anchor='ls',direction='rtl',language='fa') for t in texts]
        top=min(b[1] for b in boxes);bottom=max(b[3] for b in boxes)
        widths=[b[2]-b[0] for b in boxes];height=bottom-top
        ratio=min(ink_height/height,(max_width-gap)/sum(widths))
        newsize=max(8,int(size*ratio))
        if abs(newsize-size)<=1:break
        size=newsize
    font=ImageFont.truetype(str(path),size,layout_engine=ImageFont.Layout.RAQM)
    boxes=[font.getbbox(t,anchor='ls',direction='rtl',language='fa') for t in texts]
    top=min(b[1] for b in boxes);bottom=max(b[3] for b in boxes);pad=20
    items=[]
    for text,b in zip(texts,boxes):
        width=b[2]-b[0];mask=Image.new('L',(width+2*pad,bottom-top+2*pad))
        ImageDraw.Draw(mask).text((pad-b[0],pad-top),text,fill=255,font=font,anchor='ls',direction='rtl',language='fa')
        items.append({'mask':mask,'width':width,'height':bottom-top,'font_size':size})
    return items

def colored(mask,color,shadow=None):
    im=Image.new('RGBA',mask.size)
    if shadow:
        distance,softness,opacity=shadow
        sh=mask.filter(ImageFilter.GaussianBlur(softness))
        sh=sh.point(lambda v:round(v*opacity))
        layer=Image.new('RGBA',mask.size,(0,0,0,0));layer.putalpha(sh)
        im.alpha_composite(layer,(0,round(distance)))
    layer=Image.new('RGBA',mask.size,color+(0,));layer.putalpha(mask)
    im.alpha_composite(layer)
    return im

def transformed(im,scale,angle,opacity=1):
    if scale<=.005 or opacity<=.001:return None
    w,h=im.size;im=im.resize((max(1,round(w*scale)),max(1,round(h*scale))),Image.Resampling.BICUBIC)
    if abs(angle)>.01:im=im.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
    if opacity<.999:im.putalpha(im.getchannel('A').point(lambda v:round(v*opacity)))
    return im

def validate(cfg):
    if min(cfg['width'],cfg['height'],cfg['fps'],cfg['duration'])<=0:raise ValueError('Invalid dimensions/timing')
    if not cfg.get('events'):raise ValueError('At least one text event is required')
    for e in cfg['events']:
        for key in ['top','bottom']:
            if len(e.get(key,[]))!=2 or any(not isinstance(x,str) or not x.strip() for x in e[key]):raise ValueError('Each line requires two nonempty word-boundary chunks')
        if e['start']<0 or e['start']>=cfg['duration']:raise ValueError('Cue outside source')
        if not cfg.get('demo',False):
            if not cfg.get('speech_evidence') or e.get('speech_verified') is not True:raise ValueError('Verify spoken words and timed cues; never invent a transcript')
            if len(e.get('cues',[]))!=4 or 'exit_start' not in e:raise ValueError('Production requires four actual absolute speech cues and exit_start')
        if 'cues' in e:
            if len(e['cues'])!=4 or sorted(e['cues'])!=e['cues'] or e['cues'][0]<e['start']:raise ValueError('Speech cues must be ordered absolute seconds')
            if e.get('exit_start',1e9)<e['cues'][-1]+4/30:raise ValueError('Exit cannot precede lower-line base arrival')
    return True

class Event:
    def __init__(self,e,cfg,profile):
        self.e=e;self.p=profile;self.W=cfg['width'];self.H=cfg['height'];self.k=self.W/1080
        self.start=float(e['start']);self.fps=float(cfg['fps']);l=profile['layout']
        self.cx=float(e.get('center_x',l['center_x']))*self.W
        self.ys=[float(e.get('top_y',l['top_ink_center_y']))*self.H,float(e.get('bottom_y',l['bottom_ink_center_y']))*self.H]
        self.pivot=np.array([self.cx,sum(self.ys)/2])
        self.items=[];gap=l['word_gap']*self.W
        for row,key in enumerate(['top','bottom']):
            masks=pair_masks(e[key],l['top_font'] if row==0 else l['bottom_font'],self.H*l['top_ink_height' if row==0 else 'bottom_ink_height'],self.W*l['max_width'],gap)
            total=sum(x['width'] for x in masks)+gap;right=self.cx+total/2
            for part,item in enumerate(masks):
                item.update(center=np.array([right-item['width']/2,self.ys[row]]),row=row,part=part)
                right-=item['width']+gap;self.items.append(item)
        self.onsets=list(e.get('cues',[self.start+x/30 for x in profile['top_onsets']+profile['bottom_onsets']]))
        self.exit=float(e.get('exit_start',self.start+profile['exit_onset']/30))
        self.highlight=float(e.get('highlight_start',self.onsets[2]+(profile['highlight_onset']-profile['bottom_onsets'][0])/30))
        if self.highlight<self.onsets[2]:raise ValueError('Highlight must follow keyword onset')
        self.end=self.exit+profile['exit_duration']/30
    def state(self,t):
        if t<min(self.onsets) or t>=self.end:return None
        f=max(0,(t-self.exit)*30);x=self.p['exit']
        return (curve(x,'x',f)*self.k,curve(x,'y',f)*self.k,curve(x,'angle',f),curve(x,'scale',f))
    def render_elements(self,t):
        exitstate=self.state(t)
        if exitstate is None:return []
        ex,ey,ea,es=exitstate
        rad=math.radians(ea);mat=np.array([[math.cos(rad),-math.sin(rad)],[math.sin(rad),math.cos(rad)]])
        elements=[];cream=rgb(self.p['palette']['cream']);red=rgb(self.p['palette']['crimson'])
        for j,item in enumerate(self.items):
            age=(t-self.onsets[j])*30
            if age<0:continue
            row=item['row'];part=item['part'];block=self.p['top'] if row==0 else self.p['keyword' if part==0 else 'remainder']
            op=curve(block,'opacity',age)
            if op<=.001:continue
            pos=item['center']+np.array([spring_curve(block,'x',age,self.fps),spring_curve(block,'y',age,self.fps)])*self.k
            center=(pos-self.pivot)@mat.T*es+self.pivot+np.array([ex,ey])
            scale=spring_curve(block,'scale',age,self.fps)*es;angle=spring_curve(block,'angle',age,self.fps)+ea
            tint=mix(red,cream,min(1,max(0,age/block['tint_frames'])))
            # Keyword rectangle is a separate layer, behind the shaped word.
            if row==1 and part==0 and t>=self.highlight:
                b=self.p['highlight'];f=(t-self.highlight)*30;amount=spring_curve(b,'width_scale',f,self.fps)
                fullw=item['width']+2*b['pad_x']*self.k;boxh=item['height']+2*b['pad_y']*self.k
                boxw=max(1,round(fullw*amount));pad=max(4,round(3*b['glow_radius']*self.k))
                box=Image.new('RGBA',(boxw+2*pad,round(boxh)+2*pad))
                mask=Image.new('L',box.size);ImageDraw.Draw(mask).rectangle((pad,pad,pad+boxw-1,pad+round(boxh)-1),fill=255)
                glow=mask.filter(ImageFilter.GaussianBlur(b['glow_radius']*self.k)).point(lambda v:round(v*b['glow_opacity']))
                gl=Image.new('RGBA',box.size,red+(0,));gl.putalpha(glow);box.alpha_composite(gl)
                draw=ImageDraw.Draw(box)
                for y in range(round(boxh)):
                    gain=b['gradient_gain_top']+(b['gradient_gain_bottom']-b['gradient_gain_top'])*y/max(1,boxh-1)
                    color=tuple(min(255,round(c*gain)) for c in red)
                    draw.line((pad,pad+y,pad+boxw-1,pad+y),fill=color+(255,))
                # Grow inward from the keyword's right edge for Persian RTL.
                local_offset=np.array([(fullw-boxw)/2,0.])
                a=math.radians(angle);rot=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
                bc=center+(local_offset@rot.T)*scale
                bi=transformed(box,scale,angle,op)
                if bi:elements.append((bi,bc))
            fx=self.p['effects'];shadow=None if row==0 else (fx['bottom_shadow_distance']*self.k,fx['bottom_shadow_softness']*self.k,fx['bottom_shadow_opacity'])
            sprite=colored(item['mask'],tint,shadow)
            sprite=transformed(sprite,scale,angle,op)
            if sprite:elements.append((sprite,center))
        return elements

class Renderer:
    def __init__(self,cfg):
        validate(cfg);self.cfg=cfg;self.W=int(cfg['width']);self.H=int(cfg['height']);self.fps=float(cfg['fps'])
        self.profile=json.loads(json.dumps(PROFILE))
        self.sample_counts=[]
        self.events=[Event(e,cfg,self.profile) for e in cfg['events']]
    def elements(self,t):
        return [elem for event in self.events for elem in event.render_elements(t)]
    def sample(self,t):
        elements=self.elements(t)
        if not elements:return None
        boxes=[(round(c[0]-im.width/2),round(c[1]-im.height/2),im) for im,c in elements]
        x0=max(0,min(x for x,y,im in boxes));y0=max(0,min(y for x,y,im in boxes))
        x1=min(self.W,max(x+im.width for x,y,im in boxes));y1=min(self.H,max(y+im.height for x,y,im in boxes))
        if x1<=x0 or y1<=y0:return None
        canvas=Image.new('RGBA',(x1-x0,y1-y0))
        for x,y,im in boxes:canvas.alpha_composite(im,(x-x0,y-y0))
        arr=np.asarray(canvas,dtype=np.float32)/255;arr[:,:,:3]*=arr[:,:,3:4]
        return (x0,y0,x1,y1),arr
    def overlay(self,t):
        result=np.zeros((self.H,self.W,4),np.float32)
        if not any(e.state(t) or e.state(t+.5/self.fps) for e in self.events):return result
        # Forward 180-degree phase-zero exposure, at least16 midpoint samples.
        movement=max((abs(curve(self.profile['exit'],'y',max(0,(t+.5/self.fps-e.exit)*30))-curve(self.profile['exit'],'y',max(0,(t-e.exit)*30))) for e in self.events if e.state(t)),default=0)
        blur=self.profile['motion_blur']
        count=min(blur['adaptive_limit'],max(blur['minimum_samples'],math.ceil(movement*self.W/1080)))
        self.sample_counts.append(count)
        for i in range(count):
            sample=self.sample(t+(i+.5)/count*.5/self.fps)
            if sample:
                (x0,y0,x1,y1),arr=sample;result[y0:y1,x0:x1]+=arr/count
        return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('scene',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    cfg=json.loads(a.scene.read_text());r=Renderer(cfg);W,H=r.W,r.H;fps=r.fps;duration=cfg['duration']
    bg=cfg['background'];reader=None;source=None
    if bg.startswith('#'):frame=np.asarray(Image.new('RGB',(W,H),bg),np.float32)/255
    else:
        source=Path(bg);source=source if source.is_absolute() else a.scene.parent/source
        if source.suffix.lower() in ['.jpg','.jpeg','.png','.webp']:
            im=Image.open(source).convert('RGB')
            if im.size!=(W,H):raise ValueError('Use actual source size; no silent resize/crop')
            frame=np.asarray(im,np.float32)/255;source=None
        else:
            video=next(s for s in json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(source)]))['streams'] if s['codec_type']=='video')
            n,d=map(int,video['avg_frame_rate'].split('/'))
            if (video['width'],video['height'])!=(W,H) or abs(n/d-fps)>1e-4:raise ValueError('Preserve actual source dimensions and FPS')
            reader=subprocess.Popen(['ffmpeg','-v','error','-i',str(source),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    a.output.parent.mkdir(parents=True,exist_ok=True);temp=a.output.with_name(a.output.stem+'-silent.mp4')
    out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
    try:
        for i in range(round(duration*fps)):
            if reader:
                data=reader.stdout.read(W*H*3)
                if len(data)!=W*H*3:raise ValueError('Source too short; never loop/freeze silently')
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
    report={'renderer':'coded visual reconstruction, not original AE project','demo':cfg.get('demo',False),'width':W,'height':H,'fps':fps,'frames':round(duration*fps),'palette':r.profile['palette'],'events':[{'start':e.start,'cues':e.onsets,'exit':e.exit,'end':e.end,'font_sizes':[x['font_size'] for x in e.items]} for e in r.events],'shutter_angle':180,'phase':0,'samples_min':16,'samples_max':128,'bounce':r.profile['bounce'],'motion_blur_enabled':True,'observed_samples_min':min(r.sample_counts,default=16),'observed_samples_max':max(r.sample_counts,default=16)}
    a.output.with_suffix('.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

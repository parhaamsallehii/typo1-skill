#!/usr/bin/env python3
"""V2 progressive three-row typography with connected Persian raster deformation."""
import argparse,json,math,hashlib,subprocess
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image,ImageDraw,ImageFont,ImageFilter,features
from fontTools.ttLib import TTFont
from motion import spring_curve
ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'references/profile.json').read_text())
def rgb(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
def smooth(u):
    u=float(np.clip(u,0,1));return u*u*(3-2*u)
def motion_array(block,key,frames,fps):
    """Vectorized exact supplied expression on the same two authored base keys."""
    xs=np.array(block['frames'],float)/30;ys=np.array(block[key],float)
    if len(xs)!=2:raise ValueError('Column motion requires two base keys')
    t=np.asarray(frames)/30;T=xs[1]-xs[0];u=np.clip((t-xs[0])/T,0,1);r=block.get('arrival_velocity_ratio',.15)
    value=ys[0]+(ys[1]-ys[0])*((-2+r)*u**3+(3-r)*u**2)
    sample=xs[1]-1/(fps*10);v_u=(sample-xs[0])/T
    v=0 if not 0<v_u<1 else (ys[1]-ys[0])*(3*(-2+r)*v_u*v_u+2*(3-r)*v_u)/T
    elapsed=t-xs[1];active=(elapsed>=0)&(elapsed<1)
    e=np.clip(elapsed,0,1)
    return value+np.where(active,v*.1*np.sin(2*np.pi*2*e)/np.exp(6*e),0)

def evidence_check(cfg,folder):
    if cfg.get('demo',False):return
    path=Path(cfg.get('speech_evidence',''));path=path if path.is_absolute() else folder/path
    if not path.is_file():raise ValueError('Real speech test requires actual word-timed evidence, not guessed words')
    evidence=json.loads(path.read_text())
    source=Path(cfg['background']);source=source if source.is_absolute() else folder/source
    if hashlib.sha256(source.read_bytes()).hexdigest()!=evidence.get('source_sha256'):raise ValueError('Speech evidence belongs to a different source')
    for event in cfg['events']:
        for w in event['words']:
            index=w.get('source_index')
            if not isinstance(index,int) or not 0<=index<len(evidence['words']):raise ValueError('Each production word must link to actual transcript index')
            actual=evidence['words'][index]
            if w['text']!=actual['text'] or abs(w['start']-actual['start_seconds'])>.001 or abs(w['end']-actual['end_seconds'])>.001:raise ValueError('Displayed word/cue differs from its transcription evidence')
def validate(cfg,folder=Path('.')):
    if min(cfg['width'],cfg['height'],cfg['fps'],cfg['duration'])<=0:raise ValueError('Invalid output')
    for e in cfg['events']:
        words=e['words']
        if not words or sorted(w['start'] for w in words)!=[w['start'] for w in words]:raise ValueError('Provide ordered actual word cues')
        if {w['row'] for w in words}!={0,1,2}:raise ValueError('V2 needs three rows; first has accent plus regular words')
        if not any(w.get('accent') and w['row']==0 for w in words):raise ValueError('First row needs a marked accent word')
        if any(w['start']<e['start'] or w['end']<=w['start'] for w in words):raise ValueError('Invalid word interval')
        if e['close_start']<max(w['end'] for w in words):raise ValueError('Do not close before final spoken word ends')
        if e['close_start']+e.get('close_duration',7/30)>cfg['duration']+1e-7:raise ValueError('Need real source time for a complete close; do not freeze or truncate silently')
    spans=sorted((e['start'],e['close_start']+e.get('close_duration',7/30)) for e in cfg['events'])
    if any(a[1]>b[0] for a,b in zip(spans,spans[1:])):raise ValueError('Events must not overlap')
    evidence_check(cfg,folder)
    return True
def shade(mask,color):
    im=Image.new('RGBA',mask.size,color+(0,));im.putalpha(mask);return im
def line(draw,pts,color,width):
    pts=[tuple(map(float,p)) for p in pts];draw.line(pts,fill=color,width=max(1,round(width)),joint='curve')
    r=width/2
    for x,y in [pts[0],pts[-1]]:draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
class Event:
    def __init__(self,e,cfg):
        self.e=e;self.W=cfg['width'];self.H=cfg['height'];self.k=self.W/1080;self.fps=cfg['fps'];self.p=PROFILE
        self.start=e['start'];self.close=e['close_start'];self.close_duration=e.get('close_duration',7/30);self.end=self.close+self.close_duration
        self.items=[];layout=self.p['layout'];self.cx=e.get('center_x',layout['center_x'])*self.W
        self.centers=[y*self.H for y in e.get('row_y',layout['row_y'])]
        self.row_boxes=[]
        if not features.check('raqm'):raise RuntimeError('Pillow RAQM is required for joined Persian')
        for row in range(3):
            words=[w for w in e['words'] if w['row']==row];weight=layout['fonts'][row]
            texts=' '.join(w['text'] for w in words);path=ROOT/'assets/fonts'/('MODAM-'+weight+'.TTF')
            size=160
            for _ in range(6):
                font=ImageFont.truetype(str(path),size,layout_engine=ImageFont.Layout.RAQM);b=font.getbbox(texts,anchor='ls',direction='rtl',language='fa')
                heights=b[3]-b[1];width=sum(font.getlength(w['text'],direction='rtl',language='fa') for w in words)+(len(words)-1)*layout['word_gap']*self.W
                ratio=min(layout['row_ink_height'][row]*self.H/heights,layout['max_width']*self.W/width)
                new=max(8,round(size*ratio))
                if abs(new-size)<=1:break
                size=new
            regular=ImageFont.truetype(str(path),size,layout_engine=ImageFont.Layout.RAQM)
            full=regular.getbbox(texts,anchor='ls',direction='rtl',language='fa')
            baseline=self.centers[row]-(full[1]+full[3])/2
            rowitems=[]
            for w in words:
                wt=layout['accent_font'] if w.get('accent') else weight
                fp=ROOT/'assets/fonts'/('MODAM-'+wt+'.TTF');ft=TTFont(fp);cmap=ft.getBestCmap();ft.close()
                if any(ord(c) not in cmap for c in w['text'] if not c.isspace() and c not in '\u200c\u200d'):raise ValueError('Missing supplied font glyph')
                f=ImageFont.truetype(str(fp),size,layout_engine=ImageFont.Layout.RAQM);b=f.getbbox(w['text'],anchor='ls',direction='rtl',language='fa')
                pad=16;mask=Image.new('L',(b[2]-b[0]+2*pad,b[3]-b[1]+2*pad))
                ImageDraw.Draw(mask).text((pad-b[0],pad-b[1]),w['text'],font=f,fill=255,anchor='ls',direction='rtl',language='fa')
                if w.get('accent'):
                    shear=layout['accent_shear'];extra=math.ceil(abs(shear)*mask.height)
                    mask=mask.transform((mask.width+extra,mask.height),Image.Transform.AFFINE,(1,shear,extra if shear<0 else 0,0,1,0),resample=Image.Resampling.BICUBIC)
                ink=mask.width-2*pad
                rowitems.append({'w':w,'mask':np.asarray(mask,np.float32)/255,'width':ink,'height':b[3]-b[1],'cy':baseline+(b[1]+b[3])/2,'font_size':size,'pad':pad})
            gap=layout['word_gap']*self.W;total=sum(it['width'] for it in rowitems)+(len(words)-1)*gap;right=self.cx+total/2
            for it in rowitems:
                it['cx']=right-it['width']/2;right-=it['width']+gap;self.items.append(it)
            self.row_boxes.append((self.cx-total/2,baseline+full[1],self.cx+total/2,baseline+full[3]))
        self.accent=next(it for it in self.items if it['w'].get('accent'))
        self.mid=min(w['start'] for w in e['words'] if w['row']==1)
        self.third=min(w['start'] for w in e['words'] if w['row']==2)
    def word_sprite(self,it,t):
        age=(t-it['w']['start'])*30
        if age<0:return None
        mask=it['mask'];h,w=mask.shape;entry=self.p['entry']
        # All glyphs are shaped together first; column deformation never splits Unicode.
        trail=0 if it['w'].get('accent') else min(7.,max(0.,(it['w']['end']-it['w']['start'])*30-4))
        column=age-trail*(1-np.arange(w)/max(1,w-1))
        dy=motion_array(entry,'y',column,self.fps)*self.k
        scale=motion_array(entry,'scale',column,self.fps)
        angle=motion_array(entry,'angle_x',column,self.fps)
        vertical=scale*np.cos(np.deg2rad(angle))
        alpha=np.clip(column/2,0,1)
        margin=math.ceil(64*self.k);oh=h+2*margin
        yy,xx=np.mgrid[:oh,:w];sy=(yy-margin-(h-1)/2-dy[None,:])/vertical[None,:]+(h-1)/2
        warped=map_coordinates(mask,[sy,xx],order=1,mode='constant',cval=0,prefilter=False)*alpha[None,:]
        m=Image.fromarray(np.uint8(np.clip(warped*255+.5,0,255)))
        color=rgb(self.p['palette']['crimson' if it['w'].get('accent') else 'cream'])
        im=Image.new('RGBA',m.size)
        if not it['w'].get('accent'):
            sh=m.filter(ImageFilter.GaussianBlur(.8*self.k)).point(lambda v:round(v*.22));layer=shade(sh,(0,0,0));im.alpha_composite(layer,(0,max(1,round(2*self.k))))
        im.alpha_composite(shade(m,color))
        az=spring_curve(entry,'angle_z',age,self.fps)
        if abs(az)>.02:im=im.rotate(-az,resample=Image.Resampling.BICUBIC,expand=True)
        return im,(it['cx'],it['cy'])
    def draw(self,t):
        if t<self.start or t>=self.end:return None
        allboxes=self.row_boxes;pad=round(130*self.k)
        x0=max(0,math.floor(min(x[0] for x in allboxes)-pad));x1=min(self.W,math.ceil(max(x[2] for x in allboxes)+pad))
        y0=max(0,math.floor(min(x[1] for x in allboxes)-pad));y1=min(self.H,math.ceil(max(x[3] for x in allboxes)+pad))
        im=Image.new('RGBA',(x1-x0,y1-y0));draw=ImageDraw.Draw(im);red=rgb(self.p['palette']['crimson']);o=self.p['ornaments'];k=self.k
        def local(x,y):return x-x0,y-y0
        left,top,right,bottom=self.row_boxes[1];gap=o['gap']*k
        # A single thin loose contour briefly surrounds the entering middle line.
        phase=(t-self.mid)/max(.12,self.third-self.mid)
        if 0<phase<1:
            points=[];a=.5*math.sin(math.pi*phase)
            for u in np.linspace(0,2*math.pi,100):
                x=(left+right)/2+(right-left+2*gap)/2*math.cos(u)
                y=(top+bottom)/2+(bottom-top+2*gap)/2*math.sin(u)
                y+=(1-phase)*10*k*math.sin(3*u+phase*3)
                points.append(local(x,y))
            line(draw,points,red+(round(255*a),),o['wave_stroke']*k)
        # Streaks settle into an underline and opposite L-shaped corner accents.
        grow_block={'frames':[0,4],'s':[0,1],'arrival_velocity_ratio':0.}
        g=spring_curve(grow_block,'s',(t-(self.mid-.10))*30,self.fps)
        g=max(0,g)
        ax,ay=self.accent['cx'],self.accent['cy']+self.accent['height']/2+9*k
        if g>0:
            width=self.accent['width']*o['underline_width_ratio']*g
            line(draw,[local(ax-width/2,ay),local(ax+width/2,ay)],red+(255,),o['stroke']*k)
        if self.mid-.13<t<self.mid:
            q=(t-(self.mid-.13))/.13
            for side in [-1,1]:
                x=(left if side<0 else right)+side*100*k*(1-q);y=(top if side<0 else bottom)-side*75*k*(1-q)
                line(draw,[local(x-25*k,y-17*k),local(x+25*k,y+17*k)],red+(round(255*q),),6*k)
        corner=smooth((t-self.mid)/max(.10,self.third-self.mid))
        if corner>0:
            lx=o['leg_x']*k*corner;ly=o['leg_y']*k*corner
            # Persian mirror: upper-right and lower-left corners, never a full box.
            line(draw,[local(right+gap,top+ly),local(right+gap,top-gap),local(right+gap-lx,top-gap)],red+(255,),o['stroke']*k)
            line(draw,[local(left-gap,bottom-ly),local(left-gap,bottom+gap),local(left-gap+lx,bottom+gap)],red+(255,),o['stroke']*k)
        for it in self.items:
            sprite=self.word_sprite(it,t)
            if sprite:
                wi,(cx,cy)=sprite;im.alpha_composite(wi,(round(cx-wi.width/2-x0),round(cy-wi.height/2-y0)))
        # Three transient opaque accent bars sweep the existing text and upcoming row.
        available=max(.09,self.third-self.mid-.05);slot=min(.1,available/3);begin=self.third-3*slot
        idx=int((t-begin)/slot) if t>=begin else -1
        if 0<=idx<3:
            u=(t-begin-idx*slot)/slot;amount=min(1.,u*5,(1-u)*5)
            if idx==0:
                it=self.accent;box=(it['cx']-it['width']/2,it['cy']-it['height']/2,it['cx']+it['width']/2,it['cy']+it['height']/2)
            elif idx==1:
                rest=[it for it in self.items if it['w']['row']==0 and not it['w'].get('accent')]
                box=(min(it['cx']-it['width']/2 for it in rest),self.row_boxes[0][1],max(it['cx']+it['width']/2 for it in rest),self.row_boxes[0][3]) if rest else self.row_boxes[0]
            else:box=self.row_boxes[2]
            bx0,by0,bx1,by1=box;bw=(bx1-bx0)*max(0,amount)
            ImageDraw.Draw(im).rectangle((*local(bx1-bw,by0),*local(bx1,by1)),fill=red+(255,))
        if t>=self.close:
            u=smooth((t-self.close)/self.close_duration)
            edge=min(b[0] for b in allboxes)-40*k+u*(max(b[2] for b in allboxes)-min(b[0] for b in allboxes)+80*k)
            xs=np.arange(x0,x1);matte=np.clip((xs-edge)/max(.7,k)+.5,0,1)
            alpha=np.asarray(im.getchannel('A'),np.float32)*matte[None,:]
            im.putalpha(Image.fromarray(np.uint8(np.clip(alpha+.5,0,255))))
        arr=np.asarray(im,np.float32)/255;arr[:,:,:3]*=arr[:,:,3:4]
        return (x0,y0,x1,y1),arr

class Renderer:
    def __init__(self,cfg,folder=Path('.')):
        validate(cfg,folder);self.cfg=cfg;self.W=cfg['width'];self.H=cfg['height'];self.fps=cfg['fps'];self.events=[Event(e,cfg) for e in cfg['events']];self.samples=[]
    def overlay(self,t):
        result=np.zeros((self.H,self.W,4),np.float32)
        active=[e for e in self.events if t+.5/self.fps>=e.start and t<e.end]
        if not active:return result
        count=16
        for e in active:
            if t>=e.close:
                width=max(b[2] for b in e.row_boxes)-min(b[0] for b in e.row_boxes)
                delta=abs(smooth((t+.5/self.fps-e.close)/e.close_duration)-smooth((t-e.close)/e.close_duration))*width
                count=min(128,max(count,math.ceil(delta)))
        self.samples.append(count)
        for i in range(count):
            u=t+(i+.5)/count*.5/self.fps
            for e in active:
                sample=e.draw(u)
                if sample:
                    (x0,y0,x1,y1),a=sample
                    # Events are authored nonoverlapping in this style.
                    result[y0:y1,x0:x1]+=a/count
        return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('scene',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    cfg=json.loads(a.scene.read_text());r=Renderer(cfg,a.scene.parent);W,H=r.W,r.H;fps=r.fps
    bg=cfg['background'];source=None;reader=None
    if bg.startswith('#'):frame=np.asarray(Image.new('RGB',(W,H),bg),np.float32)/255
    else:
        source=Path(bg);source=source if source.is_absolute() else a.scene.parent/source
        if source.suffix.lower() in ['.jpg','.jpeg','.png']:
            im=Image.open(source).convert('RGB')
            if im.size!=(W,H):raise ValueError('Preserve actual size')
            frame=np.asarray(im,np.float32)/255;source=None
        else:
            v=next(s for s in json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(source)]))['streams'] if s['codec_type']=='video')
            n,d=map(int,v['avg_frame_rate'].split('/'))
            if (v['width'],v['height'])!=(W,H) or abs(n/d-fps)>1e-4:raise ValueError('Preserve actual source size/FPS')
            reader=subprocess.Popen(['ffmpeg','-v','error','-i',str(source),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    a.output.parent.mkdir(parents=True,exist_ok=True);temp=a.output.with_name(a.output.stem+'-silent.mp4')
    writer=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
    count=round(cfg['duration']*fps)
    try:
        for i in range(count):
            if reader:
                data=reader.stdout.read(W*H*3)
                if len(data)!=W*H*3:raise ValueError('Source too short; no silent freeze/loop')
                frame=np.frombuffer(data,np.uint8).reshape(H,W,3).astype(np.float32)/255
            ov=r.overlay(i/fps);out=ov[:,:,:3]+frame*(1-ov[:,:,3:4])
            writer.stdin.write(np.uint8(np.clip(out*255+.5,0,255)).tobytes())
        writer.stdin.close()
        if writer.wait()!=0:raise RuntimeError('Encoder failed')
    finally:
        if reader:reader.stdout.close();reader.terminate();reader.wait()
        if writer.poll() is None:writer.terminate();writer.wait()
    if source:
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-i',str(source),'-map','0:v:0','-map','1:a?','-c','copy','-t',str(count/fps),'-movflags','+faststart',str(a.output)],check=True);temp.unlink()
    else:temp.replace(a.output)
    report={'renderer':'coded V2 reconstruction; column tilt approximates native per-character projection','demo':cfg.get('demo',False),'speech_evidence':cfg.get('speech_evidence'),'width':W,'height':H,'fps':fps,'frames':count,'duration':count/fps,'words':[w for e in cfg['events'] for w in e['words']],'close':[{'start':e.close,'end':e.end} for e in r.events],'bounce':PROFILE['bounce'],'motion_blur':PROFILE['motion_blur'],'observed_samples_min':min(r.samples,default=16),'observed_samples_max':max(r.samples,default=16),'source_audio_preserved':bool(source),'added_global_flash_or_camera':False}
    a.output.with_suffix('.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

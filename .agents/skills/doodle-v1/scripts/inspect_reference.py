#!/usr/bin/env python3
import argparse,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
source=str(ROOT/'assets/references/reference.mp4')
subprocess.run(['ffmpeg','-v','error','-y','-i',source,str(a.out/'frame-%02d.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',source,'-vf','crop=1080:816:0:552,scale=360:272,tile=6x4','-frames:v','1',str(a.out/'active-contact.jpg')],check=True)
print('Inspect the 24 frames; use only thin doodle strokes as style evidence.')

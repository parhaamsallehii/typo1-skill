#!/usr/bin/env python3
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True);src=Path(__file__).resolve().parents[1]/'assets/references/reference.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),str(a.out/'frame-%03d.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-vf','crop=1080:700:0:850,scale=324:210,tile=8x7','-frames:v','1',str(a.out/'text-contact.jpg')],check=True)
print('Inspect all52 frames, especially transient bars, brackets and final masked close.')

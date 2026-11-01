#!/usr/bin/env python3
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True);src=Path(__file__).resolve().parents[1]/'assets/references/reference.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),str(a.out/'frame-%02d.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-vf','scale=270:480,tile=5x3','-frames:v','1',str(a.out/'contact.jpg')],check=True)
print('Inspect all15 frames and source graph/blur screenshots; isolate only the ring.')

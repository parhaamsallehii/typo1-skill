#!/usr/bin/env python3
"""Extract every source frame losslessly and a small contact sheet to scratch."""
import argparse,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/references/reference.mp4'),str(a.out/'frame-%02d.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/references/reference.mp4'),'-vf','scale=180:320,tile=6x6','-frames:v','1',str(a.out/'contact.jpg')],check=True)
print('Inspect all 36 extracted frames and the supplied placement still.')

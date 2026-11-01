#!/usr/bin/env python3
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True);src=Path(__file__).resolve().parents[1]/'assets/references/reference.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),str(a.out/'frame-%03d.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-vf','crop=1080:600:0:950,scale=324:180,tile=6x10','-frames:v','1',str(a.out/'text-contact.jpg')],check=True)
print('Inspect all 60 frames, enlarged entrances/exit, placement still and palette.')

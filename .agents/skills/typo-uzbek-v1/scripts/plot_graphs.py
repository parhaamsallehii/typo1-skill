#!/usr/bin/env python3
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parents[1];p=json.loads((ROOT/'references/profile.json').read_text())
fig,axes=plt.subplots(2,3,figsize=(13,7))
for ax,(name,key) in zip(axes.flat,[('top','y'),('keyword','y'),('keyword','scale'),('remainder','angle'),('highlight','width_scale'),('exit','y')]):
 b=p[name];x=np.linspace(b['frames'][0],b['frames'][-1],400);y=PchipInterpolator(b['frames'],b[key])(x)
 ax.plot(x,y,color='#B40023',linewidth=2);ax.scatter(b['frames'],b[key],color='#3b2930',s=22)
 ax.set_title(name+' / '+key);ax.set_xlabel('Reference frames at 30 fps');ax.grid(alpha=.2)
fig.suptitle('Authored reconstruction curves — NOT recovered original AE graphs')
fig.tight_layout();out=ROOT/'assets/studies/motion-graphs.png';fig.savefig(out,dpi=160);print(out)

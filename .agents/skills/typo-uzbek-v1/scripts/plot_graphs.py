#!/usr/bin/env python3
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from render import spring_curve,base_property,curve
ROOT=Path(__file__).resolve().parents[1];p=json.loads((ROOT/'references/profile.json').read_text())
fig,axes=plt.subplots(2,3,figsize=(13,7))
for ax,(name,key) in zip(axes.flat,[('top','y'),('keyword','y'),('keyword','scale'),('remainder','angle'),('highlight','width_scale'),('exit','y')]):
 b=p[name];is_exit=name=='exit';end=b['frames'][-1] if is_exit else b['frames'][-1]+32
 x=np.linspace(0,end,650)
 if is_exit:y=[curve(b,key,t) for t in x]
 else:
  y=[spring_curve(b,key,t,30) for t in x];base=[base_property(b,key,t/30)[0] for t in x]
  ax.plot(x,base,color='#888888',linestyle='--',label='authored base')
 ax.plot(x,y,color='#B40023',linewidth=2,label='exact user expression' if not is_exit else 'authored exit')
 ax.scatter(b['frames'],b[key],color='#3b2930',s=22)
 ax.set_title(name+' / '+key);ax.set_xlabel('Reference frames; actual FPS=30');ax.grid(alpha=.2);ax.legend(fontsize=7)
fig.suptitle('Exact user bounce expression on authored base keys; exit remains reconstructed')
fig.tight_layout();out=ROOT/'assets/studies/motion-graphs.png';fig.savefig(out,dpi=160);print(out)

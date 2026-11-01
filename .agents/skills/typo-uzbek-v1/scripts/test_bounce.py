#!/usr/bin/env python3
"""Regression checks for the supplied expression, not a reference-motion fit test."""
import math
from render import base_property,spring_curve,PROFILE
def independent_reference(block,key,t,fps):
    # Numerical base velocity evaluated at precisely AE's user-specified sample.
    keys=[x/30 for x in block['frames']]
    prior=[x for x in keys if x<=t]
    value=base_property(block,key,t)[0]
    if not prior:return value
    keytime=prior[-1];elapsed=t-keytime
    if elapsed>=1:return value
    sample=keytime-1/(fps*10);eps=1e-7
    velocity=(base_property(block,key,sample+eps)[0]-base_property(block,key,sample-eps)[0])/(2*eps)
    return value+velocity*.1*math.sin(2*math.pi*2*elapsed)/math.exp(6*elapsed)
def main():
    assert (PROFILE['bounce']['amp'],PROFILE['bounce']['freq'],PROFILE['bounce']['decay'])==(.1,2,6)
    blur=PROFILE['motion_blur']
    assert (blur['shutter_angle'],blur['shutter_phase'],blur['minimum_samples'],blur['adaptive_limit'])==(180,0,16,128)
    for fps in [25,30,60]:
        for values in [[0,60,80],[100,0,-30],[.12,1,1.1],[-35,0,8]]:
            block={'frames':[0,6,18],'x':values,'arrival_velocity_ratio':.15}
            for t in [-.1,0,.1,.2,.21,.27,.4,.59,.6,.65,1.,1.599,1.6,1.7]:
                actual=spring_curve(block,'x',t*30,fps)
                expected=independent_reference(block,'x',t,fps)
                assert abs(actual-expected)<2e-5,(fps,t,actual,expected)
    b={'frames':[0,6],'x':[0,60],'arrival_velocity_ratio':.15}
    assert spring_curve(b,'x',(.2+.1)*30,30)>60
    assert spring_curve(b,'x',1.2*30,30)==60
    assert spring_curve(b,'x',(.2+.1)*30,25)!=spring_curve(b,'x',(.2+.1)*30,60)
    # Base keys have no authored overshoot; the expression supplies it.
    for i in range(201):
        value,_=base_property(b,'x',i/1000)
        assert 0<=value<=60
    print('PASS: exact formula vs numerical velocity; latest-past-key reset; +/- and scale units; actual FPS epsilon; one-second cutoff; no double bounce; screenshot blur parameters.')
if __name__=='__main__':main()

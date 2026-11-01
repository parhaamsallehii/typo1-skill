#!/usr/bin/env python3
"""Curve inversion, radial geometry, temporal blending and interval regression."""
import math,numpy as np
from render import Ring,bezier,PROFILE
def main():
    assert PROFILE['easing']==[.06,.88,.10,.95]
    assert (PROFILE['shutter_angle'],PROFILE['shutter_phase'],PROFILE['samples_per_frame'],PROFILE['adaptive_sample_limit'])==(180,0,16,128)
    # Parametric points must survive the X inversion, not merely y(u).
    for s in np.linspace(0,1,29):
        x=3*(1-s)**2*s*.06+3*(1-s)*s*s*.10+s**3
        y=3*(1-s)**2*s*.88+3*(1-s)*s*s*.95+s**3
        assert abs(bezier(x)-y)<1e-10
    values=[bezier(u) for u in np.linspace(0,1,101)]
    assert all(b>=a for a,b in zip(values,values[1:]))
    cfg={'width':180,'height':320,'fps':30,'duration':2,'start':.5,'transition_duration':.5}
    r=Ring(cfg)
    assert r.weights(0) is None and r.weights(1.1) is None
    assert r.radius(.5)==r.first and r.radius(1)==r.last
    assert r.last-r.width/2>r.farthest+4*r.sigma
    for t in [.5,.533333,.6,.7,.9,.966666]:
        a,b,red=r.weights(t)
        assert np.allclose(a+b+red,1,atol=3e-6)
        assert min(a.min(),b.min(),red.min())>=0
    assert min(r.sample_counts)>=16 and max(r.sample_counts)<=128
    # Equal pixel distance in X/Y must produce equal coverage: a circle, not oval.
    assert r.distance[160,110]==r.distance[180,90]
    a=np.zeros((320,180,3),np.float32);b=np.ones_like(a)
    assert np.array_equal(r.composite(a,b,.1),a)
    assert np.array_equal(r.composite(a,b,1.1),b)
    assert not np.array_equal(r.composite(a,b,.6),a)
    print('PASS: exact Bezier X inversion; monotonicity; real circular distance; no pre/post ring; cleared corners; premultiplied temporal weights; supplied blur limits; next-scene switch.')
if __name__=='__main__':main()

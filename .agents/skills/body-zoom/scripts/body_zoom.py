#!/usr/bin/env python3
"""Virtual whole-scene camera rig and AE zero-speed 75/75 temporal curve."""
import argparse
import json
import math


def ease_75(u):
    """Invert cubic time handles (.75, .25); value handles (0, 1)."""
    if u <= 0:
        return 0.0
    if u >= 1:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(48):
        v = (lo+hi)/2
        x = 3*(1-v)**2*v*.75 + 3*(1-v)*v*v*.25 + v**3
        if x < u:
            lo = v
        else:
            hi = v
    v = (lo+hi)/2
    return 3*(1-v)*v*v + v**3


class BodyZoom:
    def __init__(self, start, end, width=1080, travel=200, distance=None):
        values = [start,end,width,travel] + ([] if distance is None else [distance])
        if not all(math.isfinite(x) for x in values):
            raise ValueError('All rig parameters must be finite')
        if start < 0 or end <= start or width <= 0 or travel < 0:
            raise ValueError('Require 0 <= start < end, positive width and nonnegative travel')
        self.start, self.end, self.width = start, end, width
        self.travel = travel*width/1080
        self.distance = 1500*width/1080 if distance is None else distance
        if self.distance <= self.travel:
            raise ValueError('Camera must remain in front of the scene: distance > travel')
        self.steps = max(0,math.floor((end-start)/2+1e-10))
        self.effective_end = start+2*self.steps

    def key_value(self,k):
        return self.travel if k%4 in (1,2) else 0.0

    def depth(self,t):
        if t < self.start or self.steps == 0:
            return 0.0
        if t >= self.effective_end:
            return self.key_value(self.steps)
        k = int((t-self.start)//2)
        u = (t-self.start-2*k)/2
        a,b = self.key_value(k),self.key_value(k+1)
        return a+(b-a)*ease_75(u)

    def scale(self,t):
        return self.distance/(self.distance-self.depth(t))

    def camera_z(self,t):
        return -self.distance+self.depth(t)

    def shutter_times(self,t,fps,samples=16):
        if fps <= 0 or not 16 <= samples <= 128:
            raise ValueError('Use positive fps and 16..128 samples')
        # Shutter angle 180 and phase 0: forward half-frame exposure.
        return [t+(i+.5)/samples*.5/fps for i in range(samples)]

    def plan(self):
        return dict(start=self.start, requested_end=self.end,
            effective_end=self.effective_end, ignored_tail=self.end-self.effective_end,
            keys=[] if self.steps==0 else [dict(time=self.start+2*k,z=self.key_value(k),
                in_speed=0,out_speed=0,in_influence=75,out_influence=75)
                for k in range(self.steps+1)],
            segment_seconds=2, pattern=['in','hold-near','out','hold-wide'],
            distance=self.distance, travel=self.travel,
            easing=dict(bezier=[.75,0,.25,1],zero_endpoint_speed=True),
            outside_policy='baseline before start; hold final keyed pose after effective_end; no forced reset',
            motion_blur=dict(enabled=True,shutter_angle=180,shutter_phase=0,
                samples_per_frame=16,adaptive_limit=128))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',type=float,required=True)
    p.add_argument('--end',type=float,required=True)
    p.add_argument('--width',type=int,default=1080)
    p.add_argument('--travel',type=float,default=200)
    p.add_argument('--distance',type=float)
    p.add_argument('--at',type=float)
    a=p.parse_args()
    try:
        r=BodyZoom(a.start,a.end,a.width,a.travel,a.distance)
    except ValueError as e:
        p.error(str(e))
    out=r.plan()
    if a.at is not None:
        out['sample']=dict(time=a.at,z=r.depth(a.at),camera_z=r.camera_z(a.at),scale=r.scale(a.at))
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()

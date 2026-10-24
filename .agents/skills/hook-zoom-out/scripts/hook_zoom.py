#!/usr/bin/env python3
"""Opening +200 Z -> baseline at 1.5 seconds, zero-speed 75/75 easing."""
import argparse
import json
from camera_core import CameraRig, ease_75


class HookZoom(CameraRig):
    def __init__(self, start=0, end=1.5, width=1080, travel=200, distance=None):
        super().__init__(start,end,width,travel,distance)
        self.effective_end=end

    def depth(self,t):
        if t <= self.start:
            return self.travel
        if t >= self.end:
            return 0.0
        return self.travel*(1-ease_75((t-self.start)/(self.end-self.start)))

    def plan(self):
        return dict(start=self.start,end=self.end,
            first_frame='ordinal frame 1 = t0; default t0=0 seconds',
            keys=[dict(time=self.start,z=self.travel,in_speed=0,out_speed=0,in_influence=75,out_influence=75),
                  dict(time=self.end,z=0,in_speed=0,out_speed=0,in_influence=75,out_influence=75)],
            distance=self.distance,travel=self.travel,
            easing=dict(bezier=[.75,0,.25,1],zero_endpoint_speed=True),
            outside_policy='hold initial close pose before first key; hold baseline after second key; no repeat',
            motion_blur=dict(enabled=True,shutter_angle=180,shutter_phase=0,
                samples_per_frame=16,adaptive_limit=128))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',type=float,default=0)
    p.add_argument('--end',type=float,default=1.5)
    p.add_argument('--width',type=int,default=1080)
    p.add_argument('--travel',type=float,default=200)
    p.add_argument('--at',type=float)
    a=p.parse_args()
    try:
        rig=HookZoom(a.start,a.end,a.width,a.travel)
    except ValueError as e:
        p.error(str(e))
    result=rig.plan()
    if a.at is not None:
        result['sample']=dict(time=a.at,z=rig.depth(a.at),camera_z=rig.camera_z(a.at),scale=rig.scale(a.at))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()

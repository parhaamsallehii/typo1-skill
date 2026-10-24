#!/usr/bin/env python3
"""Virtual whole-scene camera rig and AE zero-speed 75/75 temporal curve."""
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


class CameraRig:
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

    def scale(self,t):
        return self.distance/(self.distance-self.depth(t))

    def camera_z(self,t):
        return -self.distance+self.depth(t)

    def shutter_times(self,t,fps,samples=16):
        if fps <= 0 or not 16 <= samples <= 128:
            raise ValueError('Use positive fps and 16..128 samples')
        # Shutter angle 180 and phase 0: forward half-frame exposure.
        return [t+(i+.5)/samples*.5/fps for i in range(samples)]


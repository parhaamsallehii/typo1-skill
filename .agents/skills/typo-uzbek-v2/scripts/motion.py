import math
import numpy as np

def base_property(block,key,t):
    """Base value/analytic velocity in seconds, BEFORE expression application."""
    xs=np.asarray(block['frames'],float)/30
    ys=np.asarray(block[key],float)
    if t<xs[0] or t>=xs[-1]:return (float(ys[0] if t<xs[0] else ys[-1]),0.)
    n=int(np.searchsorted(xs,t,side='right')-1)
    duration=xs[n+1]-xs[n];u=(t-xs[n])/duration
    ratio=float(block.get('arrival_velocity_ratio',.15))
    # Monotone authored Hermite base: zero outgoing speed, specified
    # incoming speed. The user supplied the spring, not the base AE graph.
    ease=(-2+ratio)*u**3+(3-ratio)*u**2
    derivative=(3*(-2+ratio)*u*u+2*(3-ratio)*u)/duration
    delta=ys[n+1]-ys[n]
    return float(ys[n]+delta*ease),float(delta*derivative)

def spring_curve(block,key,frame_age,fps):
    t=frame_age/30
    value,_=base_property(block,key,t)
    xs=np.asarray(block['frames'],float)/30
    n=int(np.searchsorted(xs,t,side='right')-1)
    if n<0:return value
    elapsed=t-xs[n]
    if elapsed<1:
        _,velocity=base_property(block,key,xs[n]-1/(fps*10))
        value+=velocity*.1*math.sin(2*math.pi*2*elapsed)/math.exp(6*elapsed)
    return value


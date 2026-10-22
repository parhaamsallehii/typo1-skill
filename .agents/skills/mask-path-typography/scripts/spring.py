"""Stateless, signed, velocity-driven spring. Units: seconds and path px/s."""
import math


def spring_offset(t, velocity, amp=0.16, freq=2.5, decay=5.5,
                  duration=1.0, fade_duration=0.2, max_offset=300):
    if t <= 0 or t >= duration:
        return 0.0
    fade = min(max(fade_duration, 0.0), duration)
    envelope = 1.0
    if fade and t > duration - fade:
        u = (t - (duration - fade)) / fade
        envelope = 1 - u*u*(3-2*u)
    amplitude = velocity * amp
    if max_offset is not None:
        amplitude = max(-max_offset, min(max_offset, amplitude))
    return amplitude * math.sin(2*math.pi*freq*t) * math.exp(-decay*t) * envelope


def base_margin(t, start, arrival, source, target, profile="linear"):
    if arrival <= start:
        raise ValueError("arrival must be later than start")
    u = max(0.0, min(1.0, (t-start)/(arrival-start)))
    if profile == "spring-entry":
        # Cubic Hermite, normalized endpoint slopes 1.5 and 0.65.
        u = (-2*u**3+3*u**2) + (u**3-2*u**2+u)*1.5 + (u**3-u**2)*0.65
    elif profile != "linear":
        raise ValueError("profile must be linear or spring-entry")
    return source + (target-source)*u


def incoming_velocity(start, arrival, source, target, fps, profile="linear"):
    # Match the supplied expression's just-before-key sample time: fd/10.
    e = 1.0 / (fps*10)
    # Symmetric finite derivative centered strictly before arrival, base only.
    a, b = arrival-e*1.5, arrival-e*0.5
    return (base_margin(b,start,arrival,source,target,profile)
            -base_margin(a,start,arrival,source,target,profile)) / (b-a)


def margin_at(t, start, arrival, source, target, fps, profile="linear", spring=None):
    if t <= arrival:
        return base_margin(t,start,arrival,source,target,profile)
    v = incoming_velocity(start,arrival,source,target,fps,profile)
    return target + spring_offset(t-arrival,v,**(spring or {}))

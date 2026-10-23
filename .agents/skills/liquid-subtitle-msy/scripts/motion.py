"""Deterministic eight-frame anticipation and the user's AE velocity bounce."""
import math


def spring(t, velocity, amp=.1, freq=2, decay=6):
    return velocity * amp * math.sin(freq*t*2*math.pi) * math.exp(-decay*t) if 0 < t < 1 else 0.0


class WidthTrack:
    def __init__(self, cues, widths, fps):
        if fps <= 0:
            raise ValueError('fps must be positive')
        self.initial = widths[0] if widths else 0
        self.events = []
        self.shortened = []
        self.resets = []
        for i in range(1, len(cues)):
            cut = cues[i]['start']
            if abs(cues[i-1]['end'] - cut) > 1e-7:
                # A new disjoint block cuts on at its own settled width.
                self.events.append(dict(start=cut, end=cut, a=widths[i], b=widths[i], velocity=0))
                continue
            start = max(cues[i-1]['start'], cut-8/fps)
            if cut-start < 8/fps-1e-7:
                self.shortened.append(i)
            a = self.at(start)
            duration = cut-start
            if duration <= 0:
                raise ValueError('Cue transitions need increasing start times')
            self.events.append(dict(start=start, end=cut, a=a, b=widths[i],
                                    velocity=(widths[i]-a)/duration))

    def at(self, t):
        for e in reversed(self.events):
            if t < e['start']:
                continue
            if t < e['end']:
                u = (t-e['start'])/(e['end']-e['start'])
                return e['a'] + (e['b']-e['a'])*u
            return e['b'] + spring(t-e['end'], e['velocity'])
        return self.initial

    def report(self):
        return dict(events=self.events, shortened_transitions=self.shortened,
                    amp=.1, freq=2, decay=6, duration=1,
                    profile='linear with real signed incoming velocity')

# Frame and spring specification

Use actual output FPS F; do not stretch the video to 30fps. All deltas below are frame intervals, not ordinal-frame counting. At 30fps, 2 frames = 0.0666667s, 3 = 0.1s and 4 = 0.1333333s.

| Event | First Margin, relative to resting text | Opacity |
|---|---:|---:|
| S: exact requested entrance cue | +35 or −35 | 0 |
| S+2/F | 0 | in progress |
| S+4/F | spring about 0 | 100 |
| E: default S+4/F+1 second | keyed 0 | 100 |
| E+2/F | keyed +35 or −35 | fading |
| E+3/F | spring active, invisible after fade | 0 |

Interpret the user's exit wording as a two-frame margin move and a three-frame opacity fade, both starting at E, rather than a five-frame move. Keep these durations separate. Use the same sign for return toward the entry side by default; the user permits either sign. Choose side/path direction to match the reference and keep text outside the face. Treat 35 as native path units (pixels for the coded renderer), not 35%, degrees or full-frame travel. A new rest layout can have a nonzero absolute AE margin; 0 here means that resting baseline placement.

Use flat/linear keyed margin segments by default because their interpolation was not supplied. This is an authored choice, not recovered source keyframe data. Do not apply zero-velocity Easy Ease to the arrival and then fake a bounce: the expression samples velocity just before a key. An entry from +35 to 0 over 2/30s gives −525 path units/s; the opposite sign gives +525. This yields a visible, signed overshoot.

Apply exactly:

`value + v * 0.1 * sin(2*pi*2*t) / exp(6*t)` for 0 <= t < 1 second since the most recent key, with v = base-property velocity at that key's time minus frameDuration/10. Otherwise use the base value. At the initial entrance key, preceding held velocity is zero. At the exit-start hold key, preceding held velocity is zero. At the two arrival keys, use the incoming segment's signed velocity. Reset elapsed time at every key; do not sum all previous springs, clamp amplitude, change frequency/decay or add hand-drawn noise. The original complete AE expression is bundled unmodified in `scripts/first-margin-expression.jsx`.

Hold does not mean deleting the spring: let its oscillation decay naturally while base margin holds at 0. The supplied expression ends its contribution at 1s. Do not add a secret end fade to the spring. The exit opacity hides subsequent exit oscillation.

Set opacity linearly by default. Opacity is a percentage, not an angle. In the code implementation opacity values are normalized 0..1 internally.

For coded temporal blur, approximate the requested phase-zero 180° shutter with forward exposure [t, t+0.5/F], midpoint-sampled 16 times minimum, up to 128 based on displacement. Average alpha/premultiplied coverage, never duplicate opaque offset text. Sample movement along the curve and opacity at every subframe. Constant identical subframes may be collapsed analytically. This temporal approximation does not reproduce AE's proprietary rasterization.

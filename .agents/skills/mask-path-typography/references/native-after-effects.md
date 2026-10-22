# Native After Effects

Use only when AE, bundled fonts and the required plugin are actually available. These instructions have not been executed by the Python renderer.

1. Enable comp motion-blur master switch. Set Advanced > Motion Blur: **Angle 180°, Phase 0°, Samples 16, Adaptive Limit 128**. Enable every eligible text/shape/footage/precomp layer and check nested comps.
2. Install exact bundled fonts. Use a Persian-capable composer with RTL shaping.
3. Draw an open, shallow, smooth Bézier mask on the text layer with continuous tangents. Use it as a path guide, not an unintended clipping mask. Select it in Text > Path Options. Set orientation/Reverse Path as needed while preserving reading order. Keep the guide invisible; leave Force Alignment off unless requested.
4. Animate First Margin entry with ordinal frames **1 and 5**, spanning four intervals. Key **Opacity 0%→100%** on those same frames. After the entry spring settles and the title holds, animate First Margin back to its entry-side position across another four intervals; key **Opacity 100%→0%** on those exit frames. Extend the path beyond the frame for motion and overshoot. Test direction rather than assuming RTL reverses motion.
5. Use exactly four First Margin keys per layer for this preset (entry start/end and exit start/end). Paste `scripts/first-margin-expression.jsx` on First Margin. It applies the stronger signed velocity spring after entry key 2 only, with a smooth final 0.2 s fade; exit key 3 does not start a competing bounce. Keep meaningful incoming speed; do not stack elastic easing. Opacity is keyed separately, with linear interpolation rather than an elastic bounce.
6. Apply cream face/red shadow or red face/cream shadow. **Distance 3, Opacity 100%, Softness 0**. Default shadow direction is straight down; editor angle conventions vary. Clip stronger fixed noise and halftone inside the text (4 reference-pixel dot pitch, approximately 1.05-pixel radius). Add continuously evolving hand-drawn contour movement around **3.2 px at 8 Hz** at a 1080-wide composition; preserve joined letterforms and enable motion blur on the animated layer.
7. Apply native **Deep Glow Radius 1000, Exposure 0.3, Screen** to both styles. Verify against installed plugin controls. Built-in Glow is not Deep Glow.
8. Inspect fast movement, spring reversals and final hold; export and verify the actual artifact.

Adobe's guide explains composition/layer motion-blur controls and shutter/sampling concepts:
https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/assorted-animation-tools/assorted-animation-tools.html

The user's screenshot/written values are authoritative for the preset. An exact reconstruction of unknown Bézier handles, keyframe graph and plugin internals cannot be recovered from the baked MP4 alone.

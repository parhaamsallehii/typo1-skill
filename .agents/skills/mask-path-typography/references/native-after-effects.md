# Native After Effects

Use only when AE, bundled fonts and the required plugin are actually available. These instructions have not been executed by the Python renderer.

1. Enable comp motion-blur master switch. Set Advanced > Motion Blur: **Angle 180°, Phase 0°, Samples 16, Adaptive Limit 128**. Enable every eligible text/shape/footage/precomp layer and check nested comps.
2. Install exact bundled fonts. Use a Persian-capable composer with RTL shaping.
3. Draw an open, shallow, smooth Bézier mask on the text layer with continuous tangents. Use it as a path guide, not an unintended clipping mask. Select it in Text > Path Options. Set orientation/Reverse Path as needed while preserving reading order. Keep the guide invisible; leave Force Alignment off unless requested.
4. Animate First Margin with two keys. Ordinal frames 1 and 15 span 14 intervals. Extend the path beyond the frame for entry and overshoot. Test direction rather than assuming RTL reverses motion.
5. Paste `scripts/first-margin-expression.jsx` on First Margin. It implements the supplied velocity spring plus smooth final 0.2 s fade. Keep meaningful incoming speed; do not stack elastic easing.
6. Apply cream face/red shadow or red face/cream shadow. **Distance 3, Opacity 100%, Softness 0**. Default shadow direction is straight down; editor angle conventions vary. Clip fixed fine noise/halftone inside the text.
7. Apply native **Deep Glow Radius 1000, Exposure 0.3, Screen** to both styles. Verify against installed plugin controls. Built-in Glow is not Deep Glow.
8. Inspect fast movement, spring reversals and final hold; export and verify the actual artifact.

Adobe's guide explains composition/layer motion-blur controls and shutter/sampling concepts:
https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/assorted-animation-tools/assorted-animation-tools.html

The user's screenshot/written values are authoritative for the preset. An exact reconstruction of unknown Bézier handles, keyframe graph and plugin internals cannot be recovered from the baked MP4 alone.

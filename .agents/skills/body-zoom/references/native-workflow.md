# Native workflow and verified source notes

1. Open the complete scene composition, not an isolated presenter layer. Preserve source audio, caption timing and every foreground element.
2. Set options in an AE script runner, then evaluate `scripts/build_ae_rig.jsx`:

```js
$.global.BODY_ZOOM_OPTIONS={start:5,end:12,travel:200};
$.evalFile(new File('/absolute/path/to/body-zoom/scripts/build_ae_rig.jsx'));
```

The helper creates a duplicated comp instead of changing the original. For a plain 2D stack it enables 3D and motion blur on compatible visual layers. For an existing camera/3D/adjustment stack it uses a 3D precomp scene plane to preserve the original appearance. Inspect nested comps and effects in the host; syntax checks outside AE do not validate AE's rendering or version compatibility. Do not report that the internal layers became 3D in the wrapper case.

For a subsequent separate interval, inspect the existing Z keys and supply a complete merged `keyPlan` (`[{time:...,z:...}, ...]`) through `BODY_ZOOM_OPTIONS`, in output scene units. Preserve prior ranges and their resting-state transitions; do not discard them. The helper refuses an incomplete replacement and checks for custom XY/Z animation before resetting its controller. It re-enables 3D/blur for newly added compatible foreground layers when reusing the named rig.

The native helper validates the complete merged plan before clearing any keys, reports actual key counts/times, and resets static null scale/orientation/rotation. It rejects custom animated control transforms/parents and newly added foreign cameras, lights, adjustment layers or depth offsets on a reused rig; integrate those into the preserved scene group first instead of silently converting them.

3. The camera is a 3D camera by definition. Parent it to the 3D null; animate the null's separated Z Position. Keep content outside that moving control. Camera auto-orient is disabled, orientation fixed, depth of field off, camera zoom equal to baseline distance. Confirm that positive null Z moves closer in AE's default forward-looking coordinate system.
4. Every moving segment lasts exactly two seconds. Set both temporal influences to 75 and speeds to zero. Constant endpoints define the holds. Do not use Auto Bezier/roving keys or default Easy Ease as a substitute.
5. Set composition motion blur on: shutter angle 180, phase 0, minimum samples 16, adaptive limit 128. Enable eligible visual layer/precomp blur. Camera layers have no image that can be blurred independently; visible camera-induced motion is blurred on the affected content layers. Inspect the master view through the active rig camera.
6. Review first frame before/after start, zoom extremes, hold durations, final complete key and unused tail. A seven-second interval starting at 5 has keys at 5,7,9,11 and no key at 12. Three/five-second intervals end near; no return key is silently added.
7. Inspect baseline framing and effect compatibility after 3D conversion. If layer styles, mattes, effects or existing depth alter the look, preserve the composed scene using the 3D wrapper route. Preserve all visual layers in that scene; do not place new text/watermarks outside the camera pass.
8. Render in the available AE host and verify the result. If only code execution is available, use the documented virtual camera route and say the JSX was not executed in AE.

## Source references

- Adobe, “Speed”: https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/speed-between-keyframes/speed.html — distinguishes keyframe speed from temporal influence; default Easy Ease uses zero speed and 33.33% influence. The requested 75% is explicitly assigned instead.
- Adobe, “Cameras, lights, and points of interest”: https://helpx.adobe.com/after-effects/desktop/work-with-layers/camera-layer/cameras-lights-points-interest.html — camera position and Z tracking control the scene view. The code's projection formula is the mathematical coplanar implementation for the stated rig geometry.
- User's bundled motion-blur screenshot supplies the exact 180/0/16/128 settings. No claim is made that the coded sample average duplicates AE's proprietary renderer pixel for pixel.

The normalized code curve is derived from zero-speed value tangents with outgoing time-handle influence .75 and incoming .75, giving time handles .75 and 1−.75=.25, value handles 0 and 1. Invert Bezier time before evaluating value. This derivation is an implementation choice matching that temporal handle construction, not an Adobe-published CSS preset.

---
name: body-zoom
description: Apply a shared whole-scene body zoom over a requested video interval using a 3D camera parented to a 3D null, or an equivalent virtual camera in code. Repeat two seconds in, two seconds near hold, two seconds out, two seconds wide hold with 200 reference-unit Z travel, zero-speed 75/75 temporal easing, and mandatory 180-degree/phase-zero temporal motion blur at 16–128 samples. Use for body zoom, body-zoom, زوم بدنه, زوم این و زوم اوت وسط ویدیو or cyclic camera zoom. Move every visual layer together, including video, text, footage, shapes, ramp, watermark and glass subtitles. Ignore leftover spans shorter than two seconds without retiming or extra keys.
---

# Body Zoom

Apply the user's repeating camera motion to the whole edited scene. Keep all visual content together under one camera projection. Use the requested start/end times; preserve audio, cut times, caption timing and existing layer animation. Do not turn this into face tracking, an individual layer's Scale animation, or an elastic/bouncing zoom.

## Read the reference

Inspect `assets/motion-blur-settings.png`. Preserve the exact uploaded reference (1080p scene defaults are independent of the screenshot dimensions), SHA-256 `965f32295be095a55cbb10f0999d067ddafff39ebf3229eb5c0a6aae7ed9c8e1`.

Set motion blur to **Shutter Angle 180°, Shutter Phase 0°, Samples Per Frame 16, Adaptive Sample Limit 128**. Enable the composition master switch and every eligible visual layer/nested transformed precomp. Do not replace temporal blur with a static Gaussian/directional blur, optical flow or frame blending. Keep settled holds sharp except for existing motion inside the scene.

## Exact timing

Let `S` be requested start and `E` requested end. Use `N=floor((E-S)/2)` complete two-second stages; the effective last key is `S+2N`. Do not compress, stretch or distribute keys to fill `E`. If `N=0`, add no zoom motion or keys.

Generate this sequence of null Z offsets relative to baseline:

| Time | Z offset at 1080-wide reference | Meaning |
|---|---:|---|
| S | 0 | Initial wide pose |
| S+2 | +200 | Finish zoom in |
| S+4 | +200 | Finish two-second near hold |
| S+6 | 0 | Finish zoom out |
| S+8 | 0 | Finish two-second wide hold |
| S+10 | +200 | Finish next zoom in |
| S+12 | +200 | Finish next near hold |

Continue this four-stage cycle through the last complete stage. Add the unchanged-value hold keys explicitly; do not delete them as redundant. Never cumulatively add 200 each cycle. Interpret the user's 200 position amount as **Z scene units/pixels**, not 200 degrees, a 200% scale or a camera rotation. Default X/Y and rotation remain fixed.

For a 7-second range beginning at 0, keys are at `0,2,4,6`, with values `0,200,200,0`; keep the final second at that final pose without any key at 7. For a range from 5 to 12, use keys `5,7,9,11` and no key at 12.

Before `S`, keep the baseline. After the last generated key, hold that pose, including the unused tail. Do not add an unrequested return key, partial transition, snap-back or fade at `E`. This matches ordinary keyframed-property behavior. If the last complete stage ends zoomed in (e.g. a 3- or 5-second range), explicitly report that it ends on the near pose; hold it until an existing cut, subsequent instruction or separately designed transition. The interval limits animation-key generation; it does not guarantee a return to wide. Do not claim it resets automatically outside the range.

Preserve exact requested key times even when they fall between output frames; render from composition time and do not move them onto a different two-second grid. For variable-frame-rate input, normalize/handle timestamps before applying the time-based pattern. Preserve source duration and audio sync.

## 75/75 temporal curve

Use temporal Bezier with **incoming speed 0, outgoing speed 0, incoming influence 75%, outgoing influence 75%** at moving segment endpoints. Holds retain identical values and remain constant. Do not use the default Easy Ease influence of 33.33%, a generic smoothstep, power easing, or a spring.

In native AE, apply `KeyframeEase(0,75)` to both temporal sides of the scalar Z property, with temporal auto-Bezier off. Separate Position dimensions to animate only Z. Spatial path interpolation must not add XY drift or arcs.

For the same normalized zero-speed temporal handle construction in code, use cubic Bezier `(0.75,0,0.25,1)`. Solve its X/time polynomial for parameter `v`, then evaluate Y/value. Do not insert elapsed time straight into the Bezier parameter or treat 75 as a speed. `scripts/body_zoom.py:ease_75` performs the inversion deterministically. This produces slow starts/ends and a faster middle, without overshoot.

## Shared 3D rig and layer scope

Build a **3D Null named `Body Zoom Control`** and a **Camera named `Body Zoom Camera`**. Cameras are intrinsically 3D in AE; a camera does not have the same optional AV-layer 3D switch. Enable 3D for the null and every compatible rendered content layer: main video, text, shapes, footage, objects, photos, ramp, watermark and subtitle glass. Leave audio-only layers and nonvisual helpers unaffected.

Parent **only the camera** to the animated null. Leave content stationary relative to its scene; do not parent both camera and all content to the same moving null, because that cancels relative zoom. Preserve existing local parent relationships and layer order. Keep all ordinary 2D edit elements coplanar at Z=0 rather than inventing depth offsets or parallax.

Center the rig on the final canvas center. For a 1080-wide scene use baseline camera distance/zoom `D=1500` scene units and Z travel `200`. At 1080×1920, null baseline is `(540,960,0)`, camera local position `(0,0,-1500)`, looking forward with zero orientation and no depth-of-field blur. Null movement `0→+200` brings the camera closer, `+200→0` returns it. In another coordinate system choose the sign that actually zooms in; never assume +Z is forward in every engine.

For other resolutions scale both travel and camera distance by `W/1080` to preserve the same visual strength: at 2160 wide, travel 400 and distance 3000. The coplanar projected magnification is `D/(D−z)`, giving 1.0 at wide and about 1.153846 at near. If using an existing compatible camera, preserve its framing and calibrate travel consciously rather than silently changing its focal length, orientation or depth layout.

If the edit already has cameras, 3D depth, adjustment layers or effects that would break on direct conversion, preserve its composed output in a full-frame precomp/render group, make that scene plane 3D, and put the new shared camera/null outside it. Keep collapse transformations off when preserving an existing internal camera. This is an explicit appearance-preserving fallback; do not claim every original internal layer's switch changed if using it. Verify no rendered layer bypasses the shared camera. Do not destroy existing camera animation or dismantle mask/track-matte relationships.

Reuse/update an existing Body Zoom camera/control rather than stacking another rig. The native builder recognizes its named rig in the active composition and replaces that rig’s Z keys in the duplicate. For separate ranges on one timeline, pass a complete merged `keyPlan` of `{time,z}` items in output scene units, preserving every previously authorized interval. The native helper refuses to erase existing keys outside the new interval when no merged plan is supplied. It also includes newly added compatible visual layers when reusing a rig.

Apply this pass **after** composing the scene's original effects. In particular, `shadow-ramp`, `msy-watermark`, `liquid-subtitle-msy` and typography retain their local positions/source bindings inside the scene and then move/zoom together with it. Never leave watermark/text as an unaffected HUD, add a second independent zoom, or make glass sample a recursively zoomed version of itself. Include foreground layers added later in the shared scene as well. Do not add any of those optional skills merely because body-zoom is used.

## Run the native or virtual implementation

- **After Effects:** Follow [native-workflow.md](references/native-workflow.md) and run `scripts/build_ae_rig.jsx` inside AE. It duplicates the source composition, builds the null/camera, enables eligible 3D/motion-blur switches, applies exact scalar Z keys and 75/75 easing, and sets the reference blur settings. It is supplied host-side code; do not claim it ran or an .aep was created when no AE host was available.
- **Code/HTML/video pipeline:** Use the virtual rig from `scripts/body_zoom.py`. Treat its controller and camera as scene-graph nodes. Put all content under one camera view, preserving existing transforms in scene space. For coplanar edits, one whole-scene center projection using `D/(D−z)` is mathematically equivalent to the camera view. This is not native AE or an arbitrary-depth 3D renderer.
- **Existing flattened video:** `scripts/render_zoom.py` applies the same planar projection to the complete image, so all already-composited layers zoom together. It has no editable original layers to toggle to 3D. State this distinction rather than pretending a native camera/null or original layer switches were created.

```bash
python scripts/body_zoom.py --start 5 --end 12 --at 8
python scripts/render_zoom.py --input /task/finished-scene.mp4 --out /task/body-zoom.mp4 --start 5 --end 12
```

The Python renderer needs Pillow, NumPy, SciPy, FFmpeg and ffprobe. It preserves source audio by stream copying into the output container; choose a compatible container/codec rather than dropping audio. Normalize display rotation/pixel aspect/VFR first if required. Use a distinct output file. Copy reusable code/assets into portable editable projects; never overwrite the original video or skill reference.

## Temporal motion blur

For each output frame time `t`, sample the complete scene and camera over `[t, t+0.5/fps]`, because phase is 0 and shutter angle is 180. Use at least 16 midpoint samples, increasing up to 128 when projected motion requires it. Average linear-light premultiplied RGBA, then unpremultiply/encode. Evaluate existing object/text/glass animation at each sample before the shared camera projection. Do not average straight RGB against black or add a static blur to a held frame.

`scripts/render_zoom.py:render_frame(scene_at,rig,t,width,height,fps)` provides this integration point. For editable scenes, `scene_at(subframe_time)` must return the fully composed scene at that time. The standalone flattened-input CLI holds the decoded source frame within the shutter and blurs the camera transform; it does not reconstruct true subframe source/foreground motion or AE's proprietary adaptive sampler. Be explicit about that practical limit. Do not apply blur twice to existing native content motion. With the screenshot's forward shutter, a frame just before a movement key may already include a little motion from later subframes; do not move key times to hide this.

## Verify

1. Confirm actual key times/values for 7 seconds, several full cycles, an offset start, a sub-two-second range and a range ending on the near pose. Verify there are no extra tail keys or shortened stages.
2. Confirm zero endpoint velocity, strong middle velocity, monotonic in/out motion, no bounce, and unchanged two-second holds. Compare native Z influences when AE is available; inspect code curve inversion separately.
3. Place text, a shape/photo and a background marker at different positions. Verify they share one projected transform and keep relative alignment; verify ramp/watermark/glass remain in their intended internal stack.
4. Confirm native master/layer blur switches and exact screenshot values, or inspect 16–128 temporal samples in the coded report. Compare moving frames to an instantaneous sample and held frames for absence of residual camera blur.
5. Check determinism when seeking the same time, clean boundaries, stable framing and no exposed empty edges. Check camera stays in front of the scene plane and both zoom extremes remain readable.
6. Fully decode the render; check duration, dimensions, fps and preserved audio. Validate the requested range against source duration.
7. Save the skill through the supported skill workflow and report only actual code/native checks and renders. Do not call a virtual rig an executed native AE project.

Example prompt: «از ثانیهٔ ۵ تا ۱۲ از اسکیل body-zoom استفاده کن و همهٔ لایه‌ها با هم زوم شوند.»

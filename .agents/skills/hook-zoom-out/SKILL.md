---
name: hook-zoom-out
description: Create a single opening whole-scene camera zoom-out for the video hook. Start ordinal frame 1 at +200 reference-unit Z offset, return exactly to original/default framing at 1.5 seconds with zero-speed 75/75 temporal Bezier influence, then stay at baseline. Use for hook zoom out, hook-zoom-out, زوم اوت اول ویدیو or زوم خروجی هوک. Move video and all text/shapes/footage/objects/ramp/watermark/glass together under one camera/null or virtual camera. Preserve the earlier 180-degree phase-zero 16–128-sample motion blur. Never run a cyclic body zoom, add an entrance zoom-in, or animate camera rotation.
---

# Hook Zoom Out

Begin the video already close, then smoothly reveal its original framing. Create only one opening zoom-out; keep the final baseline afterward. Preserve the original audio, edit duration, cut times, subtitle timing and foreground animation. Respond concisely in Persian.

## Exact keys

| Key | Composition-relative time | Z offset from default |
|---|---:|---:|
| First visible frame, ordinal frame 1 | `0 seconds` | `+200` reference units |
| Return to default | `1.5 seconds` | `0` |

Interpret frame 1 as the first visible frame at t=0, not t=1/fps. At 30 fps the second key is zero-based frame 45 / ordinal frame 46. At 24 fps it is ordinal frame 37; at 60 fps ordinal frame 91. For rates that do not place 1.5 seconds exactly on a frame, retain the exact subframe key time rather than retiming the move.

The second key is at absolute **1.5 seconds from video start**, not 1.5 seconds after an offset first frame. Do not add a default key at t=0 before the close pose, fade/scale in, repeat the motion, or add a spring. Remain at the original framing after t=1.5 for the rest of the scene, unless another explicitly requested camera move starts later. Do not inherit body-zoom's two-second stages or tail truncation.

Treat “200 position” as 200 Z scene units/pixels at 1080 reference width, not degrees, a 200% scale, or a camera lens-zoom change. Only relative camera-to-scene distance changes. Default X/Y, orientation, lens, perspective and baseline crop remain fixed. If the video is shorter than 1.5 seconds, do not silently accelerate the move, freeze/extend the video or place keys beyond it; report that this exact preset needs 1.5 seconds and resolve an explicitly requested variation.

## Curve

At both ends use temporal Bezier with **incoming/outgoing speed 0 and incoming/outgoing influence 75%**. This gives a soft start/end and faster middle without overshoot. Keep temporal auto-Bezier off. Do not substitute default Easy Ease (33.33% influence), a generic easeInOut, smoothstep, a bounce or a spring.

For code, use the zero-speed handle construction `cubic-bezier(0.75,0,0.25,1)`: invert the X/time polynomial, then evaluate Y/value. `scripts/camera_core.py:ease_75` implements this deterministically. The offset is `200 * (1−ease_75(t/1.5))` between the two keys, 200 at/before the first and exactly 0 at/after the second.

## One shared camera

Use the same whole-scene setup as `body-zoom` where it is available, but apply this skill's two-key timeline. This skill bundles the required math/rendering/native helpers and works without body-zoom being installed. Do not run body-zoom's repeating animation merely to get a camera.

- Native setup: a 3D null `Hook Zoom Out Control`, with a camera `Hook Zoom Out Camera` parented to it. Cameras are inherently 3D. Enable 3D and layer motion blur for every compatible rendered visual layer.
- Include main footage, text, shapes, photos, inset footage, objects, shadow-ramp, watermark, glass subtitle and other foreground effects. Preserve internal layering and local animation. Do not leave a fixed HUD behind.
- Parent only the camera to the moving control; do not parent content to that same moving null, which would cancel relative zoom.
- For an ordinary planar 1080×1920 edit use null baseline `(540,960,0)`, camera local `(0,0,-1500)`, camera zoom/distance `1500`, zero orientation and no depth-of-field blur. Animate null Z `200→0`. Close magnification is about `1.153846`; default is exactly `1`.
- At other resolutions scale both travel and baseline distance by `W/1080`, preserving visual strength. At 2160 wide use travel 400, distance 3000. If adapting an existing camera, preserve its original baseline and choose the forward direction correctly rather than changing its lens/crop or assuming every engine's +Z sign is the same.
- For existing depth/cameras/adjustments/mattes/effects that would be altered by direct 3D conversion, preserve the completed scene in a single 3D precomp/render group, collapse transformations off, and apply the shared camera outside it. State when using this route: internal layers retain their original switches, while the whole scene moves together. Audio-only layers do not need a visual 3D switch.
- Keep glass sampling from its clean original source in scene space, then compose ramp/watermark/glass/text, then apply the outer camera. Do not recursively sample the finished zoomed scene or independently zoom individual assets. Optional skills are not added unless invoked/present.

If body-zoom is also requested later, use one shared camera/control and merge the two authorized key plans. For a later body move starting at 5 seconds, this hook returns to baseline at 1.5 and rests wide until that move starts. Do not stack two independent camera transforms, erase later keys, or overwrite the hook with a new baseline key at t=0. Resolve explicitly overlapping camera instructions as one coherent timeline rather than summing offsets blindly. Reuse an existing Hook/Body named rig; do not apply the hook twice.

## Motion blur

Carry forward the supplied settings from the earlier zoom skill. `assets/motion-blur-settings.png` is the original reference, SHA-256 `965f32295be095a55cbb10f0999d067ddafff39ebf3229eb5c0a6aae7ed9c8e1`.

Enable composition and eligible layer/precomp motion blur: **Angle 180°, Phase 0°, Samples Per Frame 16, Adaptive Limit 128**. For code, sample the current scene and camera over `[t,t+0.5/fps]` with at least 16 midpoint samples, adapt up to 128 as needed, average linear-light premultiplied RGBA, then encode. Do not replace it with Gaussian blur, frame blending or optical flow. Keep the returned default pose sharp when no other element is moving.

## Execute

1. Inspect the actual finished scene and source timing; establish its original framing before adding the close offset. Copy assets/code into portable task paths without modifying this skill.
2. Get the exact plan with `python scripts/hook_zoom.py`; no flags are required for the default opening. `--start/--end` are overrides only for an explicit user variation, not automatic relocation to the current playhead/work area.
3. Native AE: follow [native-workflow.md](references/native-workflow.md) and run `scripts/build_ae_hook.jsx`. It duplicates the active comp, builds/reuses the shared camera/null, keys Z at `0/1.5` with `200/0`, enables eligible 3D/blur switches and preserves the original comp. It recognizes existing Body Zoom names too; supply a complete merged `keyPlan` to preserve separately authorized ranges. Do not claim an .aep/native render exists when no AE host ran.
4. Code renderer: use `HookZoom` from `scripts/hook_zoom.py` and `render_frame(scene_at,rig,t,width,height,fps)` from `scripts/render_hook.py`. The callback must compose every original layer/effect at each shutter sample before the shared planar camera projection. This is a virtual coplanar camera, not an arbitrary-depth 3D renderer.
5. For a complete flattened video use the CLI below. All baked elements zoom together, but there are no editable original layers to toggle to 3D. It holds the decoded source frame during each exposure and temporally samples the camera; it does not reconstruct source subframe motion or AE's proprietary adaptive renderer. Report the route honestly.
6. Preserve source audio, duration and subtitle sync. Normalize display orientation, pixel aspect and VFR first where needed. The CLI stream-copies audio; use a compatible output container/codec rather than dropping it.

```bash
python scripts/hook_zoom.py --at 0.75
python scripts/render_hook.py --input /task/finished-scene.mp4 --out /task/hook-zoom-out.mp4
```

Python rendering requires Pillow, NumPy, SciPy, FFmpeg and ffprobe. Output must differ from source. Neither an installed After Effects host nor native 3D execution is implied by successful Python rendering.

## Verify and report

- Confirm exactly two default keys: ordinal first frame at t=0/+200 and t=1.5/0. At 0.75 seconds the controller is halfway in Z; perspective magnification is not linear in Z.
- Confirm monotonic outward motion, zero endpoint speed, stronger middle speed, no overshoot, no repetition and a settled default pose at/after 1.5.
- Test several fps values including fractional rates and larger resolution. Preserve key times; do not convert the 1.5-second move to body-zoom's two-second timing.
- Verify video plus every foreground marker shares a single transform; keep internal ramp/watermark/glass order and source mapping intact.
- Inspect moving frames against an instantaneous sample for temporal blur, and held frames for no residual camera blur. Repeated seeks at the same time must match.
- Fully decode the video, check duration, frame rate, dimensions and preserved audio. Verify native switches/easing in AE when an actual host is available; otherwise distinguish syntax checks and the virtual-camera render from native execution.
- Save through the supported skill workflow. Report only actual tests and outputs.

Example: «اول ویدیو از اسکیل hook-zoom-out استفاده کن.»

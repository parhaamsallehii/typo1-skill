---
name: head-track
description: >-
  Create the user's presenter head-tracking look by stabilizing one high-contrast
  facial feature, such as a nostril, on the main talking-head video during a
  requested interval. Use for head track, head-track, head tracking, ترک فیس,
  ترک سر or قفل تصویر روی صورت. Apply inverse X/Y motion to the presenter video
  only; enable motion blur at shutter angle 180, phase 0, 16 samples and adaptive
  limit 128. Prevent exposed frame edges using measured overscan or reflected
  Motion Tile extension. Preserve the supplied head-track video and blur screenshot.
---

# Head Track

Keep a selected facial point stationary while the body and background shift around
it. Apply the **opposite** translation of the point's motion to the main video.
Do not move the video in the same direction as the feature.

## References and scope

- Inspect `assets/head-track-reference.mp4` for the intended look. Treat this rendered
  reference as a visual target, not recoverable AE project data.
- Match `assets/motion-blur-settings.png`: **180° shutter, 0° phase, 16 samples/frame,
  128 adaptive limit**. Do not substitute another preset's phase.
- Apply during the user's `[start,end)` composition-time interval. If only a start
  is supplied, continue to the end of that presenter shot. Never cross an edit,
  disappearance of the presenter or a different source; split shots and reseed.
- Interpret “main/first layer” as original presenter footage, even when text occupies
  higher timeline indices. Leave foreground text, shapes, photos, footage overlays,
  watermark and shadow ramp independent. Preserve layer order and audio timing.
- With a requested whole-scene camera zoom, stabilize the presenter locally **before**
  that shared transform. Do not add a zoom or activate other skills automatically.
- If liquid-glass subtitles sample the presenter, use the stabilized clean presenter
  as their live source mapped to composition coordinates. Keep subtitle position
  independent. Do not refract the completed scene containing the subtitle itself.

## Track the face

1. Inspect the first processed frame and later frames. Choose a visible high-contrast
   detail belonging to the same face: prefer a nostril; use a nose crease or another
   stable feature if necessary. Avoid hair, background, moving mouth and blinking
   eyelids. Identify the intended presenter before tracking if multiple faces appear.
2. Use one-point **position-only X/Y** stabilization. Do not stabilize scale/rotation,
   use a whole-scene Warp Stabilizer solution or deform the face.
3. Fit a tight feature region and a search region covering frame-to-frame movement.
   Prefer native resolution and subpixel positions; respect source/composition timing.
4. Review every frame, especially turns and occlusions. Stop and correct drift or
   low confidence. Re-anchor the **same physical point**, retaining the original lock
   position. Never invent/extrapolate a lost track or smooth across tracking failure.
5. Keep the point at its first-frame composition location. Center it only if requested.
   Add no easing, spring, rotation, cyclic zoom or visible tracking marker. Retain
   real inverse motion; fix erroneous jitter at the tracking stage.

## Stabilize and cover the frame

For an isolated, unrotated video covering a `W×H` frame, let `p(t)` be the source
point, `L=p(start)` its initial lock location and `s` constant overscan. Map pixels by:

```text
destination(x,t) = L + s × (x - p(t))
```

This keeps `destination(p(t),t)=L`. Overscan zooms around the locked point. Compose
with existing transforms or use a presenter-only working precomp; do not overwrite
existing animation. Do not scale the translation inconsistently with the video.

- Measure coverage over the complete path, including all subframe shutter samples.
  Prefer the smallest **constant** overscan plus a filtering margin. Do not blindly
  use 110% or animate a breathing crop.
- For this full-rectangle mapping, scale must cover the maximum of `Lx/px`,
  `(W-Lx)/(W-px)`, `Ly/py`, `(H-Ly)/(H-py)` over the path, with an edge margin.
  Do not use this formula unchanged for a center-anchored zoom or partial alpha.
- If the crop is intrusive (coded helper threshold: 118%), use reflected source
  extension: Motion Tile, **Mirror Edges on**, sufficient Output Width/Height, then
  stabilization. Compute extension from actual motion. Keep Tile Center at the
  intended source center. Check precomp clipping and effect order.
- Inspect all four edges: no black/transparent strip, obvious duplicated anatomy or
  prominent mirrored seam. Do not assume a fixed tile extent works for every shot.
- For transparent, rotated or cropped footage, calculate the actual opaque footprint.
- Gate the effect to the requested interval, with cuts at its boundaries by default.
  Add no animated return. Preserve original framing outside; do not let blur leak
  tracked motion into inactive frames.

## Native After Effects

Read `references/after-effects.md` when operating AE. Use **Tracker → Stabilize Motion**,
Position only, then Apply X and Y. Enable motion blur on the moving presenter layer
**and** the composition master switch. Set the exact screenshot values above.
Maintain sufficient source handles for the forward half-frame shutter.

Keep original effects, transforms, audio and timing intact. Ensure a presenter precomp
does not prematurely clip extension or prevent blur on the actually moving layer.
Native stabilization can animate Anchor Point; do not add inverse Position again.

## Coded fallback

Use `scripts/head_track.py` if AE is unavailable. Describe this as coded point
stabilization, not execution of AE's tracker or Motion Tile. Dependencies: NumPy,
SciPy, Pillow, ffmpeg and ffprobe. Use an opaque, upright, constant-frame-rate,
full-frame presenter-only source. Normalize a working copy with explicit time mapping
for unsupported footage; do not flatten foreground into the tracked source.

```bash
python scripts/head_track.py analyze \
  --input /task/presenter.mp4 --start 5 --end 9 \
  --seed 575 733 --track /task/head-track.json

python scripts/head_track.py render \
  --input /task/presenter.mp4 --track /task/head-track.json \
  --out /task/presenter-head-track.mp4
```

Replace example seed/times after inspecting the actual clip. Seed coordinates are
**original source pixels** at the first active frame (`ceil(start × fps)`), not frame
zero or thumbnail coordinates. Work width defaults to at most 720; increase
`--work-width` to native width for small details/difficult footage. Patch/search radii
are reference pixels at width 1080, scaled to work width.

The fixed-template NCC tracker stops below confidence 0.65. High NCC is evidence of a
patch match, not proof of the right face/detail. Visually inspect the entire path.
Correct with `--anchors /task/anchors.json`, a list such as
`[{"frame":174,"point":[583.4,728.2]}]`, using absolute source frame numbers and the
same physical feature. Fix the first lost frame and rerun; do not lower confidence
merely to pass. Use distinct track filenames; never consume a stale file after failure.

Render at native size by default; use `--width 540` for previews. `--edge auto` selects
measured crop up to 118%, otherwise reflection. Override with `--edge crop` or
`--edge mirror` after inspection; crop refuses insufficient allowed scale. Use distinct
input/output paths. The helper copies original audio, verifies frame count/fps and
full decoding, and writes a report beside the output.

Coded blur samples transforms over `t…t+0.5/fps`, 16–128 times, in linear RGB. It uses
the current decoded frame for subframe transforms, without optical-flow intermediate
footage or native AE internals. Beyond the last track sample it holds that position.
For editable scene integration, evaluate the presenter source at each sample time,
preserve source/composition mapping and render independent foreground afterward.

## Verify

- Make a **QA-only** tracked-point preview. Inspect every frame for the same physical
  feature. Remove the marker from final output.
- Verify inverse direction: the face point stays fixed while the background moves.
  Confidence alone cannot establish this.
- Inspect strongest motion, first/last active frames and all four edges at full
  resolution, including motion-blur extent. Fix borders, seams, excessive crop and
  lost headroom before delivery.
- Check interval, independent foreground, original outside framing, duration,
  frame rate/count, audio synchronization and full decodability.
- Report what ran. Skill creation alone does not mean the reference was reprocessed
  or a native AE project was generated.

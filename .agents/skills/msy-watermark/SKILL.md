---
name: msy-watermark
description: Add Arefeh Masoudi’s exact supplied transparent watermark PNG to every main presenter or talking-head shot at the size and lower-center placement measured from the supplied reference frame. Use for msy watermark, msy-watermark, واترمارک خانم مسعودی or واتر مارک مسعودی during video editing. Composite above the main video and above shadow-ramp when that skill is also used; exclude full-screen B-roll and motion-graphics-only scenes. Preserve the original artwork and alpha.
---

# MSY Watermark

Apply the supplied watermark to the requested video edit automatically on all eligible presenter intervals. Use the bundled placement rather than inventing a corner logo layout. Respond concisely in Persian.

## Exact assets

Resolve paths relative to this SKILL.md, not the working directory:

- `assets/msy-watermark.png`: original uploaded «واتر مارک خانم مسعودی.png», byte-for-byte unchanged; 2048 × 2048 RGBA; SHA-256 `5c4c880f7c6629b5e026dd4af398d2ea166a22fc8e71684943fdb246c6258a97`.
- `assets/placement-reference.jpg`: original supplied placement frame; 1080 × 1920; SHA-256 `1de342fcde648e0856e395866289cd3695c091e560e40e368d5464d97ce751f6`. Inspect this as a placement reference only; never composite the reference photograph into another video.

Use the original PNG, not OCR, retyped lettering, generated art, an SVG trace or a screenshot crop. Preserve all names, description and website artwork as embedded. Preserve source colors and alpha with normal source-over at 100% layer opacity; do not add filters, glow, shadows, color changes or entry/exit animation. Do not flatten transparent pixels into a black rectangle.

Do not trim transparent margins before applying full-image transform values. Original nonzero-alpha bounds are `(315, 764, 1739, 1290)` in source pixels, using exclusive right/bottom. Recover the exact asset if missing or corrupted instead of replacing it.

## Placement calibrated from the reference

At a final 1080 × 1920 canvas, use the following canonical transform on the complete 2048 × 2048 PNG:

| Parameter | Value |
|---|---|
| Rendered full image size | 472 × 472 px |
| Top-left of full image | `(304, 1341)` px |
| Source center anchor | `(1024, 1024)` px |
| Layer center position | `(540, 1577)` px |
| Uniform scale relative to source | `0.23046875`, or `23.046875%` |
| Rotation | `0°` |
| Layer opacity | `100%` |

The visible artwork is approximately within `x=377…705`, `y=1517…1638`; transparent padding explains why its position is different from the full square's top-left. Treat this as the measured pixel-rounded match to the JPEG reference, not recovered original editing keyframes. Do not move the watermark to the bottom edge, add a generic safe-area margin, or center its visible text independently of the original padding.

For another 9:16 canvas, multiply all composition coordinates and rendered dimensions by `W/1080 = H/1920`. For 2160 × 3840, use full image size `944 × 944`, top-left `(608, 2682)`, center `(1080, 3154)` and source scale `46.09375%`.

For a different final aspect ratio, preserve proportions: let `k=min(W/1080,H/1920)`, full image side `472*k`, center `(W/2, H*1577/1920)`, and top-left `center - side/2`. Use the helper below for pixel rounding. Keep this as a screen-space overlay after main-video rotation, crop and reframe; do not parent it to the subject, face tracking, camera, animated zoom or handheld motion. Preserve the source file; resize only at composition/render time.

Run `python scripts/placement.py --width 1080 --height 1920` to verify the asset hash and obtain engine-neutral geometry. Pass other final canvas dimensions as needed. Use its returned integer size/top-left consistently instead of independently rounding an anchor and offset.

## Eligible intervals

1. Inspect the existing edit and representative frames, or reuse already verified shot classifications. Include every shot where the main image is the on-camera presenter, including pauses and returns to the host. Do not depend on voice activity or caption visibility.
2. Exclude full-screen B-roll, stock footage, cutaways, product footage, screen recordings, slides, full-screen photos and motion-graphics-only scenes. A person in stock footage or presenter voiceover over B-roll is not sufficient. A small presenter inset over a different full-screen main scene does not make the whole scene eligible.
3. Keep the watermark while foreground captions, shapes or inset photos/footage appear over a main presenter shot. Disable/trim it when full-screen footage or graphics replace the presenter.
4. Reuse the same presenter interval map as `shadow-ramp` if both skills are active. Do not require or add shadow-ramp merely because this watermark skill is used.
5. Use frame-accurate half-open intervals `[in, out)`. At cuts, remove the watermark on the first excluded frame. At dissolves, transition the presenter plate and its watermark together; keep incoming/outgoing excluded footage free of the watermark. Do not separately fade or animate the logo beyond the edit's existing shot transition.

## Layer order and integration

Composite bottom to top:

1. Main presenter video with its existing treatment.
2. `Shadow Ramp`, only if invoked/present.
3. Exactly one `MSY Watermark` per presenter plate.
4. Remaining foreground content: captions, typography, shapes, footage overlays, objects and photos.

Treat the watermark as a foreground element under the shadow-ramp skill’s rule that all such elements sit above the ramp. Keep it above every applicable ramp instance; never bake it into the raw presenter footage before the ramp, put a ramp over it, or darken the completed flattened frame. If it is already correctly present, reuse it; do not stamp it twice. If a source already contains a burned-in watermark, inspect it before adding another and avoid duplicating it.

Use a bounded presenter group with video, optional ramp, then watermark; composite remaining foreground layers above it. Adapt numerical layer indices to the editor's stack direction. Keep other overlays clear of the watermark when laying out new content; do not move the fixed watermark to solve collisions. Preserve source audio, shot timing, grading and existing foreground animations.

Use the project's current renderer. In browser compositions use the original PNG image/texture with preserved alpha, explicit size/position and normal blending in the correct stacking context; drive visibility from timeline time. In FFmpeg apply the normalized presenter crop/reframe, then optional ramp, then watermark, then other foreground elements; loop the PNG as a still for the shot duration. In native editors import the same PNG and use the source anchor/scale table above. Do not apply this skill as a global overlay across excluded scenes.

When packaging an editable project, copy the original PNG unchanged into its assets and use a portable path. Keep the reference photograph and skill source assets unchanged.

## Verify before delivery

- Validate the original and project-copy hashes and PNG alpha.
- Compare native 1080 × 1920 placement against the reference, including full-image padding, actual visible size and lower-center alignment; avoid a duplicate overlay on the already-watermarked reference itself.
- Check a larger requested canvas using the proportional transform.
- Check a presenter frame both with and without shadow-ramp; the watermark must stay above it and retain its original appearance. Check captions/shapes remain above the watermark when they overlap.
- Inspect cuts, returns to presenter and transitions into excluded scenes. Confirm no watermark on excluded full-screen content and no duplicate stamps on eligible shots.
- Report only actual validation and renders. Creating this skill does not itself edit an existing video or install it into unrelated Codex environments.

Example: «با اسکیل‌های msy-watermark و shadow-ramp این ویدیو را ادیت کن.»

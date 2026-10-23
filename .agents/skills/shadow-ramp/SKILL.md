---
name: shadow-ramp
description: Add the user's exact transparent shadow PNG immediately above the main talking-head video and beneath all text, shapes, footage overlays, objects, photos and other foreground layers. Use when the user invokes shadow ramp, shadow-ramp, رمپ شدو or سایه رمپ during video editing, including alongside typography skills. Apply automatically to every eligible presenter shot; exclude B-roll, full-screen footage and motion-graphics-only shots. Preserve the bundled asset and its alpha exactly.
---

# Shadow Ramp

Improve foreground readability by darkening only the main presenter plate with the supplied shadow image. Treat this as a compositing operation within the requested edit, not a request for a standalone image.

## Required asset

- Resolve `assets/shadow-ramp.png` relative to this SKILL.md, never relative to the current working directory.
- Use this PNG exclusively. It is the byte-for-byte original uploaded as `shadow org.png`, renamed for portable paths.
- Preserve the original file: 1080 × 1920, RGBA, SHA-256 `493cc6783f7e0dc2e4309bcbb6c8174dfc161c0502e238fee8de7644c9b974a1`.
- Preserve straight PNG alpha. The upper area is fully transparent, including white RGB pixels with zero alpha; the lower area fades into black with partial alpha. Ignore invisible RGB values. Do not flatten onto white/black, infer opacity from luminance, remove alpha, or treat the PNG as an opaque black rectangle.
- Use normal source-over compositing at 100% layer opacity. The existing alpha supplies the intended fade and strength. Do not add blur, masks, brightness/contrast changes, recoloring, opacity reduction, blend modes, animation or a replacement procedural/CSS gradient.
- If the asset is missing or fails its hash check, recover the bundled original or ask for that exact original; never substitute or recreate it.

## Select shots automatically

1. Inspect the existing edit/timeline and representative source frames. Reuse declared shot types when available; otherwise identify intervals from visual evidence and editing context.
2. Include every interval whose main image is a presenter addressing the camera: talking heads, host explanations, interviews addressed to camera, and returns to the presenter. Include presenter shots even when no text appears yet.
3. Keep the ramp active through pauses, cuts and zooms within eligible presenter footage. Do not gate it on detected speech or text presence.
4. Exclude full-screen B-roll, stock footage, product/detail footage, cutaways, screen recordings, image-only scenes, slides, title cards and motion-graphics-only scenes. A person appearing in stock footage or narration over B-roll does not make it an eligible presenter shot. A small presenter inset over a full-screen screen recording does not make the whole scene eligible.
5. Keep partial foreground footage/photos/graphics above the ramp when the presenter remains the main plate. For an interval replaced by full-screen footage or motion graphics, disable/trim the ramp with the replaced presenter plate.
6. Resolve truly ambiguous intervals from nearby frames and the edit plan. Ask only if that ambiguity materially affects the result. Do not claim to have classified footage that was never inspected.

## Enforce the layer stack

Composite in this order, from bottom to top:

1. Main presenter video, including its existing crop, reframing and color treatment.
2. Exactly one `Shadow Ramp` instance using the bundled PNG.
3. Every other foreground layer: subtitles, typography, shapes, additional footage, objects, photos, illustrations, logos, stickers and effects belonging to those layers.

Build a presenter sub-composition/group as `main video → ramp`, then composite all foreground elements over that result. Never put the ramp over a flattened finished frame, over text/glow/shapes, or on a global adjustment layer. Keep added asset layers above it regardless of when they are created. Reuse an existing correct ramp instead of adding duplicates when this skill is invoked again.

In stacks where a lower numerical index means visually higher (such as After Effects), adapt indices to preserve this visual order. Do not assume that a larger index always means foreground.

Bind the ramp's in/out points to the eligible shot, with frame-accurate boundaries. For dissolves/transitions, transition the video-and-ramp group together; keep the incoming/outgoing B-roll or motion-graphics group free of the ramp. Do not leave a global ramp fading across unrelated scenes. Preserve source audio and all existing foreground animation.

## Geometry

- Work in final display/composition pixels after orientation metadata and any main-video crop/reframe are resolved.
- At 1080 × 1920: keep the image at native size, default centered placement, 100% scale, zero rotation and no offsets. In a centered-anchor editor, use anchor `(540, 960)` and position `(540, 960)`; in a top-left compositor, use `(0, 0)`.
- At another 9:16 resolution: scale uniformly to fill exactly and center. At 2160 × 3840, use 200% scale and center `(1080, 1920)`.
- If the final canvas has a different aspect ratio, preserve proportions and use centered cover: `s = max(W / 1080, H / 1920)`, render size `(1080*s, 1920*s)`, top-left `((W-1080*s)/2, (H-1920*s)/2)`. Clip overflow to the frame. Do not stretch, rotate or redesign the gradient.
- Treat the ramp as screen-space, filling the finished presenter frame. Do not parent it to tracking, camera movement or animated zoom/reframe on the raw presenter video.
- Keep the original file unchanged; perform any required resampling only at render/composition time.

## Implementation

Use the current editing engine rather than introducing another renderer. Load the original PNG as a still with its alpha and duration covering the eligible shot. For a code compositor, use premultiplied or straight alpha consistently with the engine to avoid halos. Preserve alpha until the ramp is composited over the presenter.

For browser/HTML renderers, use a real image element/texture referencing the copied PNG with normal blending, `opacity: 1`, and `pointer-events: none`. Place the presenter and ramp in a bounded stacking context, with every foreground element in a higher context. Scope visibility to presenter intervals using deterministic timeline time, not wall-clock timers. Do not implement the ramp as a CSS gradient or a filter on the completed scene.

For FFmpeg, loop the PNG as a still, preserve alpha during scaling, overlay it on the normalized presenter stream first, then draw/composite text and foreground assets. Gate it with shot-local half-open intervals `[in, out)` or apply it within each presenter clip before concatenation. Do not overlay it after subtitles/graphics have already been burned in.

When packaging a project, copy the exact PNG into that project's assets and reference the portable copied path. Keep the skill asset unchanged. This skill may accompany `mask-path-typography` or `avangard-kinetic-type`; render all typography, shadows, glows and textures entirely above the ramp.

## Verify before delivery

- Confirm the bundled and copied source hashes match; confirm PNG alpha survives loading.
- Inspect a representative presenter frame: upper transparent pixels leave the video unchanged; the lower portion darkens according to the PNG's existing alpha.
- Inspect foreground text and a shape/photo over the darkest area: their color and opacity remain unchanged by the ramp.
- Inspect B-roll and motion-graphics intervals plus both sides of cuts/transitions: no ramp is composited onto excluded content.
- Check native 1080 × 1920 geometry and any requested larger resolution; confirm full-frame coverage without distortion or unexpected offsets.
- Invoke again or inspect the final stack to confirm only one ramp per presenter plate. Preserve timing, audio and all existing edit behavior.
- Report only the application and checks actually performed. Creating this skill does not itself apply it to an existing video or install it into unrelated Codex environments.

Example invocation: «با اسکیل shadow-ramp این ویدیو را ادیت کن و تایپوگرافی را بالای رمپ قرار بده.»

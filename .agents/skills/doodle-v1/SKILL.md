---
name: doodle-v1
description: "Add sparse thin doodle lines and simple shapes as ONE-frame flashes: drawing, completely blank rest frame, then a different drawing anchored to another meaningful visible element or edge. Use for doodle v1, doodle-v1, خط دودل or hand-drawn accent flashes. Latest user correction requires very light hand roughness, exactly one frame per drawing, one full rest frame between drawings, hard cuts to different shapes placed purposefully around actual objects, presenter, text or shapes. Preserve source video/audio/timing; use the bundled renderer and original line-only reference."
---

# Doodle V1

## Required behavior — latest user correction

The cadence is **drawing / EMPTY / different drawing ELSEWHERE / EMPTY / another drawing ELSEWHERE**. Each drawing, line and shape exists for exactly ONE output frame. The following frame contains NO doodle overlay. After that rest, a differently shaped drawing appears at another meaningful target or target edge in the current image. At 30fps this yields 15 one-frame flashes per second within the requested interval, with 15 blank rest frames. Use actual source FPS without retiming it.

This replaces all previous interpretations: continuously visible face outlines, mild jitter of the same contour, redraw on EVERY consecutive frame, heavy hand roughness, smooth travel and fade-ins/outs. Do not preserve earlier rejected behavior. Roughness must now be very light; the main effect is discrete appearance/disappearance and changes of location and shape.

## Inspect and author

1. Probe source dimensions, FPS, duration and audio. Resolve the requested effect interval. If no interval is given, use a short 0.6–1.2 second accent bounded by the source and state it.
2. Inspect the complete original `assets/references/reference.mp4` and [line observations](references/line-analysis.md). It is 1080×1920, 30fps, 24 frames; active picture approximately y552..1367. Use `scripts/inspect_reference.py` for frame extraction. Learn only narrow doodle line language, never reference text, portrait, red scene, blocks or transitions. The user's explicit latest timing clarification takes precedence over inferred source timing.
3. Inspect the target footage throughout the interval and identify actual visible anchors: presenter head/shoulder silhouette, physical objects, displayed text, UI cards or graphic shapes. Author at least three sparse drawing groups, each associated with a named target and tight inspected target bounds. Place its marks on or just beside a meaningful edge, arc, corner or margin of that target. For text, use a short underline, bracket or side accent with glyph clearance. For objects/shapes, echo a selected outline fragment or corner. For the presenter, accent crown/shoulder/outer silhouette without covering facial details. Empty background is not an anchor; do not scatter unrelated shapes across it by default. Do not invent text or shapes that are absent.
4. Arrange successive flashes to change shape and meaningful anchor: e.g. presenter crown → microphone edge → product corner → presenter shoulder → existing title margin. Different edges of one object are allowed when few targets exist. Do not force a far corner jump if no relevant element is there. Use approximate visual association, not an always-visible full outline. Bound local variation so the mark stays associated with its selected target. Inspect moving targets at their actual flash frames; reauthor/supply verified movement data as needed.
5. Use narrow warm off-white strokes, approximately 2.4px at1080px width. Default local roughness is only 0.65px plus0.12px fine irregularity. Adjust to final resolution. No thick cartoon stroke, neon glow, shadow, scene noise or grading changes. Region changes and local roughness are separate controls.
6. Execute the bundled renderer with the scene format below. The gate applies to the ENTIRE overlay: one visible frame followed by one completely transparent frame. Hard appearance/removal only; no draw-on, morph, fade, crossfade, carryover, continuous path travel or motion blur bleeding into blank frames. Keep one drawing fixed within its own shutter exposure. Fresh seed/frame variation changes reused templates without creating persistent lines.
7. Preserve source duration, FPS, framing and audio. Do not invoke other editing skills automatically. Explicit paths are required; the tool has no segmentation, tracking, transcription or automatic style transfer.
8. Verify EVERY active/rest pair in overlay alpha, not just a contact sheet. Confirm each drawing is visible for only one frame; the next is empty; the next visible drawing changes shape AND region. Review in motion and compare adjacent frames. Check very light roughness, sparse placement, obvious relation to a real target, subject clearance and untouched source timing/audio. A target label alone does not prove correct placement: inspect the rendered mark against the real frame.

## Execute

Read [scene format](references/scene-format.md). A complete schema illustration is in `references/demo-scene.json`.

```bash
python scripts/doodle.py /absolute/path/scene.json --output /absolute/path/final.mp4
```

Requirements: Pillow, numpy, scipy, FFmpeg/ffprobe. Output is a composited MP4, not transparent. The current implementation is demonstrated in `assets/studies/presenter-redraw-preview.mp4`; it awaits user approval and does not replace the original reference. `assets/reference-guides.json` contains approximate manually digitized source line guides, not recovered vectors, tracker data or AE settings.

## Placement priority

Latest user approval keeps the one-frame flash / one-frame rest cadence and very light roughness. Placement must now be purposeful: marks belong approximately to actual scene objects, the presenter, existing text or shapes. This supersedes the previous random empty-screen region test. The renderer validates supplied target metadata and path proximity; it does not detect targets or verify labels automatically.

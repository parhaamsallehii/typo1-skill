---
name: mask-path-typography
description: "Create Persian mask path typography: connected Bahman/Lifta text travelling along a smooth curved mask path via First Margin, with fast four-frame entry/exit, opacity fades, strong velocity-driven spring overshoot, animated hand-drawn contours, strong halftone/noise, mandatory After Effects-style temporal motion blur, crimson/cream hard-shadow styles and diffuse glow. Use for mask path typography, path mask typography, تایپوگرافی روی مسیر، فرست مارجین، متن روی منحنی and springy curved titles. Not a wipe/reveal-mask effect or automatic speech transcription."
---

# Mask Path Typography

Produce actual typography artifacts when requested. Use the current user's exact text, timing, dimensions and intended output. Respond concisely in Persian. Keep this identity separate from `avangard-kinetic-type`; do not inherit its colors, fonts or right-only entrances.

## Read and inspect

1. Read [style and motion](references/style-motion.md) before composition.
2. Inspect [motion blur settings](references/media/motion-blur.png), [palette](references/media/palette.jpg), and [texture](references/media/texture.png) before the first composition or a substantial style change.
3. Run `python scripts/prepare_reference.py` to restore the byte-identical original video from the bundled parts (no network required). Then inspect frames from [the original animation](references/media/animation.mp4), especially 0.0–0.5 s and 0.6–1.1 s; use [reference observations](references/reference-analysis.md). This is the user's actual 1080×1920, 30 fps sample. Do not infer exact AE path coordinates or keyframe graphs from a baked video.
4. Use [render workflow](references/render-workflow.md) and [scene schema](references/scene-schema.md) for output. For native After Effects, read [native settings](references/native-after-effects.md).
5. Use [style defaults](assets/style.json), [editable scene](assets/example-scene.json), and [source manifest](references/source-manifest.json). Resolve relative paths from this folder. The manifest records the duplicate video upload; one byte-identical original is stored.

## Required identity

- Enable motion blur for the composition AND every eligible layer/text/precomposition. Use **Shutter Angle 180°, Phase 0°, Samples Per Frame 16, Adaptive Sample Limit 128**. Do not disable it for speed or replace it with Gaussian blur, echo trails or directional blur on a settled still.
- In code, sample deterministic subframe positions including curve orientation and spring. Phase 0 uses `[t, t + 0.5/fps]`, not a centered shutter. Average premultiplied values in linear light. An exactly stationary layer may reuse identical samples; its blur flag stays enabled.
- Use only the four bundled fonts: `Bahman.ttf`, `E-Bahman.ttf`, `Lifta-Black.otf`, `Lifta-Bold.otf`, under `assets/fonts/`. Choose appropriate roles; do not force all four into a short phrase. Never silently substitute fonts or use generated lettering.
- Preserve Persian shaping, marks, half-spaces and logical reading order. Never reverse Unicode, split a joined word into independently moving letters, or put tracking between joined Persian letters. Shape complete words/phrases before following the curve.
- Use **red #B40023 and cream #FCF0D6**, from printed reference labels. Do not reuse the earlier skill's palette, the sample video's green or the texture image's blue.
- Apply prominent fixed noise plus halftone inside every text fill, anchored in text coordinates. Default 4 reference-pixel pitch, 1.05-pixel dot radius and 1.25 texture strength. Preserve thin strokes and dots. No per-frame texture flicker or added paper background.
- Apply noticeably animated hand-drawn contour variation to every text layer: 3.2 reference pixels at 8 Hz by default, deterministic and continuous. Keep glyphs and joined Persian letters recognizable. Include this motion in shutter sampling, even while First Margin holds still.
- Style 1: cream fill, red Drop Shadow. Style 2: red fill, cream Drop Shadow. Both: **Distance 3, Opacity 100%, Softness 0**. Default direction is straight down based on the sample; the user did not specify a numeric shadow angle. Scale geometric defaults from reference width 1080.
- Both styles: native **Deep Glow Radius 1000, Exposure 0.3, Screen**. Preserve these native values. The bundled renderer approximates the diffuse appearance; never claim it executes the proprietary plugin or matches it pixel for pixel.

## Motion contract

- Attach the text baseline to a very smooth open curve. Default to a shallow arch; permit smooth alternatives. Never introduce corners, cusps or abrupt tangent changes.
- Move First Margin in signed **arc-length pixels**, rather than translating a flat card. Text follows the curve and local tangent. Keep the guide path invisible; a mask used as a text path is not automatically a clipping mask.
- Support entry from either side, independently of RTL reading order. Keep a phrase on one path as a group unless separate word entrances are requested; whole words/lines may have independent start times.
- Enter from ordinal frame 1 to frame 5: four frame intervals (4/30 s at 30 fps). Set opacity 0% on frame 1 and 100% on frame 5. For requested exit, reverse the First Margin travel in four frame intervals and animate opacity 100%→0%. Keep entry/exit timing adjustable for another frame rate or explicit user instruction.
- Add the velocity-driven spring to First Margin after arrival, using actual signed incoming velocity from the base motion. Stronger defaults: amp 0.16, freq 2.5 Hz, decay 5.5/s, max amplitude 300 reference pixels, duration 1 s, final smooth fade 0.2 s. Use [Python](scripts/spring.py), [JavaScript](scripts/spring.mjs), or [native expression](scripts/first-margin-expression.jsx).
- Do not clamp First Margin to 0–1 or path endpoints; extend the path for arrivals and overshoot. Do not add elastic easing to the same property. Preserve incoming velocity; a full ease-out ending at zero suppresses the spring.
- Evaluate from absolute timeline time. No accumulated frame state, wall clock or nondeterministic seeds. Spring preserves position continuity, not necessarily velocity continuity; inspect arrival.
- Interpolate opacity linearly for entry and exit independently of the spring. The bounced text remains visible at 100% during the hold; the exit begins only after entry spring settles. Keep whole words/phrases connected; do not impose a word-by-word fade unless requested.

## Execute and verify

1. Resolve text, output and timing from the request. Default to 1080×1920, 30 fps only when unspecified. Existing footage keeps dimensions, audio and edit unless requested otherwise.
2. Run `python scripts/render_path_type.py --check`. Verify font coverage, RAQM and FFmpeg. Do not work around missing shaping with disconnected letters.
3. Copy `assets/example-scene.json` to a task folder and edit the copy. Choose fonts deliberately. Use the scene schema; do not modify canonical assets for one-off renders.
4. Render a settled PNG, an entrance PNG and an MP4 with the workflow commands. The bundled renderer exports opaque PNG/MP4; for alpha, adapt and validate an alpha-capable pipeline. Do not claim MP4 transparency.
5. Inspect entrance, arrival, overshoot, settling, hold and exit. Fix baseline jumps, lost dots, split joins, collisions, cropped final text, wrong reading order or ghost trails. Ensure the animated hand-drawn contour remains coherent during a path hold. Compare with the sample.
6. Verify actual duration, fps, dimensions, full decode and artifact delivery. Preserve an editable scene when useful. Report unsupported native effects honestly; never call unrendered code a finished video.
7. Save through the environment's supported artifact channel. Do not assume a local `shared` path is downloadable. A separate GitHub installation requires the whole folder at `.agents/skills/mask-path-typography/` and a successful commit/push there.

Use speech recognition and word alignment only when available and needed; never call synthetic stagger timing detected speech. Retain the supplied assets; do not publish them to a public repository without user instruction.

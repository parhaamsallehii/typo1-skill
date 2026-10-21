---
name: avangard-kinetic-type
description: "Create Persian Avangard kinetic typography, animated titles, and styled word-by-word overlays with bundled AmirFoda/Rubbama fonts, burgundy/red/beige palette, noise and halftone, faint diffuse glow, hard downward shadow, hand-drawn edge animation, and right-to-left entrances. Use for تایپوگرافی آوانگارد، متن متحرک، انیمیشن کلمه‌به‌کلمه and styling timed captions. Do not use as a general video editor or claim transcription without available speech/alignment tools."
---

# Avangard kinetic typography

Create actual typography artifacts when requested. Preserve current user text, timing, composition, and output requirements. Explicit user instructions override defaults. Respond concisely in Persian.

## Resources

1. Read [style and motion](references/style-motion.md) before designing.
2. View these images before a first composition or substantial layout change:
   - [Palette](references/media/palette.jpg): use printed hex labels, not JPEG pixels.
   - [Block composition](references/media/layout-block.jpg): dense angular stack.
   - [Expressive composition](references/media/layout-expressive.jpg): asymmetric calligraphic layout.
3. Read [render workflow](references/render-workflow.md) when making PNG/MOV/MP4 or integrating into video.
4. Read [scene schema](references/scene-schema.md) when editing text, timing, or layout.
5. Use `assets/style.json` for defaults. See [asset manifest](references/source-manifest.json) for original filenames/checksums.

Resolve relative paths from this skill directory. All five supplied files are bundled unmodified; do not depend on original uploads. No reference video was supplied: animation comes from the user's written brief.

## Required identity

- Pair KO Rubbama Black (`assets/fonts/Rubbama-Black.otf`) for compact geometric words with AmirFoda Bold (`assets/fonts/AmirFoda-Bold.ttf`) for expressive emphasis. Use deliberate word/line roles and both fonts for multiword titles unless instructed otherwise. Never mix fonts inside a connected Persian word or blend/stretch outlines.
- Use palette `#3B0016`, `#F82524`, `#D1C0A6`. Existing footage keeps its colors. Do not import the layout posters' blue, white, black, English side labels, logos, or hanging lines.
- Preserve shaping, dots, diacritics, half-spaces, punctuation, and reading order. Keep words shaped as units. Never reverse Unicode or add letter spacing between joined Persian letters.
- Build compact typographic mass with varied scale, staggered edges, and controlled asymmetry. Follow spatial principles rather than copying reference words or claiming the fonts exactly reproduce hand lettering.
- Clip combined fine noise and halftone to glyphs. Lock textures in word coordinates; avoid random per-frame flicker.
- Preserve native Deep Glow Exposure **0.02** when that plugin is available: extremely faint and diffuse. Bundled code is a documented visual approximation, not the native plugin.
- Preserve Drop Shadow **Distance 5, requested Angle 180°, Opacity 100%, Softness 0**. Semantic direction is straight down: `dx=0, dy=+5` at reference width 1080. Map angles to the target engine; never rotate the shadow sideways because conventions differ.
- Add subtle hand-drawn contour boiling while keeping final layout, baseline, glyph identity, and readability stable.

## Motion

- Lay out the complete final phrase first. Reveal into frozen positions; never reflow when another word appears.
- Reveal word by word in logical Persian reading order. A half-space does not split a word.
- Start each word to the right of its own final position, alpha 0; finish at the exact target with alpha 1.
- Use fast initial movement and an extremely slow smooth finish, zero final velocity, no bounce/overshoot. Record the user's “0 / 100 graph” as easing intent, not a universal native parameter. Fallback easing: `1-(1-t)**5`.
- Adjustable unspecified defaults: entrance 0.55 s, stagger 0.12 s, right offset 72 reference pixels; edge boil 0.65 reference pixels at 8 Hz. Scale geometry by output width / 1080; do not scale seconds or opacity.
- Honor supplied word times. If audio-synchronized captions are requested, obtain actual transcription and alignment with available tools; never pass synthetic stagger timing off as speech detection.
- Clarify source versus output timeline only when ambiguous. Preserve underlying video edit/audio unless asked to change it.

## Execute

1. Infer or obtain exact text and intended deliverable. Default to 1080×1920, 30 fps only when unspecified; existing video's dimensions/frame rate take precedence.
2. Run `python scripts/render_type.py --check`. Verify fonts, glyph coverage, RAQM, and FFmpeg as needed. Never silently substitute fonts or produce broken Arabic.
3. Copy `assets/example-scene.json` to task output and edit it. Use `lines` for designed line breaks or `words` for explicit placement. Preserve supplied text verbatim unless copy-editing is requested.
4. Render a settled PNG and animation with the bundled script or implement the same spec in the user's existing renderer/editor. Use the supplied fonts, not generated lettering.
5. Inspect settled layout and entrance frames. Fix collisions, clipping, missing dots, wrong colors, and timing. Check actual output before delivery.
6. Deliver requested artifacts and an editable scene when useful. Distinguish native plugin application from a recreation. Report actual execution blockers; never call unexecuted code a completed video.

## Quality gates

- Both fonts load; glyph coverage is checked. No silent fallback.
- Palette matches configured hex codes; compositing/antialiasing naturally produce intermediate pixels.
- Final layout is static; each entrance moves left from a rightward offset, alpha 0→1, smoothly and without overshoot.
- Shadow core is opaque, sharp, and downward; antialiasing is permitted but blur is zero. Glow remains separate.
- Noise/halftone preserve dots, counters, and strokes; edge boil never reads as a camera shake.
- Output dimensions, duration, frame rate, and alpha match the request. MP4 is not transparent: use alpha-capable MOV or RGBA PNG for overlays.
- A video opens and displays the full text. Speech synchronization is checked against actual audio when requested; a standalone title preview does not establish ASR accuracy.

## Separate Codex Cloud repositories

When asked to install in another repository, copy this entire directory including fonts/references into `.agents/skills/avangard-kinetic-type/` there and commit through its authorized workflow. A save in ChatGPT Skills does not automatically install it into an unrelated GitHub repository. Do not publish the user's bundled font/reference assets publicly without their instruction.

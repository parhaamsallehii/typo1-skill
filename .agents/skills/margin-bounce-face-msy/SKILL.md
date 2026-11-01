---
name: margin-bounce-face-msy
description: "Create MSY minimal Persian face-side curved typography from the supplied reference: two successive speech-matched phrases on open bowed paths beside the presenter's head, using bundled Saadi/Lifta fonts, flat crimson/cream fills, exact velocity-driven First Margin bounce, 2-frame margin entrances/exits, 4-frame fade-in, 3-frame fade-out and 180-degree phase-zero 16–128-sample motion blur. Use for margin bounce face msy, مارجین بانس دور صورت, مارجین بانس دور سر or two curved captions beside a face. Keep the face clear, verify actual spoken words, preserve source/audio timing, and do not inherit glow, shadow or texture from other typography skills."
---

# Margin Bounce Face MSY

Build this specific face-side look, not a generic subtitle or another typography skill. Preserve the uploaded source video, screenshots, fonts and exact expression. Normalize the requested name to `margin-bounce-face-msy`; use **Margin Bounce Face MSY** in the UI.

## Required reference inspection

Before authoring, read [reference analysis](references/reference-analysis.md) and [motion specification](references/motion-spec.md). Inspect all 36 frames of `assets/references/reference.mp4` (1080×1920, 30fps, 1.2s), especially frames 0–12 and 17–25; inspect `placement.jpg`, `palette.jpg` and `motion-blur.png` in that directory. Use `scripts/inspect_reference.py --out <scratch-dir>` to extract all frames and contact sheets. Do not claim the video was inspected by merely viewing its poster. For exact original names and SHA256 hashes consult `assets/references/manifest.json`.

## Execute in this order

1. Locate the real presenter video, requested start time and intended interval. Probe its dimensions, frame rate, duration and audio. Preserve presentation timestamps, source duration and audio. Do not apply the reference's red room, lighting, camera framing or footage to a different source.
2. Obtain actual timed speech from a verified transcript, a real transcription tool or direct audio review available in the environment. A user-supplied script is a correction aid, not proof of performed words/timing. Select two short consecutive natural phrases at/after the requested time. Do not guess the words from lip movements, image frames, subject matter or equal duration word allocation. If unavailable, complete independent layout preparation, then request timed text or working transcription access. Never fabricate alignment or silently switch speech providers.
3. Inspect head/hair/scarf/glasses bounds at start, middle and end. Author two open, smooth cubic Bezier paths outside the head contour, with visible negative space. Use one in the image-left corridor and one in the image-right corridor; align both to the head's axis, with the asymmetry of the reference. These are mostly vertical bowed side paths, NOT a horizontal title arch, exact semicircle, halo, circular orbit or cheek overlay. Let the eye travel from temple level toward jaw/upper shoulder. Leave eyes, mouth, cheeks and hair unobstructed. Keep the paths themselves invisible.
4. Shape Persian correctly before placing text on the path. Use bundled fonts only; start with Saadi Ultra for the reference-like weight and test actual text in the other supplied weights. Shorten phrase division before reducing text size excessively. Preserve joined letters, RTL order and punctuation. Do not split unshaped Unicode letters into individually rotated disconnected glyphs. Rotate the baseline/glyph tangent along the curve; never rotate the entire horizontal text block as a substitute for a path.
5. Use solid `#FCF0D6` cream and `#B40023` crimson fills, typically cream on image-left and crimson on image-right. Swap sides only for contrast while keeping both phrases clear. No stroke, shadow, drop shadow, glow, gradient, grain, halftone, hand-drawn contour, capsule or background box. Do not import the effects or 4-frame margin entrance of `mask-path-typography`.
6. At the exact user cue S, start phrase one at opacity 0 and First Margin +35 or −35 path units. Arrive at target First Margin 0 at S+2 frame intervals. Fade opacity to 100 at S+4 frames. Use the exact spring in `scripts/first-margin-expression.jsx`; read [motion specification](references/motion-spec.md) for frame semantics and the velocity requirement.
7. Start phrase two on its actual following speech cue; do not force both to appear at S and do not invent a fixed speech stagger. Both may coexist. Default each phrase to a one-second visible hold counted from its full-opacity frame. At E, key Margin 0 and opacity 100; key Margin ±35 at E+2 frames and opacity 0 at E+3 frames. Keep the margin expression active on entry and exit. Preserve speech timing if an explicitly requested interval needs a different hold; report the adjustment.
8. Enable comp motion blur and each moving text/parent/precomp layer switch. Set shutter angle 180°, phase 0°, samples/frame 16 and adaptive limit 128 exactly as the screenshot. Use true subframe accumulation for coded motion. Do not replace temporal blur with Gaussian/CSS blur or change the shutter angle to exaggerate it. Existing recorded footage needs no invented transform; preserve its original recorded blur. If a camera/parent transform is introduced, sample its movement too.
9. Preview entrance, first overshoot, settling, the two-phrase coexistence and exit at frame resolution. Check the face remains clear and text stays inside the frame during the bounce, not only at rest. Verify the transcript against audio, inspect joins/RTL, and listen to the exported video's beginning/end for audio/timing changes. Deliver the real rendered artifact, with any approximation disclosed.

## Choose execution backend

**Native After Effects:** create two separate text layers, each with an open curved mask and Text > Path Options set to that mask. Set First Margin keys relative to the composed resting alignment. Apply the bundled expression to First Margin, not scale/position. Set baseline orientation/reverse path by visual inspection; never mirror glyphs. If the presenter moves materially, track head translation/rotation/scale onto a shared null, parent the path/text rig and inspect clearance; do not stabilize or move the original presenter footage. The visible path is a text guide, not a reveal matte. Follow the frame table and motion blur settings.

**Coded fallback:** use `scripts/render.py`; do not rewrite the core spring or text shaping. It accepts an authored scene JSON, still or video source, exactly two phrases, cubic paths, bundled font keys, timings, and signed margins. It preserves audio for video sources. Its shaped-ribbon warp is an approximation of AE's glyph layout, not an actual AE render. It has no automatic face detection, head tracker or speech recognizer: supply inspected paths and verified speech. For appreciable head/camera motion use native tracking or extend/test the renderer with subframe head transforms before production; a fixed path is only suitable when the head remains safely in its corridor. Never claim it tracks a moving head.

Run:

```bash
python scripts/render.py /absolute/path/scene.json --output /absolute/path/output.mp4
```

Use Python with Pillow RAQM, numpy, scipy and fonttools; FFmpeg/ffprobe must be available. Install only missing dependencies from `scripts/requirements.txt` if permitted. Read [scene format](references/scene-format.md). Render first at the actual delivery resolution; any low-resolution preview must be labeled.

## Verification and honesty

- Keep structural validation separate from visual/style approval. Do not claim pixel-exact reconstruction of AE keyframes from flattened video.
- Preserve exact user settings as authoritative; label fitted geometry and inferred frame observations as estimates.
- Use `demo: true` only for explicitly labeled silent illustrative previews with authored words. It does not establish speech alignment or constitute an approved production result.
- Test a new input and different two-phrase wording before calling this reusable. Keep the reference media and fonts in this skill; a link to an old chat is not a replacement.

## Bundled illustrative preview

Inspect `assets/studies/illustrative-preview.mp4` for the renderer’s first implementation. Reproduce with `references/demo-scene.json`. It is a five-second 1080×1920 silent demonstration on an extracted still with authored words «ساده» and «روان», not a transcription of the speaker, not an approved benchmark and not proof of live head tracking. Source reference footage remains authoritative.

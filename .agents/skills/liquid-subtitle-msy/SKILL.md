---
name: liquid-subtitle-msy
description: Create Arefeh Masoudi’s Persian subtitles as discrete four- or five-word white Traditional Arabic captions over a live-source liquid-glass capsule. Use for liquid subtitle msy, liquid-subtitle-msy, زیرنویس لیکویید خانم مسعودی or زیرنویس شیشه‌ای مسعودی. Match the supplied references, use the bundled fonts and Windows LiquidGlass effect when native After Effects is available, otherwise identify the bundled coded renderer as an approximation. Start capsule width changes eight frames before each text cut, arriving at the cut with the user's velocity-driven bounce. Keep outer interval boundaries and text changes as hard cuts.
---

# Liquid Subtitle MSY

Build actual editable subtitles using two logical components: a live refractive glass capsule underneath and a separate shaped Persian text layer above it. Preserve audio and the edit. Respond concisely in Persian.

## Read the references and choose the execution route

Resolve all paths relative to this SKILL.md. Inspect `assets/references/style.png`, `placement.jpg` and `motion-preview.mp4` before rendering. The PNG contains a white surrounding plate and shadows; it is a visual reference, never a reusable overlay or static glass texture. The 540×960 motion preview preserves the supplied video's timing; original footage was 1080×1920 at 30 fps. Hashes/provenance are in `assets/manifest.json`.

Use the exact bundled `assets/fonts/TRADO.TTF` (Traditional Arabic Regular) as the reference default. Keep `TRADBDO.TTF` (Bold) available only for a requested variant. Preserve Persian shaping, punctuation, ZWNJ, RTL reading order and joined letters. Never reverse Unicode or place characters individually.

- **Native route:** With compatible Windows After Effects, use the supplied `assets/native/LiquidGlass.aex` and follow [native-after-effects.md](references/native-after-effects.md). Bind the effect's Source Layer to the main presenter video. Native Deep Glow 2 must also be available separately. Verify actual execution before claiming native fidelity.
- **Coded route:** If native effects cannot run, use/adapt `scripts/render.py`. It samples the current underlying video, refracts it through a capsule, adds edge highlights, shadows and separately shaped text. This is a visual approximation, not execution/emulation of the .aex or a pixel-exact Deep Glow 2 result. Say so. Do not claim the original numeric glass controls were recovered from screenshots.

## Scope, text and timing

1. Apply the style only within user-specified intervals; keep their exact boundaries. If unspecified, use the relevant presenter speech intervals in the edit plan. Do not silently import the scene exclusions of unrelated watermark/ramp skills into explicitly requested subtitle intervals.
2. Obtain a real transcript and cue timing from supplied text, existing subtitles or an actual speech/alignment tool. Do not invent captions, speech recognition or word timing. If no working transcription route exists, request the missing transcript/timing while completing independent styling work.
3. Group into readable phrases of four or five words, maximum five per cue. Keep one- or two-word leftovers at the end; also permit a short natural phrase when needed to preserve syntax/legibility. ZWNJ within a word does not split it. Never discard, summarize, add or duplicate spoken words to hit a word count.
4. Shape/measure the complete next phrase before assigning its pill width. If a five-word phrase is too wide, regroup without squeezing glyphs; preserve reading order and spoken timing. Do not add a second text line by default.
5. Keep text/source changes as hard cuts. No fades, typewriter, word highlights, slide-in, bounce, scale or entrance/exit on the text. Weak contour effects are allowed below; they do not animate text position/scale/opacity.
6. At the start of each continuous requested block, cut on the pill already at its initial width with its first text. At its end cut both off immediately, without a closing width animation. Do not borrow animation time before/after the requested block or across a gap/scene cut.

## Geometry and glass

Use final display pixels after the main video's orientation, crop, reframe and time remapping. At 1080×1920:

| Property | Reference-based default |
|---|---|
| Fixed capsule/text center | `(540,1356)` |
| Capsule height | `82 px` |
| Text font size | `78 px`, Traditional Arabic Regular |
| Capsule width | `max(130, shaped_text_width + 52)` |
| Example width for «فریلنسر برای کسب و کار» | approximately `569 px` |
| Capsule corner radius | `min(width,height)/2` |
| Maximum resting width | `90%` of canvas width; regroup text if exceeded |

Treat these as calibrated starting values, not original AE project metadata. Keep width adaptive, height and center constant. Change rectangle path size, not horizontal scale; maintain round caps throughout the bounce. At other 9:16 resolutions scale geometric/text/shadow values by `W/1080`; at 2160×3840 this gives center `(1080,2712)`, height `164`, font `156`, padding `104`. For other aspect ratios use uniform `min(W/1080,H/1920)` geometry scaling and normalized center `(W/2,H*1356/1920)`; adapt/test the fallback renderer, which defaults to 9:16 width scaling, before claiming a match.

Make the glass show the **current original main presenter video** at the pill's composition location, including correct source time/crop/reframe. Bind Source Layer/mask/parent coordinates consistently; keep the capsule in fixed screen space. While it moves or resizes, resample that live source. Do not freeze its interior, stretch a captured screenshot, fake it with an opaque tint, or sample the completed composite containing its own text, ramp, watermark or other graphics. Avoid recursive feedback and duplicate transforms. Match the reference's dark clear body, gentle lens/refraction and bright upper-left rim with a weaker lower edge. Add a very soft dark shadow beneath the shape. Coded shape-shadow defaults: opacity about `.39`, offset `12 px` down, blur sigma `18 px`; these are approximation settings, not native effect values.

## Text appearance

Use `#FFFFFF` fill and a black `1 px` stroke. Center ink bounds, preserving ascenders, dots and descenders. Apply effects in the requested order:

1. Black Drop Shadow: opacity `100%`, distance `3.5`, softness `0`, down-right.
2. Black Drop Shadow: opacity `100%`, distance `5`, softness `14`, same direction.
3. Deep Glow 2: radius `1000`, exposure `0.01`.
4. Weak hand-drawn contour variation.
5. Fine-scale Turbulent Displace.

For down-right, use Cartesian offset `(distance/√2,distance/√2)`; check an editor's angle convention rather than assuming a number. Keep the last two effects weak and deterministic, approximately `.3–.5` reference-pixel displacement at fine `7–12 px` scale as a coded starting point. Do not apply typography skills' strong halftone, grain, large contour deformation, palette or elastic text entrances. The provided renderer approximates the stroke, shadows, faint glow and contour effects; native softness/radius units are not interchangeable with Gaussian sigma.

## Eight-frame anticipation and bounce

For each next-caption cut time `T`:

1. Keep the old text visible until the frame before `T`; show the new text exactly at `T` using half-open cue intervals `[start,end)`.
2. Place the first pill-width key at `T−8/fps` and the second exactly at `T`. At 30 fps this is eight intervals (`0.2666667 s`), not eight ordinal frames including both ends. Move from the old **evaluated** width to the next phrase's width during this span.
3. At `T`, start the supplied bounce on **width only**, using actual signed incoming width velocity. Faster expansion/shrinkage gives stronger bounce with the appropriate sign. Keep height, center, text and its opacity fixed.
4. Use `scripts/motion.py` as the engine-neutral reference: `W = target + v*.1*sin(2*pi*2*t)*exp(-6*t)` for `0<t<1`, otherwise target. It preserves `amp=.1`, `freq=2`, `decay=6` and the user's one-second duration. The original expression is preserved at [user-bounce-expression.jsx](references/user-bounce-expression.jsx).
5. Gate bounce to arrival keys, not anticipation-start keys. For AE use `scripts/ae-size-expression.jsx`, which adapts the expression to paired width keys. Do not also apply elastic easing or ease to zero incoming velocity. This model is position-continuous, not necessarily velocity-continuous at arrival.
6. If the next anticipation starts before a previous spring settles, sample that spring's current width for the new start key; replace its remaining tail with the next base transition without a position jump. Do not sum independent elastic effects blindly.
7. If a cue/block is shorter than eight frames, first try a valid phrase/timing regrouping within authorization. Otherwise shorten anticipation to available time and disclose it; never animate outside the requested interval. The coded report lists shortened transitions.
8. Do not clip old glyphs to the shrinking capsule during anticipation. Text is an independent upper layer; inspect temporarily wider old text for readability. Regroup pathological widths rather than clipping letters or silently capping the bounce. Check geometry stays positive and in frame.
9. Evaluate everything from absolute timeline time; repeated seek at one timestamp must give the same frame.

## Compose and run

Keep a clean presenter source for glass sampling. Composite the main video, optional `shadow-ramp`, optional `msy-watermark`, capsule shadow/glass, then subtitle text; retain other foreground layers according to the edit. Both subtitle components sit above ramp. Keep the existing watermark at its own reference placement rather than moving it. Do not add either optional skill unless invoked/present.

Use the current editor where possible. The standalone fallback requires Python with Pillow/RAQM, NumPy, SciPy, fontTools (for font inspection), plus FFmpeg/ffprobe. It preserves source audio when encoding, with AAC re-encoding. Source must be clean: never stamp over reference footage's already-burned subtitles. Copy and edit `assets/example-scene.json` in the task folder with actual cues; the example is a timing/style demo, not an automatic transcript. `--source` starts at source time zero; trim/time-map the source first when applying a different edit segment, and restore edit time/audio on integration.

```bash
python scripts/render.py --scene /task/scene.json --source /task/clean-presenter.mp4 --out /task/subtitles.mp4
python scripts/render.py --scene assets/example-scene.json --test-pattern --out /task/test.mp4 --width 540
python scripts/render.py --scene /task/scene.json --source /task/clean-presenter.mp4 --out /task/frame.png --still 2.1
```

The synthetic pattern is a QA plate, not the user's finished edit. The fallback creates an opaque composited video, not an alpha overlay. For full multi-layer edits, integrate `Renderer.frame(source,t,underlay)` and `WidthTrack` so the glass samples clean `source` while being composited over a separately prepared underlay with ramp/watermark. Copy fonts/assets into portable project paths; do not edit canonical references for one-off projects.

## Verify and deliver

- Confirm bundled asset hashes, actual font selection and joined Persian letters, including dots/ZWNJ; do not silently substitute fonts.
- Inspect a settled phrase against the reference for position, font size, padding, capsule height/radius, translucency, edge highlights and effects strength.
- Inspect before/at `T−8/fps`, just before/at/after `T`, maximum overshoot and settling. Verify old/new text cuts exactly at `T` while only shape width anticipates and bounces.
- Test expansion, shrinkage, final one/two-word cue, short cue, interrupted spring, gap/new block and repeated seek. Check the first/last block frames are cuts without entrance/exit animation.
- Move the underlying video or capsule in a test and confirm live refraction follows the original source at current frame coordinates, never previous subtitles or a frozen patch.
- Check layer order with optional ramp/watermark, preserve audio/timing, inspect full export decode and verify dimensions/fps/duration.
- Save the skill through the supported skill workflow. For a video deliverable, use the environment's supported artifact channel. Report native versus approximate rendering honestly and do not claim an unrendered edit is a completed video.

# Visual and motion specification

## Evidence and priority

The written brief specifies motion/effects; the three still images specify palette/composition. No video was supplied. Never claim to have measured motion from those images. Current explicit user instructions override the brief, then references, then implementation defaults. Other historical Avangard palettes do not override this new one.

## Palette

Use literal hex labels from `media/palette.jpg`, not sampled JPEG pixels:

| Role | Hex |
|---|---|
| Deep burgundy: primary dark ink/background/shadow | #3B0016 |
| Bright red: emphasis | #F82524 |
| Warm beige: light ink/background | #D1C0A6 |

On beige, use mostly burgundy and selective red. On burgundy, use beige and red. For an overlay, inspect actual footage and choose legible palette colors. Do not add unrequested white/black/blue outlines.

## Font pair

| Role | Bundled file | Verified family / PostScript name |
|---|---|---|
| Geometric base | assets/fonts/Rubbama-Black.otf | KO Rubbama Black / KORubbama-Black |
| Expressive accent | assets/fonts/AmirFoda-Bold.ttf | AmirFoda / AmirFoda-Bold |

Rubbama is heavy, compact, and geometric. AmirFoda has broader flowing shapes. Divide them by word or line, never inside a joined Persian word. Do not blend outlines, add tracking to Persian joins, reverse the string, or stretch letters. Assets are user-provided; do not make claims about redistribution rights.

## Composition modes

**Block:** use `media/layout-block.jpg` for compact stacking, heavy words, variable line lengths, offset edges, scale contrast, and careful interlocking negative spaces. Small rotations are allowed but keep dots and counters clear. Do not copy the source's English text, black/white palette, every scratch, or source words.

**Expressive:** use `media/layout-expressive.jpg` for large calligraphic gestures, diagonals, asymmetry, and contrasting word scale. Use AmirFoda for the dominant flowing shape and Rubbama for support. These fonts do not reproduce the source's custom lettering exactly. Omit blue edges, hanging strings, exhibition labels, English copy, and logos unless requested.

Use compact title masses, not uniform caption rows. Start within the middle safe area for a standalone vertical card; avoid the subject/UI over footage. Centering a cluster does not put every word at the same x. Automatic line layout is a starting point: tune explicit placement for an important title.

## Effect stack

1. Shape each word correctly using its supplied font.
2. Apply fine noise and halftone within the glyph fill, fixed in local coordinates.
3. Add subtle animated contour boiling; keep the layout center stable.
4. Place a hard shadow 5 reference pixels downward, 100% core opacity, 0 softness.
5. Add an independent extremely faint diffuse glow behind the group.
6. Animate the whole word group in position and opacity together.

Keep dots/counters/thin strokes readable. Avoid grain flicker or background contamination. The texture is printed-ink character, not a filter covering the whole video.

### Glow implementation

For the actual Deep Glow plugin, preserve Exposure **0.02** and adjust spread to look very faint and diffuse. The bundled code is not that plugin: it combines broad Gaussian masks with a low alpha gain of 0.02 as a visual approximation. This gain is not numerically equivalent to a native plugin exposure transfer function. Do not call its output a native `.ffx` or `.mogrt` preset.

### Shadow direction

Keep the requested angle **180°** in scene notes. The explicit intended direction is down: `(dx,dy)=(0,+5)` at 1080 width. Apply the shadow in canvas coordinates after any word rotation so it remains vertical. Preserve fractional scaled distances with edge antialiasing. Map to each editor's actual angle convention. Keep softness 0 even though separate glow is diffuse. Matching dark text/shadow can merge visually; do not change colors silently to exaggerate it.

## Motion contract

For onset `s`, duration `d`, final center `xf`, and travel `r`:

```python
u = min(1, max(0, (time - s) / d))
p = 1 - (1 - u) ** 5
x = xf + r * (1 - p)
opacity = p
```

This creates fast initial motion, a long gentle tail, zero final velocity, no bounce/overshoot, and simultaneous opacity completion. The user's “0/100 graph” is easing intent rather than an invented cross-editor parameter. Adapt if a specific native curve is later supplied.

Use 0.55 s entrances, 0.12 s stagger, and 72 reference pixels of travel as defaults only. Read words in logical Persian order. Do not animate letters separately or let later words move settled words. Hold until explicit word end or scene end.

Contour boil defaults to 0.65 reference pixels at 8 Hz with a fixed seed. Do not shake the whole cluster. Geometric defaults scale by output width / 1080; seconds and opacity do not.

## Speech and timing

No ASR model or credentials are bundled. For speech captions obtain real transcription and word alignment, correct errors, then use those onsets. A transcript without times still needs alignment. Synthetic staggering is not speech detection.

Honor the user's interval. If entrances cannot fit with a readable hold, shorten adjustable timing or explain the constraint; do not silently extend the requested end. If a word must be fully readable at a timestamp, start its entrance beforehand within the allowed interval.

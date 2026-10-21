# Style and motion

| Role | Value |
|---|---|
| Crimson | `#B40023` |
| Cream | `#FCF0D6` |
| Cream style | Cream face, red hard shadow |
| Red style | Red face, cream hard shadow |
| Shadow | 3 px at width 1080; 100% core; 0 blur; default downward |
| Native glow | Radius 1000; Exposure 0.3; Screen |
| Motion blur | Angle 180°; Phase 0°; 16 samples; adaptive ceiling 128 |

These are source colors. Texture, antialiasing, glow, blur and compression create intermediate pixels. Preserve existing footage colors. Black is only the neutral preview stage from the supplied animation, not a third typography color.

| Scene key | Bundled file under assets/fonts | Embedded family |
|---|---|---|
| `bahman` | `Bahman.ttf` | Bahman |
| `e-bahman` | `E-Bahman.ttf` | E_Bahman |
| `lifta-black` | `Lifta-Black.otf` | Lifta-@behfont Black |
| `lifta-bold` | `Lifta-Bold.otf` | Lifta-@behfont Bold |

The two Bahman files have different hashes and designs. Keep both. Bahman gives compact geometric mass; Lifta gives pointed/calligraphic forms. Choose font per complete word/line. Four available fonts do not mean four fonts in every phrase. Preserve supplied kashida; do not insert extra kashida or stretch characters without a deliberate typographic decision.

## Texture and glow

Use the texture reference for fine printed grain and halftone density, not its blue or paper. Anchor coordinates to text before deformation. Default: fine noise plus approximately 4 reference-pixel rotated dot spacing. Scale geometry with output resolution. Inspect small dots/counters at delivery size.

Keep shadow edges hard. A moving hard shadow acquires temporal blur; this does not change the softness setting. The renderer uses a 3-pixel screen-down offset after curve deformation.

Deep Glow radius/exposure are plugin parameters, not a universal Gaussian sigma or exposure-stop formula. The fallback uses three diffuse blur scales, outer size derived from 1000 reference pixels, gain 0.3 and Screen. Do not substitute the earlier skill's Exposure 0.02.

## Path and spring

First Margin is distance along the path. Spring that scalar so position and orientation follow the same curve. Do not spring x/y independently and detach text from the path. A cubic curve's normalized parameter is not arc length; use an arc-length lookup.

The fallback shapes a whole RTL phrase as a ribbon, then bends it continuously. This preserves joins but approximates AE text-on-path, which may rotate shaped glyph clusters rather than deform a ribbon. Keep curves shallow. A flat word rotated at one point is not the default implementation.

Use open C2-smooth y(x) splines, extended beyond both screen edges. Loops, vertical sections and cusps require another mapper. Avoid curvature large enough to fold the text ribbon.

Spring reference: `velocity * 0.1 * sin(2*pi*2*t) * exp(-6*t) * final_fade`.

Sample signed velocity just before arrival from base motion only. Python samples a derivative around `arrival - frameDuration/10`. Never substitute distance for velocity. `linear` matches plain two-key motion; `spring-entry` uses a cubic with normalized initial slope 1.5 and end slope 0.65 to retain arrival speed. These are adjustable design defaults, not recovered AE graph values.

Keep velocity sign. Optional max offset limits amplitude before the sine, not the evaluated waveform. Default: no clamp. Fade the spring smoothly during its last 0.2 s of a 1 s duration. No simultaneous elastic easing. Independently time whole words/lines; do not split joined letters. Fade opacity only on request.

## Temporal blur

Enable comp and layer switches, including nested comps. Screenshot phase is **0**, not **-90**.

Sample `[t + phase/(360*fps), t + (phase+angle)/(360*fps)]`. Here exposure is half a frame, 1/60 s at 30 fps. Use midpoint samples, at least 16 and up to 128 depending on motion. Evaluate path and spring at each sample. Average premultiplied linear-light values, not straight-alpha RGB against black.

The renderer integrates text and shadow at subframes, then convolves the integrated glow source. Linear convolution commutes with averaging; Screen occurs at layer compositing. AE's proprietary adaptive sampler and complete effect order are not reproduced pixel for pixel. Visual inspection remains necessary.

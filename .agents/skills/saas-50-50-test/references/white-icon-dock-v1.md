# White dimensional icon dock — variant 1

## Scope and evidence

Treat this as one reusable visual/motion variant, not a global white-background or
single-entrance rule. Keep the user's 50/50 presenter layout in real editing;
the short study isolates the lower-panel animation because no presenter/voice was
supplied. The user requires a new test strictly under five seconds for each lesson.

Inspect `assets/variants/white-icon-dock-v1/reference.mp4` at native 1080×1920,
30fps, 85 frames, 2.833333s. It contains audio; the isolated visual study is silent.
The active light picture occupies approximately `(0,514,1080,892)` with black
letterboxing above/below. These black bars are source packaging, not panel styling.
Do not reproduce them. Preserve the original MP4 and both PNGs byte-for-byte;
their original filenames, Library identities and SHA256 are in `manifest.json`.

Read the attached entrance curve and motion-blur settings screenshots directly.
Distinguish three evidence levels: screenshot numbers are exact; cursor centroids
are image measurements; subframe interpolation, hover curves and a complete dock
lead-in are authored reconstructions. No editable AE project was supplied.

## Appearance, geometry and hierarchy

- Use a clean white/light stage for this variant. The decoded clip's stage is a
  light neutral gray around #EEE, and the user calls it white. The current study
  uses pure #FFFFFF. Keep this choice local to the variant; future shots may use
  other backgrounds. Avoid adding a decorative gradient or headline to this study.
- Use a horizontal softly translucent near-white mother capsule, a fine bright
  rim, very rounded corners and extremely soft low-contrast shadow. At the landed
  1080-wide reference state its box is about x170–910, y878–1044: 740×166, radius
  about 54. This is a dock with rounded ends, not five separate floating cards.
- Use five mildly dimensional app tiles, approximately 108–112 square, with
  rounded corners (~25% of their side), raised rim/beveled edge, subtle material
  gradients, soft highlights/contact shading and crisp raised glyphs. Preserve
  the source's notes yellow/cream, Discord violet, Pinterest red, After Effects
  deep violet and Messages green for a literal study. Do not use flat emoji or
  flat monochrome outlines as a substitute for this variant's icon treatment.
- Neutral tile centers are about x253,397,539,682,824, y960 in source coordinates.
  The production panel example remaps their baseline to y480 in 1080×960. Scale
  all geometry uniformly for a different resolution, preserving tile aspect and
  breathing room. Center the group; do not stretch the original clip into a pane.
- Use the same mild dimensional design language for new subject-specific icons.
  Exact source raster crops are bundled with a documented authored rounded alpha
  mask; they are not recovered original transparent icon exports or 3D meshes.
- Parent all five icons to the dock entrance transform. Nest hover transforms
  inside each tile so the whole group enters coherently while each tile reacts
  independently. Keep pointer above the icon faces and dock. Clip the entire lower
  scene to its half; lower pointer/camera moves must not move the presenter.

## Exact mother-shape entrance curve

The supplied Flow graph visibly reads **0.00, 0.00, 0.00, 1.00**. Use
`cubic-bezier(0,0,0,1)`, not 75/75 Easy Ease, an S curve, a linear move or a spring.
It starts very sharply and spends the remainder decelerating into an extremely
soft landing. Do not add bounce to this entrance unless another lesson asks for it.

For normalized progress u, solve x(s)=s³, so s=u^(1/3), and return
`E(u)=3*s*s-2*s*s*s`, clamping u to [0,1]. This implements the screenshot curve
directly in code; it is not a guessed stock easing preset. In GSAP use a custom
ease function with this mapping; in native AE use the Flow values or the equivalent
temporal handles. Keep spatial paths separate from temporal easing.

The supplied video begins with the dock already partially present and slightly
smaller, then settles. It does not reveal the entire preceding entrance. The study
adds a clearly identified 0.5s lead-in: animate mother Y +150→0 reference pixels
and scale .86→1, from t=.06 for .54s with the exact screenshot ease. Treat those
distance/duration values as authored test choices, not recovered source keyframes.
For production choose the entrance direction/range appropriate to the narration.

## Pointer artwork, paths and rotation

Use a solid black desktop arrow with a bright white border, mild edge softness and
no giant click rings. Its reference black silhouette is roughly 52×85 px when
upright. Keep its border visible over deep violet/red icons. Rotate the arrow
around a consistent anchor; do not let its anchor jump during turns. The bundled
renderer uses the black silhouette's centroid, with the visible tip derived from
that same geometry. A tip-anchored port must compensate its position accordingly.

The reference trajectory is **not** a single straight line or a pointer traveling
at constant speed with one universal ease. Inspect these source-local beats:

| Source time / frame (zero-based) | Observed action |
| --- | --- |
| .433–.567 / 13–17 | Pointer enters quickly from the left/lower side and sweeps past Notes/Discord toward Pinterest; pronounced travel blur |
| .567–.967 / 17–29 | Continues right across Pinterest and AE toward Messages; progressively slower horizontal travel |
| 1.00–1.40 / 30–42 | Rounds the rightmost tile; arrow turns counterclockwise, centroid travels up/right then left; silhouette faces more leftward |
| 1.40–1.633 / 42–49 | Travels left along/below the dock face, passing AE; orientation begins turning back |
| 1.667–2.167 / 50–65 | Large airborne loop above dock: rises left, arcs right across the top, descends toward AE; arrow rotates continuously through the loop |
| 2.20–2.80 / 66–84 | Returns diagonally down/left through AE toward Pinterest, decelerates and settles; Pinterest remains magnified |

Use `cursor-measurements.json` for the dense every-frame centroid and rotation
samples, not only this summary. Stored cx uses source x; cy is source y minus514;
add34 to cy in the study to align the dock to y480. Times stay source-local; add
the study's `.5s` lead-in to schedule them. Preserve this mapping when comparing.

Fit a continuous non-oscillating PCHIP curve separately to X, Y and **unwrapped**
rotation between frame samples. Do not linearly wrap 359°→0° into a full reverse
spin. Keep speed changes, small near-tile turn and large upper loop. Keep the
pointer artwork scale stable; small silhouette-fit scale fluctuations from blur
are not evidence for intentional pointer pulsing.

Rotation is relative to the extracted frame-28 silhouette: around +16° in early
rightward travel, 0° near Messages, about -82° at the right-side turn, -50° on the
left sweep, +24° rising, +102° near upper-left arc, +188° across the top, +296°
descending, then +360° on final settle. Angles are fitted estimates, not original
AE rotation key values. Low-confidence first blurred frames are explicitly marked.
Do not claim exact recovered pointer graphs. Dense measured motion is preferable
to inventing one numeric graph for all path segments.

## Hover reactions and timing

Make hover local and causally tied to the pointer's approach/contact. The nearby
tile smoothly grows about **1.14–1.17×** and its center lifts roughly **7px**.
The top edge therefore rises about16px. Return the previous tile to neutral while
the next grows. Keep neighboring centers/gaps stable; do not magnify the whole dock,
push every neighbor away, add a wild bounce or loop unrelated pulsations.

Read the colored silhouettes in consecutive frames; typical source-local cues:

| Tile | Approach/peak/hold/return in seconds |
| --- | --- |
| Notes | Brief early response around .39–.52; infer cautiously because source entry/blur obscures it |
| Discord | .43→.48, hold to .50, neutral by .57 |
| Pinterest | .49→.55, hold to .59, neutral by .67; again 2.23→2.34, remain raised to end |
| AE | .57→.66, hold to .72, return by .87; short pass1.52–1.73; return pass2.11–2.34 |
| Messages | .73→.86, hold during near-tile turn to1.44, neutral by1.62 |

The study uses `smoothstep` rise/fall for these measured cue windows, not a claim
that the source author used smoothstep. Retarget encounters to actual tile bounds
when changing icon count/layout. Distinguish hovering from clicking: this lesson
does not establish a click press, button depression or ripple. Do not invent one.

## Mandatory AE-style temporal motion blur

The screenshot specifies exactly: **Shutter Angle180°, Shutter Phase0°,
Samples Per Frame16, Adaptive Sample Limit128**. Enable both the composition
switch and each moving layer switch in native AE. Include mother transform,
icons' scale/lift, cursor translation/rotation and any lower-scene camera motion.

For code, expose `[t, t + (180/360)/fps]`; phase0 opens at the nominal frame time.
At30fps the exposure lasts1/60s. Evaluate all moving states at subframe midpoints,
average their rendered RGB colors, use at least16 samples, increase for fast
translation/rotation up to128. The renderer bases adaptive count on displacement
and angular edge travel; it actually samples and integrates the scene. Avoid
CSS Gaussian blur as motion-blur replacement, static arrow trails, a directional
smear that ignores turning, or checking a setting without temporal renders.

This is a coded temporal equivalent of the supplied AE exposure settings; it does
not mean After Effects executed or that a different renderer is pixel-identical.
Inspect fast pointer arrival, turning and upper loop in consecutive output frames;
held objects should remain crisp while moving objects smear along their motion.

## Reproduction and review

Treat the white background, dimensional icon material, mother-shape entrance,
cursor path/rotation, and local icon hover as independent tools. Select any useful
subset for the narration or combine all of them in the reference order. A pointer
may travel over a different UI; an icon may use this material without a dock;
a group may use the entrance curve without a cursor; a hover response may be
triggered by another input. White is a background option, never a global rule.
Keep the exact entrance graph local to this entrance variant and allow future
entrances/graphs to coexist. Retain all measured data and evidence distinctions
above when reusing or retiming the parts.

The study renderer accepts `--components` with independent `dock`, `icons`,
`cursor`, `hover`, and `entrance` toggles; omission preserves the complete study.
Examples: `--components cursor` shows only cursor travel over a white stage;
`--components dock,entrance` shows only group arrival;
`--components icons,hover` shows hover cues without a dock or visible pointer.
An empty component list is a clean white stage. These CLI switches demonstrate
separation; the study's fixed white stage and reference subjects do not restrict
production backgrounds, icon subjects, layouts or event triggers.

The user resubmitted this lesson and the same three source byte streams. Record
the new filenames and Library identities in `manifest.json` under
`resubmitted_sources`; preserve earlier identities and the unchanged approved
study. Read `references/white-icon-dock-user-lesson-fa.md` for the Persian
requirement record. A fresh 3.4s rerender is bundled as `recheck-study.mp4` with
`recheck-study-report.json`; it awaits review and does not replace the approved
`study.mp4`. Inspect motion again and synchronize the entire skill directory to
both destinations before claiming completion.

Run `python scripts/render_icon_dock.py --output /task/icon-dock-test.mp4`.
It renders102 frames,30fps,3.4s,1080×960, no audio/presenter; fully decodes the result
and writes a technical report with actual sample counts and output hash. It guards
existing outputs and original assets. It does not synthesize narration or test
speech synchronization. For this isolated study use the supplied icon subjects;
production must retarget content and timing to the actual spoken concept.

Compare beginning, icon encounters, Messages turn, top arc and Pinterest settle
against the supplied source. Keep the authored lead-in distinct. The exact bundled
3.4s `study.mp4` has now been explicitly approved by the user; preserve its bytes
and hash as this variant's visual benchmark. Later lessons/tests need their own
review; add alternatives without applying this white-stage dock to every scene.

# Elastic pre-click and five-disc reveal — modular lesson 2

## Contents

- Evidence and scope
- Cursor anticipation and accelerating strike
- Hollow pixel outlines
- Five discs, alternating gradients and fine rim light
- Dimensional identity and plan change
- Timing/orchestration and palette
- Native AE and coded implementation
- Study and review

## Evidence and scope

Inspect `assets/variants/anticipation-circle-reveal-v1/reference.mp4` at native
1080×1920,30fps,30frames,1.0s. Approximate active picture is
`(0,655,1080,610)`; black letterboxing is packaging, not a required design. Retain
the original MP4, original blur PNG, original names/Library identities and SHA256
in `manifest.json`. The reference has sound; the visual reconstruction is silent.

This lesson yields independent tools: cursor preparation/strike, hollow pixel
burst, five filled-gradient discs, fine edge light sweep and dimensional symbol.
Preserve their appealing reference combination **and** allow every part to run
elsewhere independently. Read `component-system.md`; this independence is the
user's most important whole-skill instruction. Red is the example icon color,
not a universal requirement. White is one starting-stage option.

The blur screenshot directly verifies180° shutter,0° phase,16samples,128adaptive
limit. No editable project or pointer rotation/curve controls were supplied.
Cursor silhouettes are measured; numeric pitch/curves and depth construction are
authored equivalents unless explicitly described as user/screenshot numbers.

## Cursor anticipation and accelerating strike

Keep the black desktop-arrow face and narrow white outline. Keep a stable target
and anchor: the tip must appear aimed at the clickable object while the arrow
draws back. Separate whole-pointer X/Y/Z/rotation from the deformable tip/body.
Do not simulate preparation with only a flat Z rotation or rigid scale pulse.

Reproduce three phases:

1. **Soft preparation / draw-back.** The mouse seems to tilt back around its X
   axis; its silhouette gets longer and its tip pulls slightly right, like a
   stretched elastic cord. The lower body/tail remains comparatively anchored.
   Increase the deformation gently, then slow near the maximum wind-up.
2. **Accelerating release / strike.** Start from the prepared pose softly, then
   accelerate toward the target so the impact is the fastest part. Do not apply
   a slow ease-out landing to the strike. Release the tip stretch and apparent
   pitch as the pointer drives in. Give the event a definite contact time.
3. **Result handoff.** Let the pointer shrink/foreshorten and become covered by
   the resulting scene at impact. A short fade under the opening object is valid.
   Do not add unrelated cursor spins, multiple clicks or mandatory click rings.

Source-local silhouette observations at1080wide:

| Frame/time | Black-arrow bounds / tip evidence |
| --- | --- |
|0 /0s | x547,y970,w37,h67; tip about(548,970) |
|4 /.133s | x547,y965,w41,h78; tip about(555,965) |
|7–8 /.233–.267s | x547,y964,w42,h79; tip about(556,964), maximum preparation |
|10 /.333s | x547,y965,w41,h76; release begins |
|12 /.400s | x547,y966,w38,h71; faster collapse/approach |
|14 /.467s | x545,y968,w32,h57; arrow drives into target as outlines begin |
|15 /.500s | x541,y969,w24,h40; rapid foreshortening; overlay takes over |

The body height grows roughly18%, width roughly14%, and the tip moves about8px
right/6px up during wind-up. These are visible silhouette measurements, not exact
3D rotation values. For a native AE starting recipe use a modest backward X pitch
(roughly15–25°, sign chosen for the actual camera), a mesh/bezier deformation
concentrated at the tip, and a small anchored body stretch. Tune against frames;
do not claim the original used those degree values or a particular deformer.

Use `cursor-deformation.json`: seven contour vertices for each frame0–15,
screen offsets from the source target(540,960). Map them to the actual target
anchor. PCHIP interpolation per vertex preserves observed changing shape at
subframe times. This coded screen-space mesh reproduces the **appearance** of
pitch and elastic tip pull; it is not recovered source3D geometry. For native
or other3D workflows, preserve the same visible silhouette and tip relationship.

Keep preparation and strike easing separate. A useful new-shot starting point is
soft in/out preparation followed by an accelerating power/expo-in strike. The
source's original numeric curves are unknown; the dense contour samples are the
reference for this study. Never claim these are the previous lesson's exact
`(0,0,0,1)` entrance graph. That graph belongs to a separate mother-shape tool.

## Hollow pixel outlines

Start sparse small squares/corner fragments shortly **before** disc expansion;
continue their outward spread during opening. Use no fill, thin brand-colored
strokes, varied small square sizes, some incomplete L/corner contours and a
grid/pixel-like distribution. Avoid filled confetti, stars or thick neon squares.

At1080wide, use approximately10–22px square sides,1–2px strokes, moderate opacity
and a spread of roughly150–520px from the event origin. These are authoring
values grounded in the reference, not user-supplied numeric settings. Keep paths
deterministic, loosely radial but with destinations aligned to a sparse grid.
Allow overlap with the discs; fade particles as the new plan settles rather than
leaving a busy permanent frame. Keep the identity readable at center.

In the supplied source faint outlines appear around frame14/.467s; disc opening
becomes clear around16–17/.533–.567s. Preserve this short lead when reproducing
the combined sequence. In standalone use give the burst its own origin/start/
spread/lifetime/color and no dependency on a cursor or disc.

## Five discs, alternating gradients and fine rim light

Use **five filled circular shapes**, concentric around the selected icon/event
origin, ordered largest behind smallest. Do not replace them with only stroke
rings, a single radial gradient, one flat expanding color or a generic crossfade.
They expand over the old shot and become the new scene's colored stage.

Give neighboring discs opposite gradient directions: e.g. light tint at top and
strong/darker hue at bottom on disc1, dark top/light bottom on disc2, then repeat.
Use related light/strong tones of the resolved brand/icon hue. Preserve the subtle
raised/layered feeling and visible boundaries. Avoid unrelated rainbow colors.

Apply a **thin light sweep / rim light** along each circle perimeter: narrow,
brighter near the top/side arc, weaker elsewhere, with a fine soft edge. Keep it
around1–2px at1080wide, not a broad glow halo. A small traveling highlight arc can
reinforce the rim. Do not rotate the vertical gradients with a rotating highlight.

At the landed study state, use approximate radii190,325,460,600,770px around the
1080×960 panel center. All five expand from the icon region; the outer disc must
cover the entire panel corners before handing off. Resize uniformly or derive
the outer radius from the farthest pane corner for another origin/aspect.
Treat these radii as an authored adaptation from the source's much shallower
active picture; do not stretch the source screenshot to fill1080×960.

The user describes an explosive early opening with an extremely soft ending.
Preserve that overall fast-to-settled impression; differentiate the short
preparation, local circle births and apparent camera/scene enlargement. The
rendered source's visible outer envelope grows most through its middle few
frames before settling. Exact original scale/camera keyframes cannot be recovered.
The study uses a monotone PCHIP radius envelope with source-local samples:
times `.49,.52,.55,.58,.61,.65,.69,.73,.78,.84,.96` and normalized radii
`0,.025,.095,.17,.26,.40,.57,.75,.91,.98,1`. These are a visual reconstruction,
not claimed AE keys. For new shots choose a fast opening with a long soft tail;
avoid a constant-speed mechanical wipe or a sudden stop at full size.

## Dimensional identity and plan change

In the linked reference the selected Pinterest identity persists at center:
the icon tile hands off to a raised white P with subtle gray side thickness,
slight oblique rotation during travel, then a near-frontal readable settle.
Retain the selected subject when using this identity-preserving transition;
do not replace it with an unrelated mark or generic text.

Use real supplied/generated3D assets when available. The bundled symbol is a
white-face alpha extracted from a late source frame; it is not the original
transparent3D asset. The coded study projects layered relief with perspective
pitch/yaw/roll and gray extrusion. It approximates the visual depth; it is not
a Blender model, physical material or native AE execution. Do not overstate it.

For standalone disc transitions an icon is optional. Reveal the next scene/result
through the covered panel, or use a supplied subject. For a cursor-only component
do not force the scene change. For a symbol-only component do not force circles.

## Timing/orchestration and palette

Bind optional events explicitly:

- Preparation: source0–.27s; release grows from around.30s to.50s.
- Faint hollow pixels: about.44–.47s, a little before the discs dominate.
- Impact/scene takeover: roughly.50–.55s, followed immediately by expansion.
- Discs and dimensional symbol: about.51–.96s, then a clean readable hold.

These event estimates come from a30fps rendered clip, not exact project timing.
For production schedule against the actual spoken cue and retime the component
while retaining its character. Optional links can share an `impact_time`; their
standalone triggers must remain usable. Preserve presenter framing and audio.

Use `component-system.md` palette precedence. If an icon triggers the reveal,
prefer its color family unless a prompt overrides it. If used independently,
follow that video's organizational palette. Example default #E60023 is Pinterest
red only for the literal study. Never force red on another video. Recolor all
disc stops and pixel strokes together; keep the fine white/light rim coherent.

## Native AE and coded implementation

Native: enable the composition and moving-layer blur switches; set180°/0°,
16samples/frame and128adaptive limit, exactly as supplied. Include cursor mesh/
transforms, disc scales, pixel motion, symbol pose and any camera movement.
Do not put blur on only the camera or final output while ignoring moving layers.

Code: evaluate actual shape/pose/position/radius/opacity at subframe times across
`[t,t+.5/fps]`; integrate at least16 samples and adapt up to128 for fast travel.
The study performs RGB temporal integration. Static CSS blur, one smeared frame
or duplicated pointer ghosts are not substitutes. Keep static holds crisp.

Expose independent classes and event parameters rather than burying all parts in
one hard-coded composite. The study's `--mode` presets demonstrate independence;
production may call `AnticipationCursor.draw`, `OutlinePixelBurst.draw`,
`FiveDiscReveal.draw` and `DimensionalSymbol.draw` separately. The fixed CLI is a
visual study, not a complete arbitrary-scene authoring engine.

## Study and review

Run `scripts/render_click_reveal.py --mode combined --color '#E60023' --output
/task/new-test.mp4`. Use a new output path. It renders72frames,30fps,1080×960,
**2.4s**, silent/no presenter. Output time equals source+.4s; the last state holds.
The exact bundled2.4s study is explicitly user-approved. Preserve its bytes/hash.
Keep the previous approved3.4s dock study
unchanged at `assets/variants/white-icon-dock-v1/study.mp4` with its verified hash.

Test independent modes `anticipation`, `transition`, `pixels`, and retarget palette
with `--color '#008F89'` or the actual instructed brand. Supply matching transparent
`--symbol` artwork when replacing Pinterest; use `--no-symbol` for no icon and
`--no-pixels` for a disc-only reveal. No narration synchronization is
claimed for these isolated tests. Compare wind-up maximum, release/impact,
pre-opening outlines, all five disc bands, alternating shading, fine perimeter
light, symbol pose and final settle in consecutive frames, not just a hero still.

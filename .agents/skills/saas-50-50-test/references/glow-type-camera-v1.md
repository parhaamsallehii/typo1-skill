# Glass input, glow typing and camera cuts — lesson 4

## Priority and independent reuse

Make **glow typing with a following camera** and **a match cut at peak pan speed**
frequently used signature tools for this user's SaaS motion work. Actively consider
the first for prompt entry, search, text creation and meaningful keyword reveals;
consider the second for moving between overview and product detail. Do not leave
them as rare decorations. Use them often when their function matches the spoken
beat, with readable holds and motivated targets rather than adding them blindly.

Keep nature footage, glass panel, peripheral focus, both pointer paths, detail cut,
typing light, follow camera and pan/match cut as selectable tools. Reproduce the
whole reference chain or use appropriate parts elsewhere. For this named typing
variant, the camera **must** track the writing head with the same progress/ease;
do not use the full typing variant as a stationary typewriter by default. The
underlying glow/head and camera are separately reusable tools in other contexts.
Do not force the nature background, reference brand, cursor or glass panel onto
every use of typing. Preserve all earlier variants and future alternatives.

## Evidence and source inspection

Restore the unchanged original MP4 before inspection:

```bash
python scripts/assemble_reference.py \
  --manifest assets/variants/glow-type-camera-v1/reference-parts.json \
  --output /task/glow-type-camera-reference.mp4
```

The21MB source exceeds the connector's16MiB request-body limit after base64
encoding. Its original bytes are therefore bundled in six raw chunks, not
re-encoded or shortened. The helper checks each chunk and the final SHA256.
The restored MP4 is byte-identical to the upload. Keep the same lossless parts
and manifest in Skills and GitHub, and restore outside the skill assets.
Inspect that full MP4 and the bundled motion-blur PNG before using this recipe. Native clip:1080×1920,30fps,155frames,
5.166667s; active picture x0–1080,y656–1264 (1080×608). Black bars are packaging.
Keep the active aspect while inspecting, then re-layout for the production pane.
Names, Library identities and SHA256 are in `manifest.json`.

| Approximate source-local span | Direct visual observation |
| --- | --- |
| 0–1.7s | Live meadow/flowers behind a translucent glass panel and pale search field; first pointer swoops, turns, approaches input and settles |
| around1.7–1.77s | Abrupt same-scene change to a close view of the input, with recognizable UI continuity |
| about1.9–3.6s | Characters appear successively; a cyan luminous leading bar and tint trail follow the latest letters; camera moves with the text |
| about3.6–3.8s | Lateral motion and a hard scale jump into the overview; no unrelated new subject/scene |
| about4.0–5.17s | Smaller pointer makes a different arc/turn and settles near the right search control |

The user specifies75/75 for writing/follow and100/100 for lateral match motion.
Those numbers are user requirements, not values recovered from the rendered clip.
The blur numbers are exact screenshot evidence. Cursor positions are measured;
orientations, camera travel, timing adaptation, glow strength and glass construction
are authored fits. No original AE project, original font or editable effects were
supplied. Avoid claims of exact source keyframe recovery.

## Terminology: preserve the requested behavior

The user calls the visual cuts “جی کات”. Keep that wording as a retrieval alias
for this lesson, but execute the described picture edit: a **same-scene detail
jump cut/punch-in** or a **motion match cut with a scale jump at peak pan speed**.
Do not interpret it as a request to advance audio from the next scene. J-cut in
normal editing terminology denotes audio leading picture; this request supplies
no such audio overlap instruction. Preserve the original production audio.

## Nature-video background and glass plane

Nature footage is one useful background variant: bright sky, live plants/flowers,
foreground depth, restrained blur and a clear central region for UI. Preserve
continuous movement when actual background video is supplied; do not pretend a
still photo is live footage. Retarget subject and color to the actual video.

Use a softly rounded translucent mother panel with a pale input above it and
quiet thin utility marks below. Blur/refract the **current source underneath**
inside the glass shape, add restrained tint, fine bright edges, subtle reflected
light and soft contact shadow. Do not use one opaque colored rectangle as glass.
Preserve input readability. Keep the mother panel, input, icons and content under
the same SaaS-scene camera; local pointer or hover transforms remain separate.

The coded study approximates glass using a blurred/resampled local background,
transparent tint, narrow highlights and shadow. It is not native LiquidGlass,
Deep Glow or an AE execution. Its background is a deliberately code-native navy/
cyan abstract stage, not the original meadow. The attempted new photo generation
was unavailable due a usage limit; no generated lake asset is claimed or bundled.
Study topic is AI study planning and its exact text is `Build my AI study plan`.

## Feathered peripheral focus

Keep the center and current text/detail sharp while softly blurring peripheral
frame areas with a broad feathered mask. Make center, ellipse/range, feather and
blur amount independent. Avoid a hard blur border or uniformly blurring the whole
input. The study uses a soft elliptical focus mask at output-pane coordinates and
roughly5px wide-view /9px close-view blur, authored for1080×960.
This spatial focus/glass blur is distinct from temporal motion blur; keep both
when the scene calls for them. Do not substitute one for the other.

## Pointer variant A — input approach

Preserve the black desktop arrow with a narrow white border and a stable anchor.
The initial pointer comes from the left, arcs upward/right, turns downward and
left, then approaches and settles at the beginning of the field. Rotation evolves
through the bend; do not replace it with a straight stock tween or a rigid arrow
at a constant angle. Include travel and rotation in temporal sampling.

Use `cursor-variants.json` entry rows, not only this prose. Coordinates are native
active-picture coordinates; source y already subtracts656. Source frames6,10,14,
18,22,26,30,34,42,46 have measured black-component centroids. Interpolate X/Y and
unwrapped angle with PCHIP. The orientation fits turn clockwise through the arc
and settle near one full turn. Numeric angles are authored visual fits, not source
rotation values. Retarget the final centroid/tip to the actual input and align the
pointer's anchor consistently; do not stretch the path to a new aspect.

The study maps those frames to output .20→1.34s, holds briefly, carries the cursor
through the detail cut with the shared projection, and fades it before typing.
That time map, scale .64 and the short fade are authored test choices. Retarget
times to the actual narration/click event in production. No click audio or paid
site action is implied by this silent demonstration.

## Same-scene detail cut

Cut directly from overview to a close view of the chosen field/detail. Keep the
same scene, content and focus target. This is an abrupt scale/framing edit; do not
insert a continuous zoom ramp, a dissolve, a wipe or a different product screen.
Choose a close framing that explains the relevant detail. It may stand alone
without any typing, pointer, glow or nature backdrop.

Study: hard cut at output frame44 (44/30s), scale1→2.5 with a corresponding focus
position change. Camera and all SaaS visual layers share the new projection. The
test's earlier timing compresses the reference lead-in to keep the total exactly
5s; it is not a claim about the reference's original cut frame.

## Glow typing — 75/75 with mandatory shared follow

Reveal characters progressively. Place a small colored shape/bar at the writing
front, give it a comparatively strong diffuse Deep-Glow-like halo, and let the
most recently revealed characters retain a colored trail that fades back toward
the normal ink. The bar travels with the added letters. Do not replace this with
a whole-word opacity fade, a generic cursor blink or an unrelated sweeping glow.
Keep the luminous core narrow enough that the active letter stays readable.

Use user-specified75% incoming and75% outgoing temporal influence, with soft
beginning/end and faster middle. For a scalar progress with zero endpoint speeds,
the study implements `cubic-bezier(.75,0,.25,1)` by solving time's Bezier X first,
then evaluating Y. This mapping assumes zero endpoint speeds; do not reuse it as
a claim about arbitrary AE keyframes with nonzero velocity. Keep duration/range
separate from influence. Do not treat75/75 as .75s/.75s.

Use the **same normalized progress** for writing-head distance and follow-camera
position. A little screen-space drift is acceptable, but camera and typing must
start, accelerate and settle coherently. Follow rightward for an LTR line and
leftward for an RTL line, or use the corresponding composition's reading flow.
Do not animate camera tracking with an unrelated linear tween. Finish on a view
where the complete phrase can be read.

Study: text32 reference pixels; reveal from48/30 to100/30s. The camera follows
96% of the head's world-space travel plus an authored framing offset. The leading
bar is about4.6×34 reference pixels, with broad11px and tighter3.8px glow lobes.
The latest glyphs receive an exponentially fading accent tint. These sizes and
strengths are authored examples, not source Deep Glow parameters.

Blur the glow's alpha and keep its RGB bound to the chosen accent; avoid black
fringes from blurring transparent-black RGBA. The reference accent is not a
global color. Bind the head, glyph tint and compatible UI accents to brand/icon.

For Persian/Arabic, reveal grapheme clusters in an already shaped line or use a
shaped whole-prefix strategy with proper joining, RTL advances and visual bounds.
Do not animate raw UTF-8 bytes, split diacritics/ZWJ, or draw isolated letters as
disconnected forms. Retarget the font to the video's language and brand; the test
uses DejaVu Sans as an authored English UI choice, not a recovered source font.

## Peak-speed pan match cut — 100/100

Make this a frequently used camera handoff for the user's SaaS edits. Move laterally
within the same plane with user-specified100%/100% temporal influence: very soft
start/end, exceptionally sharp speed peak in the middle. Place a **hard framing/
scale cut exactly at that peak**, then continue the same lateral motion phase and
direction. The frame before the cut can be wide and the next close, or the reverse.
The supplied source shows a return to overview. Do not crossfade or ease a smooth
zoom through the cut; the sudden scale change is the feature.

Preserve a recognizable feature/anchor across the edit so motion connects both
views. Keep the scale-independent projected anchor/translation continuous while
the projection scale jumps. Avoid reversing lateral direction, stopping on the
cut, losing the subject or adding an unrelated transition. Keep blur on motion
within each shot; never average pre/post framing together across the hard edit.

For zero endpoint speeds, the scalar study uses `cubic-bezier(1,0,0,1)` solved by
bisection. Its continuous time mapping is extremely steep at the midpoint; avoid
naive division by a zero derivative or replacing it with a generic ease-in-out.
Evaluate actual subframes, respect the sampling cap and put the edit on an output
frame boundary. Numeric travel and framing remain shot-specific.

Study pan: frames100→122, cut at111 (3.7s), close2.5→wide1.0 at the midpoint.
This preserves the reference's close→wide direction. Both user-described scale
directions remain valid alternatives. Retarget the event to speech/edit timing.

## Pointer variant B — final control approach

Keep this separate from variant A. The pointer is smaller in the observed final
wide view, approaches from above the right control, travels up/left through a
small arc, swings down and returns toward the search icon with evolving rotation.
It settles rather than constantly orbiting. Use the exit rows in the JSON; frames
124–154 have measured black-silhouette positions, while frame122's blurred entry
is an authored estimate. Angles are visually fitted and unwrapped, with a largely
counterclockwise turn through the loop. Never interpolate359→0 as an unintended
full reverse spin. Preserve the tip/target relationship when retargeting.

Study maps source frames122–154 to4.10→4.98s and scale .38. Its last centroid
lands slightly below/right of the search-control tip target. These are authored
adaptations. A different icon/layout may use the same movement language with
different coordinates; it need not be attached to a typing or zoom sequence.

## Modular code, test and blur

`GlassStage`, `GlowTypeWriter`, `FollowCamera`, `ReferenceCursor` and
`PeripheralFocus` expose separate tools. `influence_ease` is reusable independently.
The fixed combined renderer demonstrates this lesson; it is not a complete video
editor, transcription engine or a product action executed on an external site.
Production can orchestrate the same parts with other subjects/backgrounds.

Run `python scripts/render_glow_type_camera.py --output /task/new-test.mp4`.
Use `--text`, `--color` and `--no-focus` as appropriate. Dependencies: Pillow,
numpy, scipy, DejaVu Sans and FFmpeg/ffprobe. The study is exactly1080×960,
30fps,150frames,5.000s,silent,with no presenter or speech synchronization claim.
The user's explicit five-second request overrides the usual strict-under-five
rule **for this lesson only**. Default future teaching tests remain under5s
unless the user gives another duration. Record this new study as awaiting review.

Native AE: turn on comp and every moving layer's blur, shutter180°,phase0°,
samples/frame16,adaptive limit128. Include camera, cursor position/rotation,
writing head, glyph reveal/tint and any moving background. Code: integrate actual
scene states over `[t,t+.5/fps]` with16–128 adaptive samples. Spatial glass/focus/
glow blur does not satisfy temporal blur. Keep hard-cut exposure samples on their
own shot side. Do not claim native AE, LiquidGlass or Deep Glow was executed.

Inspect first cursor turn, detail-cut adjacency, early/middle/late glyph reveal,
halo/trail, tracking motion, the two frames around peak-speed cut and final cursor
settle in the real output. Validate duration,150 frames,dimensions,silence and full
decode. Preserve old reference and approved-study bytes. Save the unchanged
original MP4/PNG, JSON data, detailed instructions, code, study and report in both
Skills and GitHub; read back the published trees and compare all file/blob hashes.

## Persian requirement record

این درس چند جزء دارد: ورژن تازهٔ حرکت موس در ابتدای مرجع، کات سادهٔ تصویری
به نمای نزدیکِ همان جزئیات در همان پلان، نوشتن حرف‌به‌حرف با شیپ رنگیِ جلو
حروف و گلو نسبتاً قوی و رنگِ فیدشونده روی آخرین حروف، دوربینِ حتماً همراه متن
با گراف هماهنگ۷۵/۷۵، مچ‌کاتِ میان حرکت افقی۱۰۰/۱۰۰ دقیقاً در اوج سرعت با
تغییر ناگهانی زوم، و ورژن متفاوت حرکت موس در پایان. تایپ گلودار با دوربین و
مچ‌کات در اوج سرعت باید جزو ابزارهای پرتکرار و مهم این سبک باشند.

جزءها می‌توانند مثل مرجع با هم ترکیب شوند یا هرکدام جدا در جای دیگری به کار
بروند. رنگ، بک‌گراند، ورود، گراف یا حرکت هر نمونه تنها یک ورژن قابل انتخاب
است؛ نسخه‌های بعدی کنار آن اضافه شوند. رنگ از برند ویدیو یا آیکون مرتبط بیاید.
موشن‌بلر با۱۸۰/۰/۱۶/۱۲۸ برای کامپوزیشن و لایه‌های متحرک روشن باشد. جزئیات و
رفرنس‌ها کامل حفظ شوند. تحلیلِ کمک‌کننده از خود رفرنس نیز مجاز است؛ برداشت‌ها
و اعداد تخمینی را از دستور صریح کاربر و تنظیمات واقعی جدا کن. تست این پیام
استثنائاً دقیقاً پنج ثانیه و با موضوع، پس‌زمینه و رنگ‌بندی متفاوت ساخته شود؛
همهٔ اجزای توصیف‌شده را نشان بدهد. نتیجه و فایل‌ها هم در اسکیل و هم GitHub
اعمال و پس از انتشار بازخوانی و تطبیق داده شوند.

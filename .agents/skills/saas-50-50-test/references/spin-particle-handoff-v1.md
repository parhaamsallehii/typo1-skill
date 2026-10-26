# Spin, glyph particles and two feathered masks — lesson 3

## Scope and evidence

Read this recipe for five-circle rotation/scale, symbol fragmentation, a soft
center aperture between shots, an ordered incoming dot field, or its center-out
cleanup. Each is independent; the complete chain is an optional reference recipe.
Do not replace the older icon-dock or click/reveal variants.

Inspect the unchanged `assets/variants/spin-particle-handoff-v1/reference.mp4`
and `motion-blur-settings.png`. The clip is 1080×1920, 30fps, 30 frames, 1s.
Active picture occupies x0–1080, y656–1264 (1080×608); black letterboxing is
packaging, not part of the composition. Preserve native aspect while inspecting.
Original filenames, Library identities and SHA256 are in `manifest.json`.

Evidence hierarchy: the screenshot's blur values and the user's qualitative
requirements are exact; source-frame timing and appearance are observations;
degree values, ease exponents, particle simulation and adaptation to 1080×960
are authored reconstructions. No original editable AE project was supplied.
Do not claim exact recovered graph handles, rotation keys or particle settings.

## Observed choreography

| Source-local frames/time | Observation |
| --- | --- |
| 0–5 / 0–.167s | Five already-open concentric gradient fills and coherent white central identity |
| 6–13 / .20–.433s | Identity starts becoming discrete small fragments; its outline remains initially recognizable |
| 14–17 / .467–.567s | Increasing dispersal and swirl; circles/material rotate and grow faster |
| 18–20 / .60–.667s | Next scene appears through a soft central circular window; red remains toward edges; ordered dots appear over the incoming scene |
| 21 onward / .70s onward | Incoming scene dominates; floating fragments cross the handoff; ordered dots are cleared from the center outward |
| 26–29 / .867–.967s | Incoming scene settles, most regular dots are gone and fragments thin out |

Treat .70s as an authored full-coverage/takeover cue for this study, not proof
of a hard source-file edit at that instant. The reference visibly reveals the next
picture spatially before full takeover. In production bind the handoff to the
actual edit/cue; do not slip the presenter, source edit or audio to fit this study.

## Five-circle spin/zoom component

Keep exactly five filled concentric circles with alternating light/dark gradient
direction and fine edge highlights. Circular silhouettes alone do not make
rotation visible: rotate the gradient/material/highlight frame with the shapes.
Keep a stable center, depth order and coherent stack. Increase shared size during
the exit. Start rotation gently, then accelerate toward takeover; do not ease out
into the cut. A new shot may use the spin without particles or a scene change.

Study adaptation: radii190,325,460,600,770 in a1080×960 pane; normalized
`u=clamp((s-.06)/.64)`, `e=u^3`; clockwise material rotation0→170° and shared
scale1→1.58. These are starting values chosen for reconstruction, not original
AE numbers. Retarget the range and direction to the scene while preserving the
slow-to-fast character. Mask the outgoing stack fully before takeover.

## Glyph-to-particle component

Make particles originate from the actual icon/glyph silhouette, not an unrelated
radial emitter laid on top of a fading intact icon. Keep the identity readable at
first, detach small pieces progressively and let them float/swirl outward. Separate
fragment release, global drift, swirl and opacity. Keep some fragments crossing
the edit into the incoming scene; do not delete the cloud abruptly at the cut.
This is distinct from both the previous hollow-square burst and the regular grid.

`GlyphParticles` samples the supplied alpha at a3px lattice, selects up to1600
positions deterministically and staggers detachment over source .17–.47s.
Keep a solid alpha silhouette underneath until its small cells detach; the
starting identity must not already look like sparse points. Fragments are roughly
3–7px in this adaptation, white like the reference glyph.
Each travels from its glyph position with radial drift, increasing angular motion
and small floating offsets. The study starts thinning them at .82s and finishes
at1.14s so the final hold is clean. The extended cleanup is authored; the supplied
clip ends at1s. Retarget count, lifetime, texture/color and motion to the subject.
Use `--symbol` for other subjects; never keep Pinterest for an unrelated brand.

## Outgoing accelerating feather aperture

Use a circular soft-edged mask centered on the transition origin. It reveals the
incoming picture while clearing the old circles from the center outward. The old
stack outside the window may still spin and scale until it is completely covered.
It must leave **no circle residue** in the new scene after full takeover.

Keep an independent center, radius, feather, start, duration and curve. A useful
study curve is `E_in(u)=u^2.6`: slow start, increasingly fast end. Here it runs
source .56→.70s, with100px feather; the final radius exceeds the farthest pane
corner plus feather. `FeatherCircle.reveal(..., curve='in')` returns a clear-window
alpha, not a CSS blur applied to the whole scene. Composite
`old*(1-alpha)+incoming*alpha`. Do not accidentally invert this polarity.

Retarget the final radius to the actual pane and origin; do not stretch a mask
from a landscape source or leave unmasked corners. A pure mask can serve another
motivated handoff without an icon, circle stack or particle cloud.

## Incoming ordered dots and decelerating cleanup

Layer a regular, spatially stable point grid over the **incoming** picture; do not
confuse it with free-floating icon fragments. The dots become visible through the
outgoing aperture. Clear the dots themselves with another soft circular window
expanding from center: fast at first, then an extremely soft finish. Keep the
incoming photograph/UI underneath visible and unchanged by this cleanup.

Study grid pitch12px and dot radius1.4px, white with restrained opacity. Cleanup
uses `E_out(u)=1-(1-u)^4` from source .70→1.00s with100px feather. Apply
`dot_alpha *= 1-cleanup_alpha`; never use it to erase the new scene. Finish beyond
the farthest corner so no grid survives in the hold. Keep origin, pitch, radius,
opacity and cleanup timing independent. The grid may be used without a cut, and
the decelerating mask may clear another overlay instead of dots.

## Independent APIs and palette

`SpinZoomDiscs`, `GlyphParticles`, `FeatherCircle` and `RegularDotOverlay` are
independent tools. Use `--mode spin`, `particles`, `aperture`, `dots` or `mask` to
isolate them. The two masks use separate starts, durations and opposite easing
directions; do not force one shared curve. `combined` reproduces the optional
reference chain. Keep lower-panel camera transforms inside its clip rectangle.

Resolve color from explicit direction, then an attached icon's defining color,
then the video's brand, as described in `component-system.md`. Red is only this
source's example. Recolor the five fills and compatible highlights together.
Keep reference materials as optional variants; never force white backgrounds,
red, one entrance curve or this chain on all future videos.

The user explicitly allows additional useful observations from the reference.
Inspect and add supported details, labeling inferred numeric settings honestly.
Use the reference to resolve ambiguity while honoring the user's explicit design
requirements. Do not treat speculative project internals as observed facts.

## Motion blur, study and production

Native AE: enable both comp and moving-layer motion blur; set shutter180°,
phase0°, samples/frame16 and adaptive limit128 exactly as in the screenshot.
Include circle transforms/materials, mask edges, glyph pieces, dots/cleanup and
any scene camera. Code: evaluate actual subframe states and integrate RGB over
`[t,t+.5/fps]`, at least16 samples adapting up to128. Static blur, synthetic trails
or an export flag are not replacements. Do not integrate unrelated shots across
a hard source edit; reach full old-scene coverage first and preserve edit timing.

Run `python scripts/render_particle_handoff.py --output /task/new-test.mp4`.
Dependencies: Pillow, numpy, FFmpeg/ffprobe; no cv2 required for this renderer.
It renders1080×960,30fps,72frames,2.4s,silent with source time shifted by+.4s
and a final hold. It integrates all animated states and fully decodes the result.
This is a coded temporal equivalent, not a native AE run or an original particle
project. `--incoming` accepts the next-scene image for a study. For production
sample the actual next footage at each subframe while preserving source timing.

The bundled `incoming-scene.png` is a final-frame crop from the supplied source,
cover-fitted without stretching for the isolated study. It contains the source's
photograph/UI and residual image details; it is not an original clean plate, a
generation performed on Pinterest, or production content for an unrelated video.
Replace it and the symbol with the actual video's subjects. Do not claim narration
alignment for this silent, presenter-free study.

Inspect the actual rendered frames around first fragmentation, rapid spin,
initial incoming window, full coverage, remaining grid and clean final hold.
Keep the new study awaiting explicit user review; all approved older study bytes
must remain unchanged. Every teaching update needs a fresh test strictly under5s.
Save this full lesson, source MP4/PNG, derived study assets, script, manifest,
study and report in Skills and the GitHub mirror. Read back the published remote
tree and compare every file/blob; a push acknowledgement alone is insufficient.

## Persian requirement record

پنج دایرهٔ موجود آرام شروع به چرخش کنند و نزدیک کات به اوج سرعت برسند.
آیکون مرکزی به‌تدریج دانه‌دانه و پارتیکل شود و حالت شناور بگیرد. هم‌زمان با
چرخش و بزرگ‌شدن دایره‌ها، ماسک دایره‌ای با لبهٔ فید از مرکز باز شود؛ شروعش
نرم و پایانش سریع باشد و در لحظهٔ رفتن به پلان بعد کل صفحه را پوشش دهد تا
اثری از دایره‌ها نماند. روی پلان تازه، نقاط منظم با ماسک دایره‌ای فیدِ دیگری
از مرکز پاک شوند؛ این ماسک شروع بسیار سریع و پایان بسیار نرم دارد و تا حذف
کامل نقاط گسترش می‌یابد. ذرات آیکون و نقاط منظم دو جزء متفاوت‌اند.

رنگ نمونه الزام نیست؛ رنگ سازمانی ویدیو یا رنگ آیکونِ مرتبط مبنا قرار گیرد.
همهٔ اجزا می‌توانند مثل مرجع با هم اجرا شوند یا هرکدام جدا جای دیگری به کار
بروند؛ این مهم‌ترین اصل اسکیل است. همهٔ توضیحات و رفرنس‌ها با جزئیات بمانند.
هر زمینه، ورود، گراف و حرکت فقط یک ورژن قابل انتخاب است و نسخه‌های بعدی
کنار آن اضافه می‌شوند. انتخاب خلاقانه بر اساس نیاز شات انجام شود. مشاهده‌های
کمک‌کنندهٔ مستقیم از رفرنس نیز مجازند؛ مقادیر تخمینی از مقادیر واقعی جدا شوند.
موشن‌بلر کامپوزیشن و لایه‌های متحرک با۱۸۰/۰/۱۶/۱۲۸ روشن باشد. هر اصلاح آموزشی
تست تازهٔ کمتر از پنج ثانیه داشته باشد و نتیجه هم در اسکیل و هم GitHub ذخیره
و پس از انتشار بازخوانی و تطبیق داده شود.

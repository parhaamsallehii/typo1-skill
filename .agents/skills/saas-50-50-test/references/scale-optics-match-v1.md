# Scale/optics motion match cut — lesson 6

## Scope and independent tools
Extract only the supplied match cut, not the cursor or unrelated source effects. Apply it to shapes, images, footage or arbitrary objects. Compose the scale handoff, full-scene optics pulse, fast-box-blur pulse and incoming color sweep together or independently. Treat the reference as one useful option, never a global mandatory transition. Bind colors to requested brand or the linked icon; original colors/background are examples. Preserve prior lessons.

## Exact frame contract
Let C be the first frame of the incoming shot. Outgoing scale keys: C-15 and C. Incoming scale keys: C and C+15. Start outgoing extremely soft, accelerate into the cut; incoming starts at peak speed and settles extremely softly. Continue the same perceived deformation direction across the hard cut. Independently animate X and Y scale around a matched focal anchor. The user describes length decreasing and width increasing; in the example demo map the wide horizontal extent to decreasing X and the short extent to increasing Y. For rotated subjects map their local axes intentionally; do not silently replace anisotropic scale with uniform zoom. Preserve a matched on-screen bounding box/center at C across the two subjects; retain a hard picture edit, not a crossfade.

## Screenshot graphs — exact coordinates
Outgoing Flow graph: cubic-bezier(0.88,0.04,0.93,0.10).
Incoming Flow graph: cubic-bezier(0.06,0.88,0.10,0.95).
Solve Bezier x(t)=normalized time, then evaluate y(t). Do not use y(time) directly, generic Easy Ease,75/75 or100/100. These graph handles are directly supplied evidence, unlike inferred scale endpoints. Frames remain frames at the actual composition FPS;15 frames=.5s only at30fps.

## Whole-scene optics compensation pulse
Place an adjustment layer above all visual layers within the intended scene. Animate Optics Compensation so center compression/peripheral stretching peaks exactly at C, with the outgoing slow-to-fast and incoming fast-to-soft envelopes. Suggested pulse span C-15 through C+15; that span is an authored synchronization choice, not separately measured keys. Match the distortion direction visually, including reverse-lens-distortion behavior if needed. The reference and text do not specify exact field-of-view or center values; expose them and do not invent source settings. Use overscan/edge extension and inspect corners. In50/50 production scope this to the lower scene unless whole-frame treatment is explicitly requested.

## Separate fast box blur adjustment
Place a separate adjustment above all relevant scene layers. Amount=0 at C-4, peak approximately8 at C,0 at C+4; user gives8 as example intensity. Keep this spatial blur distinct from mandatory temporal motion blur. Match edge repeat and avoid dark frame edges. A linear triangular envelope is the coded study's authored choice; no original blur temporal handles supplied.

## Incoming20-frame moving colors
From C through C+20 move multiple color bands across the incoming object AND image, clipped to their actual alpha. Start on the incoming cut and end at the stable destination colors at C+20. Expose palette, blend mode, sweep direction, speed and amplitude. This is moving color treatment, not random whole-frame flicker. Do not impose reference red or other hues on future brand work.

## Motion blur and provenance
The supplied screenshot requires180-degree shutter, phase0,16 samples/frame and adaptive limit128. Enable native AE composition and moving-layer switches. For coded motion sample actual scene scale and lens transforms over[t,t+0.5/fps], minimum16 samples, adapt up to128 when necessary. Do not inherit the stronger720-degree override from the separate square-reaction lesson. Keep samples within their shot; do not dissolve old/new subjects across a hard cut.

Preserve all four original files in assets/variants/scale-optics-match-v1. Inspect the clip at native aspect and consecutive frames around the cut plus both graphs. The source contains a wide nature-backed UI followed by a centered portrait image with moving colors. Source project and exact optics values are unavailable. Coded lens distortion approximates Optics Compensation; Pillow BoxBlur approximates Fast Box Blur and procedural bands approximate color processing. Do not claim native plugin output or exact recovered project parameters.

## Five-second study
Exactly150 frames at30fps,1080x1920 output. C=75(2.5s); scale spans frames60..75 and75..90; blur71..75..79; color sweep75..95. SubjectA: horizontal input control. SubjectB: abstract colored artwork. Both share an anchor and matched250x200 internal bounding box at cut; internal540x960 rendering is upscaled2x, disclosed as such. Outgoing360x110→250x200; incoming250x200→190x310. Full-scene radial warp coefficient peaks.22; box blur output-equivalent8px. These endpoints and optics coefficient are authored demo values. Study awaits explicit approval.

## شرح کاربر
فقط مچ‌کات رفرنس استخراج شود. از۱۵ فریم قبل کات طول سوژه کم و عرض آن زیاد شود با گراف شروع فوق‌العاده نرم و پایان سریع. سوژهٔ پلان بعد از لحظهٔ کات تا۱۵ فریم بعد همان تغییر را با شروع سریع و پایان بسیار نرم ادامه دهد. ادجاستمنت Optics Compensation روی تمام لایه‌های صحنه در کات به اوج برسد و مرکز جمع و گوشه‌ها کشیده شوند. ادجاستمنت Fast Box Blur از۴ فریم قبل تا۴ فریم بعد با مقادیر۰، حدود۸ و۰ باشد. از کات تا۲۰ فریم بعد رنگ‌های متحرک روی شیپ و تصویر جدید دیده شوند. استفاده برای هر تصویر و آبجکت مجاز است. اجزا مستقل و قابل ترکیب باشند و رنگ‌ها با برند هماهنگ شوند. رفرنس‌ها و جزئیات حفظ، موشن‌بلر طبق تصویر و تست پنج‌ثانیه‌ای ارائه و در اسکیل و گیت‌هاب ذخیره شود.

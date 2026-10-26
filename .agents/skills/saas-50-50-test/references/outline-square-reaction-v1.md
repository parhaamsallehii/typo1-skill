# Hollow-square feathered click reaction — lesson 5

## Required appearance and timing
Use this independently reusable reaction on an icon, shape, card or another motivated event. Create a field of small squares with colored stroke and NO fill. Reveal the field from the impact point using a growing circular alpha matte with a broad feather. Start the radius very fast at impact and decelerate into a very soft long finish. Fade the square field opacity gradually to zero late in the reaction. Do not substitute filled dots, flying confetti, five discs or a solid expanding circle.

Keep the square field, radial matte and optional rounded-box clipping in a common local coordinate system. Parent their scene transforms consistently; animate matte radius separately so revealing does not force square sizes to inflate. Multiply square alpha by circular matte, optional box alpha and late opacity envelope. The reference confines the effect to the box; allow unclipped/free-space use elsewhere. Expose origin, start, duration, maximum radius, feather, square size, spacing, stroke width, palette, clipping and fade times independently.

A practical reconstructed curve is radius=R*(1-(1-u)^5), u clamped to 0..1. This is an authored approximation of fast-start/soft-finish motion, not recovered AE keyframes. Use feather smoothstep(clamp((radius-distance)/feather+0.5)). Start final fading around normalized time .55 and finish at1; adjust by visual comparison. Keep exact source evidence separate from these authored timing choices.

## Independence and colors
This lesson adds only the click reaction. Cursor, icon, background and surrounding UI are optional demonstration context, not mandatory dependencies. Combine this component with earlier lessons or use it alone. Bind stroke color to the clicked icon when appropriate, otherwise the requested brand palette. Reference red and nature background are optional variants, never global restrictions. Preserve all earlier lessons.

## Motion blur
Inspect the supplied PNG: shutter180 degrees, phase0, samples/frame16, adaptive limit128. In native After Effects enable comp and moving-layer motion-blur switches. In code integrate actual animated states over [t,t+0.5/fps] with at least16 temporal samples and adapt up to128 for rapid travel. Spatial feathering is distinct from temporal motion blur. The accompanying coded study temporally samples the expanding matte; it is not a native AE render.

## Reference and study
Inspect assets/variants/outline-square-reaction-v1/reference.mp4 and motion-blur-settings.png. Source shows a short click response within a pale input box over nature footage. Preserve the source bytes. Test requested here: exactly5 seconds,1080x1920, different background/colors/topic; use a focus-session UI with deep green/ochre palette. Keep the new study awaiting user review. Future tests retain the skill default unless overridden.

## درخواست کاربر به فارسی
واکنش کلیک روی آیکون یا شیپ: مربع‌های کوچک بدون فیل با استروک رنگی در محدودهٔ یک دایرهٔ فیدشده نمایان شوند. ماسک دایره‌ای از محل کلیک بزرگ شود؛ شروع بسیار سریع و پایان بسیار نرم و آرام باشد. اواخر حرکت، اوپاسیتی مربع‌ها تدریجاً صفر شود. نمونه داخل باکس محدود است اما استفادهٔ آزاد در جاهای دیگر مجاز است. هر جزء ابزار مستقلی است و ترکیب با اجزای دیگر اختیاری است. رنگ براساس برند یا آیکون انتخاب شود. همهٔ جزئیات و رفرنس حفظ شوند. موشن‌بلر مطابق تصویر روشن باشد. تست این پیام دقیقاً پنج ثانیه و۱۰۸۰×۱۹۲۰ با موضوع و رنگ‌بندی متفاوت باشد. ثبت در اسکیل و گیت‌هاب الزامی است.

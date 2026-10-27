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

## Revision 2 — latest user correction, overrides broad first study
The user rejected the first study's small/sparse squares and full-box spread. Prefer larger, denser hollow squares with strong Deep Glow-style colored halos. Keep the reaction in a soft circular neighborhood around the icon; never fill the whole box. Use a closer camera framing. Preserve the empty square interiors structurally; glow may spill softly into them. Keep a sharp stroke core plus narrow and broad colored halos. Radius must be constrained relative to icon size, independently of container width.

Current coded study: square side16, pitch20, stroke2 in source coordinates; 2x close framing makes side32 and pitch40 output pixels. Radius145 source pixels around the icon, feather65; this affects only a local portion of the910px box. Use two glow scales sigma3 and12, gains1.5 and1.8, screen-composited in the accent family. These are authored reconstruction values, not original AE settings.

The user explicitly requests much stronger motion blur for this revision. Apply a local override of shutter720 degrees, phase0,64 temporal samples with adaptive limit128, integrating [t,t+2/fps]. This overrides180 degrees only for this reaction study; other lessons keep their existing settings. In native AE a comparable stronger shutter is a starting recipe; the coded glow is an approximation of Deep Glow, not that plugin. Do not claim increasing sample count alone increases blur length.

Study v2: exactly5s,1080x1920, same focus-session subject and green/ochre palette, close camera. Retain the first study as rejected/superseded history; use study-v2.mp4 as the current candidate, awaiting explicit review.

اصلاح کاربر: مربع‌ها بزرگ‌تر و شلوغ‌تر، با دیپ‌گلو؛ اثر فقط اطراف آیکون بماند و کل باکس را پر نکند. اجرا زوم‌تر و موشن‌بلر بسیار بیشتر باشد. این اصلاح بر نمونهٔ اول اولویت دارد و رنگ‌ها و اجزا همچنان مستقل و قابل تغییرند.

## Revision 3 — nested multiscale green study (latest)
Override revision2's uniform grid. Use overlapping square groups with mixed large/small sizes and smaller hollow squares nested inside larger ones. Keep colored strokes and empty fills; distribute centers with slight deterministic irregularity. Retain a local feathered circle around the icon, fast initial expansion, long soft finish and late fade. Preserve close camera and revision2 stronger temporal blur. Increase colored glow while preserving discernible square cores. Green is the requested study palette, not a universal brand restriction.

Current study implementation: seed57; center pitch34 source pixels with +/-10px jitter; outer sizes24/32/42/54; nested ratios1/.55/.24; stroke2. Output camera2x. Glow uses sigma3/12/24 at gains2.5/3.4/1.8. Stroke RGB50,245,110 and glow RGB65,255,125; icon green. Keep radius145 and feather65 source units and the720-degree phase0 64-sample local override. Values are authored fits. Render exactly5s at1080x1920. study-v3.mp4 is the latest candidate awaiting review; revision2 remains prior history, not approved.

اصلاح سوم کاربر: مربع‌ها توهم‌توهم و تودرتو با اندازه‌های بزرگ و کوچک باشند، گلو بیشتر شود و تست با رنگ سبز ارائه شود. سایر خواسته‌های قبلی شامل محدودماندن دور آیکون، نمای نزدیک، محوشدن تدریجی و بلر بیشتر حفظ شوند.

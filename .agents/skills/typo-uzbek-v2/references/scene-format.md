# ساخت scene JSON

فرمان: `python scripts/render.py /absolute/scene.json --output /absolute/result.mp4`؛ با پایتونی اجرا کن که requirements.txt و RAQM دارد.

از presenter-scene.json نمونه بگیر. کلیدهای لازم: width,height,fps,duration,background,speech_evidence,events. background مسیر فایل ویدیو نسبت به JSON یا مسیر مطلق است؛ اندازه و FPS باید عین منبع باشند. duration شمار فریم تقسیم بر FPS است.

هر event شامل start،words،close_start و close_duration است. words به ترتیب زمان، هر کدام text,start,end,row(0/1/2),accent(boolean),source_index دارند. هر سه ردیف لازم‌اند؛ ردیف اول یک کلمه accent دارد. center_x و row_y قابل تنظیم نسبی‌اند. رویدادها نباید هم‌پوشانی داشته باشند.

برای گفتار واقعی، speech_evidence مسیر JSON شامل source_sha256 و words است. هر word متن دقیق با text,start_seconds,end_seconds دارد. source_index شاخص صفرمبنا به همین آرایه است. متن و زمان‌های scene باید دقیقاً با شواهد یکسان باشند. method و service_url را برای قابلیت پیگیری نگه دار. ASR را بازبینی کن؛ اعتماد صددرصدی به آن ادعا نشود. source_sha256 از بایت‌های فایل واقعی گرفته می‌شود.

برای نمونهٔ بی‌صدای مستقل می‌توان demo:true و background:"#24101b" گذاشت؛ speech_evidence وsource_index لازم نیستند، بقیهٔ ساختار و زمان‌ها لازم‌اند. چنین خروجی را تست همگام با صحبت معرفی نکن.

رندر report.json مجاور خروجی می‌نویسد: کلمات، زمان خروج، تنظیمات و دامنهٔ نمونه‌های بلور. ویدیو و AAC منبع بدون تغییر مدت کپی می‌شوند. شواهد تست همراه از ASR ماشینی فایل اصلی خانم گرفته شده؛ عبارت نمونه «تمام این ویدیویی که دارید می‌بینید» است.

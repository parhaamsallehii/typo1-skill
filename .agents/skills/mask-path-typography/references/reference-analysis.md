# Supplied animation

- `media/animation.mp4`: original, 1080×1920, 30 fps, approximately 5.033 s.
- Two uploaded MP4s have identical SHA-256. The original bytes are bundled as binary parts to fit transfer limits. Run `python scripts/prepare_reference.py`; it verifies and concatenates them into the original MP4 without re-encoding. Both names are retained in the manifest.
- First red word enters from the right, baseline/orientation following a shallow curve. Next cream line enters from the left; a third line follows.
- Third reference line is green. Written palette takes priority: use red/cream here.
- Inspect approximately 0.1–0.4 s for curve movement/blur, 0.6–0.9 s for opposite entry and 2.5 s for settled layout. These are observation windows, not recovered keyframes.
- Settled words are compact and stacked, with angular Persian shapes, fine texture and hard offset shadow. Guide path is invisible. No handwriting stroke reveal.
- A baked MP4 does not expose mask handles, First Margin values, easing graph or plugin internals. Preserve explicit numerical settings and compare visually for remaining choices.

```bash
ffmpeg -ss 0.2 -i references/media/animation.mp4 -frames:v 1 reference-entrance.png
ffmpeg -ss 2.5 -i references/media/animation.mp4 -frames:v 1 reference-settled.png
```

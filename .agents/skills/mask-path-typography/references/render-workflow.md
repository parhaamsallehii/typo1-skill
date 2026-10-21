# Rendering

Use Python with RAQM-enabled Pillow, numpy, scipy, fonttools and FFmpeg. Dependencies are in `scripts/requirements.txt`. Prefer existing runtime dependencies. Do not substitute fonts or disconnect letters to work around missing shaping.

From the skill folder:

```bash
python scripts/render_path_type.py --check
python scripts/render_path_type.py --scene assets/example-scene.json --out /absolute/task/settled.png --still 4
python scripts/render_path_type.py --scene assets/example-scene.json --out /absolute/task/entrance.png --still 0.2
python scripts/render_path_type.py --scene assets/example-scene.json --out /absolute/task/preview.mp4
```

Append `--width 540` for a smaller design preview; it preserves effects and timing. Deliver requested resolution. Copy/edit the example scene into the task folder rather than modifying canonical assets. Re-render representative output after changing code. Judge blur on moving frames as well as the hold.

## Verification

- Check actual fonts, Persian joins, half-spaces and dots.
- Check curved movement and entry from both sides, not a flat slide over a decorative curve.
- Inspect just before/after arrival, peak overshoot and final settling. No position jump or abrupt cutoff. A vanishing incoming velocity is not a strong spring.
- Inspect source colors, fixed grain, hard shadow and diffuse glow.
- Moving frames must differ from a single instantaneous sample; stationary frames must not retain trails.
- Watch beginning, middle and end; fully decode and check metadata:

```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate,codec_name:format=duration,size -of json /absolute/task/preview.mp4
ffmpeg -v error -i /absolute/task/preview.mp4 -f null -
```

The `.render.json` sidecar records actual settings, sample counts, timing and approximation status. It does not prove exact AE equivalence.

## Formats and limits

Bundled output is opaque PNG or H.264 MP4. A PNG with black background is not an alpha overlay. If alpha is required, extend for premultiplied RGBA and use alpha-capable MOV or a PNG sequence; check over light/dark backgrounds. Exact Screen glow over arbitrary footage may need a separate glow pass/editor compositing.

The reference has no speech. Do not claim speech alignment. For video integration, preserve source dimensions/timebase/audio and add an explicit compositor. This renderer alone does not import footage.

The code uses a shaped ribbon and arc-length spline, not AE itself. Native font placement, adaptive sampling and Deep Glow internals remain engine-dependent.

# Scene schema

Start from `assets/example-scene.json`. Geometry uses a 1080-wide reference coordinate space and scales by output width/1080. Seconds do not scale. For another aspect ratio, explicitly recompose vertical positions.

| Scene field | Meaning |
|---|---|
| `width`, `height` | Positive even output pixel dimensions |
| `fps` | Output frame rate; default 30 |
| `duration` | Seconds |
| `background` | Opaque preview color; black follows reference video |
| `motion_blur` | Must be true |
| `layers` | Bottom-to-top layer order |

| Layer field | Meaning |
|---|---|
| `text` | Exact single-line text; preserve Unicode |
| `font` | bahman, e-bahman, lifta-black or lifta-bold |
| `font_size` | Reference pixel em size |
| `style` | red or cream, with opposite-color shadow |
| `path` | At least three [x,y] points, strictly increasing x; natural C2 spline |
| `center_x` | Final center by arc length, default 540 |
| `target_margin_offset` | Additional signed distance, default 0 |
| `travel` | Start margin minus target; positive from right, negative from left; default 900 |
| `start` | Start seconds, default 0 |
| `start_frame` | Ordinal first key, default 1 |
| `arrival_frame` | Ordinal second key, default 15; must exceed first |
| `profile` | linear or spring-entry (default) |
| `spring` | amp, freq, decay, duration, fade_duration, optional max_offset |
| `motion_blur` | true; missing also means mandatory true |
| `texture_pitch` | Reference-pixel dot pitch, default 4 |
| `texture_strength` | Default 1 |
| `seed` | Fixed texture seed input, default 7 |

Arrival = `start + (arrival_frame-start_frame)/fps`. Leave time for the final layer's 1 s spring plus a readable hold. Extend control points beyond both edges by at least one text width. Shallow arches, bowls and S paths are supported when x increases and curvature remains gentle.

Do not add unsupported keys and assume they work. The bundled renderer does not transcribe audio, import footage, export alpha, animate individual glyphs, or animate control points. Extend and validate the pipeline when required.

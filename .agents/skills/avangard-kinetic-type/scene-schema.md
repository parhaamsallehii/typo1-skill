# Scene schema

Pass UTF-8 JSON to `scripts/render_type.py`. Copy `assets/example-scene.json` as a starting scene. Explicit word geometry is in output pixels; style effect defaults scale from reference width 1080.

| Field | Default | Meaning |
|---|---|---|
| width, height | 1080, 1920 | Output dimensions; MP4 requires even numbers |
| fps, duration | 30, 3.2 | Frame rate and seconds |
| background | beige | Palette name, hex, or transparent |
| layout | block | block or expressive |
| start | 0.2 | First automatic word onset, seconds |
| text | none | Text; newline defines lines |
| lines | none | Deliberate line layout |
| words | none | Explicit words, replacing line layout |
| style | bundled defaults | Recursively merged partial overrides |

Supply exactly one of text, lines, or words. Do not use a source video's path as background; composite separately.

## Lines

Each line has text, optional font (block/expressive), color (palette name/hex), width (0.1–1 fraction of the available title width), align (left/center/right), and rotation in degrees (positive is counterclockwise in Pillow). The renderer fits font sizes, sets baselines, and freezes all positions. Use both fonts in a multiword title; never force a font change within a connected word.

## Explicit words

Use for custom scale, diagonal arrangements, or mixed fonts on one line:

```json
{
  "width": 1080, "height": 1920, "fps": 30, "duration": 3,
  "background": "transparent",
  "words": [
    {"text": "آینده", "font": "expressive", "color": "red", "size": 210,
     "x": 680, "y": 760, "start": 0.2, "rotation": 3},
    {"text": "را", "font": "block", "color": "beige", "size": 110,
     "x": 280, "y": 810, "start": 0.32},
    {"text": "بساز", "font": "block", "color": "beige", "size": 240,
     "x": 540, "y": 1100, "start": 0.44}
  ]
}
```

x/y are final centers of unrotated visible glyph bounds; size is font size. Optional entrance overrides duration; optional end hides the word at that scene-local time. End cannot precede entrance completion. The list sets reading/reveal order; coordinates do not sort words. Placement is a design choice, not measured from the posters.

## Overrides

```json
{"style": {
  "layout": {"center_y": 0.70, "safe_width": 0.78},
  "entrance": {"duration": 0.45, "stagger": 0.10},
  "hand_drawn": {"amplitude": 0.5}
}}
```

Do not alter requested numeric effects/colors without a user instruction. Inspect the result in the real video-safe area.

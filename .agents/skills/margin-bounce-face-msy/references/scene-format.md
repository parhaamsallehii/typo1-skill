# Coded scene format

Use output-pixel coordinates. Provide a same-size still or video background. The renderer does not crop/stretch the presenter. Relative background paths resolve next to the scene JSON. Use two layers with independently verified speech cues; each path is exactly four cubic Bezier control points, in baseline direction. Bundled fonts: `saadi`, `saadi-bold`, `saadi-ultra`, `lifta-black`, `lifta-bold`. Colors: `cream`, `red` only. `font_size`, `target_offset` and paths are authored for the actual frame. Long phrases must be redivided rather than squeezed.

```json
{
  "width":1080,"height":1920,"fps":30,"duration":5,
  "background":"source.mp4",
  "speech_evidence":{"file":"verified-words.json","method":"actual audio review or named real recognizer"},
  "layers":[
    {"text":"عبارت اول","speech_verified":true,"start":1.0,
     "font":"saadi-ultra","font_size":130,"color":"cream",
     "path":[[360,1060],[220,900],[240,650],[310,480]],
     "entry_margin":35,"exit_margin":35,"hold":1.0},
    {"text":"عبارت دوم","speech_verified":true,"start":1.3,
     "font":"lifta-black","font_size":130,"color":"red",
     "path":[[740,550],[790,690],[760,900],[660,1000]],
     "entry_margin":-35,"exit_margin":-35,"hold":1.0}
  ]
}
```

This is a schema illustration, not a timed transcript. Never copy `speech_verified:true` without verifying the words. The renderer checks the presence of evidence metadata and flags but cannot establish its truth, semantic timing or visual head clearance. Audit those independently. For authored silent tests, set `demo:true` and label them as illustrative. Optional `exit_start` is absolute seconds and replaces the one-second hold calculation; use only for explicit user timing or documented speech adaptation. Keep the raw reference clip's duration distinct from a default hold preview.

The script preserves source audio by muxing original audio streams into the render up to the scene duration. Set scene duration and FPS from ffprobe for production. It does not automatically retime cues after cuts: supply cues on the final source timeline. A static background preview has no speech and no proof of spoken-word matching.

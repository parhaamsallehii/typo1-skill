# Supplied reference observations

## Evidence and limits

Inspect the supplied files themselves. Video: 1080×1920, 30fps, exactly 36 frames / 1.2s, with AAC audio. All 36 frames were extracted and inspected in sequence and selected entrance/exit frames were enlarged during authoring. The long-form original composition, editable masks and AE keyframes were not provided. Do not pretend to have measured exact original First Margin values, interpolation, font weight or mask control points from this flattened video. No automatic transcription was run during authoring; don't treat guessed reference words as a verified transcript.

## Visible composition

The subject is centered, head roughly x360..710 and y500..1040, with room on either side. The uploaded placement still is the clearest guide. Cream text occupies approximately x220..370,y480..1030; red occupies approximately x650..815,y555..990. These are visual estimates including glyph extents, not safety masks or exact paths. The text bends around the head's vertical axis with open side bows. The two sides differ in height, curvature and length. The text is flat, bold, joined Persian, cream and crimson. There is no visible decorative text texture, external glow, outline or shadow. The red background, scarf, plant, microphone and wood figure belong to source footage and are not skill assets to paste into new user footage.

## Frame observations (zero based)

- Frame 0: neither phrase visibly present.
- Frames 1..3: cream text enters image-left, faint/blurred and displaced.
- Frames 4..8: cream becomes clear with visible travel/settling on its bowed path.
- Frames 9..12: red text becomes visible image-right while cream remains; a short sequential stagger is visible, approximately 0.27..0.33s after the first onset, but speech must determine future stagger.
- Frames 12..17: coexistence; path text remains side-facing, not a horizontal line over the forehead.
- Frames 18..20: cream exits with visible temporal streaking; by frame 21 it is absent.
- Frames 21..24: red exits later; by about frame 25 it is absent.
- Frames 25..35: neither phrase remains visible.

These boundaries are visual estimates affected by fade/blur and compression. This excerpt's visible residence is shorter than the user's one-second default hold. Preserve two distinct profiles: use the requested timing table by default; use a reference-matching shortened hold only when the user asks for the excerpt's timing. Never silently shorten the default hold and call it identical.

## Transfer geometry

Author a new rig from actual head bounds for every shot. At this source's scale, useful starting cubic baseline guesses are left bottom-to-top `[[360,1060],[220,900],[240,650],[310,480]]` and right top-to-bottom `[[740,550],[790,690],[760,900],[660,1000]]`. These are authored starting points, NOT extracted masks. Orient to keep glyph ink outward. Adjust baseline, font size and path length together while preserving the clear face corridor; do not stretch letters to fill a path. Zoomed/cropped footage needs remeasured paths.

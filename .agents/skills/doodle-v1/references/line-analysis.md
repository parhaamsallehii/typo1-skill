# Line-only reference analysis

## Source facts

The uploaded `نمونه خط doodle ورژن 1.mp4` is 1080×1920, 30fps, 24 frames and 0.8s with audio. Active picture approximately 1080×816 at y552, leaving black padding. All 24 frames were extracted; the contact sheet and enlarged line-bearing active frames were inspected. The skill intentionally learns no reference lettering, portrait design, red/orange palette, UI blocks, source labels, picture transitions or camera style. The turquoise handwritten-looking words are text, not the requested thin doodle strokes.

## Time observations, zero-based frame indices

| Frames | Thin-line evidence |
|---|---|
| 0–2 | No clear decorative thin doodle bundle; bright rectangular shapes are unrelated. |
| 3–4 | Small narrow wavy marks appear at image-right. |
| 5–8 | Approximately four long, off-white strands span part of the active image, with unequal lengths and spacing. Their broad curves are uneven; some moving portions are directionally soft. |
| 9 | Travelling strands and the arriving subject region overlap briefly; line fragments do not establish that the whole bundle morphs into a silhouette. |
| 10–12 | Several separated thin contours follow selected crown, profile/back-of-head, neck and shoulder sections. Gaps remain. |
| 13–17 | Thin outline accents persist/change around the subject while unrelated writing appears. Line geometry changes between frames. The user explicitly corrected the initial interpretation: use one-frame drawing flashes separated by fully blank frames, changing shape and screen region each time; roughness must be very light. |
| 18–23 | Some contour fragments remain while large typography changes; only the narrow contour strokes belong to this skill. |

These are visual observations from flattened, compressed footage. They do not establish exact vector shape, procedural noise, trim values, stroke width, shutter angle, hold cadence or plugin name. Do not claim native-source settings were recovered. There is no evidence that every stroke must draw itself on tip-first, make a full closed loop, or always orbit a face.

## Geometry and appearance

The travelling bundle combines broad nearly horizontal waves with gentle concave/convex bends and different lengths. In the still at frame 7, visible strands occupy roughly x290..1040 and y790..1055 in the padded 1080×1920 reference. Do not scale these y positions as if the active image were full-height. The contours at frame 15 are broken paths, including an isolated crown fragment, a profile fragment, a neck fragment and a shoulder fragment. At this width the sharp core is a few pixels across, with subtle irregular edge/pressure. Some source grain is visible; global texture is outside scope.

`assets/reference-guides.json` stores manually approximated points for these line shapes, including original padded coordinates. It is a guide to line geometry, not an automatic silhouette extractor, exact tracing or compositing mask. Keep guides separate from new-scene authored paths. The default near-white color and renderer parameters are proposed matches; user review should refine them if necessary.

## Adaptation rules

On a different subject, preserve the thinness, controlled imperfect edge and coherent motion, but redraw paths to its actual bounds. For text, treat the text block's contour/negative space as the target rather than tracing individual letters into illegibility. For a presenter, use short fragments outside selected edges. For a product, follow the object where it helps emphasis. For free accents, place an irregular bundle in a motivated direction. Keep the original image untouched and never add a fake rim-light silhouette as a substitute for actual paths.

## Authoritative latest clarification

Every drawing is a ONE-frame flash, followed by a completely empty rest frame, then a different shape in a different screen region. Local hand roughness must be even lighter. This supersedes all prior continuously visible redraw/relocation recipes. The original source is preserved for line appearance only; latest user instructions define the mandatory on/off cadence and placement changes.

## Purposeful placement refinement

The user approved the alternating flash/rest cadence, then required marks to land approximately on actual objects, the presenter, existing text or graphic shapes. Replace arbitrary empty-region placement with target-aware accents. Every flash remains one frame and each rest remains completely blank; very light roughness is unchanged.

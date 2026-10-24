# Native point stabilization

Use this workflow only when a usable After Effects host is available.

1. Isolate the original presenter reversibly. Preserve the rest of the timeline and
   map composition time to trimmed/remapped source time before tracking.
2. Choose **Tracker → Stabilize Motion**, Position enabled, Rotation/Scale disabled.
   Fit a feature region around a clear nostril or stable facial detail and put the
   attach point on it. Fit the search region to real inter-frame movement.
3. Analyze the shot interval at Full resolution/Best quality with subpixel positioning.
   Correct drift from the last good frame. Do not track across edits or occlusions.
4. Apply **X and Y** to the tracked layer. Confirm inverse compensation locks the
   selected point to its first composition position. AE may animate Anchor Point;
   do not apply a second inverse translation on Position.
5. Isolate the active interval using presenter segments or a gated transform. Otherwise
   tracking keys keep holding/extrapolating outside the interval. Preserve original
   footage, audio and shot duration; do not add boundary animation unless requested.
6. Add measured constant overscan around the lock point, or reflected Motion Tile
   extension **before** the compensating transform. Enable Mirror Edges, set sufficient
   Output Width/Height, and inspect clipping at precomp boundaries. Calculate extents
   from actual motion rather than a fixed percentage.
7. Enable blur on the moving presenter layer(s) and composition master switch:

   | Setting | Required value |
   |---|---:|
   | Shutter Angle | 180° |
   | Shutter Phase | 0° |
   | Samples Per Frame | 16 |
   | Adaptive Sample Limit | 128 |

   Match `../assets/motion-blur-settings.png`. Phase 0 is explicit; do not replace it
   with -90°, which is sometimes recommended for centered attachment blur.
8. Scrub and render with the other layers visible. Confirm independent foreground,
   face lock, no exposed borders and blur only from intended motion. Preserve audio.

Primary reference consulted:
https://helpx.adobe.com/uk/after-effects/desktop/animate-in-after-effects/track-motion/tracking-stabilizing-motion-cs5.html

Adobe distinguishes tracking another layer from stabilizing the source using opposite
motion. One point supports position; scale/rotation use two points. Use the user's
actual screenshot for blur values and the supplied clip for the visual target.

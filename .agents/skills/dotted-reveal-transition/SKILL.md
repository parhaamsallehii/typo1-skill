---
name: dotted-reveal-transition
description: >-
  Apply the user's approved dotted circular reveal exactly like dotted-reveal-test.mp4: a fixed halftone dot grid, growing clear circular window, bright irregular dotted rim, thin outline and two white hand cursors moving outward on opposite diagonal edges. Use for dotted reveal transition, dotted-reveal-transition, ترنزیشن نقطه‌ای, افکت نقطه‌ای با دو موس, بازشدن دایره هافتون or the approved circle-and-hands effect. Reveal the same live video over 43/30 seconds by default, preserve the exact bundled renderer, cursor artwork, appearance and motion, and keep source audio and timing. Do not substitute a different transition or add camera/subtitle/watermark edits.
---

# Dotted Reveal Transition

Reproduce the **user-approved rendered test**, not a new interpretation of the earlier inspiration video. Apply the effect to the supplied clip/scene, with the existing frame playing continuously underneath. Respond concisely in Persian.

## Canonical approved resources

Resolve paths relative to this SKILL.md:

- `scripts/render_dotted_reveal.py`: byte-for-byte copy of the renderer that created the approved test. SHA-256 `a52d6d0fca0e5c06ab12a7a4fdef43edd106ec02fe183bc5834aa05ebabd5b60`.
- `assets/approved-example.mp4`: the actual approved 1080×1920, 30fps, 104-frame test on «هوک تستی.mp4», copied unchanged from `dotted-reveal-test.mp4`. SHA-256 `4d1ab6d9f346880464df75b2b18dfba262d69135f1a51792e77e1b41dd385810`.
- `assets/approved-preset.json`: renderer/example hashes, exact settings and provenance. It documents constants embedded in the renderer; it is not an automatically loaded configuration file.

Inspect the approved example when applying this style. Keep the canonical source, sample and preset unchanged for one-off work. Validate their hashes before calling a different implementation an exact reproduction. The example is a visual reference, never footage to overlay into another person's video. Do not substitute the earlier external inspiration for the version the user explicitly approved.

## Approved behavior

1. Start the effect at the clip/scene beginning, t=0, unless the user explicitly chooses another time. Use `43/30 = 1.4333333333 seconds` as the default effect duration, independent of input frame rate. The full video continues afterward with no effect.
2. Show a fixed screen-space grid of round dots over the playing image. Outside a small central clear window, soften and darken the live image using the existing code. Let the dots' opacity respond to image luminance; preserve the warm light dot color and the bright dotted boundary.
3. Grow the clear circular window quickly and continuously outward. Its center stays at `(0.5W,0.49H)`; its initial radius is `78*(W/1080)` pixels. Use the approved `u**0.52` radius profile and final radius equal to the farthest corner distance plus `35*(W/1080)`. Preserve the slight irregularity of the dotted bright rim and the thin smooth guide outline.
4. Keep grid centers fixed while the window grows. Grid pitch is `20*(W/1080)` and dot radius `7.2*(W/1080)`. This is a live masked halftone reveal; do not turn it into randomly flying particles, a solid circle or a new background image.
5. Show the **same two vector hand-cursor designs** embedded in the renderer, with the approved near-white fill, dark outline and finger/cuff details. At reference width their visible maximum size is 92 px. Keep rotations −45° and 135°. Position them on the lower-left and upper-right boundary, at center ± radius/√2. They stay attached to the opening circle, move outward together and leave the frame naturally. Their own size stays constant as the circle grows.
6. Preserve the renderer's 16 midpoint samples across a forward half-frame exposure. This temporally softens the moving mask/rim/cursors while the current video frame remains live and otherwise unchanged. Retain the actual existing color/compositing pipeline; do not silently add a new gamma conversion, global blur or camera motion.
7. At the effect end, return the clean current video frame and continue the clip with its existing timing/audio. Do not freeze the source image, add a text title, add sound effects or change the edit duration.

Preserve all numeric defaults from `approved-preset.json` and the code, including exterior blur 2.4 reference pixels, outside multiplier .69, dot-opacity formula, highlight strength and cursor alpha compositing. Do not replace the approved quick opening with 75/75 easing, a spring, body-zoom or hook-zoom-out merely because those other skills exist.

The approved mode reveals **the same video** from dotted treatment to clear image. Despite the word “transition” in the name, it does not currently blend outgoing and incoming shots. Build an A/B transition only if explicitly requested as a separate variation; do not claim that the current renderer supports two-source footage.

## Execute the exact renderer

Require Python with NumPy and Pillow, plus FFmpeg/ffprobe. Hand cursors are code-native and require no font, image generator, AE plugin or external asset. Use the existing dependencies when available.

```bash
python scripts/render_dotted_reveal.py --input /task/source.mp4 --out /task/dotted-reveal.mp4
python scripts/render_dotted_reveal.py --input /task/source.mp4 --out /task/check.png --still 0.2
```

- Use a distinct task output path. The canonical CLI does not guard same-input/output use; never pass the original source as `--out` or overwrite user footage.
- The CLI defaults to width 1080 and maintains the input display aspect ratio, reading the actual average frame rate. Pass `--width 2160` explicitly for a requested 2160-wide result, or the actual input width to preserve a different input resolution. All geometric values scale with width. The reference is 9:16; inspect another aspect ratio instead of claiming the framing is identical.
- Use even output dimensions for H.264/YUV420p, and normalize orientation/pixel aspect/VFR where necessary. Preserve timing/audio during normalization. Do not silently crop or stretch the source.
- For a clip shorter than 43/30 seconds, the approved CLI already uses `min(43/30,source_duration)` and completes the reveal within that clip. Keep this existing short-clip behavior unless the user explicitly asks otherwise, and report the shorter applied duration.
- The CLI stream-copies original audio into the chosen output container and encodes video with H.264 CRF 17, preset fast, YUV420p and faststart. Choose a compatible container/audio path if necessary; never silently drop sound.
- It renders and validates the full clip, including the unmodified visual portion after the reveal; it does not only export the 1.43-second effect.
- Preserve the exact approved class/renderer for default use. For a user-requested timing/location variation, work on a task copy or integrate `DottedReveal`, and disclose only the intentional changes. Do not edit the frozen skill for each clip.

## Integrate in an existing edit

For each frame of a selected live clip/scene, use the already-composed frame at that time. Construct `DottedReveal(width,height,duration,fps)`, then call `render(frame,local_t)` only while `0 <= local_t < duration`. Outside the chosen interval return the current scene frame unchanged. For a requested start `S`, use `local_t=timeline_time−S`; the standalone CLI always begins at zero and has no `--start` argument.

Apply the effect once to the intended whole visual input. Keep the cursor layer above the treatment. Do not reuse an affected previous frame as the next source or stamp the approved example over the new video. Do not automatically invoke any typography, subtitle, ramp, watermark or camera skill; preserve already-authorized elements and their edit timing. If a separate camera pass is explicitly requested, integrate it once in the existing render order instead of changing this reveal's approved constants.

The output is an opaque composited video with source audio, not an alpha-only overlay or native After Effects project. No layer parenting structure from the external reference was recovered or is needed to reproduce this approved coded implementation.

## Verify before delivery

1. Verify the renderer/example hash against the manifest. Check the canonical renderer still matches the approved source file; avoid copying an earlier preview version with the smaller hand icons or stronger uniform dot opacity.
2. Check actual input dimensions, aspect ratio, frame rate and duration, and confirm the output is distinct from source.
3. Inspect beginning, early expansion, mid-reveal, the last affected frame and a clean frame after completion. Confirm live source playback, fixed grid, exact cursor design/size/directions and the approved rim/outline.
4. Check repeated rendering/seeking at one time is deterministic. Confirm the clear video remains unchanged after the effect end before output encoding.
5. Fully decode the exported file. Verify frame count, duration, dimensions and frame rate; compare copied audio payload hashes when feasible. Preserve the original clip.
6. Save/deliver the actual rendered video through the supported artifact channel. Report only the rendering and checks performed. Treat an unsupported two-shot variation as new work rather than claiming the approved default already implements it.

Example invocation: «با اسکیل dotted-reveal-transition همین افکت تأییدشده را اول ویدیوم اجرا کن.»

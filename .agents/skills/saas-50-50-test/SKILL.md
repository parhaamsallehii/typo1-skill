---
name: saas-50-50-test
description: >-
  Automatically split presenter-led video into an exact top/bottom 50/50 layout:
  original presenter above, SaaS product-motion matched to the actual narration
  below. Use for saas 50.50 test, saas-50-50-test, SaaS 50/50, موشن ساس نصف صفحه
  or مجری بالا موشن پایین. Inspect the three bundled video references before
  each use. Match their bright white/glass UI, soft shadows, gradient accents,
  cursor-led interactions, perspective camera moves, word emphasis and card fans.
  Preserve presenter/audio timing and verify speech cues; do not invent alignment.
---

# SaaS 50.50 Test

Create two equal horizontal panes. Put the original main talking-head presenter
in the **top** pane and narration-specific SaaS animation in the **bottom** pane.
Use the user's exact wording “saas 50.50 test” as an invocation alias.

## Inspect references actively, every time

Do this before authoring, even if this skill was used earlier:

1. Open all three videos in `assets/references/reference-1.mp4` through
   `reference-3.mp4`. Use `manifest.json` there to confirm names, native aspect,
   durations and hashes. The originals are bundled unchanged.
2. Extract and inspect beginning/middle/end frames at their **native aspect ratio**.
   Add a dense frame strip around a camera move or UI interaction. Do not stretch
   a landscape reference into a portrait contact sheet. Inspect temporal change,
   not just a single attractive screenshot.
3. Read `references/style-and-motion.md`. Select the matching reference motif for
   each narration beat. Preserve the reference's visual language when changing
   subject, text and assets. Do not reuse its unrelated travel/shopping/Pinterest
   footage as the lower panel's content.
4. After rendering, compare the new motion to the references at comparable beats.
   Record the actual inspected frames/moves. Never claim the references were
   watched solely because their filenames appeared in this document.

## Lock the layout

- Default to the input's portrait delivery size, normally **1080×1920**. Top pane:
  `(0,0,1080,960)`. Bottom pane: `(0,960,1080,960)`. At 2160×3840, each is
  2160×1920. Use an even width and a total height divisible by four for YUV420.
- Keep the split exactly at `H/2`; include no extra-height divider, black band or
  gap. Clip every lower-panel layer to its pane. Keep lower camera moves from
  shifting/scaling the presenter or changing the 50/50 boundary.
- Fit presenter footage with uniform cover scaling and an inspected crop that
  retains the face, headroom and essential gesture. Do not stretch faces. Select
  crop/focal coordinates from the actual shot; helper defaults are starting points.
- Re-layout the motion for `W×H/2`. Never squash a 16:9 composition into that pane
  or crop off UI text. A full-screen test may use a different aspect only when
  explicitly requested; production still needs the proper panel layout.
- Apply to the requested interval, or all eligible main-presenter shots if no
  interval is supplied. Do not cross edits with one camera/cue solution. Preserve
  original framing elsewhere and preserve all source shot durations.
- Preserve already-authorized foreground and presenter-specific layers; inspect
  their pane mapping and z-order after the split. Do not invoke subtitles, ramp,
  watermark, body-zoom or other skills automatically. Do not drop existing audio.

## Make the bottom panel follow actual speech

1. Inspect/listen to the source and obtain an accurate time-aligned transcript from
   an available speech/alignment tool, or use a user-supplied timed transcript.
   Correct names, technical terms and Persian words against the actual recording.
2. Break speech into semantic beats. For each, write the exact spoken text, local
   start/end, visual subject, principal action and the spoken word triggering it.
   Use `references/cue-format.json` as the schema example, replacing every example.
3. Start a meaningful visual change at its triggering utterance, normally within
   one output frame. Let the reference-style entrance settle afterward. Do not
   speed up/slip narration or move source edits to fit an animation template.
4. Explain the actual concept: upload → input card; selecting a camera → control
   chip/camera path; generation → progress/result preview; comparison → paired
   cards; numeric claims → a graph only when valid source data is available.
   Avoid decorative graphs and unrelated UI merely to fill the pane.
5. Use short accurate text, recognizable subjects and a single main action at each
   beat. Maintain RTL Persian shaping. If showing a schematic product UI, do not
   imply it is an exact screen recording or a generation actually run on that site.
6. Review onset, action and result against the original speech. `alignment: verified`
   in JSON is a bookkeeping flag, **not** evidence that speech was analyzed.

If no presenter/voice is supplied, make only the visual preview the user requests;
label the limitation in the response. Never replace the voice with unrelated speech,
reuse a random presenter or manufacture a talking-head identity. If no speech tool
or timed transcript is available, request the missing timing rather than claiming
automatic synchronization. This skill does not bundle an ASR model or credentials.

## Match the SaaS look and movement

- Use a near-white stage, raised white rounded capsules/cards, fine pale borders,
  soft layered shadows, glass planes and restrained pastel/iridescent accents.
  Use the larger full-color gradient episode only when it serves a reference motif.
- Use crisp near-black sans typography, clear hierarchy and ample negative space.
  Keep text readable at the **actual lower-panel size**, not just full-screen preview.
- Use a shared virtual camera for each lower scene: perspective yaw, push/pull,
  short pans and clear depth between UI layers. Use pointer-led selection/clicks,
  selector corners, word slots and card fans where the narration calls for them.
- Keep motion motivated: pointer → control response → camera move → resulting
  UI state. Use long-tail arrival easing and faster accelerating handoffs. Hold
  important words/results. Do not make every element bounce or continuously pulse.
- Preserve real render-time motion blur for fast transitions. Use the existing
  renderer's supported setting; do not claim native AE motion blur was executed.
- Treat CSS perspective as 3D UI planes. Do not call it a Blender mesh/physical
  scene. The rendered references do not reveal their original project, parenting
  or exact graph values; infer and compare honestly instead of inventing them.
- Match style/choreography, not a promise of pixel-identical unrelated content.

## Reuse the tested motion seed

`assets/higgsfield-demo/` contains a complete, locally resourced HyperFrames/GSAP
motion seed with fonts, photo and design rules. It renders a **five-second silent
motion-only test**, as the user explicitly chose for testing. It is not a default
presenter output and it was not tested against a supplied narration.

Copy it to the task workspace, read its `DESIGN.md` and `index.html`, then retarget
subject, assets, layout and **all timings** to the real speech plan. Its authored
viewport is 1080×960, matching the lower pane directly. Do not treat a fixed five
seconds as a requirement for production shots.

```bash
cd /task/motion
npm run check
npx hyperframes snapshot --at 0.7,2.0,4.1 --describe false
npm run render -- --output /task/lower-motion.mp4 --fps 30 --quality high
```

Use the installed HyperFrames/GSAP guidance. Inspect snapshots and fix errors before
rendering. Keep input assets local. Neither this skill nor the seed connects to a
paid video site or makes a paid generation automatically.

## Compose an interval

Use `scripts/compose.py` for already-rendered, correctly sized motion and presenter
footage. It requires FFmpeg/ffprobe and Python's standard library.

```bash
python scripts/compose.py \
  --presenter /task/presenter.mp4 --motion /task/lower-motion.mp4 \
  --start 5 --duration 8 --cues /task/verified-cues.json \
  --focal-x 0.5 --focal-y 0.35 --output /task/selected-interval.mp4
```

The output is the selected interval starting at local time zero. Reinsert it at
the original composition time; preserve the rest of the edit. The composer does
not author motion or validate semantics. It requires a checked cue plan for
production; `--layout-test` bypasses that only for explicitly labeled structural QA.
It rejects short motion instead of silently looping it, guards input/output identity,
and refuses mismatched lower-panel aspect unless `--motion-fit contain` is explicit.
Prefer a re-layout over letterboxing. Normalize VFR/rotation/pixel aspect with an
explicit source-time mapping before production. Audio is trimmed from the presenter
and encoded to AAC, not replaced or claimed byte-identical. Verify lip sync after
any resampling, crop, trimming or composition. The helper fully decodes the output
and writes its frame count, pane rectangles and mode to a companion JSON report.

## Final checks

- Verify all three references were actively inspected and the style comparison
  covers a capsule, camera handoff and card/depth state.
- Verify exactly equal panes, no stretched faces/UI, safe headroom, no glyph clipping
  and no lower animation spilling over the presenter.
- Verify action onset and semantic relevance against speech, including shot edits
  and source/composition offsets. Do not claim speech sync for a silent visual test.
- Check audio, full decode, frame count, resolution, duration and untouched source.
- Deliver the rendered video and report the actual scope. Save skill changes through
  the Skills Git workspace; do not hand the user a skill ZIP unless requested.

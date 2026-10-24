# Native opening rig

Select the complete finished scene composition. Preserve its default framing, audio, layer stack, local effects and timing. Execute in a compatible AE host:

```js
$.global.HOOK_ZOOM_OPTIONS={start:0,end:1.5,travel:200};
$.evalFile(new File('/absolute/path/to/hook-zoom-out/scripts/build_ae_hook.jsx'));
```

The source composition is duplicated. For an ordinary 2D stack, compatible visual layers become 3D with motion blur enabled. For existing cameras/depth/adjustments the scene is preserved in an outer 3D precomp plane. Only the camera is parented to the moving 3D null. The camera itself is already a 3D layer and does not have an AV-layer 3D switch. Recheck baseline appearance and effects/mattes inside the actual host.

Default null Z keys are `0s:200` and `1.5s:0` at 1080 width. Use scalar separated Z with `KeyframeEase(0,75)` on both sides and Bezier interpolation, temporal auto-Bezier off. Do not create a default-position key before the first close pose. Do not animate the camera's lens Zoom property; preserve the baseline lens and change relative camera Z. Do not repeat or bounce.

Camera default distance and camera zoom both use 1500 reference units; null is centered in the composition. A +200 offset moves the camera from −1500 to −1300. At t=1.5 it returns to −1500, preserving the original wide view. Scale distance/travel proportionally for other resolutions. Keep XY/rotation fixed and depth of field off unless an existing explicitly requested scene requires another integration.

Enable comp/master blur and compatible rendered layers: angle 180, phase 0, samples 16, adaptive limit 128. Camera layers have no independently blur-able image; their movement is reflected in affected visual layers. The forward shutter may slightly average later positions on the first displayed frame without changing its key time.

The helper reuses either Hook Zoom Out or Body Zoom names when there is only one matching rig. If the existing rig has keys outside the opening interval, supply a complete merged `keyPlan=[{time:0,z:200},{time:1.5,z:0}, ...existing later authorized keys...]` in final scene units. It validates a nonempty ordered plan before deleting keys, and refuses to erase other ranges without it. It guards custom animated/parented controls and complex newly added content on a reused rig; integrate such content into a preserved scene plane first. Do not stack another camera on top.

A native host is required to confirm AE API/version compatibility and appearance. A JavaScript syntax check does not execute the camera rig or prove a native video render. Use the self-contained Python virtual-camera path when no host is available, and state that distinction.

## Technical sources

These are the same temporal/camera principles verified for body-zoom:

- Adobe Speed: https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/speed-between-keyframes/speed.html — speed is distinct from influence; default Easy Ease is zero speed with 33.33% influence, while this preset explicitly uses 75%.
- Adobe Cameras: https://helpx.adobe.com/after-effects/desktop/work-with-layers/camera-layer/cameras-lights-points-interest.html — camera position and Z tracking affect the scene view.
- User's copied motion-blur screenshot provides 180/0/16/128. The code's Bezier handle conversion and planar projection are mathematical implementations; no pixel-exact identity with AE's proprietary renderer is claimed.

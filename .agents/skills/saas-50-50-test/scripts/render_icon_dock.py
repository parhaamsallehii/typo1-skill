#!/usr/bin/env python3
"""Render the white-icon-dock-v1 visual study; not a narration/video editor.

Dependencies: Pillow, numpy, scipy, opencv-python-headless, ffmpeg/ffprobe.
Use --output /absolute/test.mp4. No network or source mutation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/variants/white-icon-dock-v1'
FPS, WIDTH, HEIGHT, DURATION = 30, 1080, 960, 3.4
LEAD = .5
NAMES = ['notes', 'discord', 'pinterest', 'after-effects', 'messages']
CENTERS = [253, 397, 539, 682, 824]
COMPONENTS = frozenset({'dock', 'icons', 'cursor', 'hover', 'entrance'})


def entrance(u):
    """Exact cubic-bezier(0,0,0,1): x(s)=s**3, y(s)=3*s*s-2*s**3."""
    s = np.clip(u, 0, 1) ** (1 / 3)
    return float(3 * s * s - 2 * s * s * s)


def smooth(u):
    u = float(np.clip(u, 0, 1))
    return u * u * (3 - 2 * u)


def pulse(t, start, peak, leave, end):
    if t < start or t >= end:
        return 0.
    if t < peak:
        return smooth((t - start) / (peak - start))
    if t <= leave:
        return 1.
    return 1. - smooth((t - leave) / (end - leave))


def build_scene(components=None):
    """Select independent tools; hover cues do not depend on cursor visibility."""
    enabled = COMPONENTS if components is None else frozenset(components)
    if enabled - COMPONENTS:
        raise ValueError(f'Unknown components: {sorted(enabled - COMPONENTS)}')
    data = json.loads((ASSETS / 'cursor-measurements.json').read_text())
    rows = data['records']
    ts = [r['t'] for r in rows]
    curve = {k: PchipInterpolator(ts, [r[k] for r in rows], extrapolate=False)
             for k in ['cx', 'cy', 'rotation']}
    # Arrow artwork derives from reference black silhouette, rendered with a white rim.
    poly = np.array(data['polygon_centered'])
    cursor = Image.new('RGBA', (192 * 4, 192 * 4))
    d = ImageDraw.Draw(cursor)
    pts = [tuple((p + 96) * 4) for p in poly]
    d.polygon(pts, fill='black')
    d.line(pts + [pts[0]], fill='white', width=7 * 4, joint='curve')
    # Redraw black interior; exterior white stroke remains outside the silhouette.
    d.polygon(pts, fill='black')
    cursor = cursor.resize((192, 192), Image.Resampling.LANCZOS)
    plate = Image.new('RGBA', (790, 222))
    sh = Image.new('RGBA', plate.size)
    ImageDraw.Draw(sh).rounded_rectangle((25, 29, 765, 195), 54, fill=(80, 84, 88, 20))
    sh = sh.filter(ImageFilter.GaussianBlur(15))
    plate.alpha_composite(sh)
    ImageDraw.Draw(plate).rounded_rectangle((25, 23, 765, 189), 54,
                                          fill=(246, 246, 247, 242),
                                          outline=(255, 255, 255, 255), width=3)
    icons = [Image.open(ASSETS / f'icon-{name}.png').convert('RGBA') for name in NAMES]

    def state(t):
        local = t - LEAD
        if local < ts[0]:
            return None
        local = min(local, ts[-1])
        return tuple(float(curve[k](local)) for k in ['cx', 'cy', 'rotation'])

    def scene(t):
        canvas = Image.new('RGB', (WIDTH, HEIGHT), 'white')
        e = entrance((t - .06) / .54) if 'entrance' in enabled else 1.
        scale, dy = .86 + .14 * e, 150 * (1 - e)
        pw, ph = round(790 * scale), round(222 * scale)
        pl = plate.resize((pw, ph), Image.Resampling.BICUBIC)
        if 'dock' in enabled:
            canvas.paste(pl, (round(540 - pw / 2), round(480 + dy - 106 * scale)), pl)
        local = t - LEAD
        # Each cue is tied to the measured cursor encounter; no independent looping pulse.
        pulses = [pulse(local, .39, .44, .45, .52),
                  pulse(local, .43, .48, .50, .57),
                  max(pulse(local, .49, .55, .59, .67), pulse(local, 2.23, 2.34, 2.84, 3.03)),
                  max(pulse(local, .57, .66, .72, .87), pulse(local, 1.52, 1.60, 1.64, 1.73),
                      pulse(local, 2.11, 2.18, 2.21, 2.34)),
                  pulse(local, .73, .86, 1.44, 1.62)]
        for i, src in enumerate(icons):
            if 'icons' not in enabled:
                break
            hover = pulses[i] if 'hover' in enabled else 0.
            sz = (1 + .16 * hover) * scale
            w, h = round(src.width * sz), round(src.height * sz)
            icon = src.resize((w, h), Image.Resampling.BICUBIC)
            cx = 540 + (CENTERS[i] - 540) * scale
            cy = 480 + dy - 7 * hover * scale
            canvas.paste(icon, (round(cx - w / 2), round(cy - h / 2)), icon)
        st = state(t)
        if st and 'cursor' in enabled:
            x, y, angle = st
            rot = cv2.getRotationMatrix2D((96, 96), -angle, 1.)
            arr = cv2.warpAffine(np.array(cursor), rot, (192, 192), flags=cv2.INTER_CUBIC)
            ptr = Image.fromarray(arr)
            canvas.paste(ptr, (round(x - 96), round(y + 34 - 96)), ptr)
        return canvas

    return scene, state


def render(output, components=None):
    if output.suffix.lower() != '.mp4':
        raise ValueError('Output must be MP4')
    if output.exists():
        raise FileExistsError(output)
    if ASSETS == output.parent or ASSETS in output.parents:
        raise ValueError('Choose an output outside original reference assets')
    output.parent.mkdir(parents=True, exist_ok=True)
    enabled = COMPONENTS if components is None else frozenset(components)
    scene, state = build_scene(enabled)
    # White is invariant outside this ROI; integrate only the moving scene region.
    roi = (0, 100, 1080, 800)
    proc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo',
        '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}', '-r', str(FPS), '-i', '-',
        '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt',
        'yuv420p', '-movflags', '+faststart', str(output)], stdin=subprocess.PIPE)
    samples_used = []
    try:
        for frame in range(round(DURATION * FPS)):
            t = frame / FPS
            a, b = state(t), state(t + 1 / (2 * FPS))
            travel = 0.
            if a and b:
                travel = math.hypot(b[0] - a[0], b[1] - a[1]) + abs(b[2] - a[2]) * math.pi / 180 * 64
            elif a != b:
                travel = 80.
            if t < .62:
                travel = max(travel, 150 * abs(entrance((t + 1 / (2 * FPS) - .06) / .54)
                                              - entrance((t - .06) / .54)))
            samples = min(128, max(16, math.ceil(travel / .7)))
            samples_used.append(samples)
            acc = np.zeros((roi[3] - roi[1], roi[2] - roi[0], 3), np.float32)
            for j in range(samples):
                # AE phase 0 opens at t; shutter angle 180 exposes forward for half a frame.
                st = min(DURATION - 1e-6, t + (j + .5) / samples / (2 * FPS))
                acc += np.asarray(scene(st).crop(roi), dtype=np.float32)
            out = np.full((HEIGHT, WIDTH, 3), 255, dtype=np.uint8)
            out[roi[1]:roi[3], roi[0]:roi[2]] = np.clip(np.rint(acc / samples), 0, 255).astype('uint8')
            proc.stdin.write(out.tobytes())
            if frame % 30 == 0:
                print(f'frame {frame}/102, temporal samples {samples}', flush=True)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('FFmpeg failed')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                             '-show_format', '-of', 'json', str(output)]))
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    assert (v['width'], v['height'], int(v['nb_frames'])) == (WIDTH, HEIGHT, 102)
    assert not any(s['codec_type'] == 'audio' for s in info['streams'])
    report = dict(variant='white-icon-dock-v1', duration=DURATION, fps=FPS, frames=102,
        components=sorted(enabled),
        width=WIDTH, height=HEIGHT, audio=False, presenter=False, speech_sync_tested=False,
        status='visual reconstruction awaiting user review; not approved style canon',
        entrance=dict(bezier=[0, 0, 0, 1], start=.06, duration=.54, authored_lead_in=LEAD),
        motion_blur=dict(method='per-subframe RGB temporal integration; no directional blur',
                         shutter_angle=180, phase=0, minimum_samples=16, adaptive_limit=128,
                         actual_min=min(samples_used), actual_max=max(samples_used)),
        cursor='measured frame centroids/rotations; authored PCHIP subframe interpolation',
        sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_suffix('.mp4.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--components', default=','.join(sorted(COMPONENTS)),
        help='Independent tools: dock,icons,cursor,hover,entrance. Empty means white stage only.')
    args = parser.parse_args()
    selected = {part.strip() for part in args.components.split(',') if part.strip()}
    render(args.output.resolve(), selected)

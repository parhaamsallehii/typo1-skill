#!/usr/bin/env python3
"""SaaS study: independent cursor anticipation, pixels and five-disc reveal.

Python dependencies: Pillow, numpy, scipy, opencv-python-headless; FFmpeg.
Modes let the modules run separately; --color binds the transition palette.
This is a coded visual reconstruction, not a native AE project or speech editor.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/variants/anticipation-circle-reveal-v1'
W, H, FPS, DURATION, LEAD = 1080, 960, 30, 2.4, .4


def smooth(u):
    u = float(np.clip(u, 0, 1))
    return u * u * (3 - 2 * u)


def out(u):
    return 1 - (1 - float(np.clip(u, 0, 1))) ** 4


def parse_color(value):
    value = value.lstrip('#')
    if len(value) != 6 or any(c not in '0123456789abcdefABCDEF' for c in value):
        raise ValueError('Use a six-digit hex color')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


class AnticipationCursor:
    """Measured per-vertex mesh deformation; callable independently of a reveal."""
    def __init__(self):
        rows = json.loads((ASSETS / 'cursor-deformation.json').read_text())['records']
        self.ts = [r['time'] for r in rows]
        self.curve = PchipInterpolator(self.ts, np.array([r['polygon'] for r in rows]), axis=0)

    def polygon(self, t):
        return self.curve(np.clip(t, self.ts[0], self.ts[-1]))

    def draw(self, canvas, t, anchor=(540, 480), hide_after_impact=True):
        if hide_after_impact and t >= .55:
            return
        p = self.polygon(t)
        # Polygon mesh preserves tip pull/body foreshortening rather than merely rotating a rigid arrow.
        sprite = Image.new('RGBA', (160 * 3, 180 * 3))
        d = ImageDraw.Draw(sprite)
        pts = [tuple((v + [40, 25]) * 3) for v in p]
        d.polygon(pts, fill='black')
        d.line(pts + [pts[0]], fill='white', width=5 * 3, joint='curve')
        d.polygon(pts, fill='black')
        sprite = sprite.resize((160, 180), Image.Resampling.LANCZOS)
        if .5 < t < .55 and hide_after_impact:
            sprite.putalpha(sprite.getchannel('A').point(lambda a: round(a * (1 - smooth((t - .5) / .05)))))
        canvas.paste(sprite, (round(anchor[0] - 40), round(anchor[1] - 25)), sprite)


class OutlinePixelBurst:
    """Seeded, grid-like hollow squares/corners; no dependency on a mouse or disc."""
    def __init__(self, color):
        self.color = color
        rng = np.random.default_rng(20261025)
        self.particles = [(float(rng.uniform(0, 2 * math.pi)), float(rng.uniform(150, 520)),
                           int(rng.choice([10, 14, 18, 22])), float(rng.uniform(-.022, .026)),
                           int(rng.integers(0, 5))) for _ in range(68)]

    def draw(self, canvas, t, origin=(540, 480), start=.435):
        age = t - start
        if age <= 0 or age > .65:
            return
        layer = Image.new('RGBA', canvas.size)
        d = ImageDraw.Draw(layer)
        for angle, reach, size, delay, corner in self.particles:
            p = float(np.clip((age - delay) / .46, 0, 1))
            if p <= 0:
                continue
            # Quantize only destinations; preserve continuous subframe travel.
            tx0, ty0 = math.cos(angle) * 45, math.sin(angle) * 45
            tx1 = round(math.cos(angle) * (45 + reach) / 12) * 12
            ty1 = round(math.sin(angle) * (45 + reach) / 12) * 12
            tx = tx0 + (tx1 - tx0) * out(p)
            ty = ty0 + (ty1 - ty0) * out(p)
            x, y = origin[0] + tx, origin[1] + ty
            alpha = round(150 * min(1, p * 8) * (1 - smooth((age - .24) / .40)))
            if alpha <= 0:
                continue
            color = (*self.color, alpha)
            if corner:
                d.rectangle((x - size / 2, y - size / 2, x + size / 2, y + size / 2), outline=color, width=2)
            else:
                d.line([(x - size / 2, y + size / 2), (x - size / 2, y - size / 2),
                        (x + size / 2, y - size / 2)], fill=color, width=2)
        canvas.alpha_composite(layer)


class FiveDiscReveal:
    """Exactly five concentric filled gradient discs, with independent color/origin/time."""
    def __init__(self, color):
        self.color = np.array(color, dtype=float)
        self.final_radii = [190., 325., 460., 600., 770.]
        # Reference-visible envelope, with a very soft final settle; not recovered AE keys.
        self.growth = PchipInterpolator([.49, .52, .55, .58, .61, .65, .69, .73, .78, .84, .96],
                                       [0, .025, .095, .17, .26, .40, .57, .75, .91, .98, 1.])
        self.textures = [self.texture(i) for i in range(5)]

    def texture(self, index):
        n = 1024
        y, x = np.mgrid[0:n, 0:n].astype('float32')
        distance = np.hypot(x - n / 2, y - n / 2)
        f = np.clip(y / n, 0, 1)[..., None]
        light = self.color * .57 + np.array([255, 255, 255]) * .43
        dark = self.color * .91
        if index % 2:
            top, bottom = dark, light
        else:
            top, bottom = light, dark
        rgb = np.broadcast_to(top * (1 - f) + bottom * f, (n, n, 3)).copy()
        # Thin specular rim and slightly darker inside edge, not a wide glowing outline.
        angle = np.arctan2(y - n / 2, x - n / 2)
        arc = np.maximum(0, np.cos(angle + 2.25)) ** 8
        rim = np.exp(-((distance - (n / 2 - 2)) / 1.2) ** 2) * (.1 + .8 * arc)
        rgb += (255 - rgb) * rim[..., None]
        rgba = np.zeros((n, n, 4), np.uint8)
        rgba[:, :, :3] = np.clip(rgb, 0, 255)
        rgba[:, :, 3] = np.clip((n / 2 - distance) * 255, 0, 255)
        return Image.fromarray(rgba)

    def progress(self, t, start=.49):
        source = t - start + .49
        return float(self.growth(np.clip(source, .49, .96)))

    def draw(self, canvas, t, origin=(540, 480), start=.49):
        e = self.progress(t, start)
        if e <= 0:
            return
        # Back-to-front order produces five filled discs, not five hollow stroke rings.
        for i in range(4, -1, -1):
            r = self.final_radii[i] * e
            if r < .6:
                continue
            side = max(2, round(2 * r))
            disc = self.textures[i].resize((side, side), Image.Resampling.BILINEAR)
            canvas.alpha_composite(disc, (round(origin[0] - side / 2), round(origin[1] - side / 2)))
            # A fine moving light sweep stays clipped to the circular perimeter.
            sweep = Image.new('RGBA', canvas.size)
            d = ImageDraw.Draw(sweep)
            box = (origin[0] - r + .5, origin[1] - r + .5, origin[0] + r - .5, origin[1] + r - .5)
            angle = 198 + 28 * out((t - start) / .55) + i * 3
            d.arc(box, angle, angle + 60, fill=(255, 255, 255, 140 if i == 0 else 65), width=2)
            canvas.alpha_composite(sweep)


class DimensionalSymbol:
    """Perspective-projected white face plus offset extrusion layers, not a mesh asset."""
    def __init__(self, path):
        self.face = Image.open(path).convert('RGBA')

    def draw(self, canvas, t, growth, origin=(540, 480), start=.51):
        if t < start or growth <= .02:
            return
        e = out((t - start) / .36)
        yaw = math.radians(65 * (1 - e))
        pitch = math.radians(-22 * (1 - e))
        roll = math.radians(-24 * (1 - e))
        size = min(1, max(.05, growth * 1.25))
        fw, fh = self.face.size
        a = np.array(self.face)
        face = a.copy()
        side = a.copy(); side[:, :, :3] = [170, 174, 178]
        surf = Image.new('RGBA', (320, 340))
        rx = np.array([[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]])
        ry = np.array([[math.cos(yaw), 0, math.sin(yaw)], [0, 1, 0], [-math.sin(yaw), 0, math.cos(yaw)]])
        rz = np.array([[math.cos(roll), -math.sin(roll), 0], [math.sin(roll), math.cos(roll), 0], [0, 0, 1]])
        rot = rz @ ry @ rx
        corners = np.array([[-fw / 2, -fh / 2, 0], [fw / 2, -fh / 2, 0],
                            [fw / 2, fh / 2, 0], [-fw / 2, fh / 2, 0]]) * size
        projected = corners @ rot.T
        dst = projected[:, :2] * (650 / (650 + projected[:, 2:3])) + [160, 170]
        src = np.array([[0, 0], [fw, 0], [fw, fh], [0, fh]], np.float32)
        for z in range(7, -1, -1):
            offset = [z * (.5 + math.sin(yaw) * .75) * size, z * .35 * size]
            matrix = cv2.getPerspectiveTransform(src, (dst + offset).astype('float32'))
            transformed = cv2.warpPerspective(face if z == 0 else side, matrix, (320, 340), flags=cv2.INTER_LINEAR)
            surf.alpha_composite(Image.fromarray(transformed))
        canvas.alpha_composite(surf, (round(origin[0] - 160), round(origin[1] - 170)))


def build_scene(mode, color, symbol_path=None, show_symbol=True, show_pixels=True):
    spec = importlib.util.spec_from_file_location('dock_variant', ROOT / 'scripts/render_icon_dock.py')
    dock = importlib.util.module_from_spec(spec); spec.loader.exec_module(dock)
    old_scene, _ = dock.build_scene()
    background = old_scene(.7).convert('RGBA')
    # Match the already-hovered target before the click.
    target = Image.open(ROOT / 'assets/variants/white-icon-dock-v1/icon-pinterest.png').convert('RGBA')
    target = target.resize((128, 130), Image.Resampling.LANCZOS)
    background.alpha_composite(target, (475, 408))
    cursor, pixels, discs = AnticipationCursor(), OutlinePixelBurst(color), FiveDiscReveal(color)
    symbol = DimensionalSymbol(symbol_path or ASSETS / 'symbol-pinterest.png') if show_symbol else None
    frozen = None

    def scene(t):
        nonlocal frozen
        local = t - LEAD
        # All states are constant here; cache the identical subframe image.
        if local >= 1.1 and frozen is not None:
            return frozen.copy()
        combined = mode == 'combined'
        if combined or mode == 'anticipation':
            canvas = background.copy()
        else:
            canvas = Image.new('RGBA', (W, H), 'white')
        if show_pixels and (combined or mode in ('transition', 'pixels')):
            pixels.draw(canvas, local)
        if combined or mode == 'transition':
            discs.draw(canvas, local)
            # The selected icon identity survives the plan change, now a raised white symbol.
            if symbol:
                symbol.draw(canvas, local, discs.progress(local))
        if combined or mode == 'anticipation':
            cursor.draw(canvas, max(0, local), hide_after_impact=combined)
        result = canvas.convert('RGB')
        if local >= 1.1:
            frozen = result.copy()
        return result

    return scene, cursor, discs


def render(args):
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    if output.suffix.lower() != '.mp4' or ROOT == output.parent or ROOT in output.parents:
        raise ValueError('Choose a new MP4 outside the skill source folder')
    color = parse_color(args.color)
    output.parent.mkdir(parents=True, exist_ok=True)
    scene, cursor, discs = build_scene(args.mode, color, args.symbol, not args.no_symbol, not args.no_pixels)
    proc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '16',
        '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)], stdin=subprocess.PIPE)
    counts = []
    try:
        for frame in range(round(DURATION * FPS)):
            t = frame / FPS; local = t - LEAD
            half = .5 / FPS
            travel = float(np.linalg.norm(cursor.polygon(local + half) - cursor.polygon(local), axis=1).max())
            if args.mode in ('combined', 'transition'):
                travel = max(travel, abs(discs.progress(local + half) - discs.progress(local)) * 770)
            count = min(128, max(16, math.ceil(travel / .7)))
            counts.append(count)
            accum = np.zeros((H, W, 3), dtype=np.float32)
            for j in range(count):
                # Real temporal integration, shutter180/phase0: forward half-frame exposure.
                sample = min(DURATION - 1e-6, t + (j + .5) / count * half)
                accum += np.asarray(scene(sample), dtype=np.float32)
            proc.stdin.write(np.clip(np.rint(accum / count), 0, 255).astype('uint8').tobytes())
            if frame % 12 == 0:
                print(f'frame {frame}/72; temporal samples {count}', flush=True)
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('FFmpeg failed')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output)]))
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    assert int(v['nb_frames']) == 72 and (v['width'], v['height']) == (W, H)
    assert not any(s['codec_type'] == 'audio' for s in info['streams'])
    active = []
    if args.mode in ('combined', 'anticipation'):
        active.append('cursor-anticipation')
    if not args.no_pixels and args.mode in ('combined', 'transition', 'pixels'):
        active.append('outline-pixel-burst')
    if args.mode in ('combined', 'transition'):
        active.append('five-gradient-disc-reveal')
        if not args.no_symbol:
            active.append('dimensional-symbol')
    report = dict(mode=args.mode, color='#' + ''.join(f'{c:02X}' for c in color), duration=DURATION,
        fps=FPS, frames=72, width=W, height=H, audio=False, presenter=False, speech_sync_tested=False,
        modules=active,
        source_time_mapping=f'output = source + {LEAD}s; final state held',
        blur=dict(angle=180, phase=0, minimum_samples=16, adaptive_limit=128, actual_min=min(counts), actual_max=max(counts)),
        status='new reconstruction awaiting user review', native_AE_executed=False,
        geometry='deforming pointer mesh in screen space; projected layered symbol relief, not Blender mesh',
        sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_suffix('.mp4.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--mode', choices=['combined', 'anticipation', 'transition', 'pixels'], default='combined')
    parser.add_argument('--color', default='#E60023', help='Explicit video brand or selected icon hex; red is example default only')
    parser.add_argument('--symbol', type=Path, help='Transparent face artwork for the result; keep consistent with the chosen palette/subject')
    parser.add_argument('--no-symbol', action='store_true', help='No icon or symbol in the reveal')
    parser.add_argument('--no-pixels', action='store_true', help='No outline particle accents')
    render(parser.parse_args())

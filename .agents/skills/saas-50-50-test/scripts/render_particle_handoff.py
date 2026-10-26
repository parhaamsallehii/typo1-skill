#!/usr/bin/env python3
"""Modular SaaS spin, glyph particles, feather aperture and dot cleanup study.

Requires Pillow, numpy and FFmpeg. Reconstructed choreography, not native AE.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/variants/spin-particle-handoff-v1'
W, H, FPS, DURATION, LEAD = 1080, 960, 30, 2.4, .4


def clamp(u):
    return np.clip(u, 0., 1.)


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def hex_color(value):
    s = value.lstrip('#')
    if len(s) != 6 or any(c not in '0123456789abcdefABCDEF' for c in s):
        raise ValueError('Use a six-digit brand/icon hex color')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


class FeatherCircle:
    """Independent center-out soft aperture: in clears outgoing; out clears dots."""
    def __init__(self, size=(W, H), origin=None, feather=100):
        self.w, self.h = size
        self.origin = origin or (self.w / 2, self.h / 2)
        y, x = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.distance = np.hypot(x - self.origin[0], y - self.origin[1])
        self.feather = feather
        self.max_radius = float(self.distance.max()) + feather

    def progress(self, t, start, duration, curve):
        u = float(clamp((t - start) / duration))
        return u ** 2.6 if curve == 'in' else 1 - (1 - u) ** 4

    def reveal(self, t, start, duration, curve):
        e = self.progress(t, start, duration, curve)
        if e <= 0:
            return np.zeros_like(self.distance)
        if e >= 1:
            return np.ones_like(self.distance)
        return smooth((self.max_radius * e - self.distance) / self.feather + .5)


class SpinZoomDiscs:
    """Five concentric gradient fills; rotate their material as circles are symmetric."""
    def __init__(self, color):
        self.color = np.asarray(color, np.float32)
        self.radii = np.array([190, 325, 460, 600, 770], np.float32)
        self.y, self.x = np.mgrid[0:H, 0:W].astype(np.float32)
        self.x -= W / 2
        self.y -= H / 2
        self.distance = np.hypot(self.x, self.y)
        self.polar = np.arctan2(self.y, self.x)

    def state(self, t):
        u = float(clamp((t - .06) / .64))
        e = u ** 3
        return math.radians(170 * e), 1 + .58 * e

    def image(self, t):
        angle, scale = self.state(t)
        distance = self.distance / scale
        index = np.minimum(np.searchsorted(self.radii, distance), 4)
        radius = self.radii[index]
        gradient_y = (math.cos(angle) * self.y - math.sin(angle) * self.x) / scale
        f = clamp(gradient_y / (2 * radius) + .5)
        f = np.where(index % 2, 1 - f, f)[..., None]
        light = self.color * .57 + 255 * .43
        dark = self.color * .91
        rgb = light * (1 - f) + dark * f
        # Thin material edge rotates with the gradient; no broad glow replacement.
        edge = np.exp(-((distance - (radius - 1)) / 1.1) ** 2)
        arc = np.maximum(0, np.cos(self.polar - angle + 2.25)) ** 8
        rgb += (255 - rgb) * (edge * (.10 + .8 * arc))[..., None]
        return np.clip(rgb, 0, 255).astype(np.float32)


class RegularDotOverlay:
    """Ordered dot grid, separate from floating glyph fragments and outline squares."""
    def __init__(self, pitch=12, radius=1.4):
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (x + pitch / 2) % pitch - pitch / 2
        dy = (y + pitch / 2) % pitch - pitch / 2
        self.alpha = clamp(radius + .5 - np.hypot(dx, dy)) * .62

    def apply(self, rgb, keep):
        alpha = self.alpha * keep
        return rgb * (1 - alpha[..., None]) + 255 * alpha[..., None]


class GlyphParticles:
    """Seeded particles sample the actual glyph alpha, detach, swirl and float across cut."""
    def __init__(self, path, seed=20261025):
        face = Image.open(path).convert('RGBA')
        alpha = np.asarray(face.getchannel('A'))
        yy, xx = np.where(alpha[::3, ::3] > 160)
        pos = np.column_stack([xx * 3 - face.width / 2, yy * 3 - face.height / 2]).astype(np.float32)
        rng = np.random.default_rng(seed)
        take = rng.choice(len(pos), min(1600, len(pos)), replace=False)
        self.base = pos[take]
        n = len(take)
        self.detach = rng.uniform(.17, .47, n).astype(np.float32)
        self.face_alpha = alpha.astype(np.float32) / 255
        release = rng.uniform(.17, .47, ((face.height + 2) // 3, (face.width + 2) // 3))
        self.release = np.repeat(np.repeat(release, 3, axis=0), 3, axis=1)[:face.height, :face.width]
        self.face_xy = (round(W / 2 - face.width / 2), round(H / 2 - face.height / 2))
        self.reach = rng.uniform(100, 410, n).astype(np.float32)
        self.phase = rng.uniform(0, math.tau, n).astype(np.float32)
        self.size = rng.choice([1, 1, 2, 2, 3], n)
        self.alpha = rng.uniform(.65, 1., n).astype(np.float32)

    def positions(self, t):
        age = np.maximum(0, t - self.detach)
        a = np.arctan2(self.base[:, 1], self.base[:, 0]) + 4 * age ** 1.8
        radius = np.linalg.norm(self.base, axis=1) + self.reach * age ** 1.15
        x = radius * np.cos(a) + 16 * np.sin(self.phase + age * 6) * age
        y = radius * np.sin(a) - 100 * age ** 1.4
        return np.column_stack([x + W / 2, y + H / 2])

    def apply(self, rgb, t):
        # Keep the identity coherent at first; release individual pieces progressively.
        pos = self.positions(max(0, t))
        fade = float(1 - smooth((t - .82) / .32))
        if fade <= 0:
            return rgb
        # An intact identity precedes fragmentation; clear its actual alpha in small cells.
        if t < .49:
            solid = self.face_alpha * (1 - smooth((t - self.release) / .02))
            x0, y0 = self.face_xy
            h, w = solid.shape
            patch = rgb[y0:y0+h, x0:x0+w]
            rgb[y0:y0+h, x0:x0+w] = patch * (1 - solid[..., None]) + 255 * solid[..., None]
        xy = np.rint(pos).astype(int)
        layer = np.zeros((H, W), np.float32)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = xy[:, 0] + dx, xy[:, 1] + dy
                valid = (np.maximum(abs(dx), abs(dy)) <= self.size) & (x >= 0) & (x < W) & (y >= 0) & (y < H)
                np.maximum.at(layer, (y[valid], x[valid]), self.alpha[valid] * fade)
        return rgb * (1 - layer[..., None]) + 255 * layer[..., None]


def build_scene(color, mode='combined', incoming=None, symbol=None):
    discs = SpinZoomDiscs(color)
    aperture = FeatherCircle()
    dots = RegularDotOverlay()
    particles = GlyphParticles(symbol or ROOT / 'assets/variants/anticipation-circle-reveal-v1/symbol-pinterest.png')
    dest = np.asarray(ImageOps.fit(Image.open(incoming or ASSETS / 'incoming-scene.png').convert('RGB'), (W, H), method=Image.Resampling.LANCZOS), dtype=np.float32)
    white = np.full((H, W, 3), 255., np.float32)
    frozen = None

    def scene(t):
        nonlocal frozen
        s = t - LEAD
        if s >= 1.15 and frozen is not None:
            return frozen
        reveal = aperture.reveal(s, .56, .14, 'in')
        keep_dots = 1 - aperture.reveal(s, .70, .30, 'out')
        if mode == 'spin':
            rgb = discs.image(s)
        elif mode == 'particles':
            # Dark neutral stage makes independent white fragments visible.
            rgb = particles.apply(np.full_like(white, 45), s)
        elif mode == 'aperture':
            rgb = discs.image(s) * (1 - reveal[..., None]) + dest * reveal[..., None]
        elif mode == 'dots':
            rgb = dots.apply(dest.copy(), keep_dots)
        elif mode == 'mask':
            rgb = np.repeat((255 * reveal)[..., None], 3, axis=2)
        else:
            new = dots.apply(dest.copy(), keep_dots)
            if s >= .70:
                rgb = new
            else:
                rgb = discs.image(s) * (1 - reveal[..., None]) + new * reveal[..., None]
            rgb = particles.apply(rgb, s)
        result = np.clip(rgb, 0, 255).astype(np.float32)
        if s >= 1.15:
            frozen = result
        return result

    return scene, discs, aperture, particles


def render(args):
    output = args.output.resolve()
    if output.exists() or ROOT == output.parent or ROOT in output.parents:
        raise ValueError('Use a new output outside the skill sources')
    if output.suffix.lower() != '.mp4':
        raise ValueError('Output must be MP4')
    output.parent.mkdir(parents=True, exist_ok=True)
    color = hex_color(args.color)
    scene, discs, aperture, particles = build_scene(color, args.mode, args.incoming, args.symbol)
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)], stdin=subprocess.PIPE)
    counts = []
    try:
        for frame in range(round(DURATION * FPS)):
            t = frame / FPS
            s = t - LEAD
            half = .5 / FPS
            a, z = discs.state(s), discs.state(s + half)
            travel = abs(z[0] - a[0]) * 770 + abs(z[1] - a[1]) * 770
            if .56 <= s <= .71:
                travel = max(travel, abs(aperture.progress(s + half, .56, .14, 'in') - aperture.progress(s, .56, .14, 'in')) * aperture.max_radius)
            if .70 <= s <= 1.01:
                travel = max(travel, abs(aperture.progress(s + half, .70, .30, 'out') - aperture.progress(s, .70, .30, 'out')) * aperture.max_radius)
            travel = max(travel, float(np.linalg.norm(particles.positions(s + half) - particles.positions(s), axis=1).max()))
            count = min(128, max(16, math.ceil(travel / .8)))
            counts.append(count)
            accum = np.zeros((H, W, 3), np.float32)
            for j in range(count):
                # Actual subframe state integration: 180-degree shutter, phase zero.
                sample = t + (j + .5) / count * half
                accum += scene(sample)
            process.stdin.write(np.clip(np.rint(accum / count), 0, 255).astype(np.uint8).tobytes())
            if frame % 12 == 0:
                print(f'frame {frame}/72, samples {count}', flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError('FFmpeg failed')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output)]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    assert int(video['nb_frames']) == 72 and (video['width'], video['height']) == (W, H)
    assert not any(s['codec_type'] == 'audio' for s in info['streams'])
    report = dict(variant='spin-particle-handoff-v1', mode=args.mode, color=args.color,
        width=W, height=H, fps=FPS, frames=72, duration=DURATION, audio=False,
        presenter=False, speech_sync_tested=False, status='awaiting user review',
        source_time_mapping='output = source + 0.4s; final destination held',
        blur=dict(angle=180, phase=0, minimum_samples=16, adaptive_limit=128, actual_min=min(counts), actual_max=max(counts)),
        native_AE_executed=False, cut_source_time=.70, aperture=[.56,.70], dot_cleanup=[.70,1.0],
        evidence='Timing/curves and particle simulation reconstructed from rendered source; not original AE settings except blur.',
        sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_suffix('.mp4.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['combined','spin','particles','aperture','dots','mask'], default='combined')
    parser.add_argument('--color', default='#E60023', help='Resolved brand/icon hue; red is this reference only')
    parser.add_argument('--incoming', type=Path, help='Actual next scene image; replace study source crop in production')
    parser.add_argument('--symbol', type=Path, help='Transparent subject silhouette; replace Pinterest for other subjects')
    render(parser.parse_args())

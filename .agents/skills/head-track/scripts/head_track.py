#!/usr/bin/env python3
"""Single-feature position stabilization. Requires numpy, scipy, Pillow, ffmpeg/ffprobe.

Analyze a manually inspected face point; render inverse translation with coverage
and transform motion blur. This is not face recognition or a native AE tracker.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image
from scipy.signal import correlate
from scipy.ndimage import uniform_filter


def probe(path):
    d = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    def rate(s):
        a, b = s.split('/')
        return float(a) / float(b)
    fps = rate(v['avg_frame_rate'])
    if abs(rate(v['r_frame_rate']) - fps) > .001:
        raise ValueError('Use a CFR working copy and preserve its time mapping; VFR is not supported.')
    if v.get('tags', {}).get('rotate') or any('rotation' in x and x['rotation'] for x in v.get('side_data_list', [])):
        raise ValueError('Normalize display rotation in a working copy before tracking.')
    return dict(width=v['width'], height=v['height'], fps=fps,
                duration=float(v.get('duration', d['format']['duration'])),
                frames=int(v['nb_frames']) if v.get('nb_frames', '').isdigit() else None)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def frames(path, w, h, gray=False):
    pix = 'gray' if gray else 'rgb24'
    size = w * h * (1 if gray else 3)
    with tempfile.TemporaryFile() as err:
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(path), '-an',
            '-vf', f'scale={w}:{h}', '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', pix, '-'],
            stdout=subprocess.PIPE, stderr=err)
        try:
            while True:
                buf = p.stdout.read(size)
                if not buf:
                    break
                if len(buf) != size:
                    raise RuntimeError('Incomplete decoded frame')
                yield np.frombuffer(buf, np.uint8).reshape((h, w) if gray else (h, w, 3))
            if p.wait():
                err.seek(0)
                raise RuntimeError(err.read().decode())
        finally:
            p.stdout.close()
            if p.poll() is None:
                p.terminate()
                p.wait()


def patch(image, point, radius):
    x, y = np.rint(point).astype(int)
    if x-radius < 0 or y-radius < 0 or x+radius >= image.shape[1] or y+radius >= image.shape[0]:
        raise ValueError('Feature patch crosses source boundary')
    a = image[y-radius:y+radius+1, x-radius:x+radius+1].astype(np.float64)
    if a.std() < 3:
        raise ValueError('Feature lacks contrast. Inspect a nostril or another stable facial feature.')
    return a


def locate(image, template, point, search):
    r = template.shape[0] // 2
    x, y = np.rint(point).astype(int)
    x0, y0 = max(0, x-search-r), max(0, y-search-r)
    x1, y1 = min(image.shape[1], x+search+r+1), min(image.shape[0], y+search+r+1)
    area = image[y0:y1, x0:x1].astype(np.float64)
    k = template.shape[0]
    centered = template - template.mean()
    num = correlate(area, centered, mode='valid', method='fft')
    mean = uniform_filter(area, size=k, mode='constant')[r:area.shape[0]-r, r:area.shape[1]-r]
    mean2 = uniform_filter(area*area, size=k, mode='constant')[r:area.shape[0]-r, r:area.shape[1]-r]
    denom = np.sqrt(np.maximum((mean2-mean*mean)*k*k, 0) * np.sum(centered*centered))
    score = np.divide(num, denom, out=np.full_like(num, -1), where=denom > 1e-8)
    iy, ix = np.unravel_index(np.argmax(score), score.shape)
    confidence = float(score[iy, ix])
    def sub(a, b, c):
        den = a - 2*b + c
        return float(np.clip(.5*(a-c)/den, -.5, .5)) if abs(den) > 1e-9 else 0.
    dx = sub(score[iy, ix-1], score[iy, ix], score[iy, ix+1]) if 0 < ix < score.shape[1]-1 else 0.
    dy = sub(score[iy-1, ix], score[iy, ix], score[iy+1, ix]) if 0 < iy < score.shape[0]-1 else 0.
    return np.array([x0+ix+r+dx, y0+iy+r+dy]), confidence


def analyze(a):
    m = probe(a.input)
    end = m['duration'] if a.end is None else a.end
    if not 0 <= a.start < end <= m['duration'] + 1e-5:
        raise ValueError('Invalid interval')
    w = min(a.work_width, m['width'])
    h = round(w*m['height']/m['width'])
    factor = np.array([w/m['width'], h/m['height']])
    radius = max(3, round(a.patch_radius * w/1080))
    search = max(4, round(a.search_radius * w/1080))
    first = math.ceil(a.start*m['fps']-1e-4)
    last = math.ceil(end*m['fps']-1e-4)
    anchors = {int(x['frame']): np.asarray(x['point'], float) for x in
               (json.loads(Path(a.anchors).read_text()) if a.anchors else [])}
    point = np.asarray(a.seed, float)*factor
    template = None
    rows = []
    for i, frame in enumerate(frames(a.input, w, h, True)):
        if i < first:
            continue
        if i >= last:
            break
        if i == first or i in anchors:
            if i in anchors:
                point = anchors[i]*factor
            template = patch(frame, point, radius)
            # The reference template is centered at this rounded work pixel.
            point = np.rint(point)
            confidence = 1.
        else:
            point, confidence = locate(frame, template, point, search)
        if confidence < a.min_confidence:
            raise RuntimeError(f'Track lost at frame {i}, time {i/m["fps"]:.6f}, NCC {confidence:.3f}. '
                'Inspect/correct this frame and supply --anchors; no valid track was saved.')
        rows.append(dict(frame=i, time=i/m['fps'], point=(point/factor).tolist(), confidence=confidence))
    if len(rows) != last-first:
        raise RuntimeError('Missing frames in requested interval')
    out = dict(schema='head-track-v1', source_sha256=digest(a.input), source=m,
               start=a.start, end=end, point_space='untransformed-source-pixels',
               tracking='fixed-template normalized cross-correlation; manually selected facial point',
               minimum_confidence=a.min_confidence, work_width=w, samples=rows,
               motion_blur=dict(shutter_angle=180, shutter_phase=0, samples=16, adaptive_limit=128))
    Path(a.track).write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(dict(track=str(a.track), samples=len(rows),
          min_confidence=min(x['confidence'] for x in rows),
          displacement=np.ptp([x['point'] for x in rows], axis=0).tolist())))


def cover_scale(points, lock, w, h, margin=2.):
    points = np.asarray(points, float)
    available = np.column_stack([points[:, 0]-margin, w-margin-points[:, 0],
                                 points[:, 1]-margin, h-margin-points[:, 1]])
    if np.any(available <= 0):
        raise ValueError('Tracked point too close to frame edge; use reflected extension.')
    needs = np.array([lock[0], w-lock[0], lock[1], h-lock[1]])/available
    return max(1., float(needs.max())) + .002


def point_at(track, t):
    rows = track['samples']
    times = [x['time'] for x in rows]
    return np.array([np.interp(t, times, [x['point'][axis] for x in rows]) for axis in (0, 1)])


def transform(image, point, lock, scale, padding):
    w, h = image.size
    if padding:
        arr = np.pad(np.asarray(image), ((padding, padding), (padding, padding), (0, 0)), mode='reflect')
        image = Image.fromarray(arr)
    # inverse map dest -> source: source = p(t)+(dest-lock)/scale
    return image.transform((w, h), Image.Transform.AFFINE,
        (1/scale, 0, point[0]-lock[0]/scale+padding,
         0, 1/scale, point[1]-lock[1]/scale+padding), Image.Resampling.BICUBIC)


def srgb_to_linear(a):
    return np.where(a <= .04045, a/12.92, ((a+.055)/1.055)**2.4)


def linear_to_srgb(a):
    a = np.maximum(a, 0)
    return np.where(a <= .0031308, a*12.92, 1.055*a**(1/2.4)-.055)


def render(a):
    if Path(a.input).resolve() == Path(a.out).resolve():
        raise ValueError('Output must be a distinct file')
    track = json.loads(Path(a.track).read_text())
    m = probe(a.input)
    if track['schema'] != 'head-track-v1' or digest(a.input) != track['source_sha256']:
        raise ValueError('Track/source mismatch')
    if not track['samples'] or any(not np.isfinite(x['point']).all() for x in track['samples']):
        raise ValueError('Empty or non-finite track')
    w = m['width'] if a.width is None else a.width
    w -= w % 2
    h = 2*round(m['height']*w/m['width']/2)
    factor = np.array([w/m['width'], h/m['height']])
    points = np.asarray([x['point'] for x in track['samples']])*factor
    lock = points[0]
    try:
        needed = cover_scale(points, lock, w, h)
    except ValueError:
        needed = math.inf
    edge = a.edge
    if edge == 'auto':
        edge = 'crop' if needed <= a.max_scale else 'mirror'
    if edge == 'crop' and (not math.isfinite(needed) or needed > a.max_scale):
        raise ValueError(f'Coverage needs scale {needed:.4f}; use --edge mirror or review --max-scale.')
    scale = needed if edge == 'crop' else 1.03
    low = points.min(axis=0)-lock/scale
    high = points.max(axis=0)+(np.array([w, h])-lock)/scale-np.array([w, h])
    padding = max(0, math.ceil(max(float(-low.min()), float(high.max())))+4) if edge == 'mirror' else 0
    # Limits include trajectory extrema and therefore all interpolated shutter samples.
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{w}x{h}', '-r', str(m['fps']), '-i', '-', '-i', str(a.input),
        '-map', '0:v:0', '-map', '1:a?', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast',
        '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-map_metadata', '1', '-movflags', '+faststart', str(a.out)]
    maximum_samples = 16
    count = 0
    with tempfile.TemporaryFile() as err:
        encoder = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=err)
        try:
            for count, arr in enumerate(frames(a.input, w, h), start=1):
                t = (count-1)/m['fps']
                image = Image.fromarray(arr)
                if track['start'] <= t < track['end']:
                    shutter = .5/m['fps']  # 180 degrees, phase 0: forward half-frame
                    p = point_at(track, t)*factor
                    q = point_at(track, min(t+shutter, track['end']))*factor
                    samples = int(np.clip(math.ceil(np.linalg.norm(q-p)*scale), 16, 128))
                    maximum_samples = max(maximum_samples, samples)
                    acc = np.zeros((h, w, 3), np.float32)
                    for j in range(samples):
                        st = min(t+(j+.5)*shutter/samples, track['end'])
                        frame = transform(image, point_at(track, st)*factor, lock, scale, padding)
                        acc += srgb_to_linear(np.asarray(frame, dtype=np.float32)/255)/samples
                    arr = np.clip(np.rint(linear_to_srgb(acc)*255), 0, 255).astype(np.uint8)
                encoder.stdin.write(arr.tobytes())
            encoder.stdin.close()
            if encoder.wait():
                err.seek(0)
                raise RuntimeError(err.read().decode())
        finally:
            if encoder.poll() is None:
                encoder.kill()
                encoder.wait()
    out = probe(a.out)
    if out['frames'] != count or abs(out['fps']-m['fps']) > 1e-5:
        raise RuntimeError('Rendered frame count/fps mismatch')
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(a.out), '-f', 'null', '-'], check=True)
    report = dict(out=str(a.out), frames=count, edge_mode=edge, scale=scale,
                  reflected_padding_pixels=padding, required_crop_scale=needed if math.isfinite(needed) else None,
                  motion_blur=dict(shutter_angle=180, shutter_phase=0, minimum_samples=16,
                                   adaptive_limit=128, maximum_samples_used=maximum_samples),
                  note='Transform-only subframe sampling of each decoded source frame; native AE not executed.')
    Path(str(a.out)+'.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    q = sub.add_parser('analyze')
    q.add_argument('--input', required=True, type=Path)
    q.add_argument('--track', required=True, type=Path)
    q.add_argument('--start', type=float, default=0.)
    q.add_argument('--end', type=float)
    q.add_argument('--seed', nargs=2, type=float, required=True, metavar=('X', 'Y'))
    q.add_argument('--anchors', type=Path, help='JSON list of {frame, point:[source_x,source_y]} corrections')
    q.add_argument('--work-width', type=int, default=720)
    q.add_argument('--patch-radius', type=float, default=18, help='Reference radius in 1080-wide pixels')
    q.add_argument('--search-radius', type=float, default=54, help='Reference per-frame search radius')
    q.add_argument('--min-confidence', type=float, default=.65)
    q.set_defaults(func=analyze)
    q = sub.add_parser('render')
    q.add_argument('--input', required=True, type=Path)
    q.add_argument('--track', required=True, type=Path)
    q.add_argument('--out', required=True, type=Path)
    q.add_argument('--width', type=int)
    q.add_argument('--edge', choices=['auto', 'crop', 'mirror'], default='auto')
    q.add_argument('--max-scale', type=float, default=1.18)
    q.set_defaults(func=render)
    a = p.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()

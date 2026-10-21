#!/usr/bin/env python3
"""Render bundled Avangard Persian typography; no network or speech recognition.

Pillow must have RAQM. Glow is a visual approximation of the written brief,
not the commercial Deep Glow plugin. Explicit word coordinates are output px.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = json.loads((ROOT / "assets/style.json").read_text(encoding="utf-8"))


def merge(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else value
    return result


def ease(t):
    u = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - u) ** 5


def rgb(value, style):
    return ImageColor.getrgb(style["palette"].get(value, value))


def font_for(role, size, style):
    if role not in style["fonts"]:
        raise ValueError(f"Unknown font role {role!r}; choose block or expressive")
    return ImageFont.truetype(str(ROOT / style["fonts"][role]), max(1, round(size)), layout_engine=ImageFont.Layout.RAQM)


def bounds(text, font):
    return font.getbbox(text, anchor="ls", direction="rtl", language="fa")


def environment():
    fonts = {k: (ROOT / v).is_file() for k, v in DEFAULTS["fonts"].items()}
    return {"raqm": features.check_feature("raqm"), "fonts": fonts,
            "ffmpeg": shutil.which("ffmpeg"), "ffprobe": shutil.which("ffprobe"),
            "native_deep_glow": False, "glow": "procedural visual approximation"}


def require_environment(video=False):
    info = environment()
    if not info["raqm"]:
        raise RuntimeError("Pillow RAQM is required; refusing to render disconnected Persian")
    if not all(info["fonts"].values()):
        raise RuntimeError("A bundled font is missing; restore the complete skill folder")
    if video and not info["ffmpeg"]:
        raise RuntimeError("FFmpeg is required for video output")
    return info


def check_glyphs(words, style):
    cmaps = {}
    for role, name in style["fonts"].items():
        with TTFont(ROOT / name) as f:
            cmaps[role] = set(f.getBestCmap())
    for word in words:
        missing = {ch for ch in word["text"] if not ch.isspace() and ord(ch) not in (0x200c, 0x200d, 0x200e, 0x200f) and ord(ch) not in cmaps[word["font"]]}
        if missing:
            raise ValueError(f"Font {word['font']} lacks glyphs in {word['text']!r}: " + ", ".join(f"{ch!r} U+{ord(ch):04X}" for ch in sorted(missing)))


def line_metrics(line, size, gap, style):
    font = font_for(line["font"], size, style)
    bbs = [bounds(t, font) for t in line["text"].split()]
    widths = [b[2] - b[0] for b in bbs]
    return bbs, widths, sum(widths) + gap * max(0, len(bbs) - 1)


def resolve_scene(scene):
    style = merge(DEFAULTS, scene.get("style", {}))
    w, h = int(scene.get("width", 1080)), int(scene.get("height", 1920))
    fps, duration = float(scene.get("fps", 30)), float(scene.get("duration", 3.2))
    if w < 16 or h < 16 or not math.isfinite(fps) or not math.isfinite(duration) or fps <= 0 or duration <= 0:
        raise ValueError("Positive dimensions (>=16), fps, and duration are required")
    if sum(key in scene for key in ("text", "lines", "words")) != 1:
        raise ValueError("Supply exactly one of text, lines, or words")
    scale = w / style["reference_width"]
    start = float(scene.get("start", 0.2))
    mode = scene.get("layout", "block")
    if mode not in ("block", "expressive"):
        raise ValueError("layout must be block or expressive")
    if "words" in scene:
        words = copy.deepcopy(scene["words"])
        for i, word in enumerate(words):
            for key in ("text", "x", "y", "size"):
                if key not in word:
                    raise ValueError(f"Explicit word {i} is missing {key}")
            word.setdefault("font", "block" if i % 2 == 0 else "expressive")
            word.setdefault("color", "burgundy")
            word.setdefault("start", start + i * style["entrance"]["stagger"])
    else:
        lines = copy.deepcopy(scene.get("lines"))
        if lines is None:
            lines = [{"text": t} for t in scene["text"].splitlines() if t.strip()]
        if not lines:
            raise ValueError("No nonempty lines were supplied")
        lay = style["layout"]
        maxwidth, gap = w * lay["safe_width"], lay["word_gap"] * scale
        sizes = []
        for i, line in enumerate(lines):
            if not line.get("text", "").strip():
                raise ValueError("A line has no text")
            line.setdefault("font", ("block" if i % 2 == 0 else "expressive") if mode == "block" else ("expressive" if i % 2 == 0 else "block"))
            line.setdefault("color", "red" if i == 1 else "burgundy")
            line.setdefault("width", (0.88, 1.0, 0.96)[i % 3])
            line.setdefault("align", ("right", "center", "left")[i % 3])
            line.setdefault("rotation", 0 if mode == "block" else (-2, 1, 3)[i % 3])
            if not 0.1 <= float(line["width"]) <= 1 or line["align"] not in ("left", "center", "right"):
                raise ValueError("Invalid line width or alignment")
            target = maxwidth * line["width"]
            lo, hi = 8, max(16, int(h * 0.5))
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if line_metrics(line, mid, gap, style)[2] <= target:
                    lo = mid
                else:
                    hi = mid - 1
            sizes.append(lo)

        def metrics_for_sizes():
            return [line_metrics(line, size, gap, style) for line, size in zip(lines, sizes)]

        metrics = metrics_for_sizes()
        linegap = lay["line_gap"] * scale
        heights = [max(b[3] for b in m[0]) - min(b[1] for b in m[0]) for m in metrics]
        total = sum(heights) + linegap * (len(lines) - 1)
        if total > h * lay["max_height"]:
            factor = (h * lay["max_height"] - linegap * (len(lines) - 1)) / sum(heights)
            if factor <= 0:
                raise ValueError("Too many lines to fit; split into more than one scene")
            sizes = [max(8, int(s * factor)) for s in sizes]
            metrics = metrics_for_sizes()
            heights = [max(b[3] for b in m[0]) - min(b[1] for b in m[0]) for m in metrics]
            total = sum(heights) + linegap * (len(lines) - 1)
        top = h * lay["center_y"] - total / 2
        center = w * lay["center_x"]
        words = []
        for line, size, metric, height in zip(lines, sizes, metrics, heights):
            bbs, widths, tw = metric
            shift = {"left": -(maxwidth - tw) / 2, "right": (maxwidth - tw) / 2, "center": 0}[line["align"]]
            cursor = center + shift + tw / 2
            baseline = top - min(b[1] for b in bbs)
            for token, box, width in zip(line["text"].split(), bbs, widths):
                words.append({"text": token, "font": line["font"], "color": line["color"], "size": size,
                              "x": cursor - width / 2, "y": baseline + (box[1] + box[3]) / 2,
                              "start": start + len(words) * style["entrance"]["stagger"], "rotation": line["rotation"]})
                cursor -= width + gap
            top += height + linegap
    if not words:
        raise ValueError("No words were supplied")
    for word in words:
        word.setdefault("rotation", 0)
        word.setdefault("entrance", style["entrance"]["duration"])
        word.setdefault("end", duration)
        if not word["text"].strip() or word["font"] not in style["fonts"]:
            raise ValueError("Each word needs nonempty text and a valid font role")
        for key in ("x", "y", "size", "start", "entrance", "end", "rotation"):
            if not math.isfinite(float(word[key])):
                raise ValueError(f"Word {key} is not finite")
        if word["size"] <= 0 or word["entrance"] <= 0 or word["start"] < 0 or word["end"] > duration:
            raise ValueError("Invalid word size, entrance, start, or end")
        if word["start"] + word["entrance"] >= word["end"]:
            raise ValueError(f"Word {word['text']!r} has no settled hold; shorten entrances/stagger or extend the requested interval explicitly")
        rgb(word["color"], style)
    check_glyphs(words, style)
    return {"width": w, "height": h, "fps": fps, "duration": duration, "background": scene.get("background", "beige"),
            "style": style, "words": words, "glow_implementation": "visual approximation; native plugin not used"}


def boil(mask, tick, index, settings, scale):
    amp = settings["amplitude"] * scale
    if amp <= 0:
        return mask
    w, h = mask.size
    step = max(12, round(settings["mesh_step"] * scale))
    xs = list(range(0, w, step)) + [w]
    ys = list(range(0, h, step)) + [h]
    rng = np.random.default_rng(settings["seed"] + index * 100003 + tick * 997)
    displacement = rng.uniform(-amp, amp, (len(ys), len(xs), 2))
    displacement[0, :, :] = displacement[-1, :, :] = 0
    displacement[:, 0, :] = displacement[:, -1, :] = 0
    mesh = []
    for yi in range(len(ys) - 1):
        for xi in range(len(xs) - 1):
            x0, x1, y0, y1 = xs[xi], xs[xi + 1], ys[yi], ys[yi + 1]
            corners = [(x0, y0, yi, xi), (x0, y1, yi + 1, xi), (x1, y1, yi + 1, xi + 1), (x1, y0, yi, xi + 1)]
            quad = tuple(v for x, y, j, k in corners for v in (x + displacement[j, k, 0], y + displacement[j, k, 1]))
            mesh.append(((x0, y0, x1, y1), quad))
    return mask.transform(mask.size, Image.Transform.MESH, mesh, resample=Image.Resampling.BICUBIC)


class WordSprite:
    def __init__(self, word, index, style, scale):
        self.word, self.index, self.style, self.scale = word, index, style, scale
        self.tick, self.cached = None, None
        font = font_for(word["font"], word["size"], style)
        box = bounds(word["text"], font)
        pad = max(8, math.ceil(max(style["glow"]["radii"]) * scale * 2 + 8))
        self.mask = Image.new("L", (box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2), 0)
        ImageDraw.Draw(self.mask).text((pad - box[0], pad - box[1]), word["text"], font=font, fill=255,
                                       anchor="ls", direction="rtl", language="fa")
        width, height = self.mask.size
        tex = style["texture"]
        rng = np.random.default_rng(tex["seed"] + index * 2311)
        noise = rng.normal(0, 0.5, (height, width)).astype(np.float32) * tex["noise_strength"]
        yy, xx = np.mgrid[:height, :width]
        pitch, radius = max(2, tex["halftone_spacing"] * scale), max(0.45, tex["halftone_radius"] * scale)
        # Rotate dot grid by 45 degrees and soften its edge by one output pixel.
        u, v = (xx + yy) * 0.70710678, (xx - yy) * 0.70710678
        dist = np.sqrt(((u + pitch / 2) % pitch - pitch / 2) ** 2 + ((v + pitch / 2) % pitch - pitch / 2) ** 2)
        dots = np.clip(radius + 0.5 - dist, 0, 1) * tex["halftone_strength"]
        color = np.array(rgb(word["color"], style), dtype=np.float32)
        # Keep color variation visible on both dark and light ink while retaining exact palette as the base.
        ink = color[None, None, :] * (1 - dots[:, :, None]) + noise[:, :, None] * 255
        self.ink = np.clip(ink, 0, 255).astype(np.uint8)

    def sprite(self, time):
        settings = self.style["hand_drawn"]
        tick = math.floor(max(0, time - self.word["start"]) * settings["frequency"])
        if tick == self.tick:
            return self.cached
        mask = boil(self.mask, tick, self.index, settings, self.scale)
        fill = Image.fromarray(np.dstack((self.ink, np.asarray(mask))))
        if self.word["rotation"]:
            fill = fill.rotate(self.word["rotation"], Image.Resampling.BICUBIC, expand=True)
            mask = fill.getchannel("A")
        glow = self.style["glow"]
        spread = np.zeros((mask.height, mask.width), dtype=np.float32)
        for weight, radius in zip((0.2, 0.3, 0.5), glow["radii"]):
            spread += np.asarray(mask.filter(ImageFilter.GaussianBlur(radius * self.scale)), dtype=np.float32) * weight
        out = Image.new("RGBA", mask.size, rgb(self.word["color"], self.style) + (0,))
        out.putalpha(Image.fromarray(np.clip(spread * glow["exposure"], 0, 255).astype(np.uint8)))
        shadow = Image.new("RGBA", mask.size, rgb("burgundy", self.style) + (0,))
        # Apply shadow after word rotation, in canvas coordinates. Preserve fractional
        # distances with edge antialiasing; this introduces no shadow blur.
        distance = self.style["shadow"]["distance"] * self.scale
        shadow_mask = mask.transform(mask.size, Image.Transform.AFFINE,
                                     (1, 0, 0, 0, 1, -distance),
                                     resample=Image.Resampling.BILINEAR)
        shadow.putalpha(shadow_mask.point(lambda a: round(a * self.style["shadow"]["opacity"])))
        out = Image.alpha_composite(out, shadow)
        out = Image.alpha_composite(out, fill)
        self.tick, self.cached = tick, out
        return out


class Renderer:
    def __init__(self, resolved):
        self.scene = resolved
        self.style = resolved["style"]
        self.scale = resolved["width"] / self.style["reference_width"]
        self.sprites = [WordSprite(w, i, self.style, self.scale) for i, w in enumerate(resolved["words"])]

    def frame(self, time):
        scene = self.scene
        bg = (0, 0, 0, 0) if scene["background"] == "transparent" else rgb(scene["background"], self.style) + (255,)
        canvas = Image.new("RGBA", (scene["width"], scene["height"]), bg)
        for obj in self.sprites:
            word = obj.word
            if time <= word["start"] or time >= word["end"]:
                continue
            progress = ease((time - word["start"]) / word["entrance"])
            sprite = obj.sprite(time)
            if progress < 1:
                sprite = sprite.copy()
                sprite.putalpha(sprite.getchannel("A").point(lambda a: round(a * progress)))
            x = word["x"] + self.style["entrance"]["offset_right"] * self.scale * (1 - progress)
            canvas.alpha_composite(sprite, (round(x - sprite.width / 2), round(word["y"] - sprite.height / 2)))
        return canvas


def render_video(renderer, output):
    scene = renderer.scene
    if output.suffix.lower() == ".mp4":
        if scene["background"] == "transparent":
            raise ValueError("MP4 cannot preserve transparency; use MOV or PNG")
        if scene["width"] % 2 or scene["height"] % 2:
            raise ValueError("H.264 yuv420p MP4 needs even width and height")
        codec = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    elif output.suffix.lower() == ".mov":
        codec = ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16"]
    else:
        raise ValueError("Choose PNG, MP4, or MOV")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pixel_format", "rgba",
           "-video_size", f"{scene['width']}x{scene['height']}", "-framerate", str(scene["fps"]), "-i", "pipe:0", "-an"] + codec + [str(output)]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    count = math.ceil(scene["duration"] * scene["fps"])
    try:
        for n in range(count):
            process.stdin.write(renderer.frame(n / scene["fps"]).tobytes())
    except BrokenPipeError:
        pass
    finally:
        process.stdin.close()
    errors = process.stderr.read().decode("utf-8", errors="replace")
    if process.wait():
        raise RuntimeError("FFmpeg failed: " + errors[-2000:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--scene", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--poster", type=Path)
    parser.add_argument("--time", type=float, help="Scene timestamp for still/poster; default is settled")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(require_environment(), ensure_ascii=False, indent=2))
        return
    if not args.scene or not args.output:
        parser.error("--scene and --output are required")
    if args.scene.resolve() == args.output.resolve():
        raise ValueError("Output must not overwrite the scene input")
    require_environment(args.output.suffix.lower() != ".png")
    resolved = resolve_scene(json.loads(args.scene.read_text(encoding="utf-8")))
    renderer = Renderer(resolved)
    settled = max(w["start"] + w["entrance"] for w in resolved["words"])
    poster_time = args.time if args.time is not None else min(settled + 0.1, resolved["duration"] - 1 / resolved["fps"])
    if not 0 <= poster_time < resolved["duration"]:
        raise ValueError("Poster timestamp is outside the scene")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".png":
        renderer.frame(poster_time).save(args.output)
    else:
        render_video(renderer, args.output)
    if args.poster:
        args.poster.parent.mkdir(parents=True, exist_ok=True)
        renderer.frame(poster_time).save(args.poster)
    report = args.output.with_suffix(".layout.json")
    report.write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "poster": str(args.poster) if args.poster else None,
                      "layout": str(report), "words": len(resolved["words"]), "glow": resolved["glow_implementation"]}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

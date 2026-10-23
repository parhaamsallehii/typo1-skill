#!/usr/bin/env python3
"""Return deterministic placement of the original, untrimmed watermark PNG."""
import argparse
import hashlib
import json
from pathlib import Path

ASSET = Path(__file__).resolve().parents[1] / 'assets' / 'msy-watermark.png'
SHA256 = '5c4c880f7c6629b5e026dd4af398d2ea166a22fc8e71684943fdb246c6258a97'


def placement(width, height):
    if width <= 0 or height <= 0:
        raise ValueError('Canvas dimensions must be positive')
    k = min(width / 1080, height / 1920)
    side = max(1, int(472 * k + 0.5))
    cx, cy = width / 2, height * 1577 / 1920
    left = int(cx - side / 2 + 0.5)
    top = int(cy - side / 2 + 0.5)
    return {
        'canvas': [width, height], 'image_size': [side, side],
        'top_left': [left, top],
        'source_anchor': [1024, 1024],
        'center': [left + side / 2, top + side / 2],
        'source_scale_percent': side / 2048 * 100,
        'rotation_degrees': 0, 'opacity': 1,
        'blend': 'normal-source-over', 'trim_alpha_margins': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--width', type=int, default=1080)
    parser.add_argument('--height', type=int, default=1920)
    args = parser.parse_args()
    try:
        if hashlib.sha256(ASSET.read_bytes()).hexdigest() != SHA256:
            parser.error('Original watermark asset hash mismatch; do not substitute')
        result = placement(args.width, args.height)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    result.update(asset=str(ASSET), asset_sha256=SHA256)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

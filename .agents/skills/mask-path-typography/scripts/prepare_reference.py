#!/usr/bin/env python3
"""Reconstruct the byte-identical reference MP4 from bundled binary parts."""
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def main():
    info=json.loads((ROOT/'references/media/animation-parts.json').read_text())
    target=ROOT/'references/media/animation.mp4'
    if target.exists() and digest(target)==info['sha256']:
        print(target); return
    tmp=target.with_suffix('.mp4.rebuilding')
    try:
        with tmp.open('wb') as out:
            for part in info['parts']:
                p=ROOT/'references/media'/part['name']
                if p.stat().st_size!=part['bytes'] or digest(p)!=part['sha256']:
                    raise ValueError('Reference part checksum mismatch: '+part['name'])
                with p.open('rb') as f:
                    for block in iter(lambda:f.read(1024*1024),b''):out.write(block)
        if digest(tmp)!=info['sha256']:raise ValueError('Reconstructed reference checksum mismatch')
        os.replace(tmp,target)
    finally:
        if tmp.exists():tmp.unlink()
    print(target)

if __name__=='__main__':main()

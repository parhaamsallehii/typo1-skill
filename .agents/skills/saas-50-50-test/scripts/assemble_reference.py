#!/usr/bin/env python3
"""Restore a large original reference from lossless byte chunks, checking all SHA256s."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def assemble(manifest,output):
    manifest=manifest.resolve();output=output.resolve()
    data=json.loads(manifest.read_text())
    root=manifest.parent
    if root==output.parent or root in output.parents:
        raise ValueError('Restore to the task workspace, outside bundled source assets')
    if output.exists():
        if output.stat().st_size==data['size_bytes'] and digest(output)==data['sha256']:
            return output
        raise FileExistsError('Existing output differs; choose a new task path')
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=None
    try:
        full=hashlib.sha256();total=0
        with tempfile.NamedTemporaryFile(prefix=output.name+'.',dir=output.parent,delete=False) as target:
            tmp=Path(target.name)
            for row in data['parts']:
                path=(root/row['file']).resolve()
                if root not in path.parents:raise ValueError('Part escapes its asset directory')
                if path.stat().st_size!=row['size_bytes'] or digest(path)!=row['sha256']:
                    raise ValueError('Original chunk integrity failed: '+row['file'])
                with path.open('rb') as source:
                    for b in iter(lambda:source.read(1024*1024),b''):
                        target.write(b);full.update(b);total+=len(b)
        if total!=data['size_bytes'] or full.hexdigest()!=data['sha256']:
            raise ValueError('Restored reference differs from the original')
        os.replace(tmp,output);tmp=None
    finally:
        if tmp is not None:tmp.unlink(missing_ok=True)
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(assemble(args.manifest,args.output))

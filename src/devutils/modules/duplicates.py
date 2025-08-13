
from __future__ import annotations
from pathlib import Path
from hashlib import md5, sha1, sha256
from typing import List, Tuple


CHUNK = 1024 * 1024


def _hasher(name: str):
    name = name.lower()
    if name == 'md5':
        return md5
    if name == 'sha1':
        return sha1
    if name == 'sha256':
        return sha256
    return md5


def _hash_file(p: Path, algo: str) -> str:
    h = _hasher(algo)()
    with p.open('rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def find_duplicates(root: Path, min_size: int = 1, algo: str = 'md5') -> List[List[Tuple[Path, int]]]:
    files = []
    for p in root.rglob('*'):
        if p.is_file():
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size >= min_size:
                files.append((p, size))

    by_size = {}
    for p, size in files:
        by_size.setdefault(size, []).append(p)

    groups = []
    for size, same_size in by_size.items():
        if len(same_size) < 2:
            continue
        by_hash = {}
        for p in same_size:
            try:
                h = _hash_file(p, algo)
            except OSError:
                continue
            by_hash.setdefault(h, []).append(p)
        for h, dupes in by_hash.items():
            if len(dupes) > 1:
                groups.append([(p, size) for p in dupes])
    groups.sort(key=lambda g: g[0][1], reverse=True)
    return groups

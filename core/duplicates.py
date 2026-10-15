"""
Duplicate file finder.

Strategy (fast + correct):
  1. Group files by size (two files of different size can't be duplicates).
  2. Within each size group with more than one file, hash the files
     (SHA-256, read in chunks) and group by hash.
  3. Any hash group with more than one file is a set of duplicates.
"""
import os
import hashlib
from dataclasses import dataclass


@dataclass
class DuplicateGroup:
    file_hash: str
    size: int
    paths: list

    @property
    def wasted_space(self):
        # All but one copy is "wasted".
        return self.size * (len(self.paths) - 1)


def _hash_file(path, chunk_size=1024 * 1024):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def find_duplicates(path, progress_callback=None, cancel_event=None):
    """Return a list of DuplicateGroup, largest wasted space first."""
    size_groups = {}

    all_files = []
    for root, _dirs, files in os.walk(path):
        if cancel_event is not None and cancel_event.is_set():
            break
        for name in files:
            fp = os.path.join(root, name)
            all_files.append(fp)

    total = max(len(all_files), 1)

    for i, fp in enumerate(all_files, 1):
        if cancel_event is not None and cancel_event.is_set():
            break
        try:
            size = os.path.getsize(fp)
        except OSError:
            continue
        if size == 0:
            continue  # ignore empty files, they're not meaningful duplicates
        size_groups.setdefault(size, []).append(fp)

        if progress_callback:
            progress_callback(0.5 * i / total)  # first half of progress = listing

    candidates = [(size, paths) for size, paths in size_groups.items() if len(paths) > 1]
    hash_groups = {}
    total_candidates = sum(len(p) for _s, p in candidates) or 1
    done = 0

    for size, paths in candidates:
        for fp in paths:
            if cancel_event is not None and cancel_event.is_set():
                break
            file_hash = _hash_file(fp)
            done += 1
            if progress_callback:
                progress_callback(0.5 + 0.5 * done / total_candidates)
            if file_hash is None:
                continue
            key = (size, file_hash)
            hash_groups.setdefault(key, []).append(fp)

    groups = [
        DuplicateGroup(file_hash=h, size=size, paths=paths)
        for (size, h), paths in hash_groups.items()
        if len(paths) > 1
    ]
    groups.sort(key=lambda g: g.wasted_space, reverse=True)
    return groups

"""Disk scanning logic. Keeps a bounded list of the largest entries to avoid
holding every file path in memory when scanning very large drives.
"""
import heapq
import os
from dataclasses import dataclass, field

from core.utils import format_size  # re-exported for backward compatibility

MAX_RESULTS = 1000


@dataclass
class ScanResult:
    root: str
    total_size: int
    total_files: int
    total_folders: int
    largest_files: list          # [(size, path), ...]
    largest_folders: list        # [(path, own_size, total_size), ...]
    extension_totals: dict = field(default_factory=dict)


def scan(path, progress_callback=None, cancel_event=None):
    """Recursively calculate size statistics and retain up to 1,000 largest
    files and folders. Folder sizes include all nested sub-folders.
    """
    own_size = {}
    largest_file_heap = []
    extension_totals = {}
    total_size = total_files = total_folders = 0
    sequence = 0

    # Count directories in a lightweight first pass. Do not retain every
    # directory's file-name list: scanning a drive with a million files can
    # otherwise consume a surprising amount of RAM.
    total_steps = 0
    for _root, _dirs, _files in os.walk(path):
        if cancel_event is not None and cancel_event.is_set():
            break
        total_steps += 1
    total_steps = max(total_steps, 1)

    for i, (root, dirs, files) in enumerate(os.walk(path), 1):
        if cancel_event is not None and cancel_event.is_set():
            break
        total_folders += 1
        own_size.setdefault(root, 0)

        for name in files:
            if cancel_event is not None and cancel_event.is_set():
                break
            fp = os.path.join(root, name)
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            total_size += size
            total_files += 1
            own_size[root] += size
            sequence += 1
            candidate = (size, sequence, fp)
            if len(largest_file_heap) < MAX_RESULTS:
                heapq.heappush(largest_file_heap, candidate)
            elif size > largest_file_heap[0][0]:
                heapq.heapreplace(largest_file_heap, candidate)
            ext = os.path.splitext(name)[1].lower() or "(no extension)"
            extension_totals[ext] = extension_totals.get(ext, 0) + size

        if progress_callback:
            progress_callback(min(i / total_steps, 1.0))

    cumulative = dict(own_size)
    for root in sorted(cumulative.keys(), key=len, reverse=True):
        parent = os.path.dirname(root)
        if parent in cumulative and parent != root:
            cumulative[parent] += cumulative[root]

    largest_files = sorted(((size, path) for size, _seq, path in largest_file_heap), reverse=True, key=lambda item: item[0])
    largest_folders = sorted(
        ((folder, own_size.get(folder, 0), total) for folder, total in cumulative.items()),
        key=lambda item: item[2], reverse=True,
    )[:MAX_RESULTS]

    return ScanResult(
        root=path,
        total_size=total_size,
        total_files=total_files,
        total_folders=total_folders,
        largest_files=largest_files,
        largest_folders=largest_folders,
        extension_totals=extension_totals,
    )


if __name__ == "__main__":
    p = input("Folder: ").strip('"')
    r = scan(p, lambda v: print(f"\rScanning {v * 100:.0f}%", end=""))
    print("\nDone")
    print("Size:", format_size(r.total_size))
    print("Files:", r.total_files)
    print("Folders:", r.total_folders)
    print("Largest files:")
    for size, path in r.largest_files[:20]:
        print(format_size(size), path)

"""
Junk finder: empty folders, temp/cache files, and common junk artifacts
(Thumbs.db, .DS_Store, __pycache__, *.tmp, *.log, *.bak, ...).

Nothing is deleted automatically - this module only *finds* candidates.
Deletion always goes through `delete_items`, called from the UI after the
user picks what they want removed.
"""
import os
from dataclasses import dataclass

JUNK_EXTENSIONS = {".tmp", ".temp", ".log", ".bak", ".old", ".dmp", ".chk"}
JUNK_NAMES = {"Thumbs.db", ".DS_Store", "desktop.ini"}
JUNK_DIR_NAMES = {"__pycache__", ".cache", "$RECYCLE.BIN"}


@dataclass
class JunkItem:
    path: str
    kind: str      # "junk_file", "empty_folder", "junk_dir"
    size: int


def find_junk(path, progress_callback=None, cancel_event=None):
    items = []

    all_dirs = []
    for root, dirs, files in os.walk(path, topdown=True):
        if cancel_event is not None and cancel_event.is_set():
            break
        all_dirs.append((root, dirs, files))

    total = max(len(all_dirs), 1)

    for i, (root, dirs, files) in enumerate(all_dirs, 1):
        if cancel_event is not None and cancel_event.is_set():
            break

        # Junk directories (e.g. __pycache__) - measure their total size.
        for d in list(dirs):
            if d in JUNK_DIR_NAMES:
                full = os.path.join(root, d)
                size = _dir_size(full)
                items.append(JunkItem(path=full, kind="junk_dir", size=size))
                dirs.remove(d)  # don't walk into it separately

        # Junk / empty files, junk names, and empty folders.
        has_content = bool(files) or bool(dirs)
        for name in files:
            fp = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            if name in JUNK_NAMES or ext in JUNK_EXTENSIONS:
                items.append(JunkItem(path=fp, kind="junk_file", size=size))

        if not has_content:
            items.append(JunkItem(path=root, kind="empty_folder", size=0))

        if progress_callback:
            progress_callback(i / total)

    return items


def _dir_size(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                continue
    return total


def delete_items(items):
    """Delete the given JunkItem list. Returns (deleted, failed) path lists."""
    import shutil
    deleted, failed = [], []

    # Delete files/dirs before their parent empty-folder entries so that a
    # folder which becomes empty after removing junk files can still be
    # cleaned up if the user selected it too.
    files_first = sorted(items, key=lambda it: it.kind != "empty_folder")

    for item in files_first:
        try:
            if item.kind == "empty_folder" or item.kind == "junk_dir":
                if os.path.isdir(item.path):
                    shutil.rmtree(item.path)
                    deleted.append(item.path)
            else:
                if os.path.isfile(item.path):
                    os.remove(item.path)
                    deleted.append(item.path)
        except OSError:
            failed.append(item.path)

    return deleted, failed

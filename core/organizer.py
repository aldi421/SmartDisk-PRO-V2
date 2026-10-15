"""
File organizer: sorts loose files in a folder into category sub-folders
(Images, Documents, Videos, Music, Archives, Installers, Others) based on
their extension. Only files directly inside the chosen folder are moved
(sub-folders are left alone), so it's safe to point at something like a
Downloads folder.
"""
import os
import shutil

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".tiff", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v"},
    "Music": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".apk", ".deb", ".rpm"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".sh", ".ipynb"},
}


def _category_for(ext: str) -> str:
    ext = ext.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def preview_organize(path):
    """Return {category: [file_paths]} without moving anything."""
    plan = {}
    for name in os.listdir(path):
        fp = os.path.join(path, name)
        if os.path.isfile(fp):
            ext = os.path.splitext(name)[1]
            category = _category_for(ext)
            plan.setdefault(category, []).append(fp)
    return plan


def organize(path, progress_callback=None):
    """
    Move loose files in `path` into category sub-folders.
    Returns a list of (old_path, new_path) tuples for everything that was
    moved, so the caller can log it or offer an undo.
    """
    plan = preview_organize(path)
    moves = []

    all_files = [fp for files in plan.values() for fp in files]
    total = max(len(all_files), 1)
    done = 0

    for category, files in plan.items():
        dest_dir = os.path.join(path, category)
        os.makedirs(dest_dir, exist_ok=True)

        for fp in files:
            name = os.path.basename(fp)
            dest = os.path.join(dest_dir, name)

            # Avoid overwriting an existing file with the same name.
            if os.path.exists(dest):
                base, ext = os.path.splitext(name)
                counter = 1
                while os.path.exists(dest):
                    dest = os.path.join(dest_dir, f"{base} ({counter}){ext}")
                    counter += 1

            try:
                shutil.move(fp, dest)
                moves.append((fp, dest))
            except OSError:
                pass

            done += 1
            if progress_callback:
                progress_callback(done / total)

    return moves


def undo_moves(moves):
    """Move files back to where they came from. Best-effort."""
    restored = 0
    for old_path, new_path in reversed(moves):
        try:
            os.makedirs(os.path.dirname(old_path), exist_ok=True)
            shutil.move(new_path, old_path)
            restored += 1
        except OSError:
            pass
    return restored

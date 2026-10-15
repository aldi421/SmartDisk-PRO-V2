"""
Shared helper functions used across the app.
"""
import os
import sys
import subprocess
import platform


def format_size(size: float) -> str:
    """Convert a byte count into a human readable string (KB, MB, GB, ...)."""
    size = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def get_drives():
    """Return a list of available drive/mount roots on this system."""
    system = platform.system()
    drives = []

    if system == "Windows":
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
    else:
        # On macOS / Linux we just expose the root filesystem plus the
        # user's home directory, which covers the common case.
        drives.append("/")
        home = os.path.expanduser("~")
        if home and home != "/" and os.path.exists(home):
            drives.append(home)

    return drives or ["/"]


def open_in_file_manager(path: str):
    """Open the given file/folder in the OS's native file manager."""
    if not path:
        return
    target = path if os.path.isdir(path) else os.path.dirname(path)
    if not os.path.exists(target):
        return

    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(target)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", target])
        else:
            subprocess.Popen(["xdg-open", target])
    except Exception:
        pass


def safe_delete(path: str) -> bool:
    """Delete a file or an (empty or non-empty) folder. Returns True on success."""
    import shutil
    try:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except OSError:
        return False

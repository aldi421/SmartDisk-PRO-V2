"""Persistent settings stored in the user's AppData directory (writable in EXE builds)."""
import json
import os
import sys

DEFAULT_SETTINGS = {
    "appearance": "dark",
    "accent_color": "blue",
    "last_folder": "",
}


def _settings_path():
    appdata = os.environ.get("APPDATA")
    if appdata:
        folder = os.path.join(appdata, "SmartDiskAnalyzer")
    else:
        folder = os.path.join(os.path.expanduser("~"), ".smartdiskanalyzer")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "user_settings.json")


_SETTINGS_FILE = _settings_path()


def load_settings() -> dict:
    if os.path.exists(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data or {})
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    try:
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, indent=2, ensure_ascii=False)
    except OSError:
        pass

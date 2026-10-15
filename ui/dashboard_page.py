import shutil
import customtkinter as ctk

from core.utils import format_size, get_drives

BG = "#0A0D14"
PANEL = "#131A26"
PANEL_ALT = "#182131"
BORDER = "#263246"
TEXT = "#F1F5FB"
MUTED = "#8B9AB0"
ACCENT = "#5B8CFF"
TEAL = "#3DD6C6"


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        intro = ctk.CTkFrame(self, fg_color="transparent")
        intro.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(intro, text="Your storage, at a glance.", font=("Segoe UI", 26, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(intro, text="Monitor disk capacity and identify where your space is going.", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="w", pady=(5, 0))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 20))
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1, uniform="stats")
        self.card_used = self._make_card(stats, "SCANNED DATA", "—", "Total size in last scan", ACCENT, 0)
        self.card_files = self._make_card(stats, "FILES INDEXED", "—", "Files included in analysis", TEAL, 1)
        self.card_folders = self._make_card(stats, "FOLDERS VISITED", "—", "Folders included in analysis", "#B39DFF", 2)

        drive_header = ctk.CTkFrame(self, fg_color="transparent")
        drive_header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(drive_header, text="Disk health", font=("Segoe UI", 18, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkButton(drive_header, text="Refresh", width=88, height=30, corner_radius=8, fg_color=PANEL_ALT, hover_color=BORDER, command=self.refresh_drives).pack(side="right")

        self.drives_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.drives_frame.pack(fill="x")
        self.refresh_drives()

        self.summary = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=14, border_width=1, border_color=BORDER)
        self.summary.pack(fill="both", expand=True, pady=(20, 0))
        ctk.CTkLabel(self.summary, text="LATEST ANALYSIS", font=("Segoe UI", 10, "bold"), text_color=TEAL).pack(anchor="w", padx=18, pady=(16, 5))
        self.hint_label = ctk.CTkLabel(self.summary, text="No scan yet. Open Storage Analyzer and choose a folder to begin.", font=("Segoe UI", 13), text_color=MUTED, wraplength=820, justify="left")
        self.hint_label.pack(anchor="w", padx=18, pady=(0, 17))

    def _make_card(self, parent, title, value, subtitle, accent, column):
        frame = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=14, border_width=1, border_color=BORDER, height=128)
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0 if column == 2 else 8))
        frame.grid_propagate(False)
        ctk.CTkFrame(frame, width=4, height=46, corner_radius=2, fg_color=accent).place(x=0, y=20)
        ctk.CTkLabel(frame, text=title, font=("Segoe UI", 10, "bold"), text_color=MUTED).pack(anchor="w", padx=18, pady=(17, 3))
        value_label = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 25, "bold"), text_color=TEXT)
        value_label.pack(anchor="w", padx=18)
        ctk.CTkLabel(frame, text=subtitle, font=("Segoe UI", 10), text_color=MUTED).pack(anchor="w", padx=18, pady=(3, 0))
        frame.value = value_label
        return frame

    def refresh_drives(self):
        for widget in self.drives_frame.winfo_children():
            widget.destroy()
        drives = get_drives()
        for index, drive in enumerate(drives):
            try:
                usage = shutil.disk_usage(drive)
            except OSError:
                continue
            pct = usage.used / usage.total * 100 if usage.total else 0
            color = "#F0B45B" if pct >= 85 else ("#F17C86" if pct >= 95 else ACCENT)
            card = ctk.CTkFrame(self.drives_frame, fg_color=PANEL, corner_radius=14, border_width=1, border_color=BORDER, height=115)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10 if index < len(drives) - 1 else 0), pady=3)
            card.pack_propagate(False)
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(14, 4))
            ctk.CTkLabel(top, text=f"◉  {drive}", font=("Segoe UI", 13, "bold"), text_color=TEXT).pack(side="left")
            ctk.CTkLabel(top, text=f"{pct:.0f}% used", font=("Segoe UI", 11, "bold"), text_color=color).pack(side="right")
            bar = ctk.CTkProgressBar(card, height=7, progress_color=color, fg_color="#252F40")
            bar.pack(fill="x", padx=15, pady=(5, 7))
            bar.set(pct / 100 if usage.total else 0)
            ctk.CTkLabel(card, text=f"{format_size(usage.used)} used   ·   {format_size(usage.free)} free   ·   {format_size(usage.total)} total", font=("Segoe UI", 10), text_color=MUTED).pack(anchor="w", padx=15)

    def update_from_scan(self, result):
        self.card_used.value.configure(text=format_size(result.total_size))
        self.card_files.value.configure(text=f"{result.total_files:,}")
        self.card_folders.value.configure(text=f"{result.total_folders:,}")
        self.hint_label.configure(text=f"Last scanned folder: {result.root}\nIndexed {result.total_files:,} files across {result.total_folders:,} folders. Open Storage Analyzer to browse the largest files and folders.")
        self.refresh_drives()

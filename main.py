import os
import sys
import customtkinter as ctk

from core.settings import load_settings, save_settings
from ui.dashboard_page import DashboardPage
from ui.analyzer_page import AnalyzerPage
from ui.organizer_page import OrganizerPage
from ui.duplicate_page import DuplicatePage
from ui.cleaner_page import CleanerPage
from ui.insights_page import InsightsPage
from ui.settings_page import SettingsPage


COLORS = {
    "app": "#0A0D14",
    "sidebar": "#0E131D",
    "panel": "#131A26",
    "panel_alt": "#182131",
    "border": "#263246",
    "text": "#F1F5FB",
    "muted": "#8B9AB0",
    "accent": "#5B8CFF",
    "accent_hover": "#4777E8",
    "teal": "#3DD6C6",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        ctk.set_appearance_mode(self.settings.get("appearance", "dark"))
        ctk.set_default_color_theme("blue")

        self.title("SmartDiskAnalyzer | Storage Intelligence")
        self.geometry("1380x850")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["app"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.last_scan_result = None
        self.last_duplicate_groups = None
        self.last_junk_items = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=236, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(27, 30))
        ctk.CTkFrame(brand, width=42, height=42, corner_radius=13, fg_color=COLORS["accent"]).pack(side="left")
        mark = ctk.CTkLabel(brand, text="SD", font=("Segoe UI", 17, "bold"), text_color="white")
        mark.place(x=8, y=9)
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=12)
        ctk.CTkLabel(brand_text, text="SMARTDISK", font=("Segoe UI", 16, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(brand_text, text="STORAGE INTELLIGENCE", font=("Segoe UI", 9, "bold"), text_color=COLORS["muted"]).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(self.sidebar, text="WORKSPACE", font=("Segoe UI", 10, "bold"), text_color="#66758C").pack(anchor="w", padx=23, pady=(0, 10))
        self.nav_buttons = {}
        self.pages = {}
        self.main = ctk.CTkFrame(self, fg_color=COLORS["app"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # A restrained top bar gives every page a consistent app frame.
        topbar = ctk.CTkFrame(self.main, height=70, corner_radius=0, fg_color=COLORS["app"])
        topbar.grid(row=0, column=0, sticky="ew", padx=28, pady=(12, 0))
        topbar.grid_columnconfigure(0, weight=1)
        self.top_title = ctk.CTkLabel(topbar, text="Overview", font=("Segoe UI", 21, "bold"), text_color=COLORS["text"])
        self.top_title.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(topbar, text="LOCAL STORAGE  /  PRIVATE BY DESIGN", font=("Segoe UI", 10, "bold"), text_color=COLORS["muted"]).grid(row=0, column=1, sticky="e")
        ctk.CTkFrame(self.main, height=1, fg_color=COLORS["border"]).grid(row=0, column=0, sticky="sew", padx=28, pady=(67, 0))

        content = ctk.CTkFrame(self.main, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(18, 24))
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        self.content = content

        page_classes = [
            ("dashboard", "◈   Dashboard", "Overview", DashboardPage),
            ("analyzer", "⌕   Large Files Analyzer", "Storage Analyzer", AnalyzerPage),
            ("organizer", "▦   File Organizer", "File Organizer", OrganizerPage),
            ("duplicate", "⧉   Duplicate Finder", "Duplicate Finder", DuplicatePage),
            ("cleaner", "✧   Smart Cleaner", "Smart Cleaner", CleanerPage),
            ("insights", "◉   Smart Insights", "Smart Insights", InsightsPage),
            ("settings", "⚙   Settings", "Settings", SettingsPage),
        ]
        for key, label, title, page_cls in page_classes:
            button = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", height=43, corner_radius=10,
                font=("Segoe UI", 13, "bold"), text_color=COLORS["muted"],
                fg_color="transparent", hover_color=COLORS["panel_alt"],
                command=lambda k=key: self.show_page(k),
            )
            button.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[key] = button
            page = page_cls(content, self)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[key] = page

        sidebar_bottom = ctk.CTkFrame(self.sidebar, fg_color=COLORS["panel"], corner_radius=12)
        sidebar_bottom.pack(side="bottom", fill="x", padx=14, pady=18)
        ctk.CTkLabel(sidebar_bottom, text="●  SYSTEM READY", text_color=COLORS["teal"], font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=13, pady=(12, 3))
        ctk.CTkLabel(sidebar_bottom, text="Scans stay on this device", text_color=COLORS["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=13, pady=(0, 12))

        self.show_page("dashboard")

    def show_page(self, key):
        for page in self.pages.values():
            page.lower()
        self.pages[key].lift()
        titles = {
            "dashboard": "Overview", "analyzer": "Storage Analyzer", "organizer": "File Organizer",
            "duplicate": "Duplicate Finder", "cleaner": "Smart Cleaner", "insights": "Smart Insights", "settings": "Settings",
        }
        self.top_title.configure(text=titles.get(key, "SmartDiskAnalyzer"))
        for k, button in self.nav_buttons.items():
            active = k == key
            button.configure(
                fg_color=COLORS["panel_alt"] if active else "transparent",
                text_color=COLORS["text"] if active else COLORS["muted"],
                hover_color=COLORS["panel_alt"],
            )

    def on_scan_finished(self, result):
        self.last_scan_result = result
        self.pages["dashboard"].update_from_scan(result)

    def record_duplicates(self, groups):
        self.last_duplicate_groups = groups

    def record_junk(self, items):
        self.last_junk_items = items

    def on_close(self):
        save_settings(self.settings)
        self.destroy()


if __name__ == "__main__":
    App().mainloop()

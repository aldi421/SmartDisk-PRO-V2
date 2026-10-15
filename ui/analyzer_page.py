import csv
import os
import threading
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from core.analyzer import scan, format_size
from core.utils import open_in_file_manager

BG = "#0A0D14"
PANEL = "#131A26"
PANEL_ALT = "#182131"
BORDER = "#263246"
TEXT = "#F1F5FB"
MUTED = "#8B9AB0"
ACCENT = "#5B8CFF"


class AnalyzerPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.last_result = None
        self.cancel_event = None
        self.result_kind = "files"
        self.visible_limit = 100
        self.search_value = ctk.StringVar(value="")
        self.limit_value = ctk.StringVar(value="100")

        intro = ctk.CTkFrame(self, fg_color="transparent")
        intro.pack(fill="x", pady=(0, 17))
        ctk.CTkLabel(intro, text="Find what's taking up space.", font=("Segoe UI", 25, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(intro, text="Scan a folder and browse hundreds of the largest files or folders — not just a short top 10 list.", font=("Segoe UI", 12), text_color=MUTED).pack(anchor="w", pady=(5, 0))

        toolbar = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=13, border_width=1, border_color=BORDER)
        toolbar.pack(fill="x", pady=(0, 12))
        first_row = ctk.CTkFrame(toolbar, fg_color="transparent")
        first_row.pack(fill="x", padx=13, pady=(12, 8))
        self.scan_button = ctk.CTkButton(first_row, text="＋  Choose folder & scan", command=self.start_scan, width=190, height=37, corner_radius=9, font=("Segoe UI", 12, "bold"))
        self.scan_button.pack(side="left")
        self.cancel_button = ctk.CTkButton(first_row, text="Cancel scan", command=self.cancel_scan, width=110, height=37, corner_radius=9, fg_color="#63323B", hover_color="#7B3D48", state="disabled")
        self.cancel_button.pack(side="left", padx=(8, 14))
        self.progress = ctk.CTkProgressBar(first_row, height=8, progress_color=ACCENT, fg_color="#263246")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progress.set(0)
        self.status_label = ctk.CTkLabel(first_row, text="Ready", width=100, text_color=MUTED, font=("Segoe UI", 11))
        self.status_label.pack(side="right")

        second_row = ctk.CTkFrame(toolbar, fg_color="transparent")
        second_row.pack(fill="x", padx=13, pady=(0, 12))
        self.folder_label = ctk.CTkLabel(second_row, text="No folder selected", text_color=MUTED, font=("Segoe UI", 11), anchor="w")
        self.folder_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(second_row, text="Export CSV", width=100, height=30, corner_radius=8, fg_color=PANEL_ALT, hover_color=BORDER, command=self.export_csv).pack(side="right", padx=(8, 0))
        ctk.CTkButton(second_row, text="Open selected location", width=160, height=30, corner_radius=8, fg_color=PANEL_ALT, hover_color=BORDER, command=self.open_selected).pack(side="right")

        results_panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=13, border_width=1, border_color=BORDER)
        results_panel.pack(fill="both", expand=True)
        result_header = ctk.CTkFrame(results_panel, fg_color="transparent")
        result_header.pack(fill="x", padx=14, pady=(12, 8))
        self.result_title = ctk.CTkLabel(result_header, text="Largest files", font=("Segoe UI", 16, "bold"), text_color=TEXT)
        self.result_title.pack(side="left")
        self.result_count = ctk.CTkLabel(result_header, text="0 results", text_color=MUTED, font=("Segoe UI", 11))
        self.result_count.pack(side="left", padx=12)
        ctk.CTkLabel(result_header, text="Show", text_color=MUTED, font=("Segoe UI", 11)).pack(side="right", padx=(8, 5))
        self.limit_menu = ctk.CTkOptionMenu(result_header, values=["50", "100", "250", "500", "1000"], variable=self.limit_value, command=self._on_limit_change, width=92, height=30, corner_radius=8, fg_color=PANEL_ALT, button_color=ACCENT, button_hover_color="#4777E8")
        self.limit_menu.pack(side="right")
        self.search_entry = ctk.CTkEntry(result_header, textvariable=self.search_value, placeholder_text="Filter by file or folder name…", width=245, height=30, corner_radius=8, border_color=BORDER, fg_color="#0E141F")
        self.search_entry.pack(side="right", padx=(0, 10))
        self.search_value.trace_add("write", lambda *_: self._render_results())

        tab_row = ctk.CTkFrame(results_panel, fg_color="transparent")
        tab_row.pack(fill="x", padx=14, pady=(0, 8))
        self.files_tab = ctk.CTkButton(tab_row, text="Largest files", width=120, height=31, corner_radius=8, command=lambda: self.set_result_kind("files"))
        self.files_tab.pack(side="left")
        self.folders_tab = ctk.CTkButton(tab_row, text="Largest folders", width=130, height=31, corner_radius=8, fg_color=PANEL_ALT, hover_color=BORDER, command=lambda: self.set_result_kind("folders"))
        self.folders_tab.pack(side="left", padx=7)

        table_wrap = ctk.CTkFrame(results_panel, fg_color="transparent")
        table_wrap.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("SDA.Treeview", background="#0E141F", fieldbackground="#0E141F", foreground=TEXT, rowheight=31, borderwidth=0, font=("Segoe UI", 10))
        style.configure("SDA.Treeview.Heading", background=PANEL_ALT, foreground="#DCE6F5", relief="flat", font=("Segoe UI", 10, "bold"), padding=(8, 9))
        style.map("SDA.Treeview", background=[("selected", "#24447A")], foreground=[("selected", "#FFFFFF")])
        self.tree = ttk.Treeview(table_wrap, columns=("rank", "size", "path"), show="headings", style="SDA.Treeview", selectmode="browse")
        self.tree.heading("rank", text="#")
        self.tree.heading("size", text="SIZE")
        self.tree.heading("path", text="FILE / FOLDER PATH")
        self.tree.column("rank", width=55, minwidth=48, stretch=False, anchor="center")
        self.tree.column("size", width=125, minwidth=105, stretch=False, anchor="e")
        self.tree.column("path", width=600, minwidth=300, stretch=True, anchor="w")
        ybar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<Double-1>", lambda _event: self.open_selected())
        self.tree.bind("<Return>", lambda _event: self.open_selected())
        self._show_empty_state()

    def _show_empty_state(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=("—", "—", "Choose a folder and start a scan to view results"))
        self.result_count.configure(text="Waiting for scan")

    def start_scan(self):
        folder = filedialog.askdirectory(title="Choose a folder to analyze", initialdir=self.app.settings.get("last_folder") or os.path.expanduser("~"))
        if not folder:
            return
        self.app.settings["last_folder"] = folder
        self.folder_label.configure(text=folder, text_color=TEXT)
        self.progress.set(0)
        self.status_label.configure(text="Scanning…", text_color="#F0B45B")
        self.scan_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self._show_empty_state()
        self.cancel_event = threading.Event()
        threading.Thread(target=self._run_scan, args=(folder, self.cancel_event), daemon=True).start()

    def cancel_scan(self):
        if self.cancel_event:
            self.cancel_event.set()
            self.status_label.configure(text="Cancelling…", text_color="#F0B45B")
            self.cancel_button.configure(state="disabled")

    def _run_scan(self, folder, cancel_event):
        try:
            result = scan(folder, progress_callback=self._update_progress, cancel_event=cancel_event)
            error = None
        except Exception as exc:
            result = None
            error = str(exc)
        self.after(0, lambda: self._finish_scan(result, cancel_event, error))

    def _update_progress(self, value):
        self.after(0, lambda: self.progress.set(value))

    def _finish_scan(self, result, cancel_event, error=None):
        self.scan_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        if error:
            self.status_label.configure(text="Scan failed", text_color="#F17C86")
            messagebox.showerror("Scan failed", f"Could not finish scanning this folder.\n\n{error}")
            return
        self.last_result = result
        self.app.on_scan_finished(result)
        cancelled = cancel_event.is_set()
        self.progress.set(1 if not cancelled else self.progress.get())
        self.status_label.configure(text="Partial results" if cancelled else "Scan complete", text_color="#F0B45B" if cancelled else "#3DD6C6")
        self._render_results()

    def set_result_kind(self, kind):
        self.result_kind = kind
        self.files_tab.configure(fg_color=ACCENT if kind == "files" else PANEL_ALT, hover_color="#4777E8" if kind == "files" else BORDER)
        self.folders_tab.configure(fg_color=ACCENT if kind == "folders" else PANEL_ALT, hover_color="#4777E8" if kind == "folders" else BORDER)
        self.result_title.configure(text="Largest files" if kind == "files" else "Largest folders")
        self._render_results()

    def _on_limit_change(self, value):
        self.visible_limit = int(value)
        self._render_results()

    def _render_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not self.last_result:
            self._show_empty_state()
            return
        query = self.search_value.get().strip().casefold()
        if self.result_kind == "files":
            entries = [(size, path, None) for size, path in self.last_result.largest_files]
        else:
            entries = [(total, path, own) for path, own, total in self.last_result.largest_folders]
        if query:
            entries = [entry for entry in entries if query in entry[1].casefold()]
        shown = entries[:self.visible_limit]
        for index, (size, path, _own) in enumerate(shown, 1):
            self.tree.insert("", "end", values=(f"{index:03}", format_size(size), path))
        available = len(self.last_result.largest_files if self.result_kind == "files" else self.last_result.largest_folders)
        self.result_count.configure(text=f"{len(shown):,} shown · {available:,} indexed" + (f" · filtered" if query else ""))
        if not shown:
            self.tree.insert("", "end", values=("—", "—", "No results match this filter"))

    def _selected_path(self):
        selection = self.tree.selection()
        if not selection:
            return None
        values = self.tree.item(selection[0], "values")
        if len(values) < 3 or values[0] == "—":
            return None
        return values[2]

    def open_selected(self):
        path = self._selected_path()
        if path:
            open_in_file_manager(path)

    def export_csv(self):
        if not self.last_result:
            messagebox.showinfo("No results", "Run a scan before exporting results.")
            return
        filename = filedialog.asksaveasfilename(title="Export scan results", defaultextension=".csv", filetypes=[("CSV file", "*.csv")], initialfile="smartdisk-analysis.csv")
        if not filename:
            return
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.writer(handle)
                if self.result_kind == "files":
                    writer.writerow(["Rank", "Size (bytes)", "Size (readable)", "File path"])
                    entries = self.last_result.largest_files
                    for rank, (size, path) in enumerate(entries, 1):
                        writer.writerow([rank, size, format_size(size), path])
                else:
                    writer.writerow(["Rank", "Total size (bytes)", "Total size (readable)", "Direct files size (bytes)", "Folder path"])
                    for rank, (path, own, total) in enumerate(self.last_result.largest_folders, 1):
                        writer.writerow([rank, total, format_size(total), own, path])
            messagebox.showinfo("Export complete", f"Exported {len(entries) if self.result_kind == 'files' else len(self.last_result.largest_folders):,} records to:\n{filename}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

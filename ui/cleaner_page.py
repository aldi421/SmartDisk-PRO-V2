import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.cleaner import find_junk, delete_items
from core.utils import format_size

KIND_LABELS = {
    "junk_file": "File sampah",
    "empty_folder": "Folder kosong",
    "junk_dir": "Folder cache/junk",
}


class CleanerPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.selected_folder = None
        self.items = []
        self.checkbox_vars = {}

        ctk.CTkLabel(self, text="Cleaner", font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            self,
            text="Menemukan file sampah (*.tmp, *.log, Thumbs.db, __pycache__, dll) dan folder kosong.",
            text_color="gray",
        ).pack(anchor="w", pady=(0, 15))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(row, text="📁 Pilih Folder", command=self.pick_folder, width=160).pack(side="left")
        self.folder_label = ctk.CTkLabel(row, text="Belum ada folder dipilih", text_color="gray")
        self.folder_label.pack(side="left", padx=12)

        self.scan_button = ctk.CTkButton(row, text="🔍 Cari Sampah", command=self.start_scan, width=160, state="disabled")
        self.scan_button.pack(side="left", padx=8)

        self.progress = ctk.CTkProgressBar(self, width=700)
        self.progress.pack(anchor="w", pady=(0, 10))
        self.progress.set(0)

        self.summary_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 13, "bold"))
        self.summary_label.pack(anchor="w")

        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, pady=(10, 10))

        bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_row.pack(fill="x")

        ctk.CTkButton(bottom_row, text="Pilih Semua", width=110, command=lambda: self._set_all(True)).pack(side="left")
        ctk.CTkButton(bottom_row, text="Batal Pilih", width=110, command=lambda: self._set_all(False)).pack(side="left", padx=8)

        self.delete_button = ctk.CTkButton(
            bottom_row, text="🗑 Hapus yang Dipilih", command=self.delete_selected,
            fg_color="#8b3a3a", hover_color="#6e2d2d", state="disabled",
        )
        self.delete_button.pack(side="left", padx=8)

    # -------------------------------------------------------------------------
    def pick_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder untuk dibersihkan")
        if not folder:
            return
        self.selected_folder = folder
        self.folder_label.configure(text=folder)
        self.scan_button.configure(state="normal")

    def start_scan(self):
        if not self.selected_folder:
            return
        self.scan_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.progress.set(0)
        self.summary_label.configure(text="Mencari sampah...")
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.checkbox_vars.clear()

        threading.Thread(target=self._run_scan, args=(self.selected_folder,), daemon=True).start()

    def _run_scan(self, folder):
        items = find_junk(folder, progress_callback=self._update_progress)
        self.after(0, lambda: self._finish_scan(items))

    def _update_progress(self, value):
        self.after(0, lambda: self.progress.set(value))

    def _finish_scan(self, items):
        self.items = items
        self.scan_button.configure(state="normal")
        self.progress.set(1)

        for w in self.results_frame.winfo_children():
            w.destroy()
        self.checkbox_vars.clear()

        self.app.record_junk(items)

        if not items:
            self.summary_label.configure(text="Tidak ada sampah ditemukan. Rapi! 🎉")
            return

        total_size = sum(it.size for it in items)
        self.summary_label.configure(
            text=f"Ditemukan {len(items)} item - total {format_size(total_size)} (folder kosong tidak dihitung ukurannya)"
        )

        for item in items[:300]:
            row = ctk.CTkFrame(self.results_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            var = ctk.BooleanVar(value=True)
            self.checkbox_vars[item.path] = var

            label = f"[{KIND_LABELS.get(item.kind, item.kind)}] {item.path}"
            if item.size:
                label += f"  ({format_size(item.size)})"

            ctk.CTkCheckBox(row, text=label, variable=var).pack(anchor="w", padx=4)

        self.delete_button.configure(state="normal")

    def _set_all(self, value):
        for var in self.checkbox_vars.values():
            var.set(value)

    def delete_selected(self):
        selected_paths = {p for p, var in self.checkbox_vars.items() if var.get()}
        selected_items = [it for it in self.items if it.path in selected_paths]

        if not selected_items:
            messagebox.showinfo("Info", "Belum ada item yang dicentang.")
            return

        confirmed = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"{len(selected_items)} item akan dihapus permanen. Lanjutkan?",
        )
        if not confirmed:
            return

        deleted, failed = delete_items(selected_items)

        msg = f"{len(deleted)} item berhasil dihapus."
        if failed:
            msg += f"\n{len(failed)} item gagal dihapus (izin/terkunci)."
        messagebox.showinfo("Selesai", msg)

        self.start_scan()

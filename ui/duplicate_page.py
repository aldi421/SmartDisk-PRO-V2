import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.duplicates import find_duplicates
from core.utils import format_size, safe_delete


class DuplicatePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.selected_folder = None
        self.groups = []
        self.checkbox_vars = {}   # path -> BooleanVar

        ctk.CTkLabel(self, text="Duplicate Finder", font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            self, text="Mencari file yang isinya identik (dibandingkan lewat ukuran + hash SHA-256).",
            text_color="gray",
        ).pack(anchor="w", pady=(0, 15))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(row, text="📁 Pilih Folder", command=self.pick_folder, width=160).pack(side="left")
        self.folder_label = ctk.CTkLabel(row, text="Belum ada folder dipilih", text_color="gray")
        self.folder_label.pack(side="left", padx=12)

        self.scan_button = ctk.CTkButton(row, text="🔍 Cari Duplikat", command=self.start_scan, width=160, state="disabled")
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
        self.delete_button = ctk.CTkButton(
            bottom_row, text="🗑 Hapus yang Dipilih", command=self.delete_selected,
            fg_color="#8b3a3a", hover_color="#6e2d2d", state="disabled",
        )
        self.delete_button.pack(side="left")

    # -------------------------------------------------------------------------
    def pick_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder untuk dicek duplikatnya")
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
        self.summary_label.configure(text="Mencari duplikat...")
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.checkbox_vars.clear()

        threading.Thread(target=self._run_scan, args=(self.selected_folder,), daemon=True).start()

    def _run_scan(self, folder):
        groups = find_duplicates(folder, progress_callback=self._update_progress)
        self.after(0, lambda: self._finish_scan(groups))

    def _update_progress(self, value):
        self.after(0, lambda: self.progress.set(value))

    def _finish_scan(self, groups):
        self.groups = groups
        self.scan_button.configure(state="normal")
        self.progress.set(1)

        for w in self.results_frame.winfo_children():
            w.destroy()
        self.checkbox_vars.clear()

        if not groups:
            self.summary_label.configure(text="Tidak ditemukan file duplikat. 🎉")
            self.app.record_duplicates([])
            return

        total_wasted = sum(g.wasted_space for g in groups)
        self.summary_label.configure(
            text=f"Ditemukan {len(groups)} kelompok duplikat - potensi hemat {format_size(total_wasted)}"
        )
        self.app.record_duplicates(groups)

        for gi, group in enumerate(groups[:50]):
            box = ctk.CTkFrame(self.results_frame)
            box.pack(fill="x", pady=6, padx=2)

            ctk.CTkLabel(
                box,
                text=f"Grup {gi + 1} - {format_size(group.size)} tiap file, {len(group.paths)} salinan "
                     f"(boros {format_size(group.wasted_space)})",
                font=("Segoe UI", 13, "bold"),
            ).pack(anchor="w", padx=10, pady=(8, 4))

            for j, fp in enumerate(group.paths):
                var = ctk.BooleanVar(value=(j != 0))  # keep first copy unchecked by default
                self.checkbox_vars[fp] = var
                cb = ctk.CTkCheckBox(box, text=fp, variable=var)
                cb.pack(anchor="w", padx=25, pady=2)

        self.delete_button.configure(state="normal")

    def delete_selected(self):
        selected = [p for p, var in self.checkbox_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("Info", "Belum ada file yang dicentang untuk dihapus.")
            return

        confirmed = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"{len(selected)} file akan dihapus permanen. Lanjutkan?",
        )
        if not confirmed:
            return

        failed = []
        for fp in selected:
            if not safe_delete(fp):
                failed.append(fp)

        if failed:
            messagebox.showwarning("Sebagian gagal", f"{len(failed)} file gagal dihapus (izin/terkunci).")
        else:
            messagebox.showinfo("Selesai", f"{len(selected)} file berhasil dihapus.")

        # Re-scan to refresh the list.
        self.start_scan()

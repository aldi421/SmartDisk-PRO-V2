import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.organizer import preview_organize, organize, undo_moves


class OrganizerPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.selected_folder = None
        self.last_moves = []

        ctk.CTkLabel(self, text="Organizer", font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            self,
            text="Rapikan file lepas dalam sebuah folder ke sub-folder berdasarkan jenisnya\n"
                 "(Images, Documents, Videos, Music, Archives, Installers, Code, Others).",
            justify="left", text_color="gray",
        ).pack(anchor="w", pady=(0, 15))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(row, text="📁 Pilih Folder", command=self.pick_folder, width=160).pack(side="left")
        self.folder_label = ctk.CTkLabel(row, text="Belum ada folder dipilih", text_color="gray")
        self.folder_label.pack(side="left", padx=12)

        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        self.preview_button = ctk.CTkButton(row2, text="👁 Pratinjau", command=self.preview, width=140, state="disabled")
        self.preview_button.pack(side="left")

        self.organize_button = ctk.CTkButton(row2, text="🗂 Rapikan Sekarang", command=self.start_organize, width=180, state="disabled")
        self.organize_button.pack(side="left", padx=8)

        self.undo_button = ctk.CTkButton(row2, text="↩ Undo Terakhir", command=self.undo_last, width=140, state="disabled")
        self.undo_button.pack(side="left", padx=8)

        self.log = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.log.pack(fill="both", expand=True)
        self.log.insert("end", "Pilih folder, lalu klik 'Pratinjau' untuk melihat rencana, atau langsung 'Rapikan Sekarang'.\n")

    # -------------------------------------------------------------------------
    def pick_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder untuk dirapikan")
        if not folder:
            return
        self.selected_folder = folder
        self.folder_label.configure(text=folder)
        self.preview_button.configure(state="normal")
        self.organize_button.configure(state="normal")

    def preview(self):
        if not self.selected_folder:
            return
        plan = preview_organize(self.selected_folder)
        self.log.delete("1.0", "end")
        if not plan:
            self.log.insert("end", "Tidak ada file lepas untuk dirapikan di folder ini.\n")
            return

        self.log.insert("end", f"Rencana untuk: {self.selected_folder}\n\n")
        for category, files in sorted(plan.items()):
            self.log.insert("end", f"📂 {category}  ({len(files)} file)\n")
            for fp in files[:5]:
                self.log.insert("end", f"    - {fp}\n")
            if len(files) > 5:
                self.log.insert("end", f"    ... dan {len(files) - 5} file lainnya\n")
            self.log.insert("end", "\n")

    def start_organize(self):
        if not self.selected_folder:
            return
        confirmed = messagebox.askyesno(
            "Konfirmasi",
            f"File lepas di\n{self.selected_folder}\nakan dipindahkan ke sub-folder berdasarkan jenisnya. Lanjutkan?",
        )
        if not confirmed:
            return

        self.organize_button.configure(state="disabled")
        self.log.delete("1.0", "end")
        self.log.insert("end", "🗂 Merapikan file...\n\n")

        threading.Thread(target=self._run_organize, args=(self.selected_folder,), daemon=True).start()

    def _run_organize(self, folder):
        moves = organize(folder)
        self.after(0, lambda: self._finish_organize(moves))

    def _finish_organize(self, moves):
        self.last_moves = moves
        self.organize_button.configure(state="normal")
        self.undo_button.configure(state="normal" if moves else "disabled")

        self.log.delete("1.0", "end")
        if not moves:
            self.log.insert("end", "Tidak ada file yang perlu dirapikan.\n")
            return

        self.log.insert("end", f"✅ {len(moves)} file berhasil dirapikan:\n\n")
        for old, new in moves:
            self.log.insert("end", f"{old}\n  → {new}\n\n")

    def undo_last(self):
        if not self.last_moves:
            return
        restored = undo_moves(self.last_moves)
        self.log.insert("end", f"\n↩ {restored} file dikembalikan ke lokasi semula.\n")
        self.last_moves = []
        self.undo_button.configure(state="disabled")

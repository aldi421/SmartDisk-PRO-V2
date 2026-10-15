import customtkinter as ctk

from core.settings import save_settings


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Settings", font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(0, 20))

        # Appearance
        ctk.CTkLabel(self, text="Tampilan", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        appearance_row = ctk.CTkFrame(self, fg_color="transparent")
        appearance_row.pack(anchor="w", pady=(0, 20))

        self.appearance_var = ctk.StringVar(value=self.app.settings.get("appearance", "dark"))
        ctk.CTkSegmentedButton(
            appearance_row,
            values=["dark", "light"],
            variable=self.appearance_var,
            command=self.change_appearance,
        ).pack(side="left")

        # Accent color
        ctk.CTkLabel(self, text="Warna Aksen (perlu restart aplikasi)", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        accent_row = ctk.CTkFrame(self, fg_color="transparent")
        accent_row.pack(anchor="w", pady=(0, 20))

        self.accent_var = ctk.StringVar(value=self.app.settings.get("accent_color", "blue"))
        ctk.CTkSegmentedButton(
            accent_row,
            values=["blue", "green", "dark-blue"],
            variable=self.accent_var,
            command=self.change_accent,
        ).pack(side="left")

        # Last folder info
        ctk.CTkLabel(self, text="Folder Terakhir Digunakan", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        self.last_folder_label = ctk.CTkLabel(
            self, text=self.app.settings.get("last_folder") or "-", text_color="gray",
        )
        self.last_folder_label.pack(anchor="w", pady=(0, 20))

        ctk.CTkButton(self, text="💾 Simpan Pengaturan", command=self.save, width=180).pack(anchor="w")
        self.status_label = ctk.CTkLabel(self, text="", text_color="lightgreen")
        self.status_label.pack(anchor="w", pady=(10, 0))

    def change_appearance(self, value):
        ctk.set_appearance_mode(value)
        self.app.settings["appearance"] = value

    def change_accent(self, value):
        self.app.settings["accent_color"] = value
        self.status_label.configure(text="Warna aksen akan berlaku setelah aplikasi dibuka ulang.")

    def save(self):
        save_settings(self.app.settings)
        self.status_label.configure(text="✅ Pengaturan tersimpan.")

import customtkinter as ctk

from core.insights import generate_insights


class InsightsPage(ctk.CTkFrame):
    """Rule-based recommendations built from whatever the user has already
    scanned (Analyzer / Duplicate Finder / Cleaner). This is heuristic logic,
    not a live call to an external AI model."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="🤖 AI Assistant", font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            self,
            text="Rekomendasi otomatis berbasis aturan (rule-based), dibuat dari hasil scan yang sudah kamu jalankan.\n"
                 "Bukan chatbot - jalankan Analyzer/Duplicate Finder/Cleaner dulu, lalu buka halaman ini.",
            text_color="gray", justify="left",
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkButton(self, text="🔄 Perbarui Rekomendasi", command=self.refresh, width=200).pack(anchor="w", pady=(0, 15))

        self.box = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.box.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        for w in self.box.winfo_children():
            w.destroy()

        tips = generate_insights(
            scan_result=self.app.last_scan_result,
            duplicate_groups=self.app.last_duplicate_groups,
            junk_items=self.app.last_junk_items,
        )

        for tip in tips:
            card = ctk.CTkFrame(self.box)
            card.pack(fill="x", pady=6, padx=2)
            ctk.CTkLabel(card, text=tip, justify="left", wraplength=850).pack(anchor="w", padx=15, pady=12)

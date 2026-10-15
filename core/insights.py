"""
"Smart Insights" - a rule-based recommendation engine.

Note: this is deliberately NOT hooked up to any external AI/LLM API (that
would need the user's own API key). It looks at the numbers from a scan /
duplicate search / junk search and turns them into plain-language tips.
"""
from core.utils import format_size


def generate_insights(scan_result=None, duplicate_groups=None, junk_items=None):
    tips = []

    if scan_result is not None and scan_result.total_size > 0:
        top_folders = scan_result.largest_folders[:3]
        for folder, _own, total in top_folders:
            share = total / scan_result.total_size * 100
            if share >= 10:
                tips.append(
                    f"📁 '{folder}' menghabiskan {format_size(total)} "
                    f"({share:.0f}% dari total yang dipindai). Cek isinya kalau mau bebaskan ruang cepat."
                )

        if scan_result.extension_totals:
            ext, size = max(scan_result.extension_totals.items(), key=lambda kv: kv[1])
            if size / scan_result.total_size > 0.15:
                tips.append(
                    f"🎞️ File berekstensi {ext} mendominasi, totalnya {format_size(size)}."
                )

    if duplicate_groups:
        wasted = sum(g.wasted_space for g in duplicate_groups)
        if wasted > 0:
            tips.append(
                f"📑 Ditemukan {len(duplicate_groups)} kelompok file duplikat, "
                f"berpotensi menghemat {format_size(wasted)} kalau salinan berlebih dihapus."
            )

    if junk_items:
        total_junk = sum(it.size for it in junk_items)
        empty_folders = sum(1 for it in junk_items if it.kind == "empty_folder")
        if total_junk > 0:
            tips.append(
                f"🧹 Ada file/folder sampah sekitar {format_size(total_junk)} "
                f"yang bisa dibersihkan lewat menu Cleaner."
            )
        if empty_folders:
            tips.append(f"📂 {empty_folders} folder kosong ditemukan dan aman untuk dihapus.")

    if not tips:
        tips.append("✅ Belum ada data yang cukup. Jalankan Analyzer, Duplicate Finder, atau Cleaner dulu untuk mendapatkan rekomendasi.")

    return tips

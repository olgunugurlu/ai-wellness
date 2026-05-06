def get_top_priorities(scores: dict, flags: list) -> list[dict]:
    priorities = []

    # 1. KRİTİK flagler her zaman önce gelir
    critical = [f for f in flags if f.priority == "KRİTİK"]
    for f in critical[:2]:
        priorities.append({
            "title":  f.message,
            "action": f.action,
            "level":  "KRİTİK",
            "icon":   "🔴"
        })

    # 2. En düşük skorlu kategoriler
    score_map = {
        "metabolic":   ("Metabolik Sağlık",     "🔬"),
        "cardio":      ("Kardiyovasküler",       "❤️"),
        "msk":         ("Kas-İskelet",           "🦴"),
        "nutrition":   ("Beslenme",              "🥗"),
        "mental":      ("Zihinsel Sağlık",       "🧠"),
        "performance": ("Fiziksel Performans",   "🏋️"),
    }

    sorted_scores = sorted(
        [(k, v) for k, v in scores.items() if k != "overall"],
        key=lambda x: x[1]
    )

    high_flags = [f for f in flags if f.priority == "YÜKSEK"]

    for cat, score in sorted_scores:
        if len(priorities) >= 3:
            break
        if score < 70:
            label, icon = score_map[cat]
            # Bu kategoriye ait flag var mı?
            related_flag = next(
                (f for f in high_flags if cat[:4].upper() in f.code),
                None
            )
            action = related_flag.action if related_flag else f"{label} skorun düşük — detaylı değerlendirme gerek"
            priorities.append({
                "title":  f"{label} skoru düşük ({score}/100)",
                "action": action,
                "level":  "YÜKSEK" if score < 50 else "ORTA",
                "icon":   icon
            })

    # 3. Yeterli öncelik yoksa genel öneri ekle
    if not priorities:
        priorities.append({
            "title":  "Genel sağlık durumun iyi görünüyor",
            "action": "Mevcut alışkanlıklarını sürdür, düzenli takip yap",
            "level":  "DÜŞÜK",
            "icon":   "✅"
        })

    return priorities[:3]
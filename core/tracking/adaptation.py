def check_adaptations(checkins: list) -> list:
    if len(checkins) < 3:
        return []

    alerts = []
    last3  = checkins[-3:]
    last7  = checkins[-7:] if len(checkins) >= 7 else checkins

    # ── UYKU ──────────────────────────────────────────────
    sleep_last3 = [c["sleep_hours"] for c in last3 if c.get("sleep_hours")]
    if sleep_last3 and all(s < 6 for s in sleep_last3):
        alerts.append({
            "type":    "warning",
            "icon":    "😴",
            "title":   "Uyku Uyarısı",
            "message": "3 gün üst üste 6 saatten az uyudun.",
            "action":  "Antrenman hacmini %20–30 azalt, uyku hijyenine odaklan."
        })

    # ── ENERJİ ────────────────────────────────────────────
    energy_last3 = [c["energy"] for c in last3 if c.get("energy")]
    if energy_last3 and all(e < 4 for e in energy_last3):
        alerts.append({
            "type":    "warning",
            "icon":    "⚡",
            "title":   "Düşük Enerji",
            "message": "3 gün üst üste enerji seviyesi çok düşük.",
            "action":  "Kalori alımını kontrol et, demir ve B12 değerlerini gözden geçir."
        })

    # ── STRES ─────────────────────────────────────────────
    stress_last3 = [c["stress"] for c in last3 if c.get("stress")]
    if stress_last3 and all(s >= 8 for s in stress_last3):
        alerts.append({
            "type":    "warning",
            "icon":    "😰",
            "title":   "Yüksek Stres",
            "message": "3 gün üst üste stres seviyesi çok yüksek.",
            "action":  "Yoğunluğu düşür, nefes egzersizleri ve yürüyüş ekle."
        })

    # ── AĞRI ──────────────────────────────────────────────
    pain_last3 = [c["pain_level"] for c in last3 if c.get("pain_level")]
    if pain_last3 and any(p >= 7 for p in pain_last3):
        alerts.append({
            "type":    "danger",
            "icon":    "🔴",
            "title":   "Yüksek Ağrı",
            "message": f"Ağrı seviyesi {max(pain_last3)}/10'a ulaştı.",
            "action":  "İlgili egzersizleri durdur, fizyoterapist değerlendirmesi önerilir."
        })

    # ── ANTRENMAN UYUMU ───────────────────────────────────
    if len(last7) >= 7:
        workouts = sum(1 for c in last7 if c.get("workout_done"))
        if workouts == 0:
            alerts.append({
                "type":    "info",
                "icon":    "🏋️",
                "title":   "Antrenman Yok",
                "message": "Son 7 günde hiç antrenman yapılmadı.",
                "action":  "Planına geri dön. Kısa 20 dk bir yürüyüşle başlayabilirsin."
            })

    # ── BESLENME UYUMU ────────────────────────────────────
    nutrition_last5 = [c["nutrition_compliance"] for c in checkins[-5:]
                       if c.get("nutrition_compliance") is not None]
    if nutrition_last5 and sum(nutrition_last5) / len(nutrition_last5) < 50:
        alerts.append({
            "type":    "info",
            "icon":    "🥗",
            "title":   "Beslenme Uyumu Düşük",
            "message": "Son 5 günde beslenme uyumu %50'nin altında.",
            "action":  "Planını sadeleştir. Hazırlık yapılabilecek kolay tarifler dene."
        })

    # ── OLUMLU GERİ BİLDİRİM ─────────────────────────────
    if len(last7) >= 7:
        workouts_7 = sum(1 for c in last7 if c.get("workout_done"))
        if workouts_7 >= 5:
            alerts.append({
                "type":    "success",
                "icon":    "🏆",
                "title":   "Harika Antrenman Uyumu!",
                "message": f"Son 7 günde {workouts_7} antrenman yaptın.",
                "action":  "Bu tempoya devam et! Yük artırmayı düşünebilirsin."
            })

    avg_energy_7 = sum(c["energy"] for c in last7 if c.get("energy")) / max(len([c for c in last7 if c.get("energy")]), 1)
    if avg_energy_7 >= 7:
        alerts.append({
            "type":    "success",
            "icon":    "⚡",
            "title":   "Enerji Yüksek!",
            "message": f"Son 7 günde ortalama enerji {avg_energy_7:.1f}/10.",
            "action":  "Harika! Antrenman yoğunluğunu artırmak için iyi bir dönem."
        })

    return alerts
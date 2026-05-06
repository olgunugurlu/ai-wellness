from dataclasses import dataclass, field

@dataclass
class Flag:
    code:     str
    priority: str   # KRİTİK / YÜKSEK / ORTA / DÜŞÜK
    message:  str
    action:   str

def run_rules(profile, health, lifestyle, nutrition, performance) -> list[Flag]:
    flags = []

    def add(code, priority, message, action):
        flags.append(Flag(code, priority, message, action))

    # ── SAĞLIK KONTROLLÜ ─────────────────────────────────
    if health:
        # Metabolik risk
        if health.get("hba1c") and health["hba1c"] >= 5.7:
            add("META_01", "KRİTİK",
                f"HbA1c yüksek ({health['hba1c']}%) — metabolik risk",
                "Düşük GI beslenme, endokrin değerlendirmesi")

        if health.get("fasting_glucose") and health["fasting_glucose"] >= 100:
            add("META_02", "YÜKSEK",
                f"Açlık glukozu yüksek ({health['fasting_glucose']} mg/dL)",
                "Şeker ve rafine karbonhidrat kısıtlaması")

        # Tiroid
        if health.get("tsh"):
            if health["tsh"] > 4.0:
                add("TIRO_01", "YÜKSEK",
                    f"TSH yüksek ({health['tsh']}) — hipotiroidi şüphesi",
                    "Endokrin yönlendirmesi, yorgunluk protokolü")
            elif health["tsh"] < 0.4:
                add("TIRO_02", "YÜKSEK",
                    f"TSH düşük ({health['tsh']}) — hipertiroidi şüphesi",
                    "Endokrin yönlendirmesi, yoğun egzersizden kaç")

        # Vitamin D
        if health.get("vitamin_d"):
            if health["vitamin_d"] < 20:
                add("VIT_01", "YÜKSEK",
                    f"Vitamin D çok düşük ({health['vitamin_d']} ng/mL)",
                    "Yüksek doz D3+K2, güneş maruziyeti")
            elif health["vitamin_d"] < 30:
                add("VIT_02", "ORTA",
                    f"Vitamin D yetersiz ({health['vitamin_d']} ng/mL)",
                    "D3 takviyesi başla")

        # B12
        if health.get("b12") and health["b12"] < 300:
            add("VIT_03", "YÜKSEK",
                f"B12 düşük ({health['b12']} pg/mL)",
                "Metilkobalamin takviyesi")

        # Ferritin
        if health.get("ferritin") and health["ferritin"] < 15:
            add("IRON_01", "YÜKSEK",
                f"Ferritin çok düşük ({health['ferritin']} ng/mL)",
                "Demir protokolü, C vitamini kombinasyonu")

        # CRP
        if health.get("crp"):
            if health["crp"] > 3:
                add("INF_01", "YÜKSEK",
                    f"CRP yüksek ({health['crp']} mg/L) — kronik inflamasyon",
                    "Antiinflamatuar beslenme, omega-3")
            elif health["crp"] > 1:
                add("INF_02", "ORTA",
                    f"CRP artmış ({health['crp']} mg/L)",
                    "İşlenmiş gıda azalt, omega-3 ekle")

        # Omega-3 eksikliği tahmini
        if nutrition and nutrition.get("fish_per_week", 0) < 1:
            if health.get("crp") and health["crp"] > 1:
                add("NUTR_01", "ORTA",
                    "Balık tüketimi düşük + CRP yüksek → omega-3 eksikliği",
                    "Omega-3 takviyesi (EPA+DHA 2-3g/gün)")

        # Enerji düşüklüğü
        if health.get("energy_morning", 10) < 4 and health.get("energy_afternoon", 10) < 4:
            add("ENER_01", "YÜKSEK",
                "Sabah ve öğleden sonra enerji çok düşük",
                "Tiroid, ferritin, B12 tarama; uyku önceliklendirme")

        # Uyku kalitesi
        if health.get("sleep_quality", 10) < 5:
            add("SLEEP_01", "YÜKSEK",
                f"Uyku kalitesi düşük ({health['sleep_quality']}/10)",
                "Uyku hijyeni protokolü, magnezyum takviyesi")

        # Uyku süresi
        if health.get("sleep_duration_hrs", 8) < 6:
            add("SLEEP_02", "KRİTİK",
                f"Uyku süresi çok kısa ({health['sleep_duration_hrs']} saat)",
                "Antrenman hacmini %30 azalt, uyku önceliklendir")

        # Ruh hali / psikoloji
        if health.get("mood_score", 10) < 4:
            add("PSYC_01", "YÜKSEK",
                f"Ruh hali düşük ({health['mood_score']}/10)",
                "Psikososyal destek değerlendirmesi")

        # Odak
        if health.get("focus_score", 10) < 4:
            add("COG_01", "ORTA",
                f"Odak skoru düşük ({health['focus_score']}/10)",
                "Uyku, beslenme, tiroid kontrolü")

    # ── YAŞAM TARZI ──────────────────────────────────────
    if lifestyle:
        # Stres
        avg_stress = (
            (lifestyle.get("stress_morning", 0) or 0) +
            (lifestyle.get("stress_afternoon", 0) or 0) +
            (lifestyle.get("stress_evening", 0) or 0)
        ) / 3
        if avg_stress >= 7:
            add("STRESS_01", "YÜKSEK",
                f"Ortalama stres yüksek ({avg_stress:.1f}/10)",
                "Stres yönetimi protokolü, adaptogen takviyesi")

        # Tükenmişlik + PHQ-2
        if lifestyle.get("burnout"):
            add("BURN_01", "KRİTİK",
                "Tükenmişlik belirtisi var",
                "Uzman yönlendirmesi, iş yükü azaltma")

        if lifestyle.get("phq2_score") and lifestyle["phq2_score"] >= 3:
            add("PHQ_01", "KRİTİK",
                f"PHQ-2 pozitif ({lifestyle['phq2_score']})",
                "Ruh sağlığı uzmanı yönlendirmesi")

        # Adım sayısı
        if lifestyle.get("daily_steps", 10000) < 5000:
            add("MOVE_01", "ORTA",
                f"Günlük adım sayısı düşük ({lifestyle['daily_steps']})",
                "Günde minimum 7000 adım hedefle")

        # Oturma süresi
        if lifestyle.get("sitting_hrs_day", 0) and lifestyle["sitting_hrs_day"] > 8:
            add("MOVE_02", "ORTA",
                f"Günlük oturma süresi fazla ({lifestyle['sitting_hrs_day']} saat)",
                "Her saat 5 dk hareket molası")

    # ── BESLENME ─────────────────────────────────────────
    if nutrition:
        if nutrition.get("water_liters", 3) < 1.5:
            add("NUTR_02", "ORTA",
                f"Su tüketimi düşük ({nutrition['water_liters']} litre)",
                "Günde minimum 2 litre su hedefle")

        if nutrition.get("vegetable_portions", 5) < 3:
            add("NUTR_03", "ORTA",
                "Sebze/meyve tüketimi yetersiz",
                "Her öğüne 1 porsiyon sebze ekle")

        if nutrition.get("processed_food_freq") in ["3–5/hafta", "Günlük"]:
            add("NUTR_04", "ORTA",
                "İşlenmiş gıda tüketimi fazla",
                "İşlenmiş gıdayı haftada maksimum 2'ye indir")

        if nutrition.get("fastfood_per_week", 0) >= 3:
            add("NUTR_05", "ORTA",
                f"Fastfood tüketimi yüksek ({nutrition['fastfood_per_week']}x/hafta)",
                "Ev yemeği oranını artır")

    # ── PERFORMANS ────────────────────────────────────────
    if performance:
        if performance.get("training_days_per_week", 3) == 0:
            add("PERF_01", "YÜKSEK",
                "Hiç antrenman yapılmıyor",
                "Haftada 3 gün 30 dk yürüyüşle başla")

        if performance.get("vo2max_estimate") and performance["vo2max_estimate"] < 30:
            add("PERF_02", "YÜKSEK",
                f"VO2max düşük ({performance['vo2max_estimate']})",
                "Zone 2 kardiyo haftada 3x")

    return flags
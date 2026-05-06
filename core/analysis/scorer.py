def calculate_scores(profile, health, lifestyle, nutrition, performance, flags) -> dict:

    critical_flags = [f for f in flags if f.priority == "KRİTİK"]
    high_flags     = [f for f in flags if f.priority == "YÜKSEK"]

    # ── METABOLİK SKOR ────────────────────────────────────
    metabolic = 100
    if health:
        if health.get("hba1c"):
            if health["hba1c"] >= 6.5:   metabolic -= 30
            elif health["hba1c"] >= 5.7: metabolic -= 15
        if health.get("fasting_glucose"):
            if health["fasting_glucose"] >= 126: metabolic -= 20
            elif health["fasting_glucose"] >= 100: metabolic -= 10
        if health.get("tsh"):
            if health["tsh"] > 4.0 or health["tsh"] < 0.4: metabolic -= 15
        if health.get("vitamin_d"):
            if health["vitamin_d"] < 20:  metabolic -= 15
            elif health["vitamin_d"] < 30: metabolic -= 8
        if health.get("ferritin") and health["ferritin"] < 15:
            metabolic -= 10
        if health.get("energy_morning"):
            metabolic -= max(0, (5 - health["energy_morning"]) * 3)

    # ── KARDİYOVASKÜLER SKOR ──────────────────────────────
    cardio = 100
    if health:
        if health.get("triglyceride"):
            if health["triglyceride"] >= 200: cardio -= 20
            elif health["triglyceride"] >= 150: cardio -= 10
        if health.get("hdl"):
            if health["hdl"] < 40:  cardio -= 20
            elif health["hdl"] < 50: cardio -= 10
        if health.get("ldl") and health["ldl"] >= 160:
            cardio -= 15
        if health.get("crp"):
            if health["crp"] > 3:   cardio -= 20
            elif health["crp"] > 1: cardio -= 10
    if performance:
        if performance.get("vo2max_estimate"):
            if performance["vo2max_estimate"] >= 50:  cardio += 10
            elif performance["vo2max_estimate"] < 30: cardio -= 20
            elif performance["vo2max_estimate"] < 40: cardio -= 10
        if performance.get("training_days_per_week", 0) == 0:
            cardio -= 15
    if lifestyle:
        steps = lifestyle.get("daily_steps", 7000) or 7000
        if steps < 5000:    cardio -= 10
        elif steps > 10000: cardio += 5

    # ── KAS-İSKELET SKORU ─────────────────────────────────
    msk = 100
    pain_flags = [f for f in flags if "ağrı" in f.message.lower()]
    msk -= len(pain_flags) * 15
    if health:
        if health.get("muscle_fatigue") and health["muscle_fatigue"] >= 7:
            msk -= 15
    if performance:
        if performance.get("sit_reach_cm") is not None and performance["sit_reach_cm"] < 10:
            msk -= 10
        if performance.get("pushup_max") is not None and performance["pushup_max"] < 10:
            msk -= 10

    # ── BESLENME SKORU ────────────────────────────────────
    nutrition_score = 100
    if nutrition:
        if nutrition.get("vegetable_portions", 5) < 3:
            nutrition_score -= 15
        if nutrition.get("processed_food_freq") in ["3–5/hafta", "Günlük"]:
            nutrition_score -= 20
        if nutrition.get("sugary_drinks_freq") == "Günlük":
            nutrition_score -= 15
        if nutrition.get("fastfood_per_week", 0) >= 3:
            nutrition_score -= 15
        if nutrition.get("water_liters") and nutrition["water_liters"] < 1.5:
            nutrition_score -= 10
        if nutrition.get("fish_per_week", 2) < 1:
            nutrition_score -= 10
        if nutrition.get("whole_grain_freq") == "Hiç":
            nutrition_score -= 10

    # ── ZİHİNSEL SKOR ────────────────────────────────────
    mental = 100
    if health:
        if health.get("mood_score"):
            mental -= max(0, (5 - health["mood_score"]) * 5)
        if health.get("sleep_quality"):
            mental -= max(0, (5 - health["sleep_quality"]) * 4)
    if lifestyle:
        if lifestyle.get("burnout"):
            mental -= 25
        if lifestyle.get("phq2_score") and lifestyle["phq2_score"] >= 3:
            mental -= 30
        avg_stress = (
            (lifestyle.get("stress_morning", 5) or 5) +
            (lifestyle.get("stress_afternoon", 5) or 5) +
            (lifestyle.get("stress_evening", 5) or 5)
        ) / 3
        mental -= max(0, (avg_stress - 5) * 4)
        if lifestyle.get("social_support") == "İzole":
            mental -= 15
        elif lifestyle.get("social_support") == "Zayıf":
            mental -= 8

    # ── PERFORMANS SKORU ──────────────────────────────────
    perf_score = 100
    if performance:
        if performance.get("training_days_per_week", 3) == 0:
            perf_score -= 30
        elif performance.get("training_days_per_week", 3) < 2:
            perf_score -= 15
        if performance.get("vo2max_estimate"):
            if performance["vo2max_estimate"] < 30:   perf_score -= 25
            elif performance["vo2max_estimate"] < 40: perf_score -= 10
        if performance.get("pushup_max") is not None and performance["pushup_max"] < 10:
            perf_score -= 10
        if performance.get("plank_sec") is not None and performance["plank_sec"] < 30:
            perf_score -= 10

    # ── KRİTİK FLAG CEZASI ───────────────────────────────
    critical_penalty = len(critical_flags) * 10
    high_penalty     = len(high_flags) * 5

    def clamp(x): return max(0, min(100, x))

    metabolic       = clamp(metabolic       - critical_penalty)
    cardio          = clamp(cardio          - critical_penalty)
    msk             = clamp(msk             - critical_penalty)
    nutrition_score = clamp(nutrition_score - high_penalty)
    mental          = clamp(mental          - critical_penalty)
    perf_score      = clamp(perf_score      - high_penalty)

    overall = round(
        metabolic       * 0.25 +
        cardio          * 0.20 +
        msk             * 0.15 +
        nutrition_score * 0.20 +
        mental          * 0.10 +
        perf_score      * 0.10
    )

    return {
        "metabolic":   round(metabolic),
        "cardio":      round(cardio),
        "msk":         round(msk),
        "nutrition":   round(nutrition_score),
        "mental":      round(mental),
        "performance": round(perf_score),
        "overall":     overall
    }
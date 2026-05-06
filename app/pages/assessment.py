import streamlit as st
from config.database import get_connection

PREFIX = "ai_wellness_"

def get_or_create_user(name, email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT id FROM {PREFIX}users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user:
        conn.close()
        return user["id"]
    cursor.execute(f"INSERT INTO {PREFIX}users (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def save_profile(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {PREFIX}profiles 
            (user_id, age, gender, height_cm, weight_kg, waist_cm, hip_cm,
             body_fat_pct, muscle_mass_kg, resting_hr, activity_level, occupation_type, city)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            age=VALUES(age), gender=VALUES(gender), height_cm=VALUES(height_cm),
            weight_kg=VALUES(weight_kg), waist_cm=VALUES(waist_cm), hip_cm=VALUES(hip_cm),
            body_fat_pct=VALUES(body_fat_pct), muscle_mass_kg=VALUES(muscle_mass_kg),
            resting_hr=VALUES(resting_hr), activity_level=VALUES(activity_level),
            occupation_type=VALUES(occupation_type), city=VALUES(city)
    """, (
        user_id, data["age"], data["gender"], data["height_cm"], data["weight_kg"],
        data["waist_cm"], data["hip_cm"], data["body_fat_pct"], data["muscle_mass_kg"],
        data["resting_hr"], data["activity_level"], data["occupation_type"], data["city"]
    ))
    conn.commit()
    conn.close()

def save_health(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {PREFIX}health
            (user_id, energy_morning, energy_afternoon, sleep_quality, sleep_duration_hrs,
             sleep_onset_min, focus_score, digestion_score, mood_score, libido,
             headache_per_week, cold_hands_feet, muscle_fatigue,
             hba1c, fasting_glucose, insulin, tsh, free_t3, free_t4,
             vitamin_d, b12, ferritin, crp, homocysteine, testosterone, estradiol,
             triglyceride, hdl, ldl, alt, ast, creatinine,
             alcohol_frequency, smoking_status, caffeine_per_day)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            energy_morning=VALUES(energy_morning), energy_afternoon=VALUES(energy_afternoon),
            sleep_quality=VALUES(sleep_quality), sleep_duration_hrs=VALUES(sleep_duration_hrs),
            sleep_onset_min=VALUES(sleep_onset_min), focus_score=VALUES(focus_score),
            digestion_score=VALUES(digestion_score), mood_score=VALUES(mood_score),
            libido=VALUES(libido), headache_per_week=VALUES(headache_per_week),
            cold_hands_feet=VALUES(cold_hands_feet), muscle_fatigue=VALUES(muscle_fatigue),
            hba1c=VALUES(hba1c), fasting_glucose=VALUES(fasting_glucose),
            insulin=VALUES(insulin), tsh=VALUES(tsh), free_t3=VALUES(free_t3),
            free_t4=VALUES(free_t4), vitamin_d=VALUES(vitamin_d), b12=VALUES(b12),
            ferritin=VALUES(ferritin), crp=VALUES(crp), homocysteine=VALUES(homocysteine),
            testosterone=VALUES(testosterone), estradiol=VALUES(estradiol),
            triglyceride=VALUES(triglyceride), hdl=VALUES(hdl), ldl=VALUES(ldl),
            alt=VALUES(alt), ast=VALUES(ast), creatinine=VALUES(creatinine),
            alcohol_frequency=VALUES(alcohol_frequency), smoking_status=VALUES(smoking_status),
            caffeine_per_day=VALUES(caffeine_per_day)
    """, (
        user_id,
        data["energy_morning"], data["energy_afternoon"], data["sleep_quality"],
        data["sleep_duration_hrs"], data["sleep_onset_min"], data["focus_score"],
        data["digestion_score"], data["mood_score"], data["libido"],
        data["headache_per_week"], data["cold_hands_feet"], data["muscle_fatigue"],
        data.get("hba1c"), data.get("fasting_glucose"), data.get("insulin"),
        data.get("tsh"), data.get("free_t3"), data.get("free_t4"),
        data.get("vitamin_d"), data.get("b12"), data.get("ferritin"),
        data.get("crp"), data.get("homocysteine"), data.get("testosterone"),
        data.get("estradiol"), data.get("triglyceride"), data.get("hdl"),
        data.get("ldl"), data.get("alt"), data.get("ast"), data.get("creatinine"),
        data["alcohol_frequency"], data["smoking_status"], data["caffeine_per_day"]
    ))
    conn.commit()
    conn.close()

def save_diseases(user_id, diseases):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {PREFIX}diseases WHERE user_id = %s", (user_id,))
    for d in diseases:
        cursor.execute(f"INSERT INTO {PREFIX}diseases (user_id, disease) VALUES (%s, %s)", (user_id, d))
    conn.commit()
    conn.close()

def save_pain_map(user_id, pains):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {PREFIX}pain_map WHERE user_id = %s", (user_id,))
    for p in pains:
        cursor.execute(f"""
            INSERT INTO {PREFIX}pain_map
                (user_id, region, severity, pain_character, duration_type,
                 pain_trigger, radiates, worsened_by, relieved_by, previous_treatment)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id, p["region"], p["severity"], p["pain_character"],
            p["duration_type"], p["pain_trigger"], p["radiates"],
            p["worsened_by"], p["relieved_by"], p["previous_treatment"]
        ))
    conn.commit()
    conn.close()

def save_lifestyle(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {PREFIX}lifestyle
            (user_id, bedtime, wake_time, sleep_hrs, sleep_onset_min, night_wakings,
             snoring, screen_before_bed_hrs, stress_morning, stress_afternoon, stress_evening,
             stress_work, stress_family, stress_financial, stress_health, stress_social,
             cope_exercise, cope_meditation, cope_social, cope_eating, cope_isolation, cope_none,
             mindfulness_experience, pss10_score, gad7_score, phq2_score,
             burnout, social_support, daily_steps, sitting_hrs_day, transport_type, wearable_device)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            bedtime=VALUES(bedtime), wake_time=VALUES(wake_time),
            sleep_hrs=VALUES(sleep_hrs), sleep_onset_min=VALUES(sleep_onset_min),
            night_wakings=VALUES(night_wakings), snoring=VALUES(snoring),
            screen_before_bed_hrs=VALUES(screen_before_bed_hrs),
            stress_morning=VALUES(stress_morning), stress_afternoon=VALUES(stress_afternoon),
            stress_evening=VALUES(stress_evening), stress_work=VALUES(stress_work),
            stress_family=VALUES(stress_family), stress_financial=VALUES(stress_financial),
            stress_health=VALUES(stress_health), stress_social=VALUES(stress_social),
            cope_exercise=VALUES(cope_exercise), cope_meditation=VALUES(cope_meditation),
            cope_social=VALUES(cope_social), cope_eating=VALUES(cope_eating),
            cope_isolation=VALUES(cope_isolation), cope_none=VALUES(cope_none),
            mindfulness_experience=VALUES(mindfulness_experience),
            pss10_score=VALUES(pss10_score), gad7_score=VALUES(gad7_score),
            phq2_score=VALUES(phq2_score), burnout=VALUES(burnout),
            social_support=VALUES(social_support), daily_steps=VALUES(daily_steps),
            sitting_hrs_day=VALUES(sitting_hrs_day), transport_type=VALUES(transport_type),
            wearable_device=VALUES(wearable_device)
    """, (
        user_id,
        data["bedtime"], data["wake_time"], data["sleep_hrs"], data["sleep_onset_min"],
        data["night_wakings"], data["snoring"], data["screen_before_bed_hrs"],
        data["stress_morning"], data["stress_afternoon"], data["stress_evening"],
        data["stress_work"], data["stress_family"], data["stress_financial"],
        data["stress_health"], data["stress_social"],
        data["cope_exercise"], data["cope_meditation"], data["cope_social"],
        data["cope_eating"], data["cope_isolation"], data["cope_none"],
        data["mindfulness_experience"], data.get("pss10_score"), data.get("gad7_score"),
        data.get("phq2_score"), data["burnout"], data["social_support"],
        data["daily_steps"], data["sitting_hrs_day"], data["transport_type"],
        data["wearable_device"]
    ))
    conn.commit()
    conn.close()

def save_nutrition(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {PREFIX}nutrition
            (user_id, diet_type, meals_per_day, first_meal_time, last_meal_time,
             water_liters, vegetable_portions, whole_grain_freq,
             red_meat_per_week, chicken_per_week, fish_per_week, egg_per_week,
             dairy_per_week, legume_per_week, processed_food_freq, sugary_drinks_freq,
             fastfood_per_week, cooking_habit, budget_level,
             daily_calories_est, protein_g, carb_g, fat_g, fiber_g, disliked_foods)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            diet_type=VALUES(diet_type), meals_per_day=VALUES(meals_per_day),
            first_meal_time=VALUES(first_meal_time), last_meal_time=VALUES(last_meal_time),
            water_liters=VALUES(water_liters), vegetable_portions=VALUES(vegetable_portions),
            whole_grain_freq=VALUES(whole_grain_freq), red_meat_per_week=VALUES(red_meat_per_week),
            chicken_per_week=VALUES(chicken_per_week), fish_per_week=VALUES(fish_per_week),
            egg_per_week=VALUES(egg_per_week), dairy_per_week=VALUES(dairy_per_week),
            legume_per_week=VALUES(legume_per_week), processed_food_freq=VALUES(processed_food_freq),
            sugary_drinks_freq=VALUES(sugary_drinks_freq), fastfood_per_week=VALUES(fastfood_per_week),
            cooking_habit=VALUES(cooking_habit), budget_level=VALUES(budget_level),
            daily_calories_est=VALUES(daily_calories_est), protein_g=VALUES(protein_g),
            carb_g=VALUES(carb_g), fat_g=VALUES(fat_g), fiber_g=VALUES(fiber_g),
            disliked_foods=VALUES(disliked_foods)
    """, (
        user_id,
        data["diet_type"], data["meals_per_day"], data["first_meal_time"], data["last_meal_time"],
        data["water_liters"], data["vegetable_portions"], data["whole_grain_freq"],
        data["red_meat_per_week"], data["chicken_per_week"], data["fish_per_week"],
        data["egg_per_week"], data["dairy_per_week"], data["legume_per_week"],
        data["processed_food_freq"], data["sugary_drinks_freq"], data["fastfood_per_week"],
        data["cooking_habit"], data["budget_level"],
        data.get("daily_calories_est"), data.get("protein_g"), data.get("carb_g"),
        data.get("fat_g"), data.get("fiber_g"), data.get("disliked_foods")
    ))
    conn.commit()
    conn.close()

def save_food_restrictions(user_id, restrictions):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {PREFIX}food_restrictions WHERE user_id = %s", (user_id,))
    for r in restrictions:
        cursor.execute(
            f"INSERT INTO {PREFIX}food_restrictions (user_id, type, item) VALUES (%s,%s,%s)",
            (user_id, r["type"], r["item"])
        )
    conn.commit()
    conn.close()

def save_performance(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {PREFIX}performance
            (user_id, training_experience_mo, training_days_per_week, training_location,
             current_training_type, session_duration_min,
             pref_weights, pref_cardio, pref_yoga, pref_swimming, pref_cycling, pref_running, pref_other,
             disliked_exercises, sport_branch, goal,
             pushup_max, squat_max, plank_sec, run_km_time_min,
             vo2max_estimate, hrv_ms, sit_reach_cm, shoulder_flex, ankle_dorsiflexion_cm)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            training_experience_mo=VALUES(training_experience_mo),
            training_days_per_week=VALUES(training_days_per_week),
            training_location=VALUES(training_location),
            current_training_type=VALUES(current_training_type),
            session_duration_min=VALUES(session_duration_min),
            pref_weights=VALUES(pref_weights), pref_cardio=VALUES(pref_cardio),
            pref_yoga=VALUES(pref_yoga), pref_swimming=VALUES(pref_swimming),
            pref_cycling=VALUES(pref_cycling), pref_running=VALUES(pref_running),
            pref_other=VALUES(pref_other), disliked_exercises=VALUES(disliked_exercises),
            sport_branch=VALUES(sport_branch), goal=VALUES(goal),
            pushup_max=VALUES(pushup_max), squat_max=VALUES(squat_max),
            plank_sec=VALUES(plank_sec), run_km_time_min=VALUES(run_km_time_min),
            vo2max_estimate=VALUES(vo2max_estimate), hrv_ms=VALUES(hrv_ms),
            sit_reach_cm=VALUES(sit_reach_cm), shoulder_flex=VALUES(shoulder_flex),
            ankle_dorsiflexion_cm=VALUES(ankle_dorsiflexion_cm)
    """, (
        user_id,
        data["training_experience_mo"], data["training_days_per_week"], data["training_location"],
        data["current_training_type"], data["session_duration_min"],
        data["pref_weights"], data["pref_cardio"], data["pref_yoga"],
        data["pref_swimming"], data["pref_cycling"], data["pref_running"], data.get("pref_other"),
        data.get("disliked_exercises"), data.get("sport_branch"), data["goal"],
        data.get("pushup_max"), data.get("squat_max"), data.get("plank_sec"),
        data.get("run_km_time_min"), data.get("vo2max_estimate"), data.get("hrv_ms"),
        data.get("sit_reach_cm"), data.get("shoulder_flex"), data.get("ankle_dorsiflexion_cm")
    ))
    conn.commit()
    conn.close()


# ─── ANA FORM ──────────────────────────────────────────────
def show(current_user=None):
    st.title("📋 Sağlık Değerlendirme Formu")
    st.caption("Tüm alanları doldurman gerekmez — elimdeki veriyle sana en iyi planı üretirim.")

    # ── KULLANICI BİLGİSİ ──
    st.subheader("👤 Kullanıcı Bilgisi")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Adın", key="k201")
    with col2:
        email = st.text_input("E-posta", key="k202")

    st.divider()
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧍 Demografi", "🏥 Sağlık", "🌙 Yaşam Tarzı", "🥗 Beslenme", "🏋️ Performans"
    ])

    # ════════════════════════════════
    # SEKME 1 — DEMOGRAFİ
    # ════════════════════════════════
    with tab1:
        st.subheader("Temel Bilgiler")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Yaş", 18, 90, 30, key="k203")
            height_cm = st.number_input("Boy (cm)", 140, 220, 170, key="k204")
            waist_cm = st.number_input("Bel Çevresi (cm) — opsiyonel", 0, 200, 0, key="k205")
        with col2:
            gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Belirtmek istemiyorum"], key="k206")
            weight_kg = st.number_input("Kilo (kg)", 40, 200, 70, key="k207")
            hip_cm = st.number_input("Kalça Çevresi (cm) — opsiyonel", 0, 200, 0, key="k208")
        with col3:
            activity_level = st.selectbox("Aktivite Seviyesi", [
                "Sedanter", "Az Aktif", "Orta Aktif", "Çok Aktif", "Sporcu"
            ], key="k009")
            body_fat_pct = st.number_input("Yağ Oranı (%) — opsiyonel", 0.0, 60.0, 0.0, key="k209")
            muscle_mass_kg = st.number_input("Kas Kütlesi (kg) — opsiyonel", 0.0, 100.0, 0.0, key="k210")

        col1, col2, col3 = st.columns(3)
        with col1:
            resting_hr = st.number_input("Dinlenik Nabız (BPM) — opsiyonel", 0, 120, 0, key="k211")
        with col2:
            occupation_type = st.selectbox("Meslek Tipi", [
                "Oturarak", "Ayakta", "Ağır Fiziksel İş"
            ], key="k013")
        with col3:
            city = st.text_input("Şehir", key="k212")

    # ════════════════════════════════
    # SEKME 2 — SAĞLIK
    # ════════════════════════════════
    with tab2:
        st.subheader("Semptomlar")
        col1, col2 = st.columns(2)
        with col1:
            energy_morning   = st.slider("Sabah Enerji (0–10)", 0, 10, 5, key="k213")
            sleep_quality    = st.slider("Uyku Kalitesi (0–10)", 0, 10, 5, key="k214")
            focus_score      = st.slider("Odak & Konsantrasyon (0–10)", 0, 10, 5, key="k215")
            mood_score       = st.slider("Ruh Hali (0–10)", 0, 10, 5, key="k216")
            muscle_fatigue   = st.slider("Kas Yorgunluğu (0–10)", 0, 10, 3, key="k217")
        with col2:
            energy_afternoon = st.slider("Öğleden Sonra Enerji (0–10)", 0, 10, 5, key="k218")
            sleep_duration_hrs = st.number_input("Uyku Süresi (saat)", 0.0, 12.0, 7.0, 0.5, key="k219")
            sleep_onset_min  = st.number_input("Uykuya Dalma Süresi (dk)", 0, 120, 15, key="k220")
            digestion_score  = st.slider("Sindirim (0–10, 10=sorunsuz)", 0, 10, 7, key="k221")
            headache_per_week = st.number_input("Baş Ağrısı (gün/hafta)", 0, 7, 0, key="k222")

        col1, col2, col3 = st.columns(3)
        with col1:
            libido = st.selectbox("Libido", ["Normal", "Düşük", "Yüksek"], key="k223")
        with col2:
            cold_hands_feet = st.checkbox("El/Ayaklarda Soğukluk", key="k224")
        with col3:
            alcohol_frequency = st.selectbox("Alkol", ["Yok", "Hafif (1–2/hafta)", "Orta (3–5/hafta)", "Ağır"], key="k225")
            smoking_status    = st.selectbox("Sigara", ["Hiç kullanmadım", "Bıraktım", "Kullanıyorum"], key="k226")
            caffeine_per_day  = st.number_input("Günlük Kafein (bardak)", 0, 10, 1, key="k227")

        st.subheader("Hastalıklar")
        disease_options = [
            "Tip 2 Diyabet", "Tip 1 Diyabet", "Hipertansiyon", "Hipotiroidi",
            "Hipertiroidi", "PCOS", "Gut", "Osteoporoz", "Reflü/GERD",
            "IBS", "Kardiyovasküler Hastalık", "Depresyon/Anksiyete",
            "Kronik Ağrı/Fibromiyalji", "Astım/KOAH", "Böbrek Hastalığı"
        ]
        selected_diseases = st.multiselect("Mevcut hastalıklarını seç", disease_options, key="k228")

        st.subheader("Ağrı Haritası")
        pain_count = st.number_input("Kaç farklı bölgede ağrın var?", 0, 5, 0, key="k229")
        pains = []
        for i in range(pain_count):
            st.markdown(f"**Ağrı #{i+1}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                region   = st.selectbox(f"Bölge #{i+1}", ["Bel", "Boyun", "Diz", "Omuz", "Kalça", "Dirsek", "Ayak Bileği", "Diğer"], key=f"region_{i}")
                severity = st.slider(f"Şiddet #{i+1} (0–10)", 0, 10, 5, key=f"sev_{i}")
            with c2:
                pain_character = st.selectbox(f"Karakter #{i+1}", ["Keskin", "Künt", "Yanma", "Sızlama", "Uyuşma"], key=f"char_{i}")
                duration_type  = st.selectbox(f"Süre #{i+1}", ["Akut (<4 hafta)", "Subakut (4–12 hafta)", "Kronik (>3 ay)"], key=f"dur_{i}")
            with c3:
                pain_trigger = st.selectbox(f"Tetikleyici #{i+1}", ["Hareket", "Oturma", "Sabah", "Gece", "Sürekli"], key=f"trig_{i}")
                radiates     = st.checkbox(f"Yayılıyor mu? #{i+1}", key=f"rad_{i}")
            worsened_by        = st.text_input(f"Kötüleştiren #{i+1}", key=f"worse_{i}")
            relieved_by        = st.text_input(f"İyileştiren #{i+1}", key=f"relief_{i}")
            previous_treatment = st.text_input(f"Önceki Tedavi #{i+1}", key=f"treat_{i}")
            pains.append({
                "region": region, "severity": severity, "pain_character": pain_character,
                "duration_type": duration_type, "pain_trigger": pain_trigger, "radiates": radiates,
                "worsened_by": worsened_by, "relieved_by": relieved_by,
                "previous_treatment": previous_treatment
            })

        st.subheader("Kan Değerleri (opsiyonel)")
        st.caption("Varsa gir, yoksa boş bırak — sistem elimdeki veriyle çalışır.")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            hba1c          = st.number_input("HbA1c (%)", 0.0, 15.0, 0.0, key="k230")
            fasting_glucose = st.number_input("Açlık Glukozu (mg/dL)", 0.0, 400.0, 0.0, key="k231")
            insulin        = st.number_input("İnsülin (µU/mL)", 0.0, 100.0, 0.0, key="k232")
            tsh            = st.number_input("TSH (mIU/L)", 0.0, 20.0, 0.0, key="k233")
            free_t3        = st.number_input("Serbest T3", 0.0, 10.0, 0.0, key="k234")
            free_t4        = st.number_input("Serbest T4", 0.0, 10.0, 0.0, key="k235")
        with col2:
            vitamin_d      = st.number_input("Vitamin D (ng/mL)", 0.0, 150.0, 0.0, key="k236")
            b12            = st.number_input("B12 (pg/mL)", 0.0, 2000.0, 0.0, key="k237")
            ferritin       = st.number_input("Ferritin (ng/mL)", 0.0, 500.0, 0.0, key="k238")
            crp            = st.number_input("CRP (mg/L)", 0.0, 50.0, 0.0, key="k239")
            homocysteine   = st.number_input("Homosistein (µmol/L)", 0.0, 50.0, 0.0, key="k240")
        with col3:
            testosterone   = st.number_input("Testosteron (ng/dL)", 0.0, 1200.0, 0.0, key="k241")
            estradiol      = st.number_input("Östradiol (pg/mL)", 0.0, 500.0, 0.0, key="k242")
            triglyceride   = st.number_input("Trigliserit (mg/dL)", 0.0, 500.0, 0.0, key="k243")
            hdl            = st.number_input("HDL (mg/dL)", 0.0, 150.0, 0.0, key="k244")
            ldl            = st.number_input("LDL (mg/dL)", 0.0, 300.0, 0.0, key="k245")
        with col4:
            alt            = st.number_input("ALT (U/L)", 0.0, 200.0, 0.0, key="k246")
            ast            = st.number_input("AST (U/L)", 0.0, 200.0, 0.0, key="k247")
            creatinine     = st.number_input("Kreatinin", 0.0, 10.0, 0.0, key="k248")

    # ════════════════════════════════
    # SEKME 3 — YAŞAM TARZI
    # ════════════════════════════════
    with tab3:
        st.subheader("Uyku")
        col1, col2, col3 = st.columns(3)
        with col1:
            bedtime            = st.text_input("Yatış Saati (örn. 23:30)", "23:00", key="k249")
            sleep_hrs          = st.number_input("Uyku Süresi (saat)", 0.0, 12.0, 7.0, 0.5, key="k250")
            night_wakings      = st.number_input("Gece Uyanma (kez)", 0, 10, 0, key="k251")
        with col2:
            wake_time          = st.text_input("Kalkış Saati (örn. 07:00)", "07:00", key="k252")
            sleep_onset_min_ls = st.number_input("Uykuya Dalma (dk)", 0, 120, 15, key="ls_onset")
            screen_before_bed  = st.number_input("Yatmadan Önce Ekran (saat)", 0.0, 5.0, 1.0, 0.5, key="k253")
        with col3:
            snoring            = st.checkbox("Horlama / Apne", key="k254")

        st.subheader("Stres")
        col1, col2, col3 = st.columns(3)
        with col1:
            stress_morning   = st.slider("Sabah Stresi (0–10)", 0, 10, 4, key="k255")
        with col2:
            stress_afternoon = st.slider("Öğleden Sonra Stresi (0–10)", 0, 10, 5, key="k256")
        with col3:
            stress_evening   = st.slider("Akşam Stresi (0–10)", 0, 10, 4, key="k257")

        st.markdown("**Stres Kaynakları**")
        col1, col2, col3, col4, col5 = st.columns(5)
        stress_work      = col1.checkbox("İş",      key="k110")
        stress_family    = col2.checkbox("Aile",    key="k111")
        stress_financial = col3.checkbox("Mali",    key="k112")
        stress_health    = col4.checkbox("Sağlık",  key="k113")
        stress_social    = col5.checkbox("Sosyal",  key="k114")

        st.markdown("**Baş Etme Yöntemleri**")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        cope_exercise   = col1.checkbox("Egzersiz",    key="k115")
        cope_meditation = col2.checkbox("Meditasyon",  key="k116")
        cope_social     = col3.checkbox("Sosyalleşme", key="k117")
        cope_eating     = col4.checkbox("Yeme",        key="k118")
        cope_isolation  = col5.checkbox("İzolasyon",   key="k119")
        cope_none       = col6.checkbox("Yok",         key="k120")

        col1, col2 = st.columns(2)
        with col1:
            mindfulness = st.selectbox("Mindfulness Deneyimi", ["Hiç", "Denedim", "Düzenli uyguluyorum"], key="k258")
            burnout     = st.checkbox("Tükenmişlik Belirtileri", key="k259")
        with col2:
            social_support = st.selectbox("Sosyal Destek", ["Güçlü", "Orta", "Zayıf", "İzole"], key="k260")

        st.subheader("Hareket")
        col1, col2, col3 = st.columns(3)
        with col1:
            daily_steps    = st.number_input("Günlük Adım Sayısı", 0, 30000, 5000, 500, key="k261")
        with col2:
            sitting_hrs    = st.number_input("Günlük Oturma (saat)", 0.0, 16.0, 8.0, 0.5, key="k262")
        with col3:
            transport_type = st.selectbox("Ulaşım", ["Araç", "Toplu Taşıma", "Yürüyüş", "Bisiklet"], key="k263")
            wearable       = st.selectbox("Giyilebilir Cihaz", ["Yok", "Apple Watch", "Garmin", "Fitbit", "Xiaomi", "Diğer"], key="k264")

    # ════════════════════════════════
    # SEKME 4 — BESLENME
    # ════════════════════════════════
    with tab4:
        col1, col2, col3 = st.columns(3)
        with col1:
            diet_type      = st.selectbox("Beslenme Tipi", ["Omnivore", "Vejetaryen", "Vegan", "Pescatarian", "Keto", "Paleo"], key="k265")
            meals_per_day  = st.number_input("Günlük Öğün Sayısı", 1, 8, 3, key="k266")
            first_meal     = st.text_input("İlk Öğün Saati", "08:00", key="k267")
            last_meal      = st.text_input("Son Öğün Saati", "20:00", key="k268")
            water_liters   = st.number_input("Su Tüketimi (litre)", 0.0, 6.0, 2.0, 0.25, key="k269")
        with col2:
            vegetable_portions = st.number_input("Günlük Sebze/Meyve (porsiyon)", 0, 15, 3, key="k270")
            whole_grain_freq   = st.selectbox("Tam Tahıl", ["Hiç", "Bazen", "Her gün"], key="k271")
            processed_freq     = st.selectbox("İşlenmiş Gıda", ["Hiç", "1–2/hafta", "3–5/hafta", "Günlük"], key="k272")
            sugary_drinks      = st.selectbox("Şekerli İçecek", ["Hiç", "Bazen", "Günlük"], key="k273")
            fastfood_week      = st.number_input("Fastfood (kez/hafta)", 0, 14, 0, key="k274")
        with col3:
            red_meat_week  = st.number_input("Kırmızı Et (kez/hafta)", 0, 14, 2, key="k275")
            chicken_week   = st.number_input("Tavuk (kez/hafta)", 0, 14, 3, key="k276")
            fish_week      = st.number_input("Balık (kez/hafta)", 0, 14, 1, key="k277")
            egg_week       = st.number_input("Yumurta (kez/hafta)", 0, 21, 5, key="k278")
            dairy_week     = st.number_input("Süt Ürünleri (kez/hafta)", 0, 21, 4, key="k279")
            legume_week    = st.number_input("Baklagil (kez/hafta)", 0, 14, 2, key="k280")

        col1, col2 = st.columns(2)
        with col1:
            cooking_habit  = st.selectbox("Yemek Pişirme", ["Ben pişiririm", "Ailede biri", "Dışarıdan", "Karma"], key="k281")
            budget_level   = st.selectbox("Beslenme Bütçesi", ["Düşük", "Orta", "Yüksek"], key="k282")
        with col2:
            disliked_foods = st.text_area("Sevmediğin Yiyecekler (serbest yaz)", height=80, key="k283")

        st.subheader("Tahmini Günlük Makro (opsiyonel)")
        col1, col2, col3, col4, col5 = st.columns(5)
        daily_calories = col1.number_input("Kalori (kcal)", 0, 5000, 0, key="k284")
        protein_g      = col2.number_input("Protein (g)", 0.0, 400.0, 0.0, key="k285")
        carb_g         = col3.number_input("Karbonhidrat (g)", 0.0, 600.0, 0.0, key="k286")
        fat_g          = col4.number_input("Yağ (g)", 0.0, 300.0, 0.0, key="k287")
        fiber_g        = col5.number_input("Lif (g)", 0.0, 100.0, 0.0, key="k288")

        st.subheader("Gıda Kısıtlamaları")
        restriction_types = ["Alerji", "İntolerans", "Dinsel/Kültürel"]
        food_items = st.text_area("Kısıtlı gıdaları yaz (her satıra bir tane, önüne 'Alerji:', 'İntolerans:' veya 'Dinsel:' ekle)", height=100, key="k289")

    # ════════════════════════════════
    # SEKME 5 — PERFORMANS
    # ════════════════════════════════
    with tab5:
        st.subheader("Antrenman Geçmişi")
        col1, col2, col3 = st.columns(3)
        with col1:
            training_exp_mo   = st.number_input("Antrenman Deneyimi (ay)", 0, 300, 0, key="k290")
            training_days     = st.number_input("Haftalık Antrenman Günü", 0, 7, 3, key="k291")
            session_duration  = st.number_input("Seans Süresi (dk)", 0, 180, 60, key="k292")
        with col2:
            training_location = st.selectbox("Antrenman Yeri", ["Spor Salonu", "Ev", "Outdoor", "Karma"], key="k293")
            current_training  = st.selectbox("Mevcut Antrenman Türü", [
                "Hiç", "Direnç Antrenmanı", "Kardiyo", "Yoga/Pilates", "Spor Branşı", "Karma"
            ], key="k091")
            goal              = st.selectbox("Hedef", [
                "Kilo Verme", "Kas Kazanımı", "Dayanıklılık", "Güç", "Genel Sağlık", "Performans"
            ], key="k092")
        with col3:
            sport_branch      = st.text_input("Spor Branşı (varsa)", key="k294")
            disliked_exercises = st.text_area("Sevmediğin Egzersizler", height=80, key="k295")

        st.markdown("**Tercih Edilen Egzersizler**")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        pref_weights  = col1.checkbox("Ağırlık",  key="k121")
        pref_cardio   = col2.checkbox("Kardiyo",  key="k122")
        pref_yoga     = col3.checkbox("Yoga",     key="k123")
        pref_swimming = col4.checkbox("Yüzme",    key="k124")
        pref_cycling  = col5.checkbox("Bisiklet", key="k125")
        pref_running  = col6.checkbox("Koşu",     key="k126")
        pref_other    = st.text_input("Diğer tercihler", key="k296")

        st.subheader("Performans Testleri (opsiyonel)")
        col1, col2, col3 = st.columns(3)
        with col1:
            pushup_max   = st.number_input("Max Push-up (tekrar)", 0, 200, 0, key="k297")
            squat_max    = st.number_input("Max Squat (tekrar)", 0, 200, 0, key="k298")
            plank_sec    = st.number_input("Plank Süresi (saniye)", 0, 600, 0, key="k299")
        with col2:
            run_km_time  = st.number_input("2.4 km Koşu Süresi (dk)", 0.0, 60.0, 0.0, 0.5, key="k300")
            vo2max       = st.number_input("VO2max Tahmini", 0.0, 80.0, 0.0, 0.5, key="k301")
            hrv_ms       = st.number_input("HRV (ms)", 0.0, 200.0, 0.0, 0.5, key="k302")
        with col3:
            sit_reach    = st.number_input("Sit & Reach (cm)", 0.0, 50.0, 0.0, 0.5, key="k303")
            shoulder_flex = st.selectbox("Omuz Fleksibilite", ["Normal", "Kısıtlı Sağ", "Kısıtlı Sol", "İkisi de Kısıtlı"], key="k304")
            ankle_cm     = st.number_input("Ayak Bileği Dorsifleksiyon (cm)", 0.0, 20.0, 0.0, 0.5, key="k305")

    # ════════════════════════════════
    # KAYDET BUTONU
    # ════════════════════════════════
    st.divider()
    if st.button("🚀 Analizi Başlat", type="primary", use_container_width=True):
        if not name or not email:
            st.error("Lütfen ad ve e-posta gir.")
            return

        with st.spinner("Veriler kaydediliyor..."):
            if current_user:
                user_id = current_user["user_id"]
            else:
                user_id = get_or_create_user(name, email)
            st.session_state.user_id = user_id

            save_profile(user_id, {
                "age": age, "gender": gender, "height_cm": height_cm, "weight_kg": weight_kg,
                "waist_cm": waist_cm or None, "hip_cm": hip_cm or None,
                "body_fat_pct": body_fat_pct or None, "muscle_mass_kg": muscle_mass_kg or None,
                "resting_hr": resting_hr or None, "activity_level": activity_level,
                "occupation_type": occupation_type, "city": city
            })

            save_health(user_id, {
                "energy_morning": energy_morning, "energy_afternoon": energy_afternoon,
                "sleep_quality": sleep_quality, "sleep_duration_hrs": sleep_duration_hrs,
                "sleep_onset_min": sleep_onset_min, "focus_score": focus_score,
                "digestion_score": digestion_score, "mood_score": mood_score,
                "libido": libido, "headache_per_week": headache_per_week,
                "cold_hands_feet": cold_hands_feet, "muscle_fatigue": muscle_fatigue,
                "hba1c": hba1c or None, "fasting_glucose": fasting_glucose or None,
                "insulin": insulin or None, "tsh": tsh or None,
                "free_t3": free_t3 or None, "free_t4": free_t4 or None,
                "vitamin_d": vitamin_d or None, "b12": b12 or None,
                "ferritin": ferritin or None, "crp": crp or None,
                "homocysteine": homocysteine or None, "testosterone": testosterone or None,
                "estradiol": estradiol or None, "triglyceride": triglyceride or None,
                "hdl": hdl or None, "ldl": ldl or None,
                "alt": alt or None, "ast": ast or None, "creatinine": creatinine or None,
                "alcohol_frequency": alcohol_frequency, "smoking_status": smoking_status,
                "caffeine_per_day": caffeine_per_day
            })

            save_diseases(user_id, selected_diseases)
            save_pain_map(user_id, pains)

            save_lifestyle(user_id, {
                "bedtime": bedtime, "wake_time": wake_time, "sleep_hrs": sleep_hrs,
                "sleep_onset_min": sleep_onset_min_ls, "night_wakings": night_wakings,
                "snoring": snoring, "screen_before_bed_hrs": screen_before_bed,
                "stress_morning": stress_morning, "stress_afternoon": stress_afternoon,
                "stress_evening": stress_evening,
                "stress_work": stress_work, "stress_family": stress_family,
                "stress_financial": stress_financial, "stress_health": stress_health,
                "stress_social": stress_social,
                "cope_exercise": cope_exercise, "cope_meditation": cope_meditation,
                "cope_social": cope_social, "cope_eating": cope_eating,
                "cope_isolation": cope_isolation, "cope_none": cope_none,
                "mindfulness_experience": mindfulness, "burnout": burnout,
                "social_support": social_support, "daily_steps": daily_steps,
                "sitting_hrs_day": sitting_hrs, "transport_type": transport_type,
                "wearable_device": wearable
            })

            save_nutrition(user_id, {
                "diet_type": diet_type, "meals_per_day": meals_per_day,
                "first_meal_time": first_meal, "last_meal_time": last_meal,
                "water_liters": water_liters, "vegetable_portions": vegetable_portions,
                "whole_grain_freq": whole_grain_freq,
                "red_meat_per_week": red_meat_week, "chicken_per_week": chicken_week,
                "fish_per_week": fish_week, "egg_per_week": egg_week,
                "dairy_per_week": dairy_week, "legume_per_week": legume_week,
                "processed_food_freq": processed_freq, "sugary_drinks_freq": sugary_drinks,
                "fastfood_per_week": fastfood_week, "cooking_habit": cooking_habit,
                "budget_level": budget_level, "daily_calories_est": daily_calories or None,
                "protein_g": protein_g or None, "carb_g": carb_g or None,
                "fat_g": fat_g or None, "fiber_g": fiber_g or None,
                "disliked_foods": disliked_foods
            })

            # Gıda kısıtlamaları
            restrictions = []
            for line in food_items.strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    rtype, ritem = line.split(":", 1)
                    restrictions.append({"type": rtype.strip(), "item": ritem.strip()})
            save_food_restrictions(user_id, restrictions)

            save_performance(user_id, {
                "training_experience_mo": training_exp_mo,
                "training_days_per_week": training_days,
                "training_location": training_location,
                "current_training_type": current_training,
                "session_duration_min": session_duration,
                "pref_weights": pref_weights, "pref_cardio": pref_cardio,
                "pref_yoga": pref_yoga, "pref_swimming": pref_swimming,
                "pref_cycling": pref_cycling, "pref_running": pref_running,
                "pref_other": pref_other,
                "disliked_exercises": disliked_exercises,
                "sport_branch": sport_branch, "goal": goal,
                "pushup_max": pushup_max or None, "squat_max": squat_max or None,
                "plank_sec": plank_sec or None, "run_km_time_min": run_km_time or None,
                "vo2max_estimate": vo2max or None, "hrv_ms": hrv_ms or None,
                "sit_reach_cm": sit_reach or None, "shoulder_flex": shoulder_flex,
                "ankle_dorsiflexion_cm": ankle_cm or None
            })

        st.success("✅ Veriler kaydedildi! Analiz sayfasına geçiliyor...")
        st.session_state.page = "analysis"
        st.rerun()
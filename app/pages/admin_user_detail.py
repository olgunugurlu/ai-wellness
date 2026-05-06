import streamlit as st
from config.user_data import (
    get_user_profile, get_user_health, get_user_diseases,
    get_user_pain_map, get_user_lifestyle, get_user_nutrition,
    get_user_food_restrictions, get_user_performance,
    get_user_medications, get_user_supplements,
    update_profile, update_health, update_lifestyle,
    update_nutrition, update_performance
)

def v_int(val, default=0):
    try:
        return int(val) if val is not None and val != "" else default
    except:
        return default

def v_float(val, default=0.0):
    try:
        return float(val) if val is not None and val != "" else default
    except:
        return default

def v_bool(val):
    return bool(val) if val is not None else False

def v_str(val, default=""):
    return str(val) if val is not None else default

def sel_index(options, val):
    try:
        return options.index(val) if val in options else 0
    except:
        return 0

def show(user_info):
    uid = user_info["id"]

    if st.button("← Admin Paneline Dön", key="back_to_admin"):
        st.session_state.page = "admin"
        st.session_state.pop("selected_user", None)
        st.rerun()

    st.title(f"👤 {user_info['name']}")
    st.caption(f"{user_info['email']}  |  Kayıt: {str(user_info['created_at'])[:10]}")
    st.divider()

    profile     = get_user_profile(uid)
    health      = get_user_health(uid)
    diseases    = get_user_diseases(uid)
    pain_map    = get_user_pain_map(uid)
    lifestyle   = get_user_lifestyle(uid)
    nutrition   = get_user_nutrition(uid)
    restrictions= get_user_food_restrictions(uid)
    performance = get_user_performance(uid)
    medications = get_user_medications(uid)
    supplements = get_user_supplements(uid)

    if not profile:
        st.warning("Bu kullanıcı henüz değerlendirme formunu doldurmamış.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧍 Profil", "🏥 Sağlık", "🌙 Yaşam Tarzı", "🥗 Beslenme", "🏋️ Performans"
    ])

    # ════════════════════════════
    # TAB 1 — PROFİL
    # ════════════════════════════
    with tab1:
        with st.form("edit_profile"):
            st.subheader("Demografik Bilgiler")
            col1, col2, col3 = st.columns(3)
            with col1:
                age             = st.number_input("Yaş",        18, 90,  v_int(profile.get("age"), 30),          key="d_age")
                height_cm       = st.number_input("Boy (cm)",   140, 220, v_int(profile.get("height_cm"), 170),   key="d_height")
                waist_cm        = st.number_input("Bel (cm)",   0, 200,   v_int(profile.get("waist_cm"), 0),      key="d_waist")
            with col2:
                gender_opts     = ["Erkek", "Kadın", "Belirtmek istemiyorum"]
                gender          = st.selectbox("Cinsiyet", gender_opts,
                                    index=sel_index(gender_opts, profile.get("gender")), key="d_gender")
                weight_kg       = st.number_input("Kilo (kg)",  40.0, 200.0, v_float(profile.get("weight_kg"), 70.0), key="d_weight")
                hip_cm          = st.number_input("Kalça (cm)", 0, 200,   v_int(profile.get("hip_cm"), 0),        key="d_hip")
            with col3:
                act_opts        = ["Sedanter", "Az Aktif", "Orta Aktif", "Çok Aktif", "Sporcu"]
                activity_level  = st.selectbox("Aktivite", act_opts,
                                    index=sel_index(act_opts, profile.get("activity_level")), key="d_activity")
                body_fat_pct    = st.number_input("Yağ (%)",    0.0, 60.0, v_float(profile.get("body_fat_pct"), 0.0),   key="d_fat")
                muscle_mass_kg  = st.number_input("Kas (kg)",   0.0, 100.0, v_float(profile.get("muscle_mass_kg"), 0.0), key="d_muscle")

            col1, col2, col3 = st.columns(3)
            with col1:
                resting_hr      = st.number_input("Dinlenik Nabız", 0, 120, v_int(profile.get("resting_hr"), 0), key="d_hr")
            with col2:
                occ_opts        = ["Oturarak", "Ayakta", "Ağır Fiziksel İş"]
                occupation_type = st.selectbox("Meslek", occ_opts,
                                    index=sel_index(occ_opts, profile.get("occupation_type")), key="d_occ")
            with col3:
                city            = st.text_input("Şehir", v_str(profile.get("city")), key="d_city")

            if st.form_submit_button("💾 Profili Kaydet", use_container_width=True):
                update_profile(uid, {
                    "age": age, "gender": gender, "height_cm": height_cm,
                    "weight_kg": weight_kg, "waist_cm": waist_cm or None,
                    "hip_cm": hip_cm or None, "body_fat_pct": body_fat_pct or None,
                    "muscle_mass_kg": muscle_mass_kg or None, "resting_hr": resting_hr or None,
                    "activity_level": activity_level, "occupation_type": occupation_type, "city": city
                })
                st.success("✅ Profil güncellendi!")

    # ════════════════════════════
    # TAB 2 — SAĞLIK
    # ════════════════════════════
    with tab2:
        if health:
            with st.form("edit_health"):
                st.subheader("Semptomlar")
                col1, col2 = st.columns(2)
                with col1:
                    energy_morning   = st.slider("Sabah Enerjisi",        0, 10, v_int(health.get("energy_morning"),   5), key="d_em")
                    sleep_quality    = st.slider("Uyku Kalitesi",          0, 10, v_int(health.get("sleep_quality"),    5), key="d_sq")
                    focus_score      = st.slider("Odak",                   0, 10, v_int(health.get("focus_score"),      5), key="d_fs")
                    mood_score       = st.slider("Ruh Hali",               0, 10, v_int(health.get("mood_score"),       5), key="d_ms")
                    muscle_fatigue   = st.slider("Kas Yorgunluğu",         0, 10, v_int(health.get("muscle_fatigue"),   3), key="d_mf")
                with col2:
                    energy_afternoon = st.slider("Öğleden Sonra Enerjisi", 0, 10, v_int(health.get("energy_afternoon"), 5), key="d_ea")
                    sleep_duration   = st.number_input("Uyku Süresi (saat)", 0.0, 12.0, v_float(health.get("sleep_duration_hrs"), 7.0), 0.5, key="d_sd")
                    sleep_onset      = st.number_input("Uykuya Dalma (dk)",  0, 120,    v_int(health.get("sleep_onset_min"), 15),        key="d_so")
                    digestion_score  = st.slider("Sindirim",               0, 10, v_int(health.get("digestion_score"),  7), key="d_dg")
                    headache         = st.number_input("Baş Ağrısı (gün/hafta)", 0, 7, v_int(health.get("headache_per_week"), 0), key="d_ha")

                col1, col2, col3 = st.columns(3)
                with col1:
                    lib_opts = ["Normal", "Düşük", "Yüksek"]
                    libido   = st.selectbox("Libido", lib_opts,
                                index=sel_index(lib_opts, health.get("libido")), key="d_lib")
                with col2:
                    cold_hands = st.checkbox("El/Ayak Soğukluğu", v_bool(health.get("cold_hands_feet")), key="d_ch")
                with col3:
                    alc_opts = ["Yok", "Hafif (1–2/hafta)", "Orta (3–5/hafta)", "Ağır"]
                    alcohol  = st.selectbox("Alkol", alc_opts,
                                index=sel_index(alc_opts, health.get("alcohol_frequency")), key="d_alc")
                    smk_opts = ["Hiç kullanmadım", "Bıraktım", "Kullanıyorum"]
                    smoking  = st.selectbox("Sigara", smk_opts,
                                index=sel_index(smk_opts, health.get("smoking_status")), key="d_smk")
                    caffeine = st.number_input("Kafein (bardak/gün)", 0, 10, v_int(health.get("caffeine_per_day"), 1), key="d_caf")

                st.subheader("Kan Değerleri")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hba1c      = st.number_input("HbA1c",          0.0, 15.0,   v_float(health.get("hba1c"),          0.0), key="d_hba")
                    glucose    = st.number_input("Açlık Glukoz",   0.0, 400.0,  v_float(health.get("fasting_glucose"), 0.0), key="d_glc")
                    insulin    = st.number_input("İnsülin",         0.0, 100.0,  v_float(health.get("insulin"),         0.0), key="d_ins")
                    tsh        = st.number_input("TSH",             0.0, 20.0,   v_float(health.get("tsh"),             0.0), key="d_tsh")
                    t3         = st.number_input("Serbest T3",      0.0, 10.0,   v_float(health.get("free_t3"),         0.0), key="d_t3")
                    t4         = st.number_input("Serbest T4",      0.0, 10.0,   v_float(health.get("free_t4"),         0.0), key="d_t4")
                with col2:
                    vitd       = st.number_input("Vitamin D",       0.0, 150.0,  v_float(health.get("vitamin_d"),       0.0), key="d_vitd")
                    b12        = st.number_input("B12",              0.0, 2000.0, v_float(health.get("b12"),             0.0), key="d_b12")
                    ferritin   = st.number_input("Ferritin",         0.0, 500.0,  v_float(health.get("ferritin"),        0.0), key="d_fer")
                    crp        = st.number_input("CRP",              0.0, 50.0,   v_float(health.get("crp"),             0.0), key="d_crp")
                    homocys    = st.number_input("Homosistein",      0.0, 50.0,   v_float(health.get("homocysteine"),    0.0), key="d_hom")
                with col3:
                    testo      = st.number_input("Testosteron",      0.0, 1200.0, v_float(health.get("testosterone"),   0.0), key="d_tes")
                    estradiol  = st.number_input("Östradiol",        0.0, 500.0,  v_float(health.get("estradiol"),       0.0), key="d_est")
                    trig       = st.number_input("Trigliserit",      0.0, 500.0,  v_float(health.get("triglyceride"),    0.0), key="d_tri")
                    hdl        = st.number_input("HDL",              0.0, 150.0,  v_float(health.get("hdl"),             0.0), key="d_hdl")
                    ldl        = st.number_input("LDL",              0.0, 300.0,  v_float(health.get("ldl"),             0.0), key="d_ldl")
                with col4:
                    alt        = st.number_input("ALT",              0.0, 200.0,  v_float(health.get("alt"),             0.0), key="d_alt")
                    ast        = st.number_input("AST",              0.0, 200.0,  v_float(health.get("ast"),             0.0), key="d_ast")
                    creatinine = st.number_input("Kreatinin",        0.0, 10.0,   v_float(health.get("creatinine"),      0.0), key="d_cre")

                if st.form_submit_button("💾 Sağlık Verilerini Kaydet", use_container_width=True):
                    update_health(uid, {
                        "energy_morning": energy_morning, "energy_afternoon": energy_afternoon,
                        "sleep_quality": sleep_quality, "sleep_duration_hrs": sleep_duration,
                        "sleep_onset_min": sleep_onset, "focus_score": focus_score,
                        "digestion_score": digestion_score, "mood_score": mood_score,
                        "libido": libido, "headache_per_week": headache,
                        "cold_hands_feet": cold_hands, "muscle_fatigue": muscle_fatigue,
                        "hba1c": hba1c or None, "fasting_glucose": glucose or None,
                        "insulin": insulin or None, "tsh": tsh or None,
                        "free_t3": t3 or None, "free_t4": t4 or None,
                        "vitamin_d": vitd or None, "b12": b12 or None,
                        "ferritin": ferritin or None, "crp": crp or None,
                        "homocysteine": homocys or None, "testosterone": testo or None,
                        "estradiol": estradiol or None, "triglyceride": trig or None,
                        "hdl": hdl or None, "ldl": ldl or None,
                        "alt": alt or None, "ast": ast or None, "creatinine": creatinine or None,
                        "alcohol_frequency": alcohol, "smoking_status": smoking,
                        "caffeine_per_day": caffeine
                    })
                    st.success("✅ Sağlık verileri güncellendi!")
        else:
            st.warning("Sağlık verisi henüz girilmemiş.")

        st.subheader("Hastalıklar")
        if diseases:
            for d in diseases:
                st.markdown(f"- {d['disease']}")
        else:
            st.caption("Hastalık kaydı yok.")

        st.subheader("Ağrı Haritası")
        if pain_map:
            for p in pain_map:
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"**Bölge:** {p['region']}  \n**Şiddet:** {p['severity']}/10")
                    col2.markdown(f"**Karakter:** {p['pain_character']}  \n**Süre:** {p['duration_type']}")
                    col3.markdown(f"**Tetikleyici:** {p['pain_trigger']}  \n**Yayılım:** {'Evet' if p['radiates'] else 'Hayır'}")
        else:
            st.caption("Ağrı kaydı yok.")

        st.subheader("İlaçlar")
        if medications:
            for m in medications:
                st.markdown(f"- **{m['name']}** — {m['dose']} / {m['duration']}")
        else:
            st.caption("İlaç kaydı yok.")

    # ════════════════════════════
    # TAB 3 — YAŞAM TARZI
    # ════════════════════════════
    with tab3:
        if lifestyle:
            with st.form("edit_lifestyle"):
                st.subheader("Uyku")
                col1, col2, col3 = st.columns(3)
                with col1:
                    bedtime       = st.text_input("Yatış Saati",      v_str(lifestyle.get("bedtime"), "23:00"),    key="d_bed")
                    sleep_hrs     = st.number_input("Uyku (saat)",     0.0, 12.0, v_float(lifestyle.get("sleep_hrs"), 7.0), 0.5, key="d_slh")
                    night_wakings = st.number_input("Gece Uyanma",     0, 10,     v_int(lifestyle.get("night_wakings"), 0),      key="d_nw")
                with col2:
                    wake_time     = st.text_input("Kalkış Saati",      v_str(lifestyle.get("wake_time"), "07:00"), key="d_wake")
                    sleep_onset   = st.number_input("Uykuya Dalma (dk)", 0, 120, v_int(lifestyle.get("sleep_onset_min"), 15),    key="d_lso")
                    screen        = st.number_input("Ekran (saat)",    0.0, 5.0,  v_float(lifestyle.get("screen_before_bed_hrs"), 1.0), 0.5, key="d_scr")
                with col3:
                    snoring       = st.checkbox("Horlama", v_bool(lifestyle.get("snoring")), key="d_snr")

                st.subheader("Stres")
                col1, col2, col3 = st.columns(3)
                stress_morning   = col1.slider("Sabah",         0, 10, v_int(lifestyle.get("stress_morning"),   4), key="d_sm")
                stress_afternoon = col2.slider("Öğleden Sonra", 0, 10, v_int(lifestyle.get("stress_afternoon"), 5), key="d_sa")
                stress_evening   = col3.slider("Akşam",         0, 10, v_int(lifestyle.get("stress_evening"),   4), key="d_se")

                st.markdown("**Stres Kaynakları**")
                col1, col2, col3, col4, col5 = st.columns(5)
                stress_work      = col1.checkbox("İş",      v_bool(lifestyle.get("stress_work")),      key="d_sw")
                stress_family    = col2.checkbox("Aile",    v_bool(lifestyle.get("stress_family")),    key="d_sf")
                stress_financial = col3.checkbox("Mali",    v_bool(lifestyle.get("stress_financial")), key="d_sfi")
                stress_health    = col4.checkbox("Sağlık",  v_bool(lifestyle.get("stress_health")),    key="d_sh")
                stress_social    = col5.checkbox("Sosyal",  v_bool(lifestyle.get("stress_social")),    key="d_ss")

                st.markdown("**Baş Etme Yöntemleri**")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                cope_exercise   = col1.checkbox("Egzersiz",    v_bool(lifestyle.get("cope_exercise")),   key="d_ce")
                cope_meditation = col2.checkbox("Meditasyon",  v_bool(lifestyle.get("cope_meditation")), key="d_cm")
                cope_social     = col3.checkbox("Sosyalleşme", v_bool(lifestyle.get("cope_social")),     key="d_cs")
                cope_eating     = col4.checkbox("Yeme",        v_bool(lifestyle.get("cope_eating")),     key="d_cea")
                cope_isolation  = col5.checkbox("İzolasyon",   v_bool(lifestyle.get("cope_isolation")),  key="d_ci")
                cope_none       = col6.checkbox("Yok",         v_bool(lifestyle.get("cope_none")),       key="d_cn")

                col1, col2 = st.columns(2)
                with col1:
                    mind_opts   = ["Hiç", "Denedim", "Düzenli uyguluyorum"]
                    mindfulness = st.selectbox("Mindfulness", mind_opts,
                                    index=sel_index(mind_opts, lifestyle.get("mindfulness_experience")), key="d_mind")
                    burnout     = st.checkbox("Tükenmişlik", v_bool(lifestyle.get("burnout")), key="d_burn")
                with col2:
                    sup_opts       = ["Güçlü", "Orta", "Zayıf", "İzole"]
                    social_support = st.selectbox("Sosyal Destek", sup_opts,
                                        index=sel_index(sup_opts, lifestyle.get("social_support")), key="d_supp")

                st.subheader("Hareket")
                col1, col2, col3 = st.columns(3)
                with col1:
                    daily_steps = st.number_input("Adım",          0, 30000, v_int(lifestyle.get("daily_steps"), 5000), 500, key="d_steps")
                with col2:
                    sitting_hrs = st.number_input("Oturma (saat)", 0.0, 16.0, v_float(lifestyle.get("sitting_hrs_day"), 8.0), 0.5, key="d_sit")
                with col3:
                    tr_opts   = ["Araç", "Toplu Taşıma", "Yürüyüş", "Bisiklet"]
                    transport = st.selectbox("Ulaşım", tr_opts,
                                    index=sel_index(tr_opts, lifestyle.get("transport_type")), key="d_tr")
                    wear_opts = ["Yok", "Apple Watch", "Garmin", "Fitbit", "Xiaomi", "Diğer"]
                    wearable  = st.selectbox("Giyilebilir", wear_opts,
                                    index=sel_index(wear_opts, lifestyle.get("wearable_device")), key="d_wear")

                if st.form_submit_button("💾 Yaşam Tarzını Kaydet", use_container_width=True):
                    update_lifestyle(uid, {
                        "bedtime": bedtime, "wake_time": wake_time,
                        "sleep_hrs": sleep_hrs, "sleep_onset_min": sleep_onset,
                        "night_wakings": night_wakings, "snoring": snoring,
                        "screen_before_bed_hrs": screen,
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
                        "sitting_hrs_day": sitting_hrs, "transport_type": transport,
                        "wearable_device": wearable
                    })
                    st.success("✅ Yaşam tarzı güncellendi!")
        else:
            st.warning("Yaşam tarzı verisi henüz girilmemiş.")

    # ════════════════════════════
    # TAB 4 — BESLENME
    # ════════════════════════════
    with tab4:
        if nutrition:
            with st.form("edit_nutrition"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    dt_opts   = ["Omnivore", "Vejetaryen", "Vegan", "Pescatarian", "Keto", "Paleo"]
                    diet_type = st.selectbox("Beslenme Tipi", dt_opts,
                                    index=sel_index(dt_opts, nutrition.get("diet_type")), key="d_dt")
                    meals     = st.number_input("Öğün Sayısı",  1, 8,    v_int(nutrition.get("meals_per_day"), 3),   key="d_meals")
                    first_meal= st.text_input("İlk Öğün",  v_str(nutrition.get("first_meal_time"), "08:00"),         key="d_fm")
                    last_meal = st.text_input("Son Öğün",  v_str(nutrition.get("last_meal_time"),  "20:00"),         key="d_lm")
                    water     = st.number_input("Su (litre)", 0.0, 6.0, v_float(nutrition.get("water_liters"), 2.0), 0.25, key="d_water")
                with col2:
                    veg       = st.number_input("Sebze/Meyve (porsiyon)", 0, 15, v_int(nutrition.get("vegetable_portions"), 3),  key="d_veg")
                    wg_opts   = ["Hiç", "Bazen", "Her gün"]
                    wgrain    = st.selectbox("Tam Tahıl", wg_opts,
                                    index=sel_index(wg_opts, nutrition.get("whole_grain_freq")), key="d_wg")
                    pf_opts   = ["Hiç", "1–2/hafta", "3–5/hafta", "Günlük"]
                    processed = st.selectbox("İşlenmiş Gıda", pf_opts,
                                    index=sel_index(pf_opts, nutrition.get("processed_food_freq")), key="d_pf")
                    sd_opts   = ["Hiç", "Bazen", "Günlük"]
                    sugary    = st.selectbox("Şekerli İçecek", sd_opts,
                                    index=sel_index(sd_opts, nutrition.get("sugary_drinks_freq")), key="d_sd2")
                    fastfood  = st.number_input("Fastfood/hafta", 0, 14, v_int(nutrition.get("fastfood_per_week"), 0), key="d_ff")
                with col3:
                    red_meat  = st.number_input("Kırmızı Et/hafta",  0, 14, v_int(nutrition.get("red_meat_per_week"),  2), key="d_rm")
                    chicken   = st.number_input("Tavuk/hafta",        0, 14, v_int(nutrition.get("chicken_per_week"),   3), key="d_ch2")
                    fish      = st.number_input("Balık/hafta",        0, 14, v_int(nutrition.get("fish_per_week"),      1), key="d_fish")
                    egg       = st.number_input("Yumurta/hafta",      0, 21, v_int(nutrition.get("egg_per_week"),       5), key="d_egg")
                    dairy     = st.number_input("Süt Ürünleri/hafta", 0, 21, v_int(nutrition.get("dairy_per_week"),     4), key="d_dairy")
                    legume    = st.number_input("Baklagil/hafta",     0, 14, v_int(nutrition.get("legume_per_week"),    2), key="d_leg")

                col1, col2 = st.columns(2)
                with col1:
                    ck_opts = ["Ben pişiririm", "Ailede biri", "Dışarıdan", "Karma"]
                    cooking = st.selectbox("Pişirme", ck_opts,
                                index=sel_index(ck_opts, nutrition.get("cooking_habit")), key="d_cook")
                    bg_opts = ["Düşük", "Orta", "Yüksek"]
                    budget  = st.selectbox("Bütçe", bg_opts,
                                index=sel_index(bg_opts, nutrition.get("budget_level")), key="d_bud")
                with col2:
                    disliked = st.text_area("Sevmediği Yiyecekler", v_str(nutrition.get("disliked_foods")), key="d_dis")

                if st.form_submit_button("💾 Beslenmeyi Kaydet", use_container_width=True):
                    update_nutrition(uid, {
                        "diet_type": diet_type, "meals_per_day": meals,
                        "first_meal_time": first_meal, "last_meal_time": last_meal,
                        "water_liters": water, "vegetable_portions": veg,
                        "whole_grain_freq": wgrain, "red_meat_per_week": red_meat,
                        "chicken_per_week": chicken, "fish_per_week": fish,
                        "egg_per_week": egg, "dairy_per_week": dairy,
                        "legume_per_week": legume, "processed_food_freq": processed,
                        "sugary_drinks_freq": sugary, "fastfood_per_week": fastfood,
                        "cooking_habit": cooking, "budget_level": budget,
                        "disliked_foods": disliked
                    })
                    st.success("✅ Beslenme güncellendi!")

            st.subheader("Gıda Kısıtlamaları")
            if restrictions:
                for r in restrictions:
                    st.markdown(f"- **{r['type']}:** {r['item']}")
            else:
                st.caption("Kısıtlama kaydı yok.")
        else:
            st.warning("Beslenme verisi henüz girilmemiş.")

    # ════════════════════════════
    # TAB 5 — PERFORMANS
    # ════════════════════════════
    with tab5:
        if performance:
            with st.form("edit_performance"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    exp_mo   = st.number_input("Deneyim (ay)",    0, 300, v_int(performance.get("training_experience_mo"),  0),  key="d_exp")
                    days     = st.number_input("Antrenman Günü",  0, 7,   v_int(performance.get("training_days_per_week"),  3),  key="d_days")
                    duration = st.number_input("Seans (dk)",      0, 180, v_int(performance.get("session_duration_min"),    60), key="d_dur")
                with col2:
                    loc_opts = ["Spor Salonu", "Ev", "Outdoor", "Karma"]
                    location = st.selectbox("Yer", loc_opts,
                                    index=sel_index(loc_opts, performance.get("training_location")), key="d_loc")
                    typ_opts = ["Hiç", "Direnç Antrenmanı", "Kardiyo", "Yoga/Pilates", "Spor Branşı", "Karma"]
                    tr_type  = st.selectbox("Antrenman Türü", typ_opts,
                                    index=sel_index(typ_opts, performance.get("current_training_type")), key="d_ttype")
                    goal_opts= ["Kilo Verme", "Kas Kazanımı", "Dayanıklılık", "Güç", "Genel Sağlık", "Performans"]
                    goal     = st.selectbox("Hedef", goal_opts,
                                    index=sel_index(goal_opts, performance.get("goal")), key="d_goal")
                with col3:
                    sport      = st.text_input("Branş", v_str(performance.get("sport_branch")), key="d_sport")
                    disliked_ex= st.text_area("Sevmediği Egzersizler", v_str(performance.get("disliked_exercises")), key="d_disex")

                st.markdown("**Tercihler**")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                pw  = col1.checkbox("Ağırlık",  v_bool(performance.get("pref_weights")),  key="d_pw")
                pc  = col2.checkbox("Kardiyo",  v_bool(performance.get("pref_cardio")),   key="d_pc")
                py  = col3.checkbox("Yoga",     v_bool(performance.get("pref_yoga")),     key="d_py")
                ps  = col4.checkbox("Yüzme",    v_bool(performance.get("pref_swimming")), key="d_ps")
                pcy = col5.checkbox("Bisiklet", v_bool(performance.get("pref_cycling")),  key="d_pcy")
                pr  = col6.checkbox("Koşu",     v_bool(performance.get("pref_running")),  key="d_pr")
                pother = st.text_input("Diğer", v_str(performance.get("pref_other")), key="d_pother")

                st.subheader("Performans Testleri")
                col1, col2, col3 = st.columns(3)
                with col1:
                    pushup = st.number_input("Push-up",    0, 200, v_int(performance.get("pushup_max"),  0), key="d_push")
                    squat  = st.number_input("Squat",      0, 200, v_int(performance.get("squat_max"),   0), key="d_squat")
                    plank  = st.number_input("Plank (sn)", 0, 600, v_int(performance.get("plank_sec"),   0), key="d_plank")
                with col2:
                    run    = st.number_input("2.4km (dk)",  0.0, 60.0,  v_float(performance.get("run_km_time_min"),  0.0), 0.5, key="d_run")
                    vo2    = st.number_input("VO2max",       0.0, 80.0,  v_float(performance.get("vo2max_estimate"),  0.0), 0.5, key="d_vo2")
                    hrv    = st.number_input("HRV (ms)",     0.0, 200.0, v_float(performance.get("hrv_ms"),           0.0), 0.5, key="d_hrv")
                with col3:
                    sit_reach = st.number_input("Sit&Reach", 0.0, 50.0,  v_float(performance.get("sit_reach_cm"),          0.0), 0.5, key="d_sr")
                    sf_opts   = ["Normal", "Kısıtlı Sağ", "Kısıtlı Sol", "İkisi de Kısıtlı"]
                    sh_flex   = st.selectbox("Omuz Flex", sf_opts,
                                    index=sel_index(sf_opts, performance.get("shoulder_flex")), key="d_shf")
                    ankle     = st.number_input("Ayak Bileği", 0.0, 20.0, v_float(performance.get("ankle_dorsiflexion_cm"), 0.0), 0.5, key="d_ankle")

                if st.form_submit_button("💾 Performansı Kaydet", use_container_width=True):
                    update_performance(uid, {
                        "training_experience_mo": exp_mo, "training_days_per_week": days,
                        "training_location": location, "current_training_type": tr_type,
                        "session_duration_min": duration,
                        "pref_weights": pw, "pref_cardio": pc, "pref_yoga": py,
                        "pref_swimming": ps, "pref_cycling": pcy, "pref_running": pr,
                        "pref_other": pother, "disliked_exercises": disliked_ex,
                        "sport_branch": sport, "goal": goal,
                        "pushup_max": pushup or None, "squat_max": squat or None,
                        "plank_sec": plank or None, "run_km_time_min": run or None,
                        "vo2max_estimate": vo2 or None, "hrv_ms": hrv or None,
                        "sit_reach_cm": sit_reach or None, "shoulder_flex": sh_flex,
                        "ankle_dorsiflexion_cm": ankle or None
                    })
                    st.success("✅ Performans güncellendi!")
        else:
            st.warning("Performans verisi henüz girilmemiş.")
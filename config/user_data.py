from mysql.connector import Error

from config.database import get_connection

PREFIX = "ai_wellness_"

def get_user_profile(user_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {PREFIX}profiles WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    except Error as e:
        return None
    finally:
        conn.close()  # Her durumda kapat

def get_user_health(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}health WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_diseases(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}diseases WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_user_pain_map(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}pain_map WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_user_lifestyle(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}lifestyle WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_nutrition(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}nutrition WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_food_restrictions(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}food_restrictions WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_user_performance(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}performance WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_medications(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}medications WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_user_supplements(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {PREFIX}current_supplements WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def update_profile(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {PREFIX}profiles SET
            age=%s, gender=%s, height_cm=%s, weight_kg=%s,
            waist_cm=%s, hip_cm=%s, body_fat_pct=%s, muscle_mass_kg=%s,
            resting_hr=%s, activity_level=%s, occupation_type=%s, city=%s
        WHERE user_id=%s
    """, (
        data["age"], data["gender"], data["height_cm"], data["weight_kg"],
        data["waist_cm"], data["hip_cm"], data["body_fat_pct"], data["muscle_mass_kg"],
        data["resting_hr"], data["activity_level"], data["occupation_type"], data["city"],
        user_id
    ))
    conn.commit()
    conn.close()

def update_health(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {PREFIX}health SET
            energy_morning=%s, energy_afternoon=%s, sleep_quality=%s,
            sleep_duration_hrs=%s, sleep_onset_min=%s, focus_score=%s,
            digestion_score=%s, mood_score=%s, libido=%s,
            headache_per_week=%s, cold_hands_feet=%s, muscle_fatigue=%s,
            hba1c=%s, fasting_glucose=%s, insulin=%s, tsh=%s,
            free_t3=%s, free_t4=%s, vitamin_d=%s, b12=%s,
            ferritin=%s, crp=%s, homocysteine=%s, testosterone=%s,
            estradiol=%s, triglyceride=%s, hdl=%s, ldl=%s,
            alt=%s, ast=%s, creatinine=%s,
            alcohol_frequency=%s, smoking_status=%s, caffeine_per_day=%s
        WHERE user_id=%s
    """, (
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
        data["alcohol_frequency"], data["smoking_status"], data["caffeine_per_day"],
        user_id
    ))
    conn.commit()
    conn.close()

def update_lifestyle(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {PREFIX}lifestyle SET
            bedtime=%s, wake_time=%s, sleep_hrs=%s, sleep_onset_min=%s,
            night_wakings=%s, snoring=%s, screen_before_bed_hrs=%s,
            stress_morning=%s, stress_afternoon=%s, stress_evening=%s,
            stress_work=%s, stress_family=%s, stress_financial=%s,
            stress_health=%s, stress_social=%s,
            cope_exercise=%s, cope_meditation=%s, cope_social=%s,
            cope_eating=%s, cope_isolation=%s, cope_none=%s,
            mindfulness_experience=%s, burnout=%s, social_support=%s,
            daily_steps=%s, sitting_hrs_day=%s, transport_type=%s, wearable_device=%s
        WHERE user_id=%s
    """, (
        data["bedtime"], data["wake_time"], data["sleep_hrs"], data["sleep_onset_min"],
        data["night_wakings"], data["snoring"], data["screen_before_bed_hrs"],
        data["stress_morning"], data["stress_afternoon"], data["stress_evening"],
        data["stress_work"], data["stress_family"], data["stress_financial"],
        data["stress_health"], data["stress_social"],
        data["cope_exercise"], data["cope_meditation"], data["cope_social"],
        data["cope_eating"], data["cope_isolation"], data["cope_none"],
        data["mindfulness_experience"], data["burnout"], data["social_support"],
        data["daily_steps"], data["sitting_hrs_day"], data["transport_type"],
        data["wearable_device"], user_id
    ))
    conn.commit()
    conn.close()

def update_nutrition(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {PREFIX}nutrition SET
            diet_type=%s, meals_per_day=%s, first_meal_time=%s, last_meal_time=%s,
            water_liters=%s, vegetable_portions=%s, whole_grain_freq=%s,
            red_meat_per_week=%s, chicken_per_week=%s, fish_per_week=%s,
            egg_per_week=%s, dairy_per_week=%s, legume_per_week=%s,
            processed_food_freq=%s, sugary_drinks_freq=%s, fastfood_per_week=%s,
            cooking_habit=%s, budget_level=%s, disliked_foods=%s
        WHERE user_id=%s
    """, (
        data["diet_type"], data["meals_per_day"], data["first_meal_time"],
        data["last_meal_time"], data["water_liters"], data["vegetable_portions"],
        data["whole_grain_freq"], data["red_meat_per_week"], data["chicken_per_week"],
        data["fish_per_week"], data["egg_per_week"], data["dairy_per_week"],
        data["legume_per_week"], data["processed_food_freq"], data["sugary_drinks_freq"],
        data["fastfood_per_week"], data["cooking_habit"], data["budget_level"],
        data["disliked_foods"], user_id
    ))
    conn.commit()
    conn.close()

def update_performance(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {PREFIX}performance SET
            training_experience_mo=%s, training_days_per_week=%s,
            training_location=%s, current_training_type=%s, session_duration_min=%s,
            pref_weights=%s, pref_cardio=%s, pref_yoga=%s, pref_swimming=%s,
            pref_cycling=%s, pref_running=%s, pref_other=%s,
            disliked_exercises=%s, sport_branch=%s, goal=%s,
            pushup_max=%s, squat_max=%s, plank_sec=%s, run_km_time_min=%s,
            vo2max_estimate=%s, hrv_ms=%s, sit_reach_cm=%s,
            shoulder_flex=%s, ankle_dorsiflexion_cm=%s
        WHERE user_id=%s
    """, (
        data["training_experience_mo"], data["training_days_per_week"],
        data["training_location"], data["current_training_type"], data["session_duration_min"],
        data["pref_weights"], data["pref_cardio"], data["pref_yoga"],
        data["pref_swimming"], data["pref_cycling"], data["pref_running"],
        data["pref_other"], data["disliked_exercises"], data["sport_branch"], data["goal"],
        data.get("pushup_max"), data.get("squat_max"), data.get("plank_sec"),
        data.get("run_km_time_min"), data.get("vo2max_estimate"), data.get("hrv_ms"),
        data.get("sit_reach_cm"), data["shoulder_flex"], data.get("ankle_dorsiflexion_cm"),
        user_id
    ))
    conn.commit()
    conn.close()
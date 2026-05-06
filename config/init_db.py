from config.database import get_connection

PREFIX = "ai_wellness_"

def init_tables():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

        # 1. KULLANICILAR
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}users (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            name            VARCHAR(255) NOT NULL,
            email           VARCHAR(255) UNIQUE NOT NULL,
            password_hash   VARCHAR(255) NOT NULL,
            role            ENUM('user', 'admin') DEFAULT 'user',
            status          ENUM('pending', 'approved', 'rejected', 'suspended') DEFAULT 'pending',
            approved_by     INT DEFAULT NULL,
            approved_at     TIMESTAMP NULL DEFAULT NULL,
            last_login      TIMESTAMP NULL DEFAULT NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. DEMOGRAFİ / PROFİL
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}profiles (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            user_id             INT NOT NULL,
            age                 INT,
            gender              VARCHAR(20),
            height_cm           FLOAT,
            weight_kg           FLOAT,
            waist_cm            FLOAT,
            hip_cm              FLOAT,
            body_fat_pct        FLOAT,
            muscle_mass_kg      FLOAT,
            resting_hr          INT,
            activity_level      VARCHAR(50),
            occupation_type     VARCHAR(50),
            city                VARCHAR(100),
            updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 3. SAĞLIK VERİSİ
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}health (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            user_id                 INT NOT NULL,
            energy_morning          INT,
            energy_afternoon        INT,
            sleep_quality           INT,
            sleep_duration_hrs      FLOAT,
            sleep_onset_min         INT,
            focus_score             INT,
            digestion_score         INT,
            mood_score              INT,
            libido                  VARCHAR(20),
            headache_per_week       INT,
            cold_hands_feet         BOOLEAN,
            muscle_fatigue          INT,
            hba1c                   FLOAT,
            fasting_glucose         FLOAT,
            insulin                 FLOAT,
            tsh                     FLOAT,
            free_t3                 FLOAT,
            free_t4                 FLOAT,
            vitamin_d               FLOAT,
            b12                     FLOAT,
            ferritin                FLOAT,
            crp                     FLOAT,
            homocysteine            FLOAT,
            testosterone            FLOAT,
            estradiol               FLOAT,
            triglyceride            FLOAT,
            hdl                     FLOAT,
            ldl                     FLOAT,
            alt                     FLOAT,
            ast                     FLOAT,
            creatinine              FLOAT,
            alcohol_frequency       VARCHAR(30),
            smoking_status          VARCHAR(30),
            caffeine_per_day        INT,
            updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 4. İLAÇLAR (çoklu kayıt)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}medications (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            name        VARCHAR(255),
            dose        VARCHAR(100),
            duration    VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 5. MEVCUT TAKVİYELER (çoklu kayıt)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}current_supplements (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            name        VARCHAR(255),
            dose        VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 6. HASTALIKLAR (çoklu kayıt)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}diseases (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            disease     VARCHAR(100) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)
      # 7. AĞRI HARİTASI (çoklu kayıt)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}pain_map (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            user_id             INT NOT NULL,
            region              VARCHAR(50),
            severity            INT,
            pain_character      VARCHAR(30),
            duration_type       VARCHAR(20),
            pain_trigger        VARCHAR(50),
            radiates            BOOLEAN,
            worsened_by         VARCHAR(100),
            relieved_by         VARCHAR(100),
            previous_treatment  TEXT,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)
    # 8. YAŞAM TARZI
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}lifestyle (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            user_id                 INT NOT NULL,
            bedtime                 VARCHAR(10),
            wake_time               VARCHAR(10),
            sleep_hrs               FLOAT,
            sleep_onset_min         INT,
            night_wakings           INT,
            snoring                 BOOLEAN,
            screen_before_bed_hrs   FLOAT,
            stress_morning          INT,
            stress_afternoon        INT,
            stress_evening          INT,
            stress_work             BOOLEAN,
            stress_family           BOOLEAN,
            stress_financial        BOOLEAN,
            stress_health           BOOLEAN,
            stress_social           BOOLEAN,
            cope_exercise           BOOLEAN,
            cope_meditation         BOOLEAN,
            cope_social             BOOLEAN,
            cope_eating             BOOLEAN,
            cope_isolation          BOOLEAN,
            cope_none               BOOLEAN,
            mindfulness_experience  VARCHAR(30),
            pss10_score             INT,
            gad7_score              INT,
            phq2_score              INT,
            burnout                 BOOLEAN,
            social_support          VARCHAR(20),
            daily_steps             INT,
            sitting_hrs_day         FLOAT,
            transport_type          VARCHAR(30),
            wearable_device         VARCHAR(50),
            updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 9. BESLENME
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}nutrition (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            user_id                 INT NOT NULL,
            diet_type               VARCHAR(50),
            meals_per_day           INT,
            first_meal_time         VARCHAR(10),
            last_meal_time          VARCHAR(10),
            water_liters            FLOAT,
            vegetable_portions      INT,
            whole_grain_freq        VARCHAR(30),
            red_meat_per_week       INT,
            chicken_per_week        INT,
            fish_per_week           INT,
            egg_per_week            INT,
            dairy_per_week          INT,
            legume_per_week         INT,
            processed_food_freq     VARCHAR(30),
            sugary_drinks_freq      VARCHAR(30),
            fastfood_per_week       INT,
            cooking_habit           VARCHAR(30),
            budget_level            VARCHAR(20),
            daily_calories_est      INT,
            protein_g               FLOAT,
            carb_g                  FLOAT,
            fat_g                   FLOAT,
            fiber_g                 FLOAT,
            disliked_foods          TEXT,
            updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 10. GIDA KISITLAMALARI (çoklu kayıt)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}food_restrictions (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            user_id         INT NOT NULL,
            type            VARCHAR(30),
            item            VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 11. PERFORMANS & ANTRENMAN
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}performance (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            user_id                 INT NOT NULL,
            training_experience_mo  INT,
            training_days_per_week  INT,
            training_location       VARCHAR(30),
            current_training_type   VARCHAR(50),
            session_duration_min    INT,
            pref_weights            BOOLEAN,
            pref_cardio             BOOLEAN,
            pref_yoga               BOOLEAN,
            pref_swimming           BOOLEAN,
            pref_cycling            BOOLEAN,
            pref_running            BOOLEAN,
            pref_other              VARCHAR(100),
            disliked_exercises      TEXT,
            sport_branch            VARCHAR(50),
            goal                    VARCHAR(50),
            pushup_max              INT,
            squat_max               INT,
            plank_sec               INT,
            run_km_time_min         FLOAT,
            vo2max_estimate         FLOAT,
            hrv_ms                  FLOAT,
            sit_reach_cm            FLOAT,
            shoulder_flex           VARCHAR(20),
            ankle_dorsiflexion_cm   FLOAT,
            updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 12. SKORLAR
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}scores (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            user_id             INT NOT NULL,
            metabolic_score     FLOAT,
            cardio_score        FLOAT,
            msk_score           FLOAT,
            nutrition_score     FLOAT,
            mental_score        FLOAT,
            performance_score   FLOAT,
            overall_score       FLOAT,
            scored_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 13. PLANLAR — ANA
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}plans (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            user_id         INT NOT NULL,
            priority_1      VARCHAR(100),
            priority_2      VARCHAR(100),
            priority_3      VARCHAR(100),
            coach_message   TEXT,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    # 14. BESLENME PLANI DETAYI
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}nutrition_plan (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            plan_id         INT NOT NULL,
            meal_name       VARCHAR(50),
            meal_time       VARCHAR(10),
            calories        INT,
            protein_g       FLOAT,
            carb_g          FLOAT,
            fat_g           FLOAT,
            description     TEXT,
            FOREIGN KEY (plan_id) REFERENCES {PREFIX}plans(id)
        )
    """)

    # 15. ANTRENMAN PLANI DETAYI
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}training_plan (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            plan_id         INT NOT NULL,
            day_name        VARCHAR(20),
            exercise_name   VARCHAR(100),
            muscle_group    VARCHAR(50),
            sets            INT,
            reps            VARCHAR(20),
            weight_kg       FLOAT,
            rest_sec        INT,
            progression     VARCHAR(100),
            FOREIGN KEY (plan_id) REFERENCES {PREFIX}plans(id)
        )
    """)

    # 16. TAKVİYE PLANI DETAYI
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}supplement_plan (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            plan_id     INT NOT NULL,
            name        VARCHAR(100),
            dose        VARCHAR(50),
            timing      VARCHAR(50),
            indication  VARCHAR(255),
            priority    INT,
            FOREIGN KEY (plan_id) REFERENCES {PREFIX}plans(id)
        )
    """)

    # 17. GÜNLÜK TAKİP
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PREFIX}check_ins (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            user_id                 INT NOT NULL,
            energy                  INT,
            sleep_hours             FLOAT,
            sleep_quality           INT,
            mood                    INT,
            stress                  INT,
            workout_done            BOOLEAN,
            workout_performance     INT,
            nutrition_compliance    INT,
            pain_level              INT,
            pain_region             VARCHAR(50),
            water_liters            FLOAT,
            daily_steps             INT,
            notes                   TEXT,
            checked_at              DATE DEFAULT (CURRENT_DATE),
            FOREIGN KEY (user_id) REFERENCES {PREFIX}users(id)
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Tüm tablolar başarıyla oluşturuldu!")
    print(f"""
    Oluşturulan tablolar:
    ├── {PREFIX}users
    ├── {PREFIX}profiles
    ├── {PREFIX}health
    ├── {PREFIX}medications
    ├── {PREFIX}current_supplements
    ├── {PREFIX}diseases
    ├── {PREFIX}pain_map
    ├── {PREFIX}lifestyle
    ├── {PREFIX}nutrition
    ├── {PREFIX}food_restrictions
    ├── {PREFIX}performance
    ├── {PREFIX}scores
    ├── {PREFIX}plans
    ├── {PREFIX}nutrition_plan
    ├── {PREFIX}training_plan
    ├── {PREFIX}supplement_plan
    └── {PREFIX}check_ins
    """)

if __name__ == "__main__":
    init_tables()
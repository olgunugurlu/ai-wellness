from config.database import get_connection
from datetime import date, timedelta

PREFIX = "ai_wellness_"

def save_checkin(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    # Bugün zaten check-in var mı?
    cursor.execute(f"""
        SELECT id FROM {PREFIX}check_ins
        WHERE user_id = %s AND checked_at = %s
    """, (user_id, date.today()))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(f"""
            UPDATE {PREFIX}check_ins SET
                energy=%s, sleep_hours=%s, sleep_quality=%s,
                mood=%s, stress=%s, workout_done=%s,
                workout_performance=%s, nutrition_compliance=%s,
                pain_level=%s, pain_region=%s, water_liters=%s,
                daily_steps=%s, notes=%s
            WHERE user_id=%s AND checked_at=%s
        """, (
            data["energy"], data["sleep_hours"], data["sleep_quality"],
            data["mood"], data["stress"], data["workout_done"],
            data["workout_performance"], data["nutrition_compliance"],
            data["pain_level"], data["pain_region"], data["water_liters"],
            data["daily_steps"], data["notes"],
            user_id, date.today()
        ))
    else:
        cursor.execute(f"""
            INSERT INTO {PREFIX}check_ins
                (user_id, energy, sleep_hours, sleep_quality, mood, stress,
                 workout_done, workout_performance, nutrition_compliance,
                 pain_level, pain_region, water_liters, daily_steps, notes, checked_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            data["energy"], data["sleep_hours"], data["sleep_quality"],
            data["mood"], data["stress"], data["workout_done"],
            data["workout_performance"], data["nutrition_compliance"],
            data["pain_level"], data["pain_region"], data["water_liters"],
            data["daily_steps"], data["notes"],
            date.today()
        ))

    conn.commit()
    conn.close()

def get_checkins(user_id, days=30):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    since = date.today() - timedelta(days=days)
    cursor.execute(f"""
        SELECT * FROM {PREFIX}check_ins
        WHERE user_id = %s AND checked_at >= %s
        ORDER BY checked_at ASC
    """, (user_id, since))
    data = cursor.fetchall()
    conn.close()
    return data

def get_today_checkin(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT * FROM {PREFIX}check_ins
        WHERE user_id = %s AND checked_at = %s
    """, (user_id, date.today()))
    data = cursor.fetchone()
    conn.close()
    return data

def get_last_n_days_avg(user_id, days=7):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    since = date.today() - timedelta(days=days)
    cursor.execute(f"""
        SELECT
            ROUND(AVG(energy), 1)               as avg_energy,
            ROUND(AVG(sleep_hours), 1)          as avg_sleep,
            ROUND(AVG(sleep_quality), 1)        as avg_sleep_quality,
            ROUND(AVG(mood), 1)                 as avg_mood,
            ROUND(AVG(stress), 1)               as avg_stress,
            ROUND(AVG(nutrition_compliance), 1) as avg_nutrition,
            SUM(workout_done)                   as total_workouts,
            ROUND(AVG(daily_steps), 0)          as avg_steps
        FROM {PREFIX}check_ins
        WHERE user_id = %s AND checked_at >= %s
    """, (user_id, since))
    data = cursor.fetchone()
    conn.close()
    return data
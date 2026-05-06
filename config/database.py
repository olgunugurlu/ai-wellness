import mysql.connector
from mysql.connector import Error, pooling
import streamlit as st

PREFIX = "ai_wellness_"

# Bağlantı havuzu — tek seferlik oluşturulur
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="ai_wellness_pool",
            pool_size=3,
            pool_reset_session=True,
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            port=st.secrets["mysql"]["port"],
            connect_timeout=10
        )
    return _pool

def get_connection():
    try:
        return get_pool().get_connection()
    except Error as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None
    

def save_scores(user_id, scores):
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO ai_wellness_scores
                (user_id, metabolic_score, cardio_score, msk_score,
                 nutrition_score, mental_score, performance_score, overall_score)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            scores["metabolic"], scores["cardio"], scores["msk"],
            scores["nutrition"], scores["mental"], scores["performance"],
            scores["overall"]
        ))
        conn.commit()
    except Exception as e:
        pass
    finally:
        conn.close()
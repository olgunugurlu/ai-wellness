import mysql.connector
from mysql.connector import Error
import streamlit as st

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            port=st.secrets["mysql"]["port"]
        )
        return conn
    except Error as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None

def run_query(query, params=None, fetch=False):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        st.error(f"Sorgu hatası: {e}")
        return None
    finally:
        conn.close()

def save_scores(user_id, scores):
    conn = get_connection()
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
    conn.close()
import mysql.connector
import streamlit as st

def test_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            port=st.secrets["mysql"]["port"]
        )
        if conn.is_connected():
            print("✅ MySQL bağlantısı başarılı!")
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL versiyonu: {version[0]}")
            conn.close()
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

test_connection()
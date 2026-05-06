import bcrypt
import jwt
import streamlit as st
from datetime import datetime, timedelta
from config.database import get_connection

PREFIX = "ai_wellness_"
SECRET_KEY = st.secrets.get("JWT_SECRET", "ai_wellness_super_secret_2025")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# ─── ŞİFRE ───────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT ─────────────────────────────────────────────────
def create_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ─── KULLANICI İŞLEMLERİ ─────────────────────────────────
def register_user(name: str, email: str, password: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Email var mı?
    cursor.execute(f"SELECT id FROM {PREFIX}users WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Bu email zaten kayıtlı."}

    password_hash = hash_password(password)
    cursor.execute(f"""
        INSERT INTO {PREFIX}users (name, email, password_hash, role, status)
        VALUES (%s, %s, %s, 'user', 'pending')
    """, (name, email, password_hash))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Kaydın alındı. Admin onayından sonra giriş yapabilirsin."}

def login_user(email: str, password: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT id, name, email, password_hash, role, status
        FROM {PREFIX}users WHERE email = %s
    """, (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"success": False, "message": "Email veya şifre hatalı."}

    if not verify_password(password, user["password_hash"]):
        conn.close()
        return {"success": False, "message": "Email veya şifre hatalı."}

    if user["status"] == "pending":
        conn.close()
        return {"success": False, "message": "Hesabın henüz onaylanmadı. Admin onayı bekleniyor."}

    if user["status"] == "rejected":
        conn.close()
        return {"success": False, "message": "Hesabın reddedildi. Lütfen iletişime geç."}

    if user["status"] == "suspended":
        conn.close()
        return {"success": False, "message": "Hesabın askıya alındı."}

    # Son giriş güncelle
    cursor.execute(f"""
        UPDATE {PREFIX}users SET last_login = NOW() WHERE id = %s
    """, (user["id"],))
    conn.commit()
    conn.close()

    token = create_token(user["id"], user["email"], user["role"])
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

def get_current_user() -> dict | None:
    token = st.session_state.get("token")
    if not token:
        return None
    return decode_token(token)

def logout():
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)
    st.session_state.page = "login"


# ─── ADMIN İŞLEMLERİ ─────────────────────────────────────
def get_all_users() -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT id, name, email, role, status, last_login, created_at
        FROM {PREFIX}users ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def get_pending_users() -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT id, name, email, created_at
        FROM {PREFIX}users WHERE status = 'pending'
        ORDER BY created_at ASC
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def update_user_status(user_id: int, status: str, admin_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {PREFIX}users
        SET status = %s, approved_by = %s, approved_at = NOW()
        WHERE id = %s
    """, (status, admin_id, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    # Bağlı tüm verileri sil
    for table in ["check_ins", "plans", "scores", "performance",
                  "food_restrictions", "nutrition", "lifestyle",
                  "pain_map", "diseases", "current_supplements",
                  "medications", "health", "profiles"]:
        cursor.execute(f"DELETE FROM {PREFIX}{table} WHERE user_id = %s", (user_id,))
    cursor.execute(f"DELETE FROM {PREFIX}users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()

def get_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT
            COUNT(*) as total,
            SUM(status = 'approved') as approved,
            SUM(status = 'pending') as pending,
            SUM(status = 'rejected') as rejected,
            SUM(status = 'suspended') as suspended,
            SUM(role = 'admin') as admins
        FROM {PREFIX}users
    """)
    stats = cursor.fetchone()
    conn.close()
    return stats
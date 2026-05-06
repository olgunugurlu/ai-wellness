from config.auth import hash_password
from config.database import get_connection

PREFIX = "ai_wellness_"

def create_admin(name, email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT id FROM {PREFIX}users WHERE email = %s", (email,))
    if cursor.fetchone():
        print("❌ Bu email zaten kayıtlı.")
        conn.close()
        return
    password_hash = hash_password(password)
    cursor.execute(f"""
        INSERT INTO {PREFIX}users (name, email, password_hash, role, status)
        VALUES (%s, %s, %s, 'admin', 'approved')
    """, (name, email, password_hash))
    conn.commit()
    conn.close()
    print(f"✅ Admin oluşturuldu: {email}")

if __name__ == "__main__":
    create_admin(
        name="Admin",
        email="admin@aiwellness.com",
        password="Admin123!"
    )
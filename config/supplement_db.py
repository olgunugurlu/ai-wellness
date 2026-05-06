from config.database import get_connection

PREFIX = "ai_wellness_"

def get_all_supplements(active_only=True):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if active_only:
        cursor.execute(f"""
            SELECT * FROM {PREFIX}supplements_db
            WHERE is_active = TRUE
            ORDER BY category, price_try ASC
        """)
    else:
        cursor.execute(f"""
            SELECT * FROM {PREFIX}supplements_db
            ORDER BY category, price_try ASC
        """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_supplements_by_category(category):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT * FROM {PREFIX}supplements_db
        WHERE category = %s AND is_active = TRUE
        ORDER BY price_try ASC
    """, (category,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT DISTINCT category FROM {PREFIX}supplements_db
        WHERE is_active = TRUE ORDER BY category
    """)
    data = [row["category"] for row in cursor.fetchall()]
    conn.close()
    return data

def add_supplement(data):
    conn = get_connection()
    cursor = conn.cursor()
    price_per_serving = round(
        data["price_try"] / data["serving_count"], 2
    ) if data.get("serving_count") else None
    cursor.execute(f"""
        INSERT INTO {PREFIX}supplements_db
            (category, brand, name, dose_mg, dose_unit, form,
             price_try, serving_count, price_per_serving, is_active)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["category"], data["brand"], data["name"],
        data["dose_mg"], data["dose_unit"], data["form"],
        data["price_try"], data["serving_count"],
        price_per_serving, data.get("is_active", True)
    ))
    conn.commit()
    conn.close()

def update_supplement(sup_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    price_per_serving = round(
        data["price_try"] / data["serving_count"], 2
    ) if data.get("serving_count") else None
    cursor.execute(f"""
        UPDATE {PREFIX}supplements_db SET
            category=%s, brand=%s, name=%s, dose_mg=%s, dose_unit=%s,
            form=%s, price_try=%s, serving_count=%s,
            price_per_serving=%s, is_active=%s
        WHERE id=%s
    """, (
        data["category"], data["brand"], data["name"],
        data["dose_mg"], data["dose_unit"], data["form"],
        data["price_try"], data["serving_count"],
        price_per_serving, data["is_active"], sup_id
    ))
    conn.commit()
    conn.close()

def delete_supplement(sup_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {PREFIX}supplements_db WHERE id=%s", (sup_id,))
    conn.commit()
    conn.close()

def match_supplements(supplement_name, budget_max=None):
    """AI'ın önerdiği takviye adına göre DB'den ürün eşleştir"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Kategori eşleştirme tablosu
    category_map = {
        "omega": "Omega-3",
        "balık yağı": "Omega-3",
        "magnezyum": "Magnezyum",
        "vitamin d": "Vitamin D3",
        "d3": "Vitamin D3",
        "b12": "Vitamin B12",
        "demir": "Demir",
        "ferritin": "Demir",
        "kreatin": "Kreatin",
        "ashwagandha": "Ashwagandha",
        "probiyotik": "Probiyotik",
        "çinko": "Çinko",
        "zinc": "Çinko",
    }

    category = None
    name_lower = supplement_name.lower()
    for key, cat in category_map.items():
        if key in name_lower:
            category = cat
            break

    if not category:
        conn.close()
        return []

    query = f"""
        SELECT * FROM {PREFIX}supplements_db
        WHERE category = %s AND is_active = TRUE
    """
    params = [category]

    if budget_max:
        query += " AND price_try <= %s"
        params.append(budget_max)

    query += " ORDER BY price_try ASC LIMIT 3"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data
from config.database import get_connection

PREFIX = "ai_wellness_"

supplements = [
    # Omega-3
    ("Omega-3", "Solgar", "Omega-3 EPA & DHA", 950, "mg", "Softgel", 485, 120, None),
    ("Omega-3", "Now Foods", "Omega-3 1000mg", 1000, "mg", "Softgel", 280, 100, None),
    ("Omega-3", "Biopharma", "Omega-3 2000mg", 2000, "mg", "Softgel", 320, 60, None),
    ("Omega-3", "Thorne", "Super EPA", 1300, "mg", "Softgel", 650, 90, None),

    # Magnezyum
    ("Magnezyum", "Solgar", "Magnesium Glycinate 400mg", 400, "mg", "Tablet", 420, 60, None),
    ("Magnezyum", "Now Foods", "Magnesium Glycinate 200mg", 200, "mg", "Kapsül", 250, 180, None),
    ("Magnezyum", "Life Extension", "Magnesium Caps 500mg", 500, "mg", "Kapsül", 380, 100, None),
    ("Magnezyum", "Thorne", "Magnesium Bisglycinate", 200, "mg", "Kapsül", 480, 120, None),

    # Vitamin D3
    ("Vitamin D3", "Solgar", "Vitamin D3 2200 IU", 2200, "IU", "Softgel", 210, 100, None),
    ("Vitamin D3", "Now Foods", "Vitamin D3 5000 IU", 5000, "IU", "Softgel", 180, 240, None),
    ("Vitamin D3", "Thorne", "Vitamin D/K2 Liquid", 1000, "IU", "Sıvı", 520, 30, None),
    ("Vitamin D3", "Life Extension", "Vitamin D3 5000 IU", 5000, "IU", "Softgel", 290, 60, None),

    # Vitamin B12
    ("Vitamin B12", "Solgar", "Methylcobalamin 1000mcg", 1000, "mcg", "Tablet", 285, 60, None),
    ("Vitamin B12", "Now Foods", "B-12 1000mcg", 1000, "mcg", "Pastil", 195, 100, None),
    ("Vitamin B12", "Jarrow", "Methyl B-12 1000mcg", 1000, "mcg", "Pastil", 240, 100, None),
    ("Vitamin B12", "Thorne", "B12 Methylcobalamin", 1000, "mcg", "Kapsül", 420, 60, None),

    # Demir
    ("Demir", "Solgar", "Gentle Iron 25mg", 25, "mg", "Kapsül", 310, 90, None),
    ("Demir", "Now Foods", "Iron 36mg", 36, "mg", "Kapsül", 220, 90, None),
    ("Demir", "Thorne", "Iron Bisglycinate 25mg", 25, "mg", "Kapsül", 480, 60, None),

    # Kreatin
    ("Kreatin", "Optimum Nutrition", "Micronized Creatine 5g", 5000, "mg", "Toz", 450, 60, None),
    ("Kreatin", "Now Foods", "Creatine Monohydrate 5g", 5000, "mg", "Toz", 320, 120, None),
    ("Kreatin", "Thorne", "Creatine 5g", 5000, "mg", "Toz", 580, 90, None),

    # Ashwagandha
    ("Ashwagandha", "KSM-66", "Ashwagandha 600mg", 600, "mg", "Kapsül", 380, 60, None),
    ("Ashwagandha", "Now Foods", "Ashwagandha 450mg", 450, "mg", "Kapsül", 290, 90, None),
    ("Ashwagandha", "Solgar", "Ashwagandha Root 300mg", 300, "mg", "Kapsül", 420, 60, None),

    # Probiyotik
    ("Probiyotik", "Solgar", "Probi 20 Billion", 20, "milyar CFU", "Kapsül", 520, 30, None),
    ("Probiyotik", "Now Foods", "Probiotic-10 25 Billion", 25, "milyar CFU", "Kapsül", 380, 50, None),
    ("Probiyotik", "Life Extension", "FLORASSIST Probiotic", 15, "milyar CFU", "Kapsül", 450, 30, None),

    # Çinko
    ("Çinko", "Solgar", "Zinc 22mg", 22, "mg", "Tablet", 180, 100, None),
    ("Çinko", "Now Foods", "Zinc Glycinate 30mg", 30, "mg", "Kapsül", 220, 120, None),
    ("Çinko", "Thorne", "Zinc Picolinate 15mg", 15, "mg", "Kapsül", 350, 60, None),
]

def seed():
    conn = get_connection()
    cursor = conn.cursor()

    # Önce mevcut verileri temizle
    cursor.execute(f"DELETE FROM {PREFIX}supplements_db")

    for sup in supplements:
        category, brand, name, dose_mg, dose_unit, form, price_try, serving_count, _ = sup
        price_per_serving = round(price_try / serving_count, 2) if serving_count else None
        cursor.execute(f"""
            INSERT INTO {PREFIX}supplements_db
                (category, brand, name, dose_mg, dose_unit, form,
                 price_try, serving_count, price_per_serving)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (category, brand, name, dose_mg, dose_unit, form,
              price_try, serving_count, price_per_serving))

    conn.commit()
    conn.close()
    print(f"✅ {len(supplements)} takviye ürünü yüklendi.")

if __name__ == "__main__":
    seed()
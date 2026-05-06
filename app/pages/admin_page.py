import streamlit as st
from config.auth import (
    get_all_users, get_pending_users,
    update_user_status, delete_user, get_stats
)

def show(current_user):
    st.title("⚙️ Admin Paneli")

    # ── İSTATİSTİKLER ──
    stats = get_stats()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👥 Toplam",    stats["total"]     or 0)
    col2.metric("✅ Onaylı",    stats["approved"]  or 0)
    col3.metric("⏳ Bekleyen",  stats["pending"]   or 0)
    col4.metric("❌ Reddedilen",stats["rejected"]  or 0)
    col5.metric("🔴 Askıya",   stats["suspended"] or 0)

    st.divider()

    tab1, tab2, tab3 = st.tabs(["⏳ Onay Bekleyenler", "👥 Tüm Kullanıcılar", "💊 Takviye Ürünleri"])

    # ── ONAY BEKLEYENLer ──
    with tab1:
        pending = get_pending_users()
        if not pending:
            st.info("Onay bekleyen kullanıcı yok.")
        else:
            st.markdown(f"**{len(pending)} kullanıcı onay bekliyor**")
            for u in pending:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
                    col1.markdown(f"**{u['name']}**")
                    col2.markdown(f"{u['email']}")
                    col3.markdown(f"🕐 {str(u['created_at'])[:10]}")
                    with col4:
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Onayla", key=f"approve_{u['id']}"):
                            update_user_status(u["id"], "approved", current_user["user_id"])
                            st.success(f"{u['name']} onaylandı!")
                            st.rerun()
                        if c2.button("❌ Reddet", key=f"reject_{u['id']}"):
                            update_user_status(u["id"], "rejected", current_user["user_id"])
                            st.warning(f"{u['name']} reddedildi.")
                            st.rerun()

    # ── TÜM KULLANICILAR ──
    with tab2:

        users = get_all_users()
        if not users:
            st.info("Henüz kullanıcı yok.")
            return

        # Filtre
        col1, col2 = st.columns(2)
        filter_status = col1.selectbox(
            "Durum Filtresi",
            ["Tümü", "approved", "pending", "rejected", "suspended"],
            key="admin_filter_status"
        )
        filter_role = col2.selectbox(
            "Rol Filtresi",
            ["Tümü", "user", "admin"],
            key="admin_filter_role"
        )

        filtered = users
        if filter_status != "Tümü":
            filtered = [u for u in filtered if u["status"] == filter_status]
        if filter_role != "Tümü":
            filtered = [u for u in filtered if u["role"] == filter_role]

        st.markdown(f"**{len(filtered)} kullanıcı listeleniyor**")
        st.divider()

        for u in filtered:
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 3])

                # Durum rengi
                status_icon = {
                    "approved":  "🟢",
                    "pending":   "🟡",
                    "rejected":  "🔴",
                    "suspended": "⚫"
                }.get(u["status"], "⚪")

                col1.markdown(f"**{u['name']}**  \n{u['email']}")
                # Detay butonu ekle
                if col1.button("🔍 Detay", key=f"detail_{u['id']}"):
                    st.session_state.selected_user = u
                    st.session_state.page = "admin_user_detail"
                    st.rerun()
                col2.markdown(f"Rol: `{u['role']}`  \nKayıt: {str(u['created_at'])[:10]}")
                col3.markdown(f"Durum:  \n{status_icon} {u['status']}")
                col4.markdown(f"Son Giriş:  \n{str(u['last_login'])[:10] if u['last_login'] else '—'}")

                with col5:
                    # Admin kendini değiştiremez
                    if u["id"] == current_user["user_id"]:
                        st.caption("(Sen)")
                        continue

                    action_col1, action_col2 = st.columns(2)

                    if u["status"] != "approved":
                        if action_col1.button("✅ Onayla", key=f"all_approve_{u['id']}"):
                            update_user_status(u["id"], "approved", current_user["user_id"])
                            st.rerun()

                    if u["status"] == "approved":
                        if action_col1.button("⏸ Askıya Al", key=f"suspend_{u['id']}"):
                            update_user_status(u["id"], "suspended", current_user["user_id"])
                            st.rerun()

                    if action_col2.button("🗑 Sil", key=f"delete_{u['id']}"):
                        delete_user(u["id"])
                        st.warning(f"{u['name']} silindi.")
                        st.rerun()



    # ── TAKVİYE YÖNETİMİ ──
    with tab3:

        from config.supplement_db import (
            get_all_supplements, add_supplement,
            update_supplement, delete_supplement, get_categories
        )

        st.subheader("💊 Takviye Ürün Veritabanı")

        # Yeni ürün ekle
        with st.expander("➕ Yeni Ürün Ekle"):
            with st.form("add_supplement"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_category = st.text_input("Kategori", key="ns_cat")
                    new_brand    = st.text_input("Marka",    key="ns_brand")
                    new_name     = st.text_input("Ürün Adı", key="ns_name")
                with col2:
                    new_dose     = st.number_input("Doz",      0.0, 10000.0, 0.0, key="ns_dose")
                    new_unit     = st.text_input("Birim (mg/mcg/IU)", key="ns_unit")
                    new_form     = st.selectbox("Form", ["Kapsül","Tablet","Softgel","Toz","Sıvı","Pastil"], key="ns_form")
                with col3:
                    new_price    = st.number_input("Fiyat (₺)", 0.0, 5000.0, 0.0, key="ns_price")
                    new_serving  = st.number_input("Porsiyon Sayısı", 0, 500, 60, key="ns_serving")
                    new_active   = st.checkbox("Aktif", value=True, key="ns_active")

                if st.form_submit_button("💾 Ekle", use_container_width=True):
                    if new_category and new_brand and new_name:
                        add_supplement({
                            "category": new_category, "brand": new_brand,
                            "name": new_name, "dose_mg": new_dose,
                            "dose_unit": new_unit, "form": new_form,
                            "price_try": new_price, "serving_count": new_serving,
                            "is_active": new_active
                        })
                        st.success("✅ Ürün eklendi!")
                        st.rerun()
                    else:
                        st.error("Kategori, marka ve ürün adı zorunlu.")

        # Filtre
        all_sups = get_all_supplements(active_only=False)
        categories = ["Tümü"] + list(set(s["category"] for s in all_sups))
        filter_cat = st.selectbox("Kategori Filtresi", categories, key="sup_filter_cat")

        filtered_sups = all_sups if filter_cat == "Tümü" else [
            s for s in all_sups if s["category"] == filter_cat
        ]

        st.markdown(f"**{len(filtered_sups)} ürün listeleniyor**")
        st.divider()

        for sup in filtered_sups:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                col1.markdown(f"**{sup['brand']}** — {sup['name']}")
                col1.caption(f"Kategori: {sup['category']} | Form: {sup['form']}")
                col2.markdown(f"💊 {sup['dose_mg']} {sup['dose_unit']}")
                col2.markdown(f"📦 {sup['serving_count']} porsiyon")
                col3.markdown(f"💰 **{sup['price_try']} ₺**")
                if sup.get("price_per_serving"):
                    col3.caption(f"Porsiyon başı: {sup['price_per_serving']} ₺")
                status = "🟢 Aktif" if sup["is_active"] else "🔴 Pasif"
                col4.markdown(status)

                with st.expander(f"✏️ Düzenle / Sil — {sup['name']}", expanded=False):
                    with st.form(f"edit_sup_{sup['id']}"):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_cat   = st.text_input("Kategori", sup["category"],  key=f"ec_{sup['id']}")
                            e_brand = st.text_input("Marka",    sup["brand"],     key=f"eb_{sup['id']}")
                            e_name  = st.text_input("Ürün Adı", sup["name"],      key=f"en_{sup['id']}")
                        with c2:
                            e_dose  = st.number_input("Doz",    0.0, 10000.0, float(sup["dose_mg"] or 0),  key=f"ed_{sup['id']}")
                            e_unit  = st.text_input("Birim",    sup["dose_unit"] or "",                     key=f"eu_{sup['id']}")
                            form_opts = ["Kapsül","Tablet","Softgel","Toz","Sıvı","Pastil"]
                            e_form  = st.selectbox("Form", form_opts,
                                        index=form_opts.index(sup["form"]) if sup["form"] in form_opts else 0,
                                        key=f"ef_{sup['id']}")
                        with c3:
                            e_price   = st.number_input("Fiyat (₺)", 0.0, 5000.0, float(sup["price_try"] or 0),       key=f"ep_{sup['id']}")
                            e_serving = st.number_input("Porsiyon",  0, 500,       int(sup["serving_count"] or 0),     key=f"es_{sup['id']}")
                            e_active  = st.checkbox("Aktif", bool(sup["is_active"]), key=f"ea_{sup['id']}")

                        sc1, sc2 = st.columns(2)
                        if sc1.form_submit_button("💾 Güncelle", use_container_width=True):
                            update_supplement(sup["id"], {
                                "category": e_cat, "brand": e_brand, "name": e_name,
                                "dose_mg": e_dose, "dose_unit": e_unit, "form": e_form,
                                "price_try": e_price, "serving_count": e_serving,
                                "is_active": e_active
                            })
                            st.success("✅ Güncellendi!")
                            st.rerun()
                        if sc2.form_submit_button("🗑 Sil", use_container_width=True):
                            delete_supplement(sup["id"])
                            st.warning("Silindi.")
                            st.rerun()

# ── AI İLE ÜRÜN BUL ──────────────────────────────
        with st.expander("🤖 AI ile Ürün Ara & Ekle", expanded=False):
            st.caption("Kategori ve kriterleri gir, AI piyasadaki gerçek ürünleri önersin.")

            with st.form("ai_supplement_search"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    ai_category = st.text_input("Kategori", "Omega-3", key="ai_cat")
                    ai_budget   = st.number_input("Maks Fiyat (₺)", 0, 2000, 500, key="ai_budget")
                with col2:
                    ai_criteria = st.text_area(
                        "Kriterler",
                        "Yüksek emilimli, iyi marka, Türkiye'de bulunabilir",
                        height=80, key="ai_criteria"
                    )
                with col3:
                    ai_count = st.number_input("Kaç ürün önerilsin?", 2, 10, 5, key="ai_count")

                search_btn = st.form_submit_button("🔍 AI ile Ara", use_container_width=True)

            if search_btn:
                with st.spinner("AI ürünleri araştırıyor..."):
                    import anthropic, json
                    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

                    prompt = f"""
Sen bir takviye ürün uzmanısın. Türkiye pazarında gerçekten bulunan ve satın alınabilen ürünleri öner.
Sadece JSON döndür, başka hiçbir şey yazma.

Kategori: {ai_category}
Kriterler: {ai_criteria}
Maks Fiyat: {ai_budget} TL
Ürün Sayısı: {ai_count}

Şu JSON formatında yanıt ver:
{{
  "urunler": [
    {{
      "marka": "Solgar",
      "urun_adi": "Omega-3 950mg EPA & DHA",
      "doz_mg": 950,
      "doz_birimi": "mg",
      "form": "Softgel",
      "fiyat_tl": 485,
      "porsiyon_sayisi": 120,
      "neden_onerildi": "Yüksek EPA/DHA oranı, iyi emilim"
    }}
  ]
}}

Form değerleri yalnızca şunlardan biri olabilir: Kapsül, Tablet, Softgel, Toz, Sıvı, Pastil
Fiyatlar Türkiye piyasasına yakın gerçekçi olsun.
"""
                    try:
                        msg = client.messages.create(
                            model="claude-sonnet-4-5",
                            max_tokens=2000,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        raw = msg.content[0].text.strip()
                        if "```" in raw:
                            raw = raw.split("```")[1]
                            if raw.startswith("json"):
                                raw = raw[4:]
                        ai_results = json.loads(raw.strip())
                        st.session_state.ai_sup_results = ai_results.get("urunler", [])
                        st.session_state.ai_sup_category = ai_category
                    except Exception as e:
                        st.error(f"AI hatası: {e}")

            # AI sonuçlarını göster
            if st.session_state.get("ai_sup_results"):
                st.divider()
                st.markdown(f"**🤖 AI {len(st.session_state.ai_sup_results)} ürün önerdi — eklemek istediklerini seç:**")

                for idx, prod in enumerate(st.session_state.ai_sup_results):
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        with col1:
                            st.markdown(f"**{prod.get('marka','')}** — {prod.get('urun_adi','')}")
                            st.caption(prod.get("neden_onerildi", ""))
                        with col2:
                            st.markdown(f"💊 {prod.get('doz_mg',0)} {prod.get('doz_birimi','')}")
                            st.markdown(f"📦 {prod.get('porsiyon_sayisi',0)} porsiyon")
                        with col3:
                            st.markdown(f"💰 **{prod.get('fiyat_tl',0)} ₺**")
                            if prod.get("porsiyon_sayisi") and prod.get("fiyat_tl"):
                                pps = round(prod["fiyat_tl"] / prod["porsiyon_sayisi"], 2)
                                st.caption(f"Porsiyon başı: {pps} ₺")
                        with col4:
                            if st.button("➕ Ekle", key=f"ai_add_{idx}", use_container_width=True):
                                from config.supplement_db import add_supplement
                                add_supplement({
                                    "category": st.session_state.get("ai_sup_category", prod.get("marka","")),
                                    "brand":    prod.get("marka", ""),
                                    "name":     prod.get("urun_adi", ""),
                                    "dose_mg":  prod.get("doz_mg", 0),
                                    "dose_unit":prod.get("doz_birimi", "mg"),
                                    "form":     prod.get("form", "Kapsül"),
                                    "price_try":prod.get("fiyat_tl", 0),
                                    "serving_count": prod.get("porsiyon_sayisi", 0),
                                    "is_active": True
                                })
                                st.success(f"✅ {prod.get('urun_adi','')} eklendi!")
                                st.rerun()




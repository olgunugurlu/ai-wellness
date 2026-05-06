import streamlit as st
import json
from datetime import date
from config.user_data import (
    get_user_profile, get_user_health, get_user_lifestyle,
    get_user_nutrition, get_user_performance
)
from config.database import get_connection, save_scores
from core.analysis.rule_engine import run_rules
from core.analysis.scorer import calculate_scores
from core.planning.plan_generator import generate_plan

PREFIX = "ai_wellness_"

def save_plan(user_id, plan):
    conn = get_connection()
    cursor = conn.cursor()

    # Önceki aktif planı kapat
    cursor.execute(f"""
        UPDATE {PREFIX}plans SET is_active = FALSE WHERE user_id = %s
    """, (user_id,))

    # Öncelikler
    bp = plan.get("beslenme_plani", {})
    ap = plan.get("antrenman_plani", {})
    sp = plan.get("supplement_plani", [])
    yasam = plan.get("yasam_tarzi_onerileri", [])

    priorities = []
    if bp: priorities.append("Beslenme Planı")
    if ap: priorities.append("Antrenman Planı")
    if sp: priorities.append("Supplement Planı")

    cursor.execute(f"""
        INSERT INTO {PREFIX}plans
            (user_id, priority_1, priority_2, priority_3, coach_message, is_active)
        VALUES (%s, %s, %s, %s, %s, TRUE)
    """, (
        user_id,
        priorities[0] if len(priorities) > 0 else None,
        priorities[1] if len(priorities) > 1 else None,
        priorities[2] if len(priorities) > 2 else None,
        plan.get("coach_notu", "")
    ))
    plan_id = cursor.lastrowid

    # Beslenme planı detayı
    if bp and "ogutler" in bp:
        for ogut_key, ogut in bp["ogutler"].items():
            cursor.execute(f"""
                INSERT INTO {PREFIX}nutrition_plan
                    (plan_id, meal_name, meal_time, calories, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                plan_id,
                ogut_key,
                ogut.get("saat", ""),
                ogut.get("kalori", 0),
                ogut.get("icerik", "")
            ))

    # Antrenman planı detayı
    if ap and "gunler" in ap:
        for gun in ap["gunler"]:
            for egzersiz in gun.get("egzersizler", []):
                try:
                    tekrar = egzersiz.get("tekrar", "0")
                    tekrar_int = int(str(tekrar).split("-")[0]) if tekrar else 0
                except:
                    tekrar_int = 0
                cursor.execute(f"""
                    INSERT INTO {PREFIX}training_plan
                        (plan_id, day_name, exercise_name, sets, reps, rest_sec)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    plan_id,
                    gun.get("gun", ""),
                    egzersiz.get("ad", ""),
                    egzersiz.get("set", 0),
                    tekrar_int,
                    egzersiz.get("dinlenme_sn", 60)
                ))

    # Supplement planı detayı
    for i, sup in enumerate(sp):
        cursor.execute(f"""
            INSERT INTO {PREFIX}supplement_plan
                (plan_id, name, dose, timing, indication, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            plan_id,
            sup.get("ad", ""),
            sup.get("doz", ""),
            sup.get("zamanlama", ""),
            sup.get("neden", ""),
            sup.get("oncelik", i+1)
        ))

    conn.commit()
    conn.close()
    return plan_id

def show_beslenme(bp):
    st.subheader("🥗 Beslenme Planı")

    if not bp:
        st.warning("Beslenme planı bulunamadı.")
        return

    # Makrolar
    makro = bp.get("makrolar", {})
    kalori = bp.get("gunluk_kalori", 0)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔥 Günlük Kalori",   f"{kalori} kcal")
    col2.metric("🥩 Protein",         f"{makro.get('protein_g', 0)}g")
    col3.metric("🍞 Karbonhidrat",    f"{makro.get('karbonhidrat_g', 0)}g")
    col4.metric("🥑 Yağ",             f"{makro.get('yag_g', 0)}g")

    st.divider()

    # Öğünler
    ogut_labels = {
        "sabah":      "🌅 Kahvaltı",
        "ara_ogut_1": "🍎 Ara Öğün 1",
        "ogle":       "☀️ Öğle",
        "ara_ogut_2": "🍌 Ara Öğün 2",
        "aksam":      "🌙 Akşam"
    }
    ogutler = bp.get("ogutler", {})
    for key, label in ogut_labels.items():
        ogut = ogutler.get(key)
        if ogut:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{label}** — {ogut.get('saat', '')}")
                    st.write(ogut.get("icerik", ""))
                    if ogut.get("ipucu"):
                        st.caption(f"💡 {ogut['ipucu']}")
                with col2:
                    st.metric("Kalori", f"{ogut.get('kalori', 0)} kcal")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**✅ Önerilen Gıdalar**")
        for g in bp.get("onerilen_gidalar", []):
            st.markdown(f"- {g}")
    with col2:
        st.markdown("**❌ Kaçınılacak Gıdalar**")
        for g in bp.get("kacinilacak_gidalar", []):
            st.markdown(f"- {g}")

    if bp.get("haftalik_ipuclari"):
        st.divider()
        st.markdown("**💡 Haftalık İpuçları**")
        for ipucu in bp["haftalik_ipuclari"]:
            st.info(f"→ {ipucu}")

def show_antrenman(ap):
    st.subheader("🏋️ Antrenman Planı")

    if not ap:
        st.warning("Antrenman planı bulunamadı.")
        return

    st.info(f"📅 **Haftalık Yapı:** {ap.get('haftalik_yapi', '')}")

    gunler = ap.get("gunler", [])
    for gun in gunler:
        with st.expander(f"📅 {gun.get('gun', '')} — {gun.get('tur', '')} ({gun.get('sure_dk', 0)} dk)"):
            if gun.get("isinma"):
                st.markdown(f"**🔥 Isınma:** {gun['isinma']}")

            egzersizler = gun.get("egzersizler", [])
            if egzersizler:
                st.markdown("**Egzersizler:**")
                for e in egzersizler:
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        col1.markdown(f"**{e.get('ad', '')}**")
                        col2.metric("Set",     e.get("set", 0))
                        col3.metric("Tekrar",  e.get("tekrar", 0))
                        col4.metric("Dinlenme", f"{e.get('dinlenme_sn', 60)}sn")
                        if e.get("not"):
                            st.caption(f"📌 {e['not']}")

            if gun.get("soguma"):
                st.markdown(f"**❄️ Soğuma:** {gun['soguma']}")

    if ap.get("ilerleme_protokolu"):
        st.divider()
        st.success(f"📈 **İlerleme Protokolü:** {ap['ilerleme_protokolu']}")

    if ap.get("haftalik_ipuclari"):
        st.divider()
        st.markdown("**💡 İpuçları**")
        for ipucu in ap["haftalik_ipuclari"]:
            st.info(f"→ {ipucu}")

def show_supplement(sp):
    st.subheader("💊 Supplement Planı")

    if not sp:
        st.warning("Supplement planı bulunamadı.")
        return

    sp_sorted = sorted(sp, key=lambda x: x.get("oncelik", 99))
    for i, sup in enumerate(sp_sorted):
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{i+1}. {sup.get('ad', '')}**")
                st.caption(sup.get("neden", ""))
            with col2:
                st.markdown(f"💊 **Doz:** {sup.get('doz', '')}")
            with col3:
                st.markdown(f"⏰ **Zamanlama:** {sup.get('zamanlama', '')}")

def show_yasam(yasam):
    st.subheader("🌿 Yaşam Tarzı Önerileri")

    if not yasam:
        return

    kat_icons = {
        "Uyku": "🌙", "Stres": "🧘", "Hareket": "🚶",
        "Hidrasyon": "💧", "Sosyal": "👥", "Zihinsel": "🧠"
    }

    for oneri in yasam:
        kat = oneri.get("kategori", "")
        icon = next((v for k, v in kat_icons.items() if k.lower() in kat.lower()), "💡")
        with st.container(border=True):
            st.markdown(f"**{icon} {kat}**")
            st.write(oneri.get("oneri", ""))
            if oneri.get("nasil"):
                st.caption(f"→ {oneri['nasil']}")

def show(current_user):
    user_id = current_user["user_id"]
    st.title("🥗 Kişisel Sağlık Planım")

    # Veri yükle
    profile     = get_user_profile(user_id)
    health      = get_user_health(user_id)
    lifestyle   = get_user_lifestyle(user_id)
    nutrition   = get_user_nutrition(user_id)
    performance = get_user_performance(user_id)

    if not profile:
        st.warning("Önce değerlendirme formunu doldurman gerekiyor.")
        if st.button("📋 Değerlendirme Formuna Git", key="goto_assessment"):
            st.session_state.page = "assessment"
            st.rerun()
        return

    # Mevcut plan var mı kontrol et
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT * FROM {PREFIX}plans
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    existing_plan = cursor.fetchone()
    conn.close()

    # Plan oluştur butonu
    col1, col2 = st.columns([3, 1])
    with col1:
        if existing_plan:
            st.success(f"✅ Aktif planın var — oluşturulma: {str(existing_plan['created_at'])[:10]}")
        else:
            st.info("Henüz planın yok. Aşağıdan oluşturabilirsin.")
    with col2:
        btn_label = "🔄 Planı Yenile" if existing_plan else "✨ Plan Oluştur"
        generate_btn = st.button(btn_label, type="primary",
                                  use_container_width=True, key="generate_plan")

    if generate_btn:
        with st.spinner("🤖 Claude planını oluşturuyor... (30-60 saniye sürebilir)"):
            flags  = run_rules(profile, health, lifestyle, nutrition, performance)
            scores = calculate_scores(profile, health, lifestyle, nutrition, performance, flags)
            result = generate_plan(profile, health, lifestyle, nutrition, performance, scores, flags)

        if result["success"]:
            plan_data = result["plan"]
            save_plan(user_id, plan_data)
            st.session_state.current_plan = plan_data
            st.success("✅ Planın oluşturuldu!")
            st.rerun()
        else:
            st.error(f"Plan oluşturulurken hata: {result['error']}")
        return

    # Plan göster
    plan_data = st.session_state.get("current_plan")

    # Session'da yoksa DB'den yükle
    if not plan_data and existing_plan:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Beslenme
        cursor.execute(f"""
            SELECT * FROM {PREFIX}nutrition_plan WHERE plan_id = %s
        """, (existing_plan["id"],))
        nutrition_rows = cursor.fetchall()

        # Antrenman
        cursor.execute(f"""
            SELECT * FROM {PREFIX}training_plan WHERE plan_id = %s
        """, (existing_plan["id"],))
        training_rows = cursor.fetchall()

        # Supplement
        cursor.execute(f"""
            SELECT * FROM {PREFIX}supplement_plan
            WHERE plan_id = %s ORDER BY priority
        """, (existing_plan["id"],))
        supplement_rows = cursor.fetchall()
        conn.close()

        # DB verilerini plan formatına çevir
        ogutler = {}
        for row in nutrition_rows:
            ogutler[row["meal_name"]] = {
                "saat": row["meal_time"],
                "icerik": row["description"],
                "kalori": row["calories"],
                "ipucu": ""
            }

        gunler_dict = {}
        for row in training_rows:
            gun = row["day_name"]
            if gun not in gunler_dict:
                gunler_dict[gun] = {"gun": gun, "tur": "", "sure_dk": 0, "egzersizler": []}
            gunler_dict[gun]["egzersizler"].append({
                "ad": row["exercise_name"],
                "set": row["sets"],
                "tekrar": str(row["reps"]),
                "dinlenme_sn": row["rest_sec"],
                "not": ""
            })

        plan_data = {
            "beslenme_plani": {
                "gunluk_kalori": 0,
                "makrolar": {"protein_g": 0, "karbonhidrat_g": 0, "yag_g": 0},
                "ogutler": ogutler,
                "onerilen_gidalar": [],
                "kacinilacak_gidalar": [],
                "haftalik_ipuclari": []
            },
            "antrenman_plani": {
                "haftalik_yapi": "",
                "gunler": list(gunler_dict.values()),
                "haftalik_ipuclari": [],
                "ilerleme_protokolu": ""
            },
            "supplement_plani": [
                {
                    "ad": r["name"], "doz": r["dose"],
                    "zamanlama": r["timing"], "neden": r["indication"],
                    "oncelik": r["priority"]
                } for r in supplement_rows
            ],
            "yasam_tarzi_onerileri": [],
            "coach_notu": existing_plan.get("coach_message", "")
        }

    if not plan_data:
        return

    # Koç notu
    if plan_data.get("coach_notu"):
        st.info(f"💬 **Koç Notun:** {plan_data['coach_notu']}")

    st.divider()

    # Sekmeler
    tab1, tab2, tab3, tab4 = st.tabs([
        "🥗 Beslenme", "🏋️ Antrenman", "💊 Supplement", "🌿 Yaşam Tarzı"
    ])

    with tab1:
        show_beslenme(plan_data.get("beslenme_plani"))
    with tab2:
        show_antrenman(plan_data.get("antrenman_plani"))
    with tab3:
        show_supplement(plan_data.get("supplement_plani", []))
    with tab4:
        show_yasam(plan_data.get("yasam_tarzi_onerileri", []))

# PDF İNDİR
    st.divider()
    st.subheader("📄 Rapor İndir")

    # Session state başlat
    if "pdf_tr_bytes" not in st.session_state:
        st.session_state.pdf_tr_bytes = None
    if "pdf_en_bytes" not in st.session_state:
        st.session_state.pdf_en_bytes = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🇹🇷 Türkçe PDF Oluştur", use_container_width=True, key="btn_pdf_tr"):
            with st.spinner("PDF oluşturuluyor..."):
                try:
                    from core.pdf_generator import generate_pdf
                    flags_pdf  = run_rules(profile, health, lifestyle, nutrition, performance)
                    scores_pdf = calculate_scores(profile, health, lifestyle, nutrition, performance, flags_pdf)
                    user_info  = {"name": current_user.get("email", "").split("@")[0]}
                    st.session_state.pdf_tr_bytes = generate_pdf(
                        user_info, scores_pdf, flags_pdf, plan_data, lang="tr"
                    )
                    st.success("✅ PDF hazır, aşağıdan indir.")
                except Exception as e:
                    st.error(f"PDF hatası: {e}")

    with col2:
        if st.button("🇬🇧 English PDF Generate", use_container_width=True, key="btn_pdf_en"):
            with st.spinner("Generating PDF..."):
                try:
                    from core.pdf_generator import generate_pdf
                    flags_pdf  = run_rules(profile, health, lifestyle, nutrition, performance)
                    scores_pdf = calculate_scores(profile, health, lifestyle, nutrition, performance, flags_pdf)
                    user_info  = {"name": current_user.get("email", "").split("@")[0]}
                    st.session_state.pdf_en_bytes = generate_pdf(
                        user_info, scores_pdf, flags_pdf, plan_data, lang="en"
                    )
                    st.success("✅ PDF ready, download below.")
                except Exception as e:
                    st.error(f"PDF error: {e}")

    # İndirme butonları
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.pdf_tr_bytes:
            st.download_button(
                label="⬇️ Türkçe PDF İndir",
                data=st.session_state.pdf_tr_bytes,
                file_name=f"ai_wellness_rapor_{date.today()}.pdf",
                mime="application/pdf",
                key="dl_tr"
            )
    with col2:
        if st.session_state.pdf_en_bytes:
            st.download_button(
                label="⬇️ Download English PDF",
                data=st.session_state.pdf_en_bytes,
                file_name=f"ai_wellness_report_{date.today()}.pdf",
                mime="application/pdf",
                key="dl_en"
            )

    st.divider()
    st.caption("⚠️ Bu plan bilgi amaçlıdır. Tıbbi tavsiye niteliği taşımaz. "
               "Herhangi bir sağlık kararı almadan önce doktorunuza danışın.")
import streamlit as st
import plotly.graph_objects as go
from config.user_data import (
    get_user_profile, get_user_health, get_user_lifestyle,
    get_user_nutrition, get_user_performance
)
from config.database import save_scores
from core.analysis.rule_engine import run_rules
from core.analysis.scorer import calculate_scores
from core.analysis.priority import get_top_priorities
from core.analysis.ai_analyzer import analyze_with_ai

def radar_chart(scores):
    categories = ["Metabolik", "Kardiyovasküler", "Kas-İskelet",
                  "Beslenme", "Zihinsel", "Performans"]
    values = [
        scores["metabolic"], scores["cardio"], scores["msk"],
        scores["nutrition"], scores["mental"], scores["performance"]
    ]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(43, 134, 171, 0.2)",
        line=dict(color="rgba(43, 134, 171, 0.9)", width=2),
        name="Wellness Skoru"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        showlegend=False,
        height=380,
        margin=dict(t=30, b=30, l=30, r=30)
    )
    return fig

def score_color(score):
    if score >= 75: return "🟢"
    if score >= 50: return "🟡"
    return "🔴"

def show(current_user):
    user_id = current_user["user_id"]
    st.title("📊 Sağlık Analizi & Dashboard")

    # Veri yükle
    profile     = get_user_profile(user_id)
    health      = get_user_health(user_id)
    lifestyle   = get_user_lifestyle(user_id)
    nutrition   = get_user_nutrition(user_id)
    performance = get_user_performance(user_id)

    if not profile:
        st.warning("Henüz değerlendirme formu doldurulmamış.")
        if st.button("📋 Değerlendirme Formuna Git"):
            st.session_state.page = "assessment"
            st.rerun()
        return

    # Analiz çalıştır
    with st.spinner("🔬 Analiz yapılıyor..."):
        flags  = run_rules(profile, health, lifestyle, nutrition, performance)
        scores = calculate_scores(profile, health, lifestyle, nutrition, performance, flags)
        priorities = get_top_priorities(scores, flags)
        save_scores(user_id, scores)

    # ── GENEL SKOR ───────────────────────────────────────
    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        overall = scores["overall"]
        color   = score_color(overall)
        st.markdown(f"""
        <div style='text-align:center; padding:20px;
                    border-radius:12px; background:#f0f4f8;'>
            <div style='font-size:64px'>{color}</div>
            <div style='font-size:48px; font-weight:bold;
                        color:#1B4F72'>{overall}</div>
            <div style='font-size:16px; color:#5D6D7E'>
                Genel Wellness Skoru
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Kategori Skorları")
        score_items = [
            ("🔬 Metabolik",       scores["metabolic"]),
            ("❤️ Kardiyovasküler", scores["cardio"]),
            ("🦴 Kas-İskelet",     scores["msk"]),
            ("🥗 Beslenme",        scores["nutrition"]),
            ("🧠 Zihinsel",        scores["mental"]),
            ("🏋️ Performans",      scores["performance"]),
        ]
        for label, score in score_items:
            icon = score_color(score)
            st.markdown(f"{icon} **{label}:** {score}/100")

    with col2:
        st.plotly_chart(radar_chart(scores), use_container_width=True)

    # ── AI ANALİZİ ───────────────────────────────────────
    st.divider()
    st.subheader("🤖 AI Değerlendirmesi")

    if st.button("✨ AI Analizi Oluştur", type="primary", key="run_ai"):
        with st.spinner("Claude analiz yapıyor..."):
            ai_result = analyze_with_ai(
                profile, health, lifestyle, nutrition, performance, scores, flags
            )
            st.session_state.ai_result = ai_result

    ai_result = st.session_state.get("ai_result")

    if ai_result:
        st.info(ai_result.get("motivasyon_mesaji", ""))
        st.markdown(f"**📋 Genel Değerlendirme**")
        st.write(ai_result.get("genel_degerlendirme", ""))

        # Güçlü yönler
        guclu = ai_result.get("guclu_yonler", [])
        if guclu:
            st.markdown("**💪 Güçlü Yönlerin**")
            cols = st.columns(len(guclu))
            for i, g in enumerate(guclu):
                cols[i].success(f"✅ {g}")

        # Top 3 Öncelik
        st.divider()
        st.subheader("🎯 En Kritik 3 Önceliğin")
        icons = ["🥇", "🥈", "🥉"]
        for i, key in enumerate(["oncelik_1", "oncelik_2", "oncelik_3"]):
            onc = ai_result.get(key, {})
            if onc.get("baslik") and onc["baslik"] != "—":
                with st.container(border=True):
                    st.markdown(f"#### {icons[i]} {onc['baslik']}")
                    st.write(onc.get("aciklama", ""))
                    adimlar = onc.get("adimlar", [])
                    if adimlar:
                        st.markdown("**Somut Adımlar:**")
                        for adim in adimlar:
                            st.markdown(f"→ {adim}")

    # ── KURAL FLAGLERI ───────────────────────────────────
    if flags:
        st.divider()
        with st.expander(f"⚠️ Tespit Edilen Riskler ({len(flags)} adet)"):
            priority_order = {"KRİTİK": 0, "YÜKSEK": 1, "ORTA": 2, "DÜŞÜK": 3}
            sorted_flags = sorted(flags, key=lambda f: priority_order.get(f.priority, 4))

            for f in sorted_flags:
                icon = {"KRİTİK": "🔴", "YÜKSEK": "🟠", "ORTA": "🟡", "DÜŞÜK": "🔵"}.get(f.priority, "⚪")
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    col1.markdown(f"{icon} **{f.priority}**  \n{f.message}")
                    col2.markdown(f"**Öneri:** {f.action}")

    # ── ETİK UYARI ───────────────────────────────────────
    st.divider()
    st.caption("⚠️ Bu analiz bilgi amaçlıdır. Tıbbi teşhis niteliği taşımaz. "
               "Herhangi bir sağlık kararı almadan önce doktorunuza danışın.")
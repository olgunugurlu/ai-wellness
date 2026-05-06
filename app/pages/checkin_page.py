import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from core.tracking.checkin import (
    save_checkin, get_checkins, get_today_checkin, get_last_n_days_avg
)
from core.tracking.adaptation import check_adaptations

def trend_chart(checkins, field, label, color="#2E86AB"):
    if not checkins:
        return None
    dates  = [str(c["checked_at"]) for c in checkins]
    values = [c.get(field, 0) or 0 for c in checkins]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=values, mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(size=6),
        name=label
    ))
    fig.update_layout(
        height=200,
        margin=dict(t=10, b=10, l=10, r=10),
        yaxis=dict(range=[0, 10]),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def show(current_user):
    user_id = current_user["user_id"]
    st.title("✅ Günlük Takip")

    today_checkin = get_today_checkin(user_id)
    checkins      = get_checkins(user_id, days=30)
    avg7          = get_last_n_days_avg(user_id, days=7)

    tab1, tab2, tab3 = st.tabs(["📝 Bugünkü Check-in", "📈 Trendler", "⚡ Adaptasyon"])

    # ════════════════════════════
    # TAB 1 — CHECK-IN FORMU
    # ════════════════════════════
    with tab1:
        st.subheader(f"📅 {date.today().strftime('%d %B %Y')} Günlük Check-in")

        if today_checkin:
            st.success("✅ Bugünkü check-in'ini tamamladın!")
            if not st.checkbox("Güncelle", key="update_checkin"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("⚡ Enerji",      f"{today_checkin.get('energy', 0)}/10")
                col2.metric("😴 Uyku",        f"{today_checkin.get('sleep_hours', 0)} saat")
                col3.metric("😊 Ruh Hali",    f"{today_checkin.get('mood', 0)}/10")
                col4.metric("😰 Stres",       f"{today_checkin.get('stress', 0)}/10")
                return

        with st.form("checkin_form"):
            st.markdown("**⚡ Enerji & Uyku**")
            col1, col2, col3 = st.columns(3)
            with col1:
                energy        = st.slider("Enerji Seviyesi (0–10)", 0, 10, 5, key="ci_energy")
            with col2:
                sleep_hours   = st.number_input("Uyku Süresi (saat)", 0.0, 12.0, 7.0, 0.5, key="ci_sleep")
            with col3:
                sleep_quality = st.slider("Uyku Kalitesi (0–10)", 0, 10, 5, key="ci_sq")

            st.markdown("**😊 Ruh Hali & Stres**")
            col1, col2 = st.columns(2)
            with col1:
                mood   = st.slider("Ruh Hali (0–10)", 0, 10, 5, key="ci_mood")
            with col2:
                stress = st.slider("Stres (0–10)", 0, 10, 4, key="ci_stress")

            st.markdown("**🏋️ Antrenman**")
            col1, col2 = st.columns(2)
            with col1:
                workout_done = st.checkbox("Antrenman yaptım", key="ci_workout")
            with col2:
                workout_performance = st.slider(
                    "Antrenman Performansı (0–10)", 0, 10, 5,
                    disabled=not workout_done, key="ci_wp"
                )

            st.markdown("**🥗 Beslenme & Hareket**")
            col1, col2, col3 = st.columns(3)
            with col1:
                nutrition_compliance = st.select_slider(
                    "Beslenme Uyumu (%)",
                    options=[0, 25, 50, 75, 100],
                    value=75, key="ci_nutrition"
                )
            with col2:
                water_liters = st.number_input("Su (litre)", 0.0, 6.0, 2.0, 0.25, key="ci_water")
            with col3:
                daily_steps = st.number_input("Adım Sayısı", 0, 30000, 5000, 500, key="ci_steps")

            st.markdown("**🔴 Ağrı**")
            col1, col2 = st.columns(2)
            with col1:
                pain_level = st.slider("Ağrı Seviyesi (0–10, 0=yok)", 0, 10, 0, key="ci_pain")
            with col2:
                pain_region = st.text_input("Ağrı Bölgesi (varsa)", key="ci_pain_region")

            notes = st.text_area("Notlar (isteğe bağlı)", height=80, key="ci_notes")

            if st.form_submit_button("💾 Check-in Kaydet", type="primary", use_container_width=True):
                save_checkin(user_id, {
                    "energy": energy, "sleep_hours": sleep_hours,
                    "sleep_quality": sleep_quality, "mood": mood,
                    "stress": stress, "workout_done": workout_done,
                    "workout_performance": workout_performance if workout_done else 0,
                    "nutrition_compliance": nutrition_compliance,
                    "pain_level": pain_level, "pain_region": pain_region,
                    "water_liters": water_liters, "daily_steps": daily_steps,
                    "notes": notes
                })
                st.success("✅ Check-in kaydedildi!")
                st.rerun()

    # ════════════════════════════
    # TAB 2 — TRENDLER
    # ════════════════════════════
    with tab2:
        if not checkins:
            st.info("Henüz check-in verisi yok. İlk check-in'ini yap!")
            return

        # 7 günlük ortalamalar
        if avg7:
            st.subheader("📊 Son 7 Gün Ortalaması")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("⚡ Enerji",      avg7.get("avg_energy") or "—")
            col2.metric("😴 Uyku",        f"{avg7.get('avg_sleep') or '—'} saat")
            col3.metric("😊 Ruh Hali",    avg7.get("avg_mood") or "—")
            col4.metric("😰 Stres",       avg7.get("avg_stress") or "—")
            col5.metric("🏋️ Antrenman",   f"{int(avg7.get('total_workouts') or 0)} gün")

        st.divider()
        st.subheader("📈 30 Günlük Trendler")

        col1, col2 = st.columns(2)
        with col1:
            fig = trend_chart(checkins, "energy", "Enerji", "#2E86AB")
            if fig:
                st.markdown("**⚡ Enerji**")
                st.plotly_chart(fig, use_container_width=True, key="chart_energy")

            fig = trend_chart(checkins, "mood", "Ruh Hali", "#A8D8A8")
            if fig:
                st.markdown("**😊 Ruh Hali**")
                st.plotly_chart(fig, use_container_width=True, key="chart_mood")

            fig = trend_chart(checkins, "sleep_quality", "Uyku Kalitesi", "#9B59B6")
            if fig:
                st.markdown("**😴 Uyku Kalitesi**")
                st.plotly_chart(fig, use_container_width=True, key="chart_sleep_q")

        with col2:
            fig = trend_chart(checkins, "stress", "Stres", "#E74C3C")
            if fig:
                st.markdown("**😰 Stres**")
                st.plotly_chart(fig, use_container_width=True, key="chart_stress")

            fig = trend_chart(checkins, "pain_level", "Ağrı", "#E67E22")
            if fig:
                st.markdown("**🔴 Ağrı**")
                st.plotly_chart(fig, use_container_width=True, key="chart_pain")

            fig = trend_chart(checkins, "nutrition_compliance", "Beslenme Uyumu", "#27AE60")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_nutrition")
                st.markdown("**🥗 Beslenme Uyumu (%)**")

        # Antrenman takvimi
        st.divider()
        st.subheader("🏋️ Antrenman Takvimi")
        workout_data = {str(c["checked_at"]): "✅" if c.get("workout_done") else "❌"
                       for c in checkins}
        cols = st.columns(7)
        for i, (day, status) in enumerate(list(workout_data.items())[-14:]):
            cols[i % 7].markdown(f"**{day[-5:]}**  \n{status}")

    # ════════════════════════════
    # TAB 3 — ADAPTASYON
    # ════════════════════════════
    with tab3:
        st.subheader("⚡ Adaptasyon Önerileri")

        if not checkins or len(checkins) < 3:
            st.info("En az 3 günlük veri gerekiyor. Check-in yapmaya devam et!")
            return

        alerts = check_adaptations(checkins)

        if not alerts:
            st.success("✅ Her şey yolunda görünüyor! Planına devam et.")
            return

        for alert in alerts:
            alert_type = alert["type"]
            if alert_type == "danger":
                container = st.error
            elif alert_type == "warning":
                container = st.warning
            elif alert_type == "success":
                container = st.success
            else:
                container = st.info

            with st.container(border=True):
                st.markdown(f"### {alert['icon']} {alert['title']}")
                st.write(alert["message"])
                st.markdown(f"**→ Öneri:** {alert['action']}")
import streamlit as st
import anthropic
from config.user_data import (
    get_user_profile, get_user_health, get_user_lifestyle,
    get_user_nutrition, get_user_performance
)
from core.tracking.checkin import get_last_n_days_avg, get_checkins
from core.analysis.rule_engine import run_rules
from core.analysis.scorer import calculate_scores

def build_system_prompt(profile, health, lifestyle, nutrition, performance, scores, avg7):
    flag_summary = ""
    if profile and health:
        flags = run_rules(profile, health, lifestyle, nutrition, performance)
        critical = [f for f in flags if f.priority == "KRİTİK"]
        high     = [f for f in flags if f.priority == "YÜKSEK"]
        if critical:
            flag_summary += f"\nKRİTİK RİSKLER: {', '.join([f.message for f in critical])}"
        if high:
            flag_summary += f"\nYÜKSEK RİSKLER: {', '.join([f.message for f in high])}"

    profile_summary = ""
    if profile:
        profile_summary = f"""
Kullanıcı Profili:
- Yaş: {profile.get('age')} | Cinsiyet: {profile.get('gender')}
- Boy: {profile.get('height_cm')} cm | Kilo: {profile.get('weight_kg')} kg
- Aktivite: {profile.get('activity_level')} | Meslek: {profile.get('occupation_type')}
"""

    health_summary = ""
    if health:
        health_summary = f"""
Sağlık Durumu:
- Sabah Enerjisi: {health.get('energy_morning')}/10
- Uyku Kalitesi: {health.get('sleep_quality')}/10
- Odak: {health.get('focus_score')}/10
- Ruh Hali: {health.get('mood_score')}/10
"""

    scores_summary = ""
    if scores:
        scores_summary = f"""
Wellness Skorları:
- Genel: {scores.get('overall')}/100
- Metabolik: {scores.get('metabolic')}/100
- Beslenme: {scores.get('nutrition')}/100
- Performans: {scores.get('performance')}/100
- Zihinsel: {scores.get('mental')}/100
"""

    avg7_summary = ""
    if avg7:
        avg7_summary = f"""
Son 7 Gün Ortalaması:
- Enerji: {avg7.get('avg_energy') or '—'}/10
- Uyku: {avg7.get('avg_sleep') or '—'} saat
- Ruh Hali: {avg7.get('avg_mood') or '—'}/10
- Stres: {avg7.get('avg_stress') or '—'}/10
- Antrenman: {int(avg7.get('total_workouts') or 0)} gün/hafta
"""

    return f"""Sen AI Wellness platformunun kişisel sağlık koçusun.
Fizyoterapist, diyetisyen, fitness koçu ve psikolog perspektifini birleştiriyorsun.

TEMEL KURALLAR:
- Türkçe konuş, samimi ve motive edici ol
- Teşhis koyma, doktor yerine geçme
- Kanıta dayalı, uygulanabilir öneriler sun
- Kısa ve net yanıtlar ver (çok uzun yazma)
- Kullanıcının verilerini referans al
- Gerektiğinde doktora yönlendir

{profile_summary}
{health_summary}
{scores_summary}
{avg7_summary}
{flag_summary}

Kullanıcı sana her türlü sağlık, beslenme, antrenman ve yaşam tarzı sorusu sorabilir.
Verilerini bilerek kişiselleştirilmiş yanıtlar ver."""

def show(current_user):
    user_id = current_user["user_id"]
    st.title("🤖 AI Koç")
    st.caption("Sağlık, beslenme, antrenman ve yaşam tarzı hakkında her şeyi sorabilirsin.")

    # Kullanıcı verilerini yükle
    profile     = get_user_profile(user_id)
    health      = get_user_health(user_id)
    lifestyle   = get_user_lifestyle(user_id)
    nutrition   = get_user_nutrition(user_id)
    performance = get_user_performance(user_id)
    avg7        = get_last_n_days_avg(user_id, days=7)

    # Skorları hesapla
    scores = None
    if profile and health:
        flags  = run_rules(profile, health, lifestyle, nutrition, performance)
        scores = calculate_scores(profile, health, lifestyle, nutrition, performance, flags)

    # Sistem promptu oluştur
    system_prompt = build_system_prompt(
        profile, health, lifestyle, nutrition, performance, scores, avg7
    )

    # Chat geçmişini başlat
    if "coach_messages" not in st.session_state:
        st.session_state.coach_messages = []

    # Karşılama mesajı
    if not st.session_state.coach_messages:
        name = current_user.get("email", "").split("@")[0]
        if profile:
            welcome = f"Merhaba! Ben senin AI koçunum 👋 Verilerini inceledim. Sana nasıl yardımcı olabilirim?"
        else:
            welcome = "Merhaba! Ben senin AI koçunum 👋 Değerlendirme formunu doldurursan sana çok daha kişisel öneriler sunabilirim. Şimdilik genel sorularını yanıtlayabilirim!"
        st.session_state.coach_messages.append({
            "role": "assistant",
            "content": welcome
        })

    # Hızlı soru butonları
    if len(st.session_state.coach_messages) <= 1:
        st.markdown("**💡 Hızlı Sorular:**")
        col1, col2, col3, col4 = st.columns(4)
        quick_questions = [
            "Bugün ne yemeliyim?",
            "Antrenman önerir misin?",
            "Uyku kalitemi nasıl artırırım?",
            "Hangi takviyeyi almalıyım?"
        ]
        cols = [col1, col2, col3, col4]
        for i, (col, q) in enumerate(zip(cols, quick_questions)):
            if col.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.coach_messages.append({"role": "user", "content": q})
                st.rerun()

    # Mesajları göster
    for msg in st.session_state.coach_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Mesajını yaz...", key="coach_input"):
        st.session_state.coach_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                try:
                    client = anthropic.Anthropic(
                        api_key=st.secrets["ANTHROPIC_API_KEY"]
                    )

                    # Son 10 mesajı al (token tasarrufu)
                    messages = st.session_state.coach_messages[-10:]
                    # Sadece user/assistant mesajları
                    api_messages = [
                        {"role": m["role"], "content": m["content"]}
                        for m in messages
                        if m["role"] in ["user", "assistant"]
                    ]

                    response = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1000,
                        system=system_prompt,
                        messages=api_messages
                    )

                    answer = response.content[0].text
                    st.write(answer)
                    st.session_state.coach_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    error_msg = "Şu an yanıt veremiyorum. Lütfen tekrar dene."
                    st.error(error_msg)
                    st.session_state.coach_messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    # Sohbeti temizle
    st.divider()
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑 Sohbeti Temizle", key="clear_chat", use_container_width=True):
            st.session_state.coach_messages = []
            st.rerun()

    st.caption("⚠️ AI Koç tıbbi tavsiye vermez. Sağlık kararları için doktorunuza danışın.")
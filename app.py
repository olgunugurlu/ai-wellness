import streamlit as st
from config.init_db import init_tables
from config.auth import get_current_user, logout

st.set_page_config(
    page_title="AI Wellness",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Oturum kontrolü
current_user = get_current_user()

# Tabloları kontrol et
init_tables()

# Session state başlat
if "page" not in st.session_state:
    st.session_state.page = "login"
# Giriş yapıldıysa ve hâlâ login/register sayfasındaysa home'a yönlendir
if current_user and st.session_state.page in ["login", "register"]:
    st.session_state.page = "home"
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# Oturum kontrolü
current_user = get_current_user()

# ─── GİRİŞ GEREKTİREN SAYFALAR ───────────────────────────
if not current_user:
    # Sadece login ve register erişilebilir
    if st.session_state.page not in ["login", "register"]:
        st.session_state.page = "login"

    page = st.session_state.page
    if page == "login":
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app", "pages"))
        from auth_page import show_login
        show_login()
    elif page == "register":
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app", "pages"))
        from auth_page import show_register
        show_register()
    st.stop()

# ─── GİRİŞ YAPILMIŞ ─────────────────────────────────────
# Sidebar
with st.sidebar:
    st.title("🧠 AI Wellness")
    st.caption(f"👤 {current_user['email']}")
    st.caption(f"🔑 {current_user['role'].upper()}")
    st.divider()

    if st.button("🏠 Ana Sayfa",      use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
    if st.button("📋 Değerlendirme",  use_container_width=True, key="nav_assessment"):
        st.session_state.page = "assessment"
        st.rerun()
    if st.button("📊 Analiz",         use_container_width=True, key="nav_analysis"):
        st.session_state.page = "analysis"
        st.rerun()
    if st.button("🥗 Planım",         use_container_width=True, key="nav_plan"):
        st.session_state.page = "plan"
        st.rerun()
    if st.button("✅ Günlük Takip",   use_container_width=True, key="nav_checkin"):
        st.session_state.page = "checkin"
        st.rerun()
    if st.button("🤖 AI Koç",         use_container_width=True, key="nav_coach"):
        st.session_state.page = "coach"
        st.rerun()

    # Sadece admin görsün
    if current_user["role"] == "admin":
        st.divider()
        if st.button("⚙️ Admin Paneli", use_container_width=True, key="nav_admin"):
            st.session_state.page = "admin"
            st.rerun()

    st.divider()
    if st.button("🚪 Çıkış Yap", use_container_width=True, key="nav_logout"):
        logout()
        st.rerun()

# ─── SAYFA YÖNLENDİRME ───────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app", "pages"))

page = st.session_state.page

if page == "home":
    st.title("🧠 AI Wellness'e Hoş Geldin")
    st.markdown(f"### Merhaba, {current_user['email']} 👋")
    st.markdown("""
    Bu platform sana özel:
    - 🥗 Beslenme planı
    - 🏋️ Antrenman programı
    - 💊 Takviye önerileri
    - 🧠 Psikolojik destek

    üretmek için verilerini analiz eder.

    > ⚠️ Bu platform tıbbi tavsiye niteliği taşımaz. Doktor yerine geçmez.
    """)
    st.info("Başlamak için sol menüden **Değerlendirme**'ye tıkla.")

elif page == "assessment":
    from assessment import show
    show(current_user)

elif page == "analysis":
    from analysis import show
    show(current_user)

elif page == "plan":
    from plan import show
    show(current_user)

elif page == "checkin":
    from checkin_page import show
    show(current_user)

elif page == "coach":
    from coach_page import show
    show(current_user)
    
elif page == "admin_user_detail":
    if current_user["role"] != "admin":
        st.error("Erişim yetkin yok.")
        st.stop()
    from admin_user_detail import show
    selected = st.session_state.get("selected_user")
    if not selected:
        st.session_state.page = "admin"
        st.rerun()
    show(selected)

elif page == "admin":
    if current_user["role"] != "admin":
        st.error("Bu sayfaya erişim yetkin yok.")
        st.stop()
    from admin_page import show
    show(current_user)


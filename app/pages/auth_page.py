import streamlit as st
from config.auth import register_user, login_user

def show_login():
    st.title("🔐 Giriş Yap")

    with st.form("login_form"):
        email    = st.text_input("E-posta", key="login_email")
        password = st.text_input("Şifre", type="password", key="login_password")
        submit   = st.form_submit_button("Giriş Yap", use_container_width=True)

    if submit:
        if not email or not password:
            st.error("E-posta ve şifre gerekli.")
            return
        result = login_user(email, password)
        if result["success"]:
            st.session_state.token = result["token"]
            st.session_state.user  = result["user"]
            st.session_state.page  = "home"
            st.rerun()

        else:
            st.error(result["message"])

    st.divider()
    st.markdown("Hesabın yok mu?")
    if st.button("Kayıt Ol", use_container_width=True, key="goto_register"):
        st.session_state.page = "register"
        st.rerun()


def show_register():
    st.title("📝 Kayıt Ol")
    st.caption("Kaydın admin onayından sonra aktif olacak.")

    with st.form("register_form"):
        name     = st.text_input("Ad Soyad", key="reg_name")
        email    = st.text_input("E-posta", key="reg_email")
        password = st.text_input("Şifre", type="password", key="reg_password")
        password2= st.text_input("Şifre Tekrar", type="password", key="reg_password2")
        submit   = st.form_submit_button("Kayıt Ol", use_container_width=True)

    if submit:
        if not name or not email or not password:
            st.error("Tüm alanları doldur.")
            return
        if password != password2:
            st.error("Şifreler eşleşmiyor.")
            return
        if len(password) < 6:
            st.error("Şifre en az 6 karakter olmalı.")
            return
        result = register_user(name, email, password)
        if result["success"]:
            st.success(result["message"])
            st.info("Giriş sayfasına yönlendiriliyorsun...")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(result["message"])

    st.divider()
    if st.button("← Giriş sayfasına dön", key="goto_login"):
        st.session_state.page = "login"
        st.rerun()
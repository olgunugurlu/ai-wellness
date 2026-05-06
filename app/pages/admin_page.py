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

    tab1, tab2 = st.tabs(["⏳ Onay Bekleyenler", "👥 Tüm Kullanıcılar"])

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
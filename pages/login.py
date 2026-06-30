"""VYANTARA login and registration page."""

import streamlit as st

from components.logo_header import render_brand_title, render_logo
from helpers.auth import login_user, register_user


def render() -> None:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    render_logo(width=100)
    render_brand_title()

    st.markdown(
        '<p class="vy-subtitle" style="font-size:0.95rem;margin-bottom:1.5rem;">'
        "Secure access to the mission dashboard</p>",
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["LOGIN", "REGISTER"])

    with login_tab:
        st.markdown('<p class="vy-section-title">Sign In</p>', unsafe_allow_html=True)
        login_user_input = st.text_input("Username", key="login_username")
        login_pass_input = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn", use_container_width=True):
            success, message = login_user(login_user_input, login_pass_input)
            if success:
                st.success(message)
                st.session_state.logged_in = True
                st.session_state.username = login_user_input.strip()
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error(message)

    with register_tab:
        st.markdown('<p class="vy-section-title">Create Account</p>', unsafe_allow_html=True)
        reg_user_input = st.text_input("Username", key="reg_username")
        reg_pass_input = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_input = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", key="register_btn", use_container_width=True):
            if reg_pass_input != reg_confirm_input:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(reg_user_input, reg_pass_input)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    if st.button("← Back to Home", type="secondary"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

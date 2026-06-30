"""VYANTARA logo and brand header component."""

import streamlit as st

from helpers.paths import LOGO_PATH


def render_logo(width: int = 120, centered: bool = True) -> None:
    """Display the official VYANTARA logo from assets/logo.png."""
    if LOGO_PATH.is_file():
        if centered:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(str(LOGO_PATH), width=width)
        else:
            st.image(str(LOGO_PATH), width=width)
    else:
        st.markdown(
            '<div class="logo-missing">Place official logo at assets/logo.png</div>',
            unsafe_allow_html=True,
        )


def render_brand_title(compact: bool = False, home: bool = False) -> None:
    """Render VYANTARA title text."""
    if compact:
        st.markdown('<p class="vy-sidebar-title">VYANTARA</p>', unsafe_allow_html=True)
    elif home:
        st.markdown('<h1 class="vy-title vy-title-home">VYANTARA</h1>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 class="vy-title">VYANTARA</h1>', unsafe_allow_html=True)

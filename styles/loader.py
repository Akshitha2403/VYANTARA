"""Load VYANTARA theme styles into Streamlit."""

from pathlib import Path

import streamlit as st

_STYLES_DIR = Path(__file__).resolve().parent


def load_css() -> None:
    """Inject custom CSS theme."""
    css_path = _STYLES_DIR / "theme.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

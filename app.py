"""
VYANTARA — Streamlit Application
Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os

os.chdir(ROOT)

from helpers.session import init_session_state
from pages import dashboard, home, login
from styles.loader import load_css


def main() -> None:
    st.set_page_config(
        page_title="VYANTARA",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    load_css()

    if st.session_state.logged_in:
        dashboard.render()
    elif st.session_state.page == "login":
        login.render()
    else:
        home.render()


if __name__ == "__main__":
    main()

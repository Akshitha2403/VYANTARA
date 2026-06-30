"""VYANTARA home page."""

import streamlit as st

from components.logo_header import render_brand_title, render_logo


def render() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 0.2rem !important;
                padding-bottom: 0.4rem !important;
            }
            .home-hero {
                min-height: calc(100dvh - 0.8rem);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                padding: 0.1rem 1rem 0.4rem;
                margin-top: 0;
            }
            .home-hero-inner {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                width: 100%;
                max-width: 920px;
                margin: 0 auto;
                text-align: center;
            }
            .home-hero-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 0.2rem;
                width: 100%;
            }
            .home-hero-text {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: min(680px, 100%);
                margin: 0 auto;
            }
            .home-hero-actions {
                margin-top: 0.3rem;
                width: min(280px, 100%);
            }
            .home-hero-inner [data-testid="stImage"] {
                margin-bottom: 0.08rem;
            }
            .vy-title-home {
                margin: 0.2rem 0 0.25rem !important;
                line-height: 1.05 !important;
            }
            .vy-subtitle {
                margin: 0.16rem auto 0.7rem !important;
                max-width: 640px !important;
                line-height: 1.65 !important;
            }
            .vy-description {
                margin: 0 auto 1rem !important;
                max-width: 640px !important;
                line-height: 1.75 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="home-hero">', unsafe_allow_html=True)
    st.markdown('<div class="home-hero-inner">', unsafe_allow_html=True)
    st.markdown('<div class="home-hero-content">', unsafe_allow_html=True)

    render_logo(width=320)
    render_brand_title(home=True)

    st.markdown('<div class="home-hero-text">', unsafe_allow_html=True)
    st.markdown(
        """
        <p class="vy-subtitle">
            Occlusion-Robust Road Extraction &amp; Graph-Theoretic Criticality Analysis for Urban Mobility
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class="vy-description">
            VYANTARA is an AI-powered geospatial intelligence platform for urban road networks.
            It extracts roads from satellite imagery under occlusion, builds graph-theoretic
            network models, identifies critical infrastructure nodes, simulates disaster impact,
            and quantifies network resilience — delivering mission-control-grade analytics for
            urban mobility planning.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="home-hero-actions">', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        if st.button("Get Started", use_container_width=True, type="primary", key="home_get_started"):
            st.session_state.page = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div></div>', unsafe_allow_html=True)

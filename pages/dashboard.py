"""VYANTARA main dashboard page."""

from pathlib import Path

import streamlit as st

from components.analytics_panel import render_analytics_panel
from components.progress_display import render_progress
from components.results_gallery import render_results_gallery
from components.sidebar import render_sidebar
from helpers.downloads import load_analytics_from_report
from helpers.pipeline import run_complete_pipeline


def render() -> None:
    render_sidebar()

    center_col, right_col = st.columns([0.68, 0.32], gap="medium")

    with center_col:
        st.markdown(
            f'<p class="vy-section-title">Mission Dashboard'
            f' — {st.session_state.get("username", "Operator")}</p>',
            unsafe_allow_html=True,
        )

        preview_path = st.session_state.get("preview_path")
        selection_ready = st.session_state.get("image_selection_applied", False)
        st.markdown('<p class="vy-section-title">Image Preview</p>', unsafe_allow_html=True)

        if preview_path and Path(preview_path).is_file() and selection_ready:
            st.image(str(preview_path), use_container_width=True, caption=Path(preview_path).name)
        else:
            st.markdown(
                """
                <div class="vy-preview-placeholder">
                    <h4>No image selected.</h4>
                    <p>Choose a Sample Image or Upload a Satellite Image to begin.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        pipeline_running = st.session_state.get("pipeline_running", False)
        run_clicked = st.button(
            "Run Complete Pipeline",
            use_container_width=True,
            disabled=pipeline_running or not preview_path or not selection_ready,
            type="primary",
        )

        if run_clicked and not pipeline_running:
            previous_analytics = st.session_state.get("analytics") or {}
            st.session_state.analytics_backup = dict(previous_analytics)
            run_complete_pipeline(preview_path)
            if not st.session_state.get("analytics") and st.session_state.get("analytics_backup"):
                st.session_state.analytics = dict(st.session_state.analytics_backup)
            st.rerun()

        render_progress()

        if st.session_state.get("pipeline_warning"):
            st.warning(st.session_state.pipeline_warning)

        if st.session_state.get("pipeline_error"):
            st.error(st.session_state.pipeline_error)

        if st.session_state.get("report_path"):
            loaded = load_analytics_from_report()
            if loaded:
                st.session_state.analytics = loaded

        render_results_gallery()

    with right_col:
        render_analytics_panel()

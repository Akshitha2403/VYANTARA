"""Pipeline progress bar and stage display."""

import streamlit as st

from helpers.session import PIPELINE_STAGES


def render_progress() -> None:
    """Show pipeline progress bar and current stage name."""
    progress = st.session_state.get("pipeline_progress", 0.0)
    stage = st.session_state.get("pipeline_stage", "")

    st.markdown('<p class="vy-section-title">Pipeline Progress</p>', unsafe_allow_html=True)
    st.progress(min(max(progress, 0.0), 1.0))

    if stage:
        st.markdown(f'<p class="vy-stage-text">{stage}</p>', unsafe_allow_html=True)
    elif st.session_state.get("pipeline_running"):
        st.markdown(
            '<p class="vy-stage-text">Initializing pipeline...</p>',
            unsafe_allow_html=True,
        )


def get_stage_progress_fraction(stage_index: int) -> float:
    """Convert a stage index to a 0–1 progress fraction."""
    total = len(PIPELINE_STAGES)
    if total <= 1:
        return 1.0
    return min(stage_index / (total - 1), 1.0)

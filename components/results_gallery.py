"""Results gallery with enlarge-on-click viewing."""

from pathlib import Path

import streamlit as st

from helpers.paths import OUTPUT_IMAGE_KEYS


@st.dialog(" ", width="large")
def _show_enlarged_image(image_path: str, label: str) -> None:
    st.markdown(
        f'<p class="vy-dialog-title">{label}</p>',
        unsafe_allow_html=True,
    )
    st.image(image_path, use_container_width=True)


def render_results_gallery() -> None:
    """Display pipeline output images in a responsive grid."""
    outputs = st.session_state.get("outputs") or {}

    if not outputs:
        st.info("Pipeline results will appear here after processing completes.")
        return

    st.markdown('<p class="vy-section-title">Pipeline Results</p>', unsafe_allow_html=True)
    st.caption("Click **View Full Size** to enlarge any result.")

    cols_per_row = 4
    items = [(key, label) for key, label in OUTPUT_IMAGE_KEYS if outputs.get(key)]

    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        row_items = items[row_start : row_start + cols_per_row]

        for col, (key, label) in zip(cols, row_items):
            image_path = outputs.get(key)
            if not image_path or not Path(image_path).is_file():
                continue

            with col:
                st.markdown(
                    f'<div class="vy-gallery-label">{label}</div>',
                    unsafe_allow_html=True,
                )
                st.image(str(image_path), use_container_width=True)
                if st.button("View Full Size", key=f"enlarge_{key}", use_container_width=True):
                    _show_enlarged_image(str(image_path), label)

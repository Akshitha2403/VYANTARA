"""Dashboard left sidebar — input selection and logout."""

from pathlib import Path

import streamlit as st

from components.logo_header import render_brand_title, render_logo
from helpers.paths import SUPPORTED_UPLOAD_TYPES
from helpers.sample_images import discover_sample_images, get_sample_image_path


def _update_preview_from_selection() -> None:
    """Set preview_path based on current input source."""
    if st.session_state.input_source == "Sample Images":
        sample = st.session_state.get("selected_sample")
        path = get_sample_image_path(sample) if sample else None
        st.session_state.preview_path = str(path) if path else None
        st.session_state.uploaded_file_name = None
        st.session_state.uploaded_file_bytes = None
        st.session_state.image_selection_applied = bool(path)
    elif st.session_state.uploaded_file_bytes:
        uploads_dir = Path(__file__).resolve().parent.parent / ".ui_cache" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        filename = st.session_state.uploaded_file_name or "upload.png"
        save_path = uploads_dir / filename
        save_path.write_bytes(st.session_state.uploaded_file_bytes)
        st.session_state.preview_path = str(save_path)
        st.session_state.image_selection_applied = True


def render_sidebar() -> None:
    """Render sidebar with logo, input controls, and logout."""
    with st.sidebar:
        st.markdown('<div class="vy-sidebar-brand">', unsafe_allow_html=True)
        render_logo(width=80, centered=False)
        render_brand_title(compact=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<p class="vy-section-title">Input Source</p>', unsafe_allow_html=True)

        st.session_state.input_source = st.radio(
            "Input source",
            options=["Sample Images", "Upload Image"],
            index=0 if st.session_state.input_source == "Sample Images" else 1,
            label_visibility="collapsed",
        )

        if st.session_state.input_source == "Sample Images":
            samples = discover_sample_images()
            if not samples:
                st.error("No sample images found in sample_images/.")
                st.session_state.preview_path = None
                st.session_state.selected_sample = None
                st.session_state.image_selection_applied = False
            else:
                st.session_state.selected_sample = st.selectbox(
                    "Sample image",
                    options=samples,
                    index=None,
                    placeholder="Select a sample image...",
                    label_visibility="collapsed",
                )
                if st.session_state.selected_sample:
                    _update_preview_from_selection()
                else:
                    st.session_state.preview_path = None
                    st.session_state.image_selection_applied = False
        else:
            uploaded = st.file_uploader(
                "Upload image",
                type=list(SUPPORTED_UPLOAD_TYPES),
                label_visibility="collapsed",
            )
            if uploaded is not None:
                st.session_state.uploaded_file_name = uploaded.name
                st.session_state.uploaded_file_bytes = uploaded.getvalue()
                _update_preview_from_selection()
            else:
                st.session_state.uploaded_file_name = None
                st.session_state.uploaded_file_bytes = None
                st.session_state.preview_path = None
                st.session_state.image_selection_applied = False
                st.caption(f"Supported: {', '.join(ext.upper() for ext in SUPPORTED_UPLOAD_TYPES)}")

        st.markdown("---")

        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "home"
            st.rerun()

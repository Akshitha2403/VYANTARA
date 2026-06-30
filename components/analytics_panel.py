"""Analytics metric cards for the right panel."""

import streamlit as st

from helpers.session import ANALYTICS_KEYS


def _format_value(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:.4f}"
    return str(value)


def render_analytics_panel() -> None:
    """Display analytics metric cards from session state (no recomputation)."""
    st.markdown('<p class="vy-section-title">Network Analytics</p>', unsafe_allow_html=True)

    analytics = st.session_state.get("analytics") or {}

    for row_start in range(0, len(ANALYTICS_KEYS), 2):
        cols = st.columns(2)
        row_items = ANALYTICS_KEYS[row_start : row_start + 2]
        for col, (key, label) in zip(cols, row_items):
            raw = analytics.get(key)
            value = _format_value(raw)
            value_class = "vy-metric-value"
            if isinstance(raw, str) and raw.lower() in ("skipped", "not available"):
                value_class = "vy-metric-value skipped"
            col.markdown(
                f"""
                <div class="vy-metric-card">
                    <div class="vy-metric-label">{label}</div>
                    <div class="{value_class}">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown('<p class="vy-section-title">Downloads</p>', unsafe_allow_html=True)

    from helpers.downloads import build_outputs_zip, build_report_download

    report_bytes = build_report_download()
    zip_bytes = build_outputs_zip()

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="Report JSON",
            data=report_bytes if report_bytes else b"",
            file_name="report.json",
            mime="application/json",
            disabled=report_bytes is None,
            use_container_width=True,
        )
    with dl_col2:
        st.download_button(
            label="Output ZIP",
            data=zip_bytes if zip_bytes else b"",
            file_name="vyantara_outputs.zip",
            mime="application/zip",
            disabled=zip_bytes is None,
            use_container_width=True,
        )

    if report_bytes is None and zip_bytes is None:
        st.caption("Run the pipeline to enable downloads.")

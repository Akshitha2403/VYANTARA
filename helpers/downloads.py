"""Download helpers for report and output ZIP."""

import io
import json
import zipfile
from pathlib import Path

import streamlit as st

from helpers.paths import ZIP_FILES


def build_report_download() -> bytes | None:
    """Return report.json bytes if available."""
    report_path = st.session_state.get("report_path")
    if not report_path:
        return None
    path = Path(report_path)
    if not path.is_file():
        return None
    return path.read_bytes()


def build_outputs_zip() -> bytes | None:
    """Bundle output images and report into a ZIP archive."""
    output_folder = st.session_state.get("output_folder")
    if not output_folder:
        return None

    folder = Path(output_folder)
    if not folder.is_dir():
        return None

    buffer = io.BytesIO()
    files_added = 0

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename in ZIP_FILES:
            file_path = folder / filename
            if file_path.is_file():
                archive.write(file_path, arcname=filename)
                files_added += 1

    if files_added == 0:
        return None

    buffer.seek(0)
    return buffer.getvalue()


def load_analytics_from_report() -> dict:
    """Read analytics from report.json without recomputing."""
    report_path = st.session_state.get("report_path")
    if not report_path:
        return {}

    path = Path(report_path)
    if not path.is_file():
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(report, dict):
        return {}

    mapping = {
        "road_pixels": report.get("road_pixels"),
        "road_length": report.get("road_length"),
        "graph_nodes": report.get("graph_nodes"),
        "graph_edges": report.get("graph_edges"),
        "endpoints": report.get("endpoints"),
        "junctions": report.get("junctions"),
        "average_degree": report.get("average_degree"),
        "graph_density": report.get("graph_density"),
        "connectivity_ratio": report.get("connectivity_ratio"),
        "high_critical_nodes": report.get("high_critical_nodes"),
        "connectivity_loss": report.get("connectivity_loss"),
        "resilience_index": report.get("resilience_index"),
    }

    return {k: v for k, v in mapping.items() if v is not None}

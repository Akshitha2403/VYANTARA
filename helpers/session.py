"""Streamlit session state initialization and defaults."""

import streamlit as st

PIPELINE_STAGES = [
    "Loading AI Model",
    "Running Road Segmentation",
    "Generating Skeleton",
    "Building Road Graph",
    "Healing Road Network",
    "Performing Criticality Analysis",
    "Running Disaster Simulation",
    "Computing Resilience Metrics",
    "Generating Report",
    "Pipeline Completed Successfully",
]

ANALYTICS_KEYS = [
    ("road_pixels", "Road Pixels"),
    ("road_length", "Road Length"),
    ("graph_nodes", "Graph Nodes"),
    ("graph_edges", "Graph Edges"),
    ("endpoints", "Endpoints"),
    ("junctions", "Junctions"),
    ("average_degree", "Average Degree"),
    ("graph_density", "Graph Density"),
    ("connectivity_ratio", "Connectivity Ratio"),
    ("high_critical_nodes", "High Critical Nodes"),
    ("connectivity_loss", "Connectivity Loss"),
    ("resilience_index", "Resilience Index"),
]


def init_session_state() -> None:
    """Initialize all session state keys with defaults."""
    defaults = {
        "page": "home",
        "logged_in": False,
        "username": "",
        "input_source": "Sample Images",
        "selected_sample": None,
        "uploaded_file_name": None,
        "uploaded_file_bytes": None,
        "preview_path": None,
        "image_selection_applied": False,
        "pipeline_running": False,
        "pipeline_progress": 0.0,
        "pipeline_stage": "",
        "pipeline_error": None,
        "pipeline_warning": None,
        "outputs": {},
        "analytics": {},
        "analytics_backup": {},
        "report_path": None,
        "output_folder": None,
        "enlarge_image": None,
        "enlarge_label": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_pipeline_state() -> None:
    """Clear pipeline outputs while preserving login and input selection."""
    st.session_state.pipeline_running = False
    st.session_state.pipeline_progress = 0.0
    st.session_state.pipeline_stage = ""
    st.session_state.pipeline_error = None
    st.session_state.pipeline_warning = None
    st.session_state.outputs = {}
    st.session_state.analytics = {}
    st.session_state.analytics_backup = {}
    st.session_state.report_path = None
    st.session_state.output_folder = None

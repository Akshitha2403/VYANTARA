"""Orchestrate the VYANTARA backend pipeline for Streamlit."""

from __future__ import annotations

import os
import traceback
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from helpers.downloads import load_analytics_from_report
from helpers.paths import BASE_DIR
from helpers.session import PIPELINE_STAGES


def _set_progress(stage_index: int, progress_bar, stage_placeholder) -> None:
    """Update session state and on-screen progress widgets."""
    fraction = stage_index / max(len(PIPELINE_STAGES) - 1, 1)
    stage_name = PIPELINE_STAGES[stage_index]

    st.session_state.pipeline_stage = stage_name
    st.session_state.pipeline_progress = fraction
    progress_bar.progress(min(fraction, 1.0))
    stage_placeholder.markdown(
        f'<p class="vy-stage-text">{stage_name}</p>',
        unsafe_allow_html=True,
    )


def _resolve_path(path: str | Path) -> str:
    """Return an absolute path string for display and downloads."""
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = BASE_DIR / resolved
    return str(resolved.resolve())


def _save_original_image(original_rgb: np.ndarray, output_folder: str) -> str:
    """Persist the original RGB image for gallery display (UI-only helper)."""
    original_path = Path(output_folder) / "original.png"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(original_rgb).save(original_path)
    return str(original_path.resolve())


def _fail_stage(stage_label: str, exc: Exception) -> None:
    """Record a stage failure without clearing prior outputs."""
    if isinstance(exc, FileNotFoundError):
        message = str(exc)
        if "Checkpoint" in message or "best_segformer" in message or ".pth" in message:
            st.session_state.pipeline_error = "Model file not found. Check models/best_segformer_tiles_focaldice.pth."
        elif "Mask not found" in message:
            st.session_state.pipeline_error = f"{stage_label} failed: Road mask not found."
        elif "Skeleton" in message:
            st.session_state.pipeline_error = f"{stage_label} failed: Skeleton image missing."
        else:
            st.session_state.pipeline_error = f"{stage_label} failed: {message}"
    else:
        st.session_state.pipeline_error = f"{stage_label} failed: {exc}"


def _is_junction_skip_error(exc: Exception) -> bool:
    """True when disaster simulation cannot run due to missing junctions."""
    message = str(exc).lower()
    return "no junctions" in message or "junctions found" in message


def run_complete_pipeline(image_path: str) -> None:
    """
    Execute the full backend pipeline in order.

    Backend modules are imported and called exactly as implemented.
    Partial results remain visible if a later stage fails.
    """
    st.session_state.pipeline_running = True
    st.session_state.pipeline_error = None
    st.session_state.pipeline_warning = None
    st.session_state.outputs = {}
    st.session_state.analytics = {}
    st.session_state.report_path = None
    st.session_state.output_folder = None

    progress_bar = st.progress(0.0)
    stage_placeholder = st.empty()

    os.chdir(BASE_DIR)

    inference_result = None
    skeleton_result = None
    graph_result = None
    healing_result = None
    criticality_result = None
    disaster_result = None
    output_folder = None
    road_length = 0

    try:
        if not image_path or not Path(image_path).is_file():
            raise FileNotFoundError(f"Sample image missing: {image_path}")

        # STEP 0 — Loading AI Model
        # STEP 0 — Loading AI Model
        _set_progress(0, progress_bar, stage_placeholder)
        try:
            from inference.inference import load_model
            load_model()
        except Exception as exc:
                import traceback
                traceback.print_exc()      # Prints full traceback to Streamlit logs
                st.exception(exc)
                          # Shows the full exception in the UI
                _fail_stage("Loading AI Model", exc)
                return

        # STEP 1 — Inference
        _set_progress(1, progress_bar, stage_placeholder)
        try:
            from inference.inference import run_inference

            inference_result = run_inference(image_path)
            output_folder = _resolve_path(inference_result["output_folder"])
            original_path = _save_original_image(
                inference_result["original_image"],
                output_folder,
            )

            st.session_state.output_folder = output_folder
            st.session_state.outputs = {
                "original": original_path,
                "mask": _resolve_path(inference_result["mask_path"]),
                "overlay": _resolve_path(inference_result["overlay_path"]),
            }
        except Exception as exc:
            _fail_stage("Inference", exc)
            return

        # STEP 2 — Skeletonization
        _set_progress(2, progress_bar, stage_placeholder)
        try:
            from graph.skeleton import run_skeletonization

            skeleton_result = run_skeletonization(output_folder)
            road_length = skeleton_result["skeleton_pixels"]
            st.session_state.outputs["skeleton"] = _resolve_path(skeleton_result["skeleton_path"])
        except Exception as exc:
            _fail_stage("Skeletonization", exc)
            return

        # STEP 3 — Graph Builder
        _set_progress(3, progress_bar, stage_placeholder)
        try:
            from graph.graph_builder import run_graph_builder

            graph_result = run_graph_builder(output_folder)
            st.session_state.outputs["graph"] = _resolve_path(graph_result["graph_path"])
        except Exception as exc:
            _fail_stage("Graph Building", exc)
            return

        # STEP 4 — Graph Healing
        _set_progress(4, progress_bar, stage_placeholder)
        try:
            from graph.graph_healing import run_graph_healing

            healing_result = run_graph_healing(graph_result["graph"], output_folder)
            st.session_state.outputs["healed_graph"] = _resolve_path(
                healing_result["healed_graph_path"]
            )
        except Exception as exc:
            _fail_stage("Graph Healing", exc)
            return

        # STEP 5 — Criticality Analysis
        _set_progress(5, progress_bar, stage_placeholder)
        try:
            from graph.criticality import run_criticality_analysis

            criticality_result = run_criticality_analysis(
                healing_result["healed_graph"],
                output_folder,
            )
            st.session_state.outputs["criticality"] = _resolve_path(
                criticality_result["criticality_path"]
            )
        except Exception as exc:
            _fail_stage("Criticality Analysis", exc)
            return

        # STEP 6 — Disaster Simulation
        _set_progress(6, progress_bar, stage_placeholder)
        disaster_skipped = False
        try:
            from simulation.disaster import run_disaster_simulation

            disaster_result = run_disaster_simulation(
                healing_result["healed_graph"],
                criticality_result["centrality_scores"],
                output_folder,
            )
            st.session_state.outputs["simulation"] = _resolve_path(
                disaster_result["simulation_path"]
            )
        except ValueError as exc:
            if _is_junction_skip_error(exc):
                disaster_skipped = True
                st.session_state.pipeline_warning = (
                    "Disaster Simulation skipped because no valid road junctions "
                    "were detected in this road network."
                )
            else:
                _fail_stage("Disaster Simulation", exc)
                return
        except Exception as exc:
            _fail_stage("Disaster Simulation", exc)
            return

        # STEP 7 — Resilience Analysis & Report (or partial report if disaster skipped)
        _set_progress(7, progress_bar, stage_placeholder)
        try:
            road_pixels = int(np.sum(inference_result["binary_mask"] > 0))

            if disaster_skipped:
                from helpers.partial_report import analytics_from_report, write_partial_report

                report_path = write_partial_report(
                    image_name=inference_result["image_name"],
                    output_folder=output_folder,
                    road_pixels=road_pixels,
                    road_length=road_length,
                    graph_result=graph_result,
                    healing_result=healing_result,
                    criticality_result=criticality_result,
                )
                st.session_state.report_path = _resolve_path(report_path)

                import json

                with open(st.session_state.report_path, encoding="utf-8") as handle:
                    report = json.load(handle)
                st.session_state.analytics = analytics_from_report(report)
            else:
                from simulation.resilience import run_resilience_analysis

                resilience_result = run_resilience_analysis(
                    image_name=inference_result["image_name"],
                    output_folder=output_folder,
                    road_pixels=road_pixels,
                    road_length=road_length,
                    graph_stats=graph_result,
                    healing_result=healing_result,
                    criticality_result=criticality_result,
                    disaster_result=disaster_result,
                )

                st.session_state.report_path = _resolve_path(resilience_result["report_path"])
        except Exception as exc:
            _fail_stage("Resilience Analysis", exc)
            return

        # STEP 8 — Generating Report (complete)
        _set_progress(8, progress_bar, stage_placeholder)

        if not disaster_skipped:
            analytics = load_analytics_from_report()
            if analytics:
                st.session_state.analytics = analytics
            elif st.session_state.report_path:
                import json

                with open(st.session_state.report_path, encoding="utf-8") as handle:
                    report = json.load(handle)
                from helpers.partial_report import analytics_from_report

                st.session_state.analytics = analytics_from_report(report)

        # STEP 9 — Pipeline Completed
        _set_progress(9, progress_bar, stage_placeholder)
        if not disaster_skipped:
            st.session_state.pipeline_error = None

    except Exception as exc:
        st.session_state.pipeline_error = f"Unexpected pipeline error: {exc}\n{traceback.format_exc()}"
    finally:
        st.session_state.pipeline_running = False

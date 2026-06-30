"""Write partial report.json when disaster simulation is skipped (UI-only)."""

from __future__ import annotations

import json
from pathlib import Path

REPORT_FILENAME = "report.json"


def write_partial_report(
    image_name: str,
    output_folder: str,
    road_pixels: int,
    road_length: int,
    graph_result: dict,
    healing_result: dict,
    criticality_result: dict,
) -> str:
    """
    Generate report.json with all metrics available before disaster simulation.

    Disaster-dependent fields are marked as Skipped / Not Available.
    Does not invoke backend resilience or disaster modules.
    """
    report = {
        "image_name": image_name,
        "road_pixels": road_pixels,
        "road_length": road_length,
        "graph_nodes": graph_result["graph_nodes"],
        "graph_edges": graph_result["graph_edges"],
        "junctions": graph_result["junction_count"],
        "endpoints": graph_result["endpoint_count"],
        "normal_nodes": graph_result["normal_nodes"],
        "average_degree": graph_result["average_degree"],
        "graph_density": graph_result["graph_density"],
        "new_connections": healing_result["new_connections"],
        "connectivity_ratio": healing_result["connectivity_ratio"],
        "high_critical_nodes": criticality_result["high_count"],
        "medium_critical_nodes": criticality_result["medium_count"],
        "low_critical_nodes": criticality_result["low_count"],
        "average_centrality": criticality_result["average_centrality"],
        "maximum_centrality": criticality_result["maximum_centrality"],
        "failed_node": "Not Available",
        "connectivity_loss": "Skipped",
        "network_efficiency_before": "Not Available",
        "network_efficiency_after": "Not Available",
        "resilience_index": "Skipped",
        "simulation_status": (
            "Disaster Simulation Skipped — no valid road junctions detected"
        ),
    }

    report_path = Path(output_folder) / REPORT_FILENAME
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=4)

    return str(report_path.resolve())


def analytics_from_report(report: dict) -> dict:
    """Extract dashboard analytics keys from a report dict."""
    keys = (
        "road_pixels",
        "road_length",
        "graph_nodes",
        "graph_edges",
        "endpoints",
        "junctions",
        "average_degree",
        "graph_density",
        "connectivity_ratio",
        "high_critical_nodes",
        "connectivity_loss",
        "resilience_index",
    )
    return {k: report[k] for k in keys if k in report and report[k] is not None}

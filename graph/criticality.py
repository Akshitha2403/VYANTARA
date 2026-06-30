"""
==========================================================
Route Resilience AI
Criticality Analysis Module
==========================================================

Purpose
-------
Analyzes the healed road graph and identifies
critical intersections and road nodes using
graph centrality measures.

Input:
    Healed NetworkX Graph

Output:
    criticality.png

Used By:
    disaster.py

Author:
    Route Resilience AI Team
==========================================================
"""

# ==========================================================
# IMPORTS
# ==========================================================

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os

import networkx as nx
import matplotlib.pyplot as plt

from config import (
    OUTPUTS_DIR,
    CRITICALITY_NAME
)

from graph.graph_builder import classify_nodes


# ==========================================================
# COMPUTE BETWEENNESS CENTRALITY
# ==========================================================

def compute_betweenness_centrality(graph):
    """
    Computes betweenness centrality.

    Parameters
    ----------
    graph : NetworkX Graph

    Returns
    -------
    dict
    """

    centrality = nx.betweenness_centrality(
        graph,
        normalized=True
    )

    return centrality


# ==========================================================
# CLASSIFY CRITICAL NODES
# ==========================================================

def classify_critical_nodes(
    centrality,
    high_threshold=0.05,
    medium_threshold=0.01
):
    """
    Classifies nodes according to
    betweenness centrality.

    High
    Medium
    Low

    Returns
    -------
    high_nodes

    medium_nodes

    low_nodes
    """

    high_nodes = []

    medium_nodes = []

    low_nodes = []

    for node, score in centrality.items():

        if score >= high_threshold:

            high_nodes.append(node)

        elif score >= medium_threshold:

            medium_nodes.append(node)

        else:

            low_nodes.append(node)

    return (

        high_nodes,

        medium_nodes,

        low_nodes

    )


# ==========================================================
# CRITICALITY STATISTICS
# ==========================================================

def criticality_statistics(
    graph,
    centrality
):
    """
    Computes statistics for the graph.

    Returns
    -------
    dict
    """

    high_nodes, medium_nodes, low_nodes = classify_critical_nodes(
        centrality
    )

    average_centrality = sum(
        centrality.values()
    ) / len(centrality) if len(centrality) > 0 else 0

    maximum_centrality = max(
        centrality.values()
    ) if len(centrality) > 0 else 0

    return {

        "high_nodes": len(high_nodes),

        "medium_nodes": len(medium_nodes),

        "low_nodes": len(low_nodes),

        "average_centrality": average_centrality,

        "maximum_centrality": maximum_centrality

    }

# ==========================================================
# SAVE CRITICALITY VISUALIZATION
# ==========================================================

def save_criticality_image(
    graph,
    centrality,
    output_folder
):
    """
    Saves graph visualization with
    critical nodes highlighted.

    Parameters
    ----------
    graph : NetworkX Graph

    centrality : dict

    output_folder : str

    Returns
    -------
    criticality_path
    """

    criticality_path = os.path.join(
        output_folder,
        CRITICALITY_NAME
    )

    positions = {

        node: (node[1], -node[0])

        for node in graph.nodes()

    }

    high_nodes, medium_nodes, low_nodes = classify_critical_nodes(
        centrality
    )

    plt.figure(figsize=(10, 10))

    # --------------------------------------------------
    # Draw Road Edges
    # --------------------------------------------------

    nx.draw_networkx_edges(

        graph,

        pos=positions,

        edge_color="black",

        width=0.4

    )

    # --------------------------------------------------
    # Draw Low Critical Nodes
    # --------------------------------------------------

    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=low_nodes,

        node_color="lime",

        node_size=6

    )

    # --------------------------------------------------
    # Draw Medium Critical Nodes
    # --------------------------------------------------

    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=medium_nodes,

        node_color="yellow",

        node_size=20

    )

    # --------------------------------------------------
    # Draw High Critical Nodes
    # --------------------------------------------------

    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=high_nodes,

        node_color="red",

        node_size=45

    )

    # --------------------------------------------------
    # Highlight Junctions
    # --------------------------------------------------

    _, _, junctions = classify_nodes(graph)

    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=junctions,

        node_color="blue",

        node_size=12,

        alpha=0.6

    )

    # --------------------------------------------------
    # Legend
    # --------------------------------------------------

    plt.scatter([], [], c="red", s=60,
                label="High Critical")

    plt.scatter([], [], c="yellow", s=40,
                label="Medium Critical")

    plt.scatter([], [], c="lime", s=20,
                label="Low Critical")

    plt.scatter([], [], c="blue", s=20,
                label="Junction")

    plt.legend(loc="upper right")

    plt.title(
        "Road Network Criticality Analysis",
        fontsize=14
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(

        criticality_path,

        dpi=300,

        bbox_inches="tight"

    )

    plt.close()

    return criticality_path

# ==========================================================
# COMPLETE CRITICALITY PIPELINE
# ==========================================================

def run_criticality_analysis(
    healed_graph,
    output_folder
):
    """
    Complete criticality analysis pipeline.

    Parameters
    ----------
    healed_graph : NetworkX Graph

    output_folder : str

    Returns
    -------
    dict
    """

    # ---------------------------------------------
    # Compute Betweenness Centrality
    # ---------------------------------------------

    centrality = compute_betweenness_centrality(
        healed_graph
    )

    # ---------------------------------------------
    # Save Visualization
    # ---------------------------------------------

    criticality_path = save_criticality_image(

        healed_graph,

        centrality,

        output_folder

    )

    # ---------------------------------------------
    # Statistics
    # ---------------------------------------------

    stats = criticality_statistics(

        healed_graph,

        centrality

    )

    high_nodes, medium_nodes, low_nodes = classify_critical_nodes(
        centrality
    )

    return {

        "criticality_path": criticality_path,

        "centrality_scores": centrality,

        "high_critical_nodes": high_nodes,

        "medium_critical_nodes": medium_nodes,

        "low_critical_nodes": low_nodes,

        "high_count": stats["high_nodes"],

        "medium_count": stats["medium_nodes"],

        "low_count": stats["low_nodes"],

        "average_centrality":
            stats["average_centrality"],

        "maximum_centrality":
            stats["maximum_centrality"]

    }


# ==========================================================
# TERMINAL TESTING
# ==========================================================

if __name__ == "__main__":

    try:

        from graph.graph_builder import run_graph_builder
        from graph.graph_healing import run_graph_healing

        print("\n" + "=" * 60)
        print("     ROUTE RESILIENCE AI - CRITICALITY ANALYSIS")
        print("=" * 60)

        folder_name = input(
            "\nEnter output folder name (Example: Road or tile_6): "
        ).strip()

        output_folder = os.path.join(
            OUTPUTS_DIR,
            folder_name
        )

        # ---------------------------------------------
        # Build Graph
        # ---------------------------------------------

        graph_result = run_graph_builder(
            output_folder
        )

        # ---------------------------------------------
        # Heal Graph
        # ---------------------------------------------

        healing_result = run_graph_healing(

            graph_result["graph"],

            output_folder

        )

        # ---------------------------------------------
        # Criticality Analysis
        # ---------------------------------------------

        result = run_criticality_analysis(

            healing_result["healed_graph"],

            output_folder

        )

        print("\n" + "=" * 60)
        print("Criticality Analysis Completed")
        print("=" * 60)

        print(f"Criticality Image : {result['criticality_path']}")
        print(f"High Critical     : {result['high_count']}")
        print(f"Medium Critical   : {result['medium_count']}")
        print(f"Low Critical      : {result['low_count']}")
        print(f"Average Centrality: {result['average_centrality']:.6f}")
        print(f"Maximum Centrality: {result['maximum_centrality']:.6f}")

        print("=" * 60)

    except Exception as e:

        print("\nERROR")

        print(type(e).__name__)

        print(e)
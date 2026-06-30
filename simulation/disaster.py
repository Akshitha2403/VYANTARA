"""
==========================================================
Route Resilience AI
Disaster Simulation Module
==========================================================

Purpose
-------
Simulates disasters by removing important
road nodes from the healed graph and
evaluates the impact on network connectivity.

Input:
    Healed NetworkX Graph

Output:
    simulation.png

Used By:
    resilience.py

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
    SIMULATION_NAME
)

from graph.graph_builder import classify_nodes


# ==========================================================
# CONNECTIVITY METRICS
# ==========================================================

def graph_connectivity(graph):
    """
    Computes graph connectivity metrics.

    Returns
    -------
    dict
    """

    if graph.number_of_nodes() == 0:

        return {

            "connected_components": 0,

            "largest_component": 0

        }

    components = list(
        nx.connected_components(graph)
    )

    largest = max(
        components,
        key=len
    )

    return {

        "connected_components": len(components),

        "largest_component": len(largest)

    }


# ==========================================================
# REMOVE NODE (DISASTER)
# ==========================================================

def simulate_node_failure(
    graph,
    node
):
    """
    Simulates failure of a road junction.

    Parameters
    ----------
    graph

    node

    Returns
    -------
    damaged_graph

    before_metrics

    after_metrics
    """

    damaged_graph = graph.copy()

    # Save node positions before removal
    positions_before = {

        node: (node[1], -node[0])

        for node in damaged_graph.nodes()

    }

    before_metrics = graph_connectivity(
        damaged_graph
    )

    if damaged_graph.has_node(node):

        damaged_graph.remove_node(node)

    after_metrics = graph_connectivity(
        damaged_graph
    )

    return (
        
        damaged_graph,
        
        before_metrics,
        
        after_metrics,
        
        positions_before
        
        )


# ==========================================================
# REMOVE EDGE (ROAD BLOCK)
# ==========================================================

def simulate_edge_failure(
    graph,
    edge
):
    """
    Simulates road blockage.

    Parameters
    ----------
    graph

    edge

    Returns
    -------
    damaged_graph

    before_metrics

    after_metrics
    """

    damaged_graph = graph.copy()

    before_metrics = graph_connectivity(
        damaged_graph
    )

    if damaged_graph.has_edge(

        edge[0],

        edge[1]

    ):

        damaged_graph.remove_edge(

            edge[0],

            edge[1]

        )

    after_metrics = graph_connectivity(
        damaged_graph
    )

    return (

        damaged_graph,

        before_metrics,

        after_metrics

    )

# ==========================================================
# SELECT MOST CRITICAL NODE
# ==========================================================

def get_most_critical_node(
    graph,
    centrality_scores
):
    """
    Returns the junction with the
    highest betweenness centrality.
    """

    _, _, junctions = classify_nodes(graph)

    if len(junctions) == 0:
        return None

    junction_scores = {

        node: centrality_scores.get(node, 0)

        for node in junctions

    }

    return max(

        junction_scores,

        key=junction_scores.get

    )


# ==========================================================
# DISASTER IMPACT
# ==========================================================

def disaster_statistics(
    before_metrics,
    after_metrics
):
    """
    Computes disaster impact.

    Returns
    -------
    dict
    """

    before_lcc = before_metrics["largest_component"]

    after_lcc = after_metrics["largest_component"]

    if before_lcc == 0:

        connectivity_loss = 0

    else:

        connectivity_loss = (

            before_lcc - after_lcc

        ) / before_lcc

    return {

        "before_components":
            before_metrics["connected_components"],

        "after_components":
            after_metrics["connected_components"],

        "before_largest_component":
            before_lcc,

        "after_largest_component":
            after_lcc,

        "connectivity_loss":
            connectivity_loss

    }


# ==========================================================
# RUN DISASTER SIMULATION
# ==========================================================

def run_disaster(
    graph,
    centrality_scores,
    selected_node=None
):
    """
    Runs disaster simulation.

    Parameters
    ----------
    graph

    centrality_scores

    selected_node

    Returns
    -------
    dict
    """

    # ---------------------------------------
    # Automatic Node Selection
    # ---------------------------------------

    if selected_node is None:

        selected_node = get_most_critical_node(
            
            graph,
            
            centrality_scores
            
            )

    if selected_node is None:
        raise ValueError(
            "No junctions found for disaster simulation."
        )

    damaged_graph, before_metrics, after_metrics, positions_before = simulate_node_failure(

        graph,

        selected_node

    )

    impact = disaster_statistics(

        before_metrics,

        after_metrics

    )

    return {

        "damaged_graph": damaged_graph,

        "failed_node": selected_node,

        "positions_before": positions_before,

        "before_metrics": before_metrics,

        "after_metrics": after_metrics,

        "impact": impact

    }

# ==========================================================
# SAVE DISASTER VISUALIZATION
# ==========================================================

def save_simulation_image(

    damaged_graph,

    failed_node,

    positions_before,

    output_folder
):
    """
    Saves the disaster simulation graph.

    Parameters
    ----------
    damaged_graph

    failed_node

    output_folder

    Returns
    -------
    simulation_path
    """

    simulation_path = os.path.join(
        output_folder,
        SIMULATION_NAME
    )

    plt.figure(figsize=(10, 10))

    positions = {

        node: (node[1], -node[0])

        for node in damaged_graph.nodes()

    }

    # -----------------------------------------
    # Draw Roads
    # -----------------------------------------

    nx.draw_networkx_edges(

        damaged_graph,

        pos=positions,

        edge_color="black",

        width=0.5

    )

    # -----------------------------------------
    # Draw Remaining Nodes
    # -----------------------------------------

    endpoints, normal_nodes, junctions = classify_nodes(
        damaged_graph
    )

    nx.draw_networkx_nodes(

        damaged_graph,

        pos=positions,

        nodelist=normal_nodes,

        node_color="blue",

        node_size=3

    )

    nx.draw_networkx_nodes(

        damaged_graph,

        pos=positions,

        nodelist=endpoints,

        node_color="lime",

        node_size=35

    )

    nx.draw_networkx_nodes(

        damaged_graph,

        pos=positions,

        nodelist=junctions,

        node_color="red",

        node_size=50

    )

    # -----------------------------------------
    # Show Removed Node
    # -----------------------------------------

    if failed_node is not None:

        x, y = positions_before[failed_node]

        plt.scatter(

            x,

            y,

            s=180,

            marker="X",

            color="black",

            edgecolors="white",

            linewidths=2,

            label="Failed Junction"

        )

    # -----------------------------------------
    # Legend
    # -----------------------------------------

    plt.scatter([], [], c="red", s=60,
                label="Junction")

    plt.scatter([], [], c="lime", s=40,
                label="Endpoint")

    plt.scatter([], [], c="blue", s=20,
                label="Road Node")

    plt.legend(loc="upper right")

    plt.title(
        "Disaster Simulation",
        fontsize=14
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(

        simulation_path,

        dpi=300,

        bbox_inches="tight"

    )

    plt.close()

    return simulation_path


# ==========================================================
# COMPLETE DISASTER PIPELINE
# ==========================================================

def run_disaster_simulation(
    healed_graph,
    centrality_scores,
    output_folder,
    selected_node=None
):
    """
    Complete disaster simulation pipeline.

    Returns
    -------
    dict
    """

    result = run_disaster(

        healed_graph,

        centrality_scores,

        selected_node

    )

    simulation_path = save_simulation_image(

    result["damaged_graph"],

    result["failed_node"],

    result["positions_before"],

    output_folder
    
    )

    return {

        "simulation_path": simulation_path,

        "damaged_graph": result["damaged_graph"],

        "failed_node": result["failed_node"],

        "before_components":
            result["impact"]["before_components"],

        "after_components":
            result["impact"]["after_components"],

        "before_largest_component":
            result["impact"]["before_largest_component"],

        "after_largest_component":
            result["impact"]["after_largest_component"],

        "connectivity_loss":
            result["impact"]["connectivity_loss"]

    }


# ==========================================================
# TERMINAL TESTING
# ==========================================================

if __name__ == "__main__":

    try:

        from graph.graph_builder import run_graph_builder
        from graph.graph_healing import run_graph_healing
        from graph.criticality import run_criticality_analysis

        print("\n" + "=" * 60)
        print("      ROUTE RESILIENCE AI - DISASTER SIMULATION")
        print("=" * 60)

        folder_name = input(
            "\nEnter output folder name (Example: Road or tile_6): "
        ).strip()

        output_folder = os.path.join(
            OUTPUTS_DIR,
            folder_name
        )

        # -----------------------------------------
        # Graph
        # -----------------------------------------

        graph_result = run_graph_builder(
            output_folder
        )

        # -----------------------------------------
        # Healing
        # -----------------------------------------

        healing_result = run_graph_healing(

            graph_result["graph"],

            output_folder

        )

        # -----------------------------------------
        # Criticality
        # -----------------------------------------

        criticality_result = run_criticality_analysis(

            healing_result["healed_graph"],

            output_folder

        )

        # -----------------------------------------
        # Disaster
        # -----------------------------------------

        result = run_disaster_simulation(

            healing_result["healed_graph"],

            criticality_result["centrality_scores"],

            output_folder

        )

        print("\n" + "=" * 60)
        print("Disaster Simulation Completed")
        print("=" * 60)

        print(f"Simulation Image      : {result['simulation_path']}")
        print(f"Failed Node           : {result['failed_node']}")
        print(f"Before Components     : {result['before_components']}")
        print(f"After Components      : {result['after_components']}")
        print(f"Largest Component Before : {result['before_largest_component']}")
        print(f"Largest Component After  : {result['after_largest_component']}")
        print(f"Connectivity Loss     : {result['connectivity_loss']:.3f}")

        print("=" * 60)

    except Exception as e:

        print("\nERROR")
        print(type(e).__name__)
        print(e)
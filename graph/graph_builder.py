"""
==========================================================
Route Resilience AI
Graph Builder Module
==========================================================

Purpose
-------
Converts the skeletonized road network into a
NetworkX graph.

Input:
    skeleton.png

Output:
    graph.png

Used By:
    graph_healing.py

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

import cv2
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from config import (
    OUTPUTS_DIR,
    SKELETON_NAME,
    GRAPH_NAME
)

# ==========================================================
# LOAD SKELETON
# ==========================================================

def load_skeleton(output_folder):
    """
    Loads the skeleton image.

    Parameters
    ----------
    output_folder : str

    Returns
    -------
    skeleton
    """

    skeleton_path = os.path.join(
        output_folder,
        SKELETON_NAME
    )

    if not os.path.exists(skeleton_path):
        raise FileNotFoundError(
            f"Skeleton image not found:\n{skeleton_path}"
        )

    skeleton = cv2.imread(
        skeleton_path,
        cv2.IMREAD_GRAYSCALE
    )

    if skeleton is None:
        raise ValueError(
            "Unable to read skeleton image."
        )

    return skeleton


# ==========================================================
# CREATE EMPTY GRAPH
# ==========================================================

def initialize_graph():
    """
    Creates an empty NetworkX graph.

    Returns
    -------
    NetworkX Graph
    """

    return nx.Graph()


# ==========================================================
# GET ROAD PIXELS
# ==========================================================

def get_road_pixels(skeleton):
    """
    Finds every white pixel in the skeleton.

    Parameters
    ----------
    skeleton

    Returns
    -------
    list of (row, col)
    """

    pixels = np.argwhere(
        skeleton > 0
    )

    return pixels

# ==========================================================
# BUILD GRAPH FROM SKELETON
# ==========================================================

def build_graph(skeleton):
    """
    Converts the skeleton image into
    a NetworkX graph.

    Parameters
    ----------
    skeleton

    Returns
    -------
    graph
    """

    graph = initialize_graph()

    road_pixels = get_road_pixels(
        skeleton
    )

    road_pixel_set = {
        tuple(pixel)
        for pixel in road_pixels
    }

    # 8-connected neighbourhood
    neighbors = [

        (-1, -1),
        (-1, 0),
        (-1, 1),

        (0, -1),
        (0, 1),

        (1, -1),
        (1, 0),
        (1, 1)

    ]

    for row, col in road_pixels:

        graph.add_node(
            (row, col)
        )

        for dr, dc in neighbors:

            nr = row + dr
            nc = col + dc

            if (nr, nc) in road_pixel_set:

                graph.add_edge(
                    (row, col),
                    (nr, nc)
                )

    return graph

def classify_nodes(graph):
    """
    Classifies graph nodes based on degree.

    Returns
    -------
    endpoints
    normal_nodes
    junctions
    """

    endpoints = []
    normal_nodes = []
    junctions = []

    for node in graph.nodes():

        degree = graph.degree(node)

        if degree == 1:
            endpoints.append(node)

        elif degree == 2:
            normal_nodes.append(node)

        elif degree >= 4:
            junctions.append(node)

    return endpoints, normal_nodes, junctions


# ==========================================================
# SAVE GRAPH VISUALIZATION
# ==========================================================

def save_graph_image(
    graph,
    output_folder
):
    """
    Saves the graph visualization with
    endpoints, junctions and normal road nodes.

    Parameters
    ----------
    graph

    output_folder

    Returns
    -------
    graph_path
    """

    graph_path = os.path.join(
        output_folder,
        GRAPH_NAME
    )

    # ----------------------------------------
    # Classify Nodes
    # ----------------------------------------

    endpoints, normal_nodes, junctions = classify_nodes(
        graph
    )

    # ----------------------------------------
    # Node Positions
    # ----------------------------------------

    positions = {

        node: (node[1], -node[0])

        for node in graph.nodes()

    }

    # ----------------------------------------
    # Plot
    # ----------------------------------------

    plt.figure(
        figsize=(10,10)
    )

    # Draw edges
    nx.draw_networkx_edges(

        graph,

        pos=positions,

        edge_color="black",

        width=0.4,

        alpha=0.8

    )

    # Draw normal road nodes
    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=normal_nodes,

        node_color="dodgerblue",

        node_size=2,

        label="Road Node"

    )

    # Draw endpoints
    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=endpoints,

        node_color="lime",

        node_size=25,

        label="Endpoint"

    )

    # Draw junctions
    nx.draw_networkx_nodes(

        graph,

        pos=positions,

        nodelist=junctions,

        node_color="red",

        node_size=45,

        label="Junction"

    )

    

    # Legend
    plt.legend(
        loc="upper right",

        fontsize=8,

        frameon=True
    )

    plt.title(
        "Road Network Graph"
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(

        graph_path,

        dpi=300,

        bbox_inches="tight"

    )

    plt.close()

    return graph_path


# ==========================================================
# GRAPH STATISTICS
# ==========================================================

def calculate_graph_statistics(
    graph
):
    """
    Computes graph statistics.

    Returns
    -------
    dict
    """

    # ----------------------------------------
    # Basic Statistics
    # ----------------------------------------

    nodes = graph.number_of_nodes()

    edges = graph.number_of_edges()

    connected_components = nx.number_connected_components(
        graph
    )

    largest_component = max(

        (
            len(component)
            for component in nx.connected_components(graph)
        ),

        default=0

    )

    # ----------------------------------------
    # Node Classification
    # ----------------------------------------

    endpoints, normal_nodes, junctions = classify_nodes(
        graph
    )

    endpoint_count = len(
        endpoints
    )

    normal_node_count = len(
        normal_nodes
    )

    junction_count = len(
        junctions
    )

    # ----------------------------------------
    # Average Degree
    # ----------------------------------------

    if nodes > 0:

        average_degree = sum(

            dict(
                graph.degree()
            ).values()

        ) / nodes

    else:

        average_degree = 0

    # ----------------------------------------
    # Graph Density
    # ----------------------------------------

    density = nx.density(
        graph
    )

    # ----------------------------------------
    # Return Statistics
    # ----------------------------------------

    return {

        "nodes": nodes,

        "edges": edges,

        "connected_components": connected_components,

        "largest_component": largest_component,

        "endpoint_count": endpoint_count,

        "normal_nodes": normal_node_count,

        "junction_count": junction_count,

        "average_degree": round(
            average_degree,
            2
        ),

        "graph_density": round(
            density,
            6
        )

    }

# ==========================================================
# COMPLETE GRAPH BUILDING PIPELINE
# ==========================================================

def run_graph_builder(output_folder):
    """
    Complete graph construction pipeline.

    Parameters
    ----------
    output_folder : str

    Returns
    -------
    dict
    """

    # -------------------------
    # Load Skeleton
    # -------------------------

    skeleton = load_skeleton(
        output_folder
    )

    # -------------------------
    # Build Graph
    # -------------------------

    graph = build_graph(
        skeleton
    )

    # -------------------------
    # Save Graph Visualization
    # -------------------------

    graph_path = save_graph_image(
        graph,
        output_folder
    )

    # -------------------------
    # Calculate Statistics
    # -------------------------

    stats = calculate_graph_statistics(
        graph
    )

    # -------------------------
    # Return Results
    # -------------------------

    return {

        "graph": graph,

        "graph_path": graph_path,

        "graph_nodes": stats["nodes"],

        "graph_edges": stats["edges"],

        "connected_components": stats["connected_components"],

        "largest_component": stats["largest_component"],

        "endpoint_count": stats["endpoint_count"],
        
        "junction_count": stats["junction_count"],
        
        "normal_nodes": stats["normal_nodes"],
        
        "average_degree": stats["average_degree"],
        
        "graph_density": stats["graph_density"]
        
        }

# ==========================================================
# TERMINAL TESTING
# ==========================================================

if __name__ == "__main__":

    try:

        print("\n" + "=" * 60)
        print("        ROUTE RESILIENCE AI - GRAPH BUILDER")
        print("=" * 60)

        folder_name = input(
            "\nEnter output folder name (Example: tile_6 or Road): "
        ).strip()

        output_folder = os.path.join(
            OUTPUTS_DIR,
            folder_name
        )

        result = run_graph_builder(
            output_folder
        )

        print("\n" + "=" * 60)
        print("      GRAPH CONSTRUCTION COMPLETED")
        print("=" * 60)

        print(f"Output Folder         : {output_folder}")
        print(f"Graph Image           : {result['graph_path']}")

        print("\n---------------- Graph Statistics ----------------")

        print(f"Graph Nodes           : {result['graph_nodes']}")
        print(f"Graph Edges           : {result['graph_edges']}")
        print(f"Connected Components  : {result['connected_components']}")
        print(f"Largest Component     : {result['largest_component']}")

        print(f"Endpoints             : {result['endpoint_count']}")
        print(f"Junctions             : {result['junction_count']}")
        print(f"Normal Road Nodes     : {result['normal_nodes']}")
        print(f"Average Degree        : {result['average_degree']}")
        print(f"Graph Density         : {result['graph_density']}")

        print("=" * 60)

    except Exception as e:

        print("\nERROR")
        print(type(e).__name__)
        print(e)
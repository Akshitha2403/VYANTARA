"""
==========================================================
Route Resilience AI
Graph Healing Module
==========================================================


Purpose
-------
Repairs disconnected road segments by connecting
nearby endpoints.


Input:
    NetworkX Graph


Output:
    healed_graph.png


Used By:
    criticality.py


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
import math


import networkx as nx
import matplotlib.pyplot as plt


from config import (
    OUTPUTS_DIR,
    HEALED_GRAPH_NAME
)


from graph.graph_builder import classify_nodes



# ==========================================================
# EUCLIDEAN DISTANCE
# ==========================================================


def euclidean_distance(node1, node2):
    """
    Computes Euclidean distance between two nodes.


    Parameters
    ----------
    node1 : tuple
    node2 : tuple


    Returns
    -------
    float
    """


    return math.sqrt(
        (node1[0] - node2[0]) ** 2 +
        (node1[1] - node2[1]) ** 2
    )



# ==========================================================
# FIND ENDPOINTS
# ==========================================================


def get_endpoints(graph):
    """
    Returns all endpoint nodes.


    Parameters
    ----------
    graph


    Returns
    -------
    list
    """


    endpoints, _, _ = classify_nodes(graph)


    return endpoints



# ==========================================================
# CONNECTIVITY METRICS
# ==========================================================


def connectivity_metrics(graph):
    """
    Computes connectivity statistics.


    Returns
    -------
    dict
    """


    connected_components = nx.number_connected_components(graph)


    largest_component = max(
        (
            len(component)
            for component in nx.connected_components(graph)
        ),
        default=0
    )


    return {


        "connected_components": connected_components,


        "largest_component": largest_component


    }



# ==========================================================
# GRAPH HEALING
# ==========================================================


def heal_graph(
    graph,
    distance_threshold=50
):
    """
    Repairs disconnected road segments by connecting
    nearby endpoints belonging to different components.


    Parameters
    ----------
    graph : NetworkX Graph


    distance_threshold : int


    Returns
    -------
    healed_graph


    new_connections


    before_metrics


    after_metrics
    """


    # ---------------------------------
    # Copy Graph
    # ---------------------------------


    healed_graph = graph.copy()


    # ---------------------------------
    # Connectivity Before Healing
    # ---------------------------------


    before_metrics = connectivity_metrics(
        healed_graph
    )


    # ---------------------------------
    # Get Endpoints
    # ---------------------------------


    endpoints = get_endpoints(
        healed_graph


    )
    


    new_connections = []


    # ---------------------------------
    # Connected Components
    # ---------------------------------


    components = list(
        nx.connected_components(
            healed_graph
        )
    )


    component_map = {}


    for idx, component in enumerate(components):


        for node in component:


            component_map[node] = idx


    # ---------------------------------
    # Compare Endpoint Pairs
    # ---------------------------------


    used_nodes = set()


    for node1 in endpoints:


        if node1 in used_nodes:
            continue


        best_node = None
        best_distance = float("inf")


        for node2 in endpoints:


            if node1 == node2:
                continue


            if node2 in used_nodes:
                continue


            # Skip endpoints already in the same component
            if component_map[node1] == component_map[node2]:
                continue


            distance = euclidean_distance(
                node1,
                node2
            )


            if distance > distance_threshold:
                continue


            if distance < best_distance:


                best_distance = distance
                best_node = node2


        # ---------------------------------
        # Create Healing Edge
        # ---------------------------------

        if best_node is not None:

            healed_graph.add_edge(
                node1,
                best_node
            )

            new_connections.append(
                (node1, best_node)
            )

            used_nodes.add(node1)
            used_nodes.add(best_node)
    # ---------------------------------
    # SECOND PASS
    # Endpoint -> Road Healing
    # ---------------------------------

    # ---------------------------------
    # Recompute connected components
    # after Pass 1 healing
    # ---------------------------------

    components = list(
        nx.connected_components(
            healed_graph
        )
    )

    component_map = {}

    for idx, component in enumerate(components):

        for node in component:

            component_map[node] = idx

    remaining_endpoints = [

        node

        for node in endpoints

        if node not in used_nodes

    ]

    for endpoint in remaining_endpoints:

        best_node = None
        best_distance = float("inf")

        for road_node in healed_graph.nodes():

            # Skip itself
            if endpoint == road_node:
                continue

            # Skip endpoints (already handled in Pass 1)
            if road_node in endpoints:
                continue

            # Skip existing neighbours
            if healed_graph.has_edge(endpoint, road_node):
                continue

            # Skip nodes already in the same connected component
            if component_map[endpoint] == component_map[road_node]:
                continue

            # Skip very close pixels
            distance = euclidean_distance(
                endpoint,
                road_node
            )

            if distance <= 2:
                continue

            if distance > distance_threshold:
                continue

            # Prefer important road nodes
            degree = healed_graph.degree(road_node)

            if degree < 2:
                continue

            # Keep nearest candidate
            if distance < best_distance:

                best_distance = distance
                best_node = road_node
            

        # Connect endpoint to road
        if best_node is not None:

            healed_graph.add_edge(
                endpoint,
                best_node,
                healed=True
            )

            new_connections.append(
                (endpoint, best_node)
            )

            used_nodes.add(endpoint)

            


    # ---------------------------------
    # Connectivity After Healing
    # ---------------------------------


    after_metrics = connectivity_metrics(
        healed_graph
    )


    return (


        healed_graph,


        new_connections,


        before_metrics,


        after_metrics


    )



# ==========================================================
# CONNECTIVITY IMPROVEMENT
# ==========================================================


def calculate_connectivity_improvement(
    before_metrics,
    after_metrics
):
    """
    Computes connectivity improvement.


    Returns
    -------
    dict
    """


    before = before_metrics["largest_component"]


    after = after_metrics["largest_component"]


    if before == 0:


        ratio = 0


    else:


        ratio = after / before


    return {


        "before_components":
            before_metrics["connected_components"],


        "after_components":
            after_metrics["connected_components"],


        "before_largest_component":
            before,


        "after_largest_component":
            after,


        "connectivity_ratio":
            ratio


    }



# ==========================================================
# SAVE HEALED GRAPH
# ==========================================================


def save_healed_graph(
    healed_graph,
    new_connections,
    output_folder
):
    """
    Saves healed graph visualization.


    Parameters
    ----------
    healed_graph


    new_connections


    output_folder


    Returns
    -------
    graph_path
    """


    graph_path = os.path.join(
        output_folder,
        HEALED_GRAPH_NAME
    )


    plt.figure(figsize=(10, 10))


    positions = {


        node: (node[1], -node[0])


        for node in healed_graph.nodes()


    }


    # --------------------------------------------------
    # Draw Original Graph
    # --------------------------------------------------


    nx.draw_networkx_edges(


        healed_graph,


        pos=positions,


        edge_color="black",


        width=0.4


    )


    # --------------------------------------------------
    # Highlight Newly Added Healing Edges
    # --------------------------------------------------


    if len(new_connections) > 0:


        nx.draw_networkx_edges(


            healed_graph,


            pos=positions,


            edgelist=new_connections,


            edge_color="lime",


            width=2.5


        )


    # --------------------------------------------------
    # Draw Nodes
    # --------------------------------------------------


    endpoints, normal_nodes, junctions = classify_nodes(
        healed_graph
    )


    nx.draw_networkx_nodes(


        healed_graph,


        positions,


        nodelist=normal_nodes,


        node_color="blue",


        node_size=3


    )


    nx.draw_networkx_nodes(


        healed_graph,


        positions,


        nodelist=endpoints,


        node_color="lime",


        node_size=35


    )


    nx.draw_networkx_nodes(


        healed_graph,


        positions,


        nodelist=junctions,


        node_color="red",


        node_size=55


    )


    # --------------------------------------------------
    # Legend
    # --------------------------------------------------


    plt.scatter([], [], c="blue", s=20, label="Road Node")


    plt.scatter([], [], c="lime", s=40, label="Endpoint")


    plt.scatter([], [], c="red", s=60, label="Junction")


    plt.plot([], [], color="lime", linewidth=2,
             label="Healed Connection")


    plt.legend(loc="upper right")


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
# COMPLETE GRAPH HEALING PIPELINE
# ==========================================================


def run_graph_healing(
    graph,
    output_folder
):
    """
    Complete graph healing pipeline.


    Parameters
    ----------
    graph


    output_folder


    Returns
    -------
    dict
    """


    healed_graph, new_connections, before_metrics, after_metrics = heal_graph(
        graph
    )


    graph_path = save_healed_graph(


        healed_graph,


        new_connections,


        output_folder


    )


    connectivity = calculate_connectivity_improvement(


        before_metrics,


        after_metrics


    )


    return {


        "healed_graph": healed_graph,


        "healed_graph_path": graph_path,


        "new_connections": len(new_connections),


        "connectivity_ratio": connectivity["connectivity_ratio"],


        "before_components": connectivity["before_components"],


        "after_components": connectivity["after_components"],


        "before_largest_component":
            connectivity["before_largest_component"],


        "after_largest_component":
            connectivity["after_largest_component"]


    }



# ==========================================================
# TERMINAL TESTING
# ==========================================================


if __name__ == "__main__":


    try:


        from graph.graph_builder import run_graph_builder


        print("\n" + "=" * 60)
        print("     ROUTE RESILIENCE AI - GRAPH HEALING")
        print("=" * 60)


        folder_name = input(
            "\nEnter output folder name (Example: Road or tile_6): "
        ).strip()


        output_folder = os.path.join(
            OUTPUTS_DIR,
            folder_name
        )


        graph_result = run_graph_builder(
            output_folder
        )


        result = run_graph_healing(


            graph_result["graph"],


            output_folder


        )


        print("\n" + "=" * 60)
        print("Graph Healing Completed Successfully")
        print("=" * 60)


        print(f"Healed Graph          : {result['healed_graph_path']}")
        print(f"New Connections       : {result['new_connections']}")
        print(f"Before Components     : {result['before_components']}")
        print(f"After Components      : {result['after_components']}")
        print(f"Connectivity Ratio    : {result['connectivity_ratio']:.3f}")
        print(f"Largest Component Before : {result['before_largest_component']}")
        print(f"Largest Component After  : {result['after_largest_component']}")


        print("=" * 60)


    except Exception as e:


        print("\nERROR")
        print(type(e).__name__)
        print(e)
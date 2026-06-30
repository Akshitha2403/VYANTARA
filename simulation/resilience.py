"""
==========================================================
Route Resilience AI
Resilience Analysis Module
==========================================================


Purpose
-------
Computes road network resilience metrics
after disaster simulation and generates
the analytics report.


Input:
Healed Graph
Disaster Simulation Results


Output:
report.json


Used By:
dashboard/app.py


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
import json
import networkx as nx


from config import (
    REPORT_NAME
)



# ==========================================================
# NETWORK EFFICIENCY
# ==========================================================


def calculate_network_efficiency(graph):
    """
    Computes global network efficiency.


    Parameters
    ----------
    graph : NetworkX Graph


    Returns
    -------
    float
    """


    if graph.number_of_nodes() <= 1:
        return 0.0


    return nx.global_efficiency(graph)



# ==========================================================
# RESILIENCE INDEX
# ==========================================================


def calculate_resilience_index(
    healed_graph,
    damaged_graph
):
    """
    Computes the resilience index.


    Formula
    -------
    RI =
    Efficiency After /
    Efficiency Before


    Returns
    -------
    dict
    """


    efficiency_before = calculate_network_efficiency(
        healed_graph
    )


    efficiency_after = calculate_network_efficiency(
        damaged_graph
    )


    if efficiency_before == 0:


        resilience_index = 0


    else:


        resilience_index = (


            efficiency_after /


            efficiency_before


        )


    return {


        "efficiency_before":
        efficiency_before,


        "efficiency_after":
        efficiency_after,


        "resilience_index":
        resilience_index


    }



# ==========================================================
# CREATE REPORT
# ==========================================================


def create_report(
    image_name,
    output_folder,
    road_pixels,
    road_length,
    graph_stats,
    healing_result,
    criticality_result,
    disaster_result,
    resilience_result
):
    """
    Parameters
----------
image_name : str
    Name of the processed image.


output_folder : str
    Folder where report.json will be saved.


road_pixels : int
    Number of road pixels detected from inference.


road_length : int
    Approximate road length (skeleton pixels).


graph_stats : dict
    Graph statistics from graph_builder.py.


healing_result : dict
    Graph healing results.


criticality_result : dict
    Critical node analysis results.


disaster_result : dict
    Disaster simulation results.


resilience_result : dict
    Resilience metrics.


Returns
-------
report_path : str
    Path to the generated report.json.
    """


    report = {


        # ----------------------------------------
        # Image Information
        # ----------------------------------------


        "image_name":
        image_name,


        # ----------------------------------------
        # Road Statistics
        # ----------------------------------------
        "road_pixels":
        road_pixels,
        "road_length":
        road_length,


        # ----------------------------------------
        # Graph Statistics
        # ----------------------------------------


        "graph_nodes":
        graph_stats["graph_nodes"],


        "graph_edges":
        graph_stats["graph_edges"],


        "junctions":
        graph_stats["junction_count"],


        "endpoints":
        graph_stats["endpoint_count"],


        "normal_nodes":
        graph_stats["normal_nodes"],


        "average_degree":
        graph_stats["average_degree"],


        "graph_density":
        graph_stats["graph_density"],


        # ----------------------------------------
        # Healing Statistics
        # ----------------------------------------


        "new_connections":
        healing_result["new_connections"],


        "connectivity_ratio":
        healing_result["connectivity_ratio"],


        # ----------------------------------------
        # Criticality
        # ----------------------------------------


        "high_critical_nodes":
        criticality_result["high_count"],


        "medium_critical_nodes":
        criticality_result["medium_count"],


        "low_critical_nodes":
        criticality_result["low_count"],


        "average_centrality":
        criticality_result["average_centrality"],


        "maximum_centrality":
        criticality_result["maximum_centrality"],


        # ----------------------------------------
        # Disaster
        # ----------------------------------------


        "failed_node": {
            
            "row": int(disaster_result["failed_node"][0]),
            
            "column": int(disaster_result["failed_node"][1])
            
            },


        "connectivity_loss":
        disaster_result["connectivity_loss"],


        # ----------------------------------------
        # Resilience
        # ----------------------------------------


        "network_efficiency_before":
        resilience_result["efficiency_before"],


        "network_efficiency_after":
        resilience_result["efficiency_after"],


        "resilience_index":
        resilience_result["resilience_index"],


        # ----------------------------------------
        # Status
        # ----------------------------------------


        "simulation_status":
        "Completed Successfully"


    }


    report_path = os.path.join(
        output_folder,
        REPORT_NAME
    )


    with open(


        report_path,


        "w",


        encoding="utf-8"


    ) as file:


        json.dump(


            report,


            file,


            indent=4


        )


    return report_path



# ==========================================================
# DISPLAY REPORT SUMMARY
# ==========================================================


def print_report_summary(report):
    """
    Prints report summary.


    Parameters
    ----------
    report : dict
    """


    print("\n" + "=" * 60)
    print(" ROUTE RESILIENCE REPORT")
    print("=" * 60)


    print(f"Image Name : {report['image_name']}")
    print(f"Road Pixels : {report['road_pixels']}")
    print(f"Road Length : {report['road_length']}")
    print(f"Graph Nodes : {report['graph_nodes']}")
    print(f"Graph Edges : {report['graph_edges']}")
    print(f"Junctions : {report['junctions']}")
    print(f"Endpoints : {report['endpoints']}")
    print(f"New Connections : {report['new_connections']}")
    print(f"Connectivity Ratio : {report['connectivity_ratio']:.3f}")
    print(f"High Critical Nodes : {report['high_critical_nodes']}")
    print(f"Connectivity Loss : {report['connectivity_loss']:.3f}")
    print(f"Resilience Index : {report['resilience_index']:.3f}")


    print("=" * 60)

# ==========================================================
# MAIN RESILIENCE ANALYSIS
# ==========================================================

def run_resilience_analysis(
    image_name,
    output_folder,
    road_pixels,
    road_length,
    graph_stats,
    healing_result,
    criticality_result,
    disaster_result
):
    """
    Executes the complete resilience analysis pipeline.

    Returns
    -------
    dict
    """

    # ----------------------------------------
    # Calculate resilience metrics
    # ----------------------------------------

    resilience_result = calculate_resilience_index(
        healing_result["healed_graph"],
        disaster_result["damaged_graph"]
    )

    # ----------------------------------------
    # Create report.json
    # ----------------------------------------

    report_path = create_report(
        image_name=image_name,
        output_folder=output_folder,
        road_pixels=road_pixels,
        road_length=road_length,
        graph_stats=graph_stats,
        healing_result=healing_result,
        criticality_result=criticality_result,
        disaster_result=disaster_result,
        resilience_result=resilience_result
    )

    # ----------------------------------------
    # Read report for display
    # ----------------------------------------

    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)

    print_report_summary(report)

    # ----------------------------------------
    # Return everything
    # ----------------------------------------

    return {

        "report_path": report_path,

        "report": report,

        "resilience_result": resilience_result
    }


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    print("\nThis module is intended to be called after")

    print("Inference → Skeleton → Graph → Healing")

    print("→ Criticality → Disaster Simulation.\n")

    print("Run the complete pipeline from app.py later.")
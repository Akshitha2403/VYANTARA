import os
import torch

# ==========================================================
# PROJECT ROOT
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================
# FOLDERS
# ==========================================================

MODELS_DIR = os.path.join(BASE_DIR, "models")

SAMPLE_IMAGES_DIR = os.path.join(BASE_DIR, "sample_images")

OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

INFERENCE_DIR = os.path.join(BASE_DIR, "inference")

GRAPH_DIR = os.path.join(BASE_DIR, "graph")

SIMULATION_DIR = os.path.join(BASE_DIR, "simulation")

UTILS_DIR = os.path.join(BASE_DIR, "utils")

DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

# ==========================================================
# MODEL
# ==========================================================

MODEL_PATH = os.path.join(
    MODELS_DIR,
    "best_segformer_tiles_focaldice.pth"
)

MODEL_NAME = "nvidia/segformer-b2-finetuned-ade-512-512"

# ==========================================================
# MODEL SETTINGS
# ==========================================================

NUM_CLASSES = 1

IMAGE_SIZE = 512

THRESHOLD = 0.5

# ==========================================================
# DEVICE
# ==========================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# ==========================================================
# OUTPUT FILE NAMES
# ==========================================================

MASK_NAME = "mask.png"

OVERLAY_NAME = "overlay.png"

SKELETON_NAME = "skeleton.png"

GRAPH_NAME = "graph.png"

HEALED_GRAPH_NAME = "healed_graph.png"

CRITICALITY_NAME = "criticality.png"

SIMULATION_NAME = "simulation.png"

REPORT_NAME = "report.json"

# ==========================================================
# CREATE OUTPUT FOLDER
# ==========================================================

os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ==========================================================
# DISPLAY CONFIGURATION
# ==========================================================

print("=" * 60)
print("       ROUTE RESILIENCE AI CONFIGURATION")
print("=" * 60)

print(f"Project Directory : {BASE_DIR}")
print(f"Model Path        : {MODEL_PATH}")
print(f"Sample Images     : {SAMPLE_IMAGES_DIR}")
print(f"Outputs           : {OUTPUTS_DIR}")
print(f"Device            : {DEVICE}")

print("=" * 60)
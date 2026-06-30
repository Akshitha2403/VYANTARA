"""Project path helpers for the Streamlit UI (no backend imports)."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
SAMPLE_IMAGES_DIR = BASE_DIR / "sample_images"
USERS_FILE = BASE_DIR / "users.json"
OUTPUTS_DIR = BASE_DIR / "outputs"

SUPPORTED_UPLOAD_TYPES = ("png", "jpg", "jpeg", "tiff")

OUTPUT_IMAGE_KEYS = (
    ("original", "Original Image"),
    ("mask", "Road Mask"),
    ("overlay", "Overlay"),
    ("skeleton", "Skeleton"),
    ("graph", "Graph"),
    ("healed_graph", "Healed Graph"),
    ("criticality", "Criticality"),
    ("simulation", "Disaster Simulation"),
)

ZIP_FILES = (
    "mask.png",
    "overlay.png",
    "skeleton.png",
    "graph.png",
    "healed_graph.png",
    "criticality.png",
    "simulation.png",
    "report.json",
)

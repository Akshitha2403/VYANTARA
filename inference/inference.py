"""
=========================================================
Route Resilience AI
Inference Module
---------------------------------------------------------
Loads the trained SegFormer model and performs
road segmentation inference.

Author : Team Route Resilience
=========================================================
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import torch
import torch.nn.functional as F

from transformers import SegformerForSemanticSegmentation

# Optional GeoTIFF support
try:
    import rasterio
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False


# =========================================================
# Configuration
# =========================================================

IMAGE_SIZE = 512

THRESHOLD = 0.5

MODEL_PATH = "models/best_segformer_tiles_focaldice.pth"

OUTPUT_DIR = "outputs"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# ImageNet Normalization (same as training)
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


# =========================================================
# Singleton Model Loader
# =========================================================

_model = None


def load_model():
    """
    Loads the trained SegFormer model only once.

    Returns
    -------
    model : torch.nn.Module
    """

    global _model

    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Checkpoint not found:\n{MODEL_PATH}"
        )

    print("Loading SegFormer B2...")

    model = SegformerForSemanticSegmentation.from_pretrained(
        "nvidia/segformer-b2-finetuned-ade-512-512",
        num_labels=1,
        ignore_mismatched_sizes=True,
    )

    state_dict = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    model.load_state_dict(state_dict)

    model.to(DEVICE)

    model.eval()

    _model = model

    print("Model loaded successfully.")

    return _model


# =========================================================
# Image Loading
# =========================================================

def read_image(image_path):
    """
    Reads an image from disk.

    Supports:
        PNG
        JPG
        JPEG
        TIFF
        GeoTIFF

    Returns
    -------
    image_rgb : numpy.ndarray
    image_name : str
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )

    suffix = image_path.suffix.lower()

    if suffix in [".png", ".jpg", ".jpeg"]:

        image = Image.open(image_path).convert("RGB")

        image = np.array(image)

    elif suffix in [".tif", ".tiff"]:

        if not RASTERIO_AVAILABLE:

            raise ImportError(
                "Rasterio is required for TIFF images."
            )

        with rasterio.open(image_path) as src:

            image = src.read([1, 2, 3])

            image = np.transpose(image, (1, 2, 0))

            image = image.astype(np.uint8)

    else:

        raise ValueError(
            f"Unsupported image format:\n{suffix}"
        )

    image_name = image_path.stem

    return image, image_name


# =========================================================
# Preprocessing
# =========================================================

def preprocess_image(image):
    """
    Prepares image for SegFormer.

    Steps:
        RGB
        Resize
        Normalize
        Tensor
        Batch

    Returns
    -------
    tensor
    original_rgb
    """

    original_rgb = image.copy()

    resized = cv2.resize(
        image,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    resized = resized.astype(np.float32) / 255.0

    resized = (resized - MEAN) / STD

    tensor = torch.from_numpy(resized)

    tensor = tensor.permute(2, 0, 1)

    tensor = tensor.unsqueeze(0)

    tensor = tensor.float()

    tensor = tensor.to(DEVICE)

    return tensor, original_rgb


# =========================================================
# Output Folder
# =========================================================

def create_output_folder(image_name):
    """
    Creates:

    outputs/

        image_name/

    Returns
    -------
    folder path
    """

    output_folder = os.path.join(
        OUTPUT_DIR,
        image_name
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    return output_folder

# =========================================================
# Prediction
# =========================================================

@torch.no_grad()
def predict_mask(image_tensor):
    """
    Runs SegFormer inference.

    Parameters
    ----------
    image_tensor : torch.Tensor
        Shape:
        (1, 3, 512, 512)

    Returns
    -------
    binary_mask : np.ndarray
        Binary mask (0 or 255)

    probability_map : np.ndarray
        Float probability map
    """

    model = load_model()

    outputs = model(pixel_values=image_tensor)

    logits = outputs.logits

    # Upsample logits to original input size
    logits = F.interpolate(
        logits,
        size=(IMAGE_SIZE, IMAGE_SIZE),
        mode="bilinear",
        align_corners=False,
    )

    probabilities = torch.sigmoid(logits)

    probability_map = (
        probabilities
        .squeeze()
        .cpu()
        .numpy()
    )

    binary_mask = (
        probability_map > THRESHOLD
    ).astype(np.uint8)

    binary_mask *= 255

    return binary_mask, probability_map


# =========================================================
# Save Binary Mask
# =========================================================

def save_mask(binary_mask, output_folder):
    """
    Saves mask.png

    Returns
    -------
    mask_path
    """

    mask_path = os.path.join(
        output_folder,
        "mask.png"
    )

    cv2.imwrite(mask_path, binary_mask)

    return mask_path


# =========================================================
# Overlay Generation
# =========================================================

def create_overlay(
    original_rgb,
    binary_mask,
    output_folder
):
    """
    Creates road overlay visualization.

    Roads are highlighted in GREEN.
    """

    overlay = original_rgb.copy()

    road_pixels = binary_mask > 0

    # Green roads
    overlay[road_pixels] = (
        0.4 * overlay[road_pixels]
        + 0.6 * np.array([0, 255, 0])
    ).astype(np.uint8)

    overlay_path = os.path.join(
        output_folder,
        "overlay.png"
    )

    Image.fromarray(overlay).save(overlay_path)

    return overlay_path


# =========================================================
# Main Inference Pipeline
# =========================================================

def run_inference(image_path):
    """
    Complete inference pipeline.

    Parameters
    ----------
    image_path

    Returns
    -------
    dict
    """

    # -------------------------
    # Read Image
    # -------------------------

    image_rgb, image_name = read_image(image_path)

    # -------------------------
    # Output Folder
    # -------------------------

    output_folder = create_output_folder(
        image_name
    )

    # -------------------------
    # Preprocess
    # -------------------------

    image_tensor, original_rgb = preprocess_image(
        image_rgb
    )

    # -------------------------
    # Predict
    # -------------------------

    binary_mask, probability_map = predict_mask(
        image_tensor
    )

    # -------------------------
    # Resize mask back to original image size
    # -------------------------

    original_h, original_w = original_rgb.shape[:2]

    binary_mask = cv2.resize(
        binary_mask,
        (original_w, original_h),
        interpolation=cv2.INTER_NEAREST
    )

    probability_map = cv2.resize(
        probability_map,
        (original_w, original_h),
        interpolation=cv2.INTER_LINEAR
    )

    # -------------------------
    # Save Outputs
    # -------------------------

    mask_path = save_mask(
        binary_mask,
        output_folder
    )

    overlay_path = create_overlay(
        original_rgb,
        binary_mask,
        output_folder
    )

    # -------------------------
    # Return Everything
    # -------------------------

    return {

        "image_name": image_name,

        "output_folder": output_folder,

        "mask_path": mask_path,

        "overlay_path": overlay_path,

        "binary_mask": binary_mask,

        "probability_map": probability_map,

        "original_image": original_rgb,
    }

# =========================================================
# Utility
# =========================================================

def print_summary(result):
    """
    Prints a summary of the inference results.
    """

    print("\n" + "=" * 55)
    print("         Route Resilience AI - Inference Summary")
    print("=" * 55)

    print(f"Image Name      : {result['image_name']}")
    print(f"Output Folder   : {result['output_folder']}")
    print(f"Mask Saved      : {result['mask_path']}")
    print(f"Overlay Saved   : {result['overlay_path']}")

    road_pixels = np.sum(result["binary_mask"] > 0)

    print(f"Road Pixels     : {road_pixels}")

    print("=" * 55)


# =========================================================
# Main
# =========================================================

def main():

    try:

        image_path = select_input_image()

        print(f"\nSelected Image:\n{image_path}")

        result = run_inference(image_path)

        print_summary(result)

        print("\nInference completed successfully.")

    except FileNotFoundError as e:

        print("\nERROR:")

        print(e)

    except ImportError as e:

        print("\nIMPORT ERROR:")

        print(e)

    except RuntimeError as e:

        print("\nMODEL ERROR:")

        print(e)

    except Exception as e:

        print("\nUNEXPECTED ERROR:")

        print(type(e).__name__)

        print(e)

# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":
    main()


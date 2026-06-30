"""
==========================================================
Route Resilience AI
Skeletonization Module
==========================================================

Purpose
-------
Converts the predicted binary road mask into a
1-pixel-wide road centerline using skeletonization.

Input:
    mask.png

Output:
    skeleton.png

Used By:
    graph_builder.py

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

from skimage.morphology import skeletonize

from config import (
    OUTPUTS_DIR,
    MASK_NAME,
    SKELETON_NAME
)

# ==========================================================
# LOAD ROAD MASK
# ==========================================================

def load_mask(output_folder):
    """
    Loads the binary road mask.

    Parameters
    ----------
    output_folder : str

    Returns
    -------
    binary_mask
    """

    mask_path = os.path.join(
        output_folder,
        MASK_NAME
    )

    if not os.path.exists(mask_path):
        raise FileNotFoundError(
            f"Mask not found:\n{mask_path}"
        )

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        raise ValueError(
            "Unable to read mask image."
        )

    return mask

# ==========================================================
# CLEAN MASK
# ==========================================================

def clean_mask(mask):
    """
    Cleans small noisy regions before
    skeletonization.

    Parameters
    ----------
    mask

    Returns
    -------
    cleaned_mask
    """

    kernel = np.ones((3, 3), np.uint8)

    cleaned = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    cleaned = cv2.morphologyEx(
        cleaned,
        cv2.MORPH_CLOSE,
        kernel
    )

    return cleaned

# ==========================================================
# SKELETONIZATION
# ==========================================================

def create_skeleton(mask):
    """
    Converts the road mask into a
    1-pixel-wide skeleton.

    Parameters
    ----------
    mask

    Returns
    -------
    skeleton
    """

    # Convert to binary (0/1)
    binary = mask > 0

    # Skeletonize
    skeleton = skeletonize(binary)

    # Convert back to uint8 image
    skeleton = (skeleton * 255).astype(np.uint8)

    return skeleton


# ==========================================================
# SAVE SKELETON
# ==========================================================

def save_skeleton(
    skeleton,
    output_folder
):
    """
    Saves skeleton image.

    Parameters
    ----------
    skeleton

    output_folder

    Returns
    -------
    skeleton_path
    """

    skeleton_path = os.path.join(
        output_folder,
        SKELETON_NAME
    )

    cv2.imwrite(
        skeleton_path,
        skeleton
    )

    return skeleton_path


# ==========================================================
# SKELETON STATISTICS
# ==========================================================

def calculate_skeleton_statistics(
    skeleton
):
    """
    Computes simple statistics.

    Returns
    -------
    dict
    """

    skeleton_pixels = np.count_nonzero(
        skeleton
    )

    return {

        "skeleton_pixels": int(
            skeleton_pixels
        )

    }

# ==========================================================
# MAIN SKELETONIZATION PIPELINE
# ==========================================================

def run_skeletonization(output_folder):
    """
    Complete skeletonization pipeline.

    Parameters
    ----------
    output_folder : str

    Returns
    -------
    dict
    """

    # -------------------------
    # Load Mask
    # -------------------------

    mask = load_mask(
        output_folder
    )

    # -------------------------
    # Clean Mask
    # -------------------------

    cleaned_mask = clean_mask(
        mask
    )

    # -------------------------
    # Skeletonize
    # -------------------------

    skeleton = create_skeleton(
        cleaned_mask
    )

    # -------------------------
    # Save Skeleton
    # -------------------------

    skeleton_path = save_skeleton(
        skeleton,
        output_folder
    )

    # -------------------------
    # Statistics
    # -------------------------

    stats = calculate_skeleton_statistics(
        skeleton
    )

    return {

        "skeleton_path": skeleton_path,

        "skeleton": skeleton,

        "skeleton_pixels": stats["skeleton_pixels"]

    }


# ==========================================================
# TERMINAL TESTING
# ==========================================================

if __name__ == "__main__":

    try:

        print("\n" + "=" * 55)
        print("      ROUTE RESILIENCE AI - SKELETONIZATION")
        print("=" * 55)

        folder_name = input(
            "\nEnter output folder name (Example: tile_6 or Road): "
        ).strip()

        output_folder = os.path.join(
            OUTPUTS_DIR,
            folder_name
        )

        result = run_skeletonization(
            output_folder
        )

        print("\n" + "=" * 55)
        print("Skeletonization Completed Successfully")
        print("=" * 55)

        print(f"Output Folder     : {output_folder}")
        print(f"Skeleton Saved    : {result['skeleton_path']}")
        print(f"Skeleton Pixels   : {result['skeleton_pixels']}")

        print("=" * 55)

    except Exception as e:

        print("\nERROR")
        print(type(e).__name__)
        print(e)
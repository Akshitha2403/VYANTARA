"""Discover sample images dynamically from sample_images/."""

from pathlib import Path

from helpers.paths import SAMPLE_IMAGES_DIR, SUPPORTED_UPLOAD_TYPES


def discover_sample_images() -> list[str]:
    """
    Return sorted sample image filenames found in sample_images/.

    Supports PNG, JPG, JPEG, and TIFF extensions.
    """
    if not SAMPLE_IMAGES_DIR.is_dir():
        return []

    images: list[str] = []
    for path in SAMPLE_IMAGES_DIR.iterdir():
        if path.is_file() and path.suffix.lower().lstrip(".") in SUPPORTED_UPLOAD_TYPES:
            images.append(path.name)

    return sorted(images, key=str.lower)


def get_sample_image_path(filename: str) -> Path | None:
    """Resolve a sample image filename to its full path."""
    if not filename:
        return None
    path = SAMPLE_IMAGES_DIR / filename
    return path if path.is_file() else None

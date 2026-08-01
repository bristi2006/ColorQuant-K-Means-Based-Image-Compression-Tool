"""Utility helpers for image loading, resizing, encoding, and metrics."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def _normalize_format(image_format: str | None, fallback_name: str | None = None) -> str:
    """Return a Pillow-compatible image format string."""
    if image_format:
        normalized = image_format.upper()
    elif fallback_name:
        normalized = Path(fallback_name).suffix.lstrip(".").upper()
    else:
        normalized = "PNG"

    if normalized == "JPG":
        return "JPEG"

    return normalized or "PNG"


def _ensure_rgb(image: Image.Image) -> Image.Image:
    """Convert an image to RGB while flattening transparency onto white."""
    if image.mode == "RGB":
        return image.copy()

    if "A" in image.getbands():
        rgba_image = image.convert("RGBA")
        background = Image.new("RGBA", rgba_image.size, (255, 255, 255, 255))
        background.alpha_composite(rgba_image)
        return background.convert("RGB")

    return image.convert("RGB")


def load_uploaded_image(uploaded_file):
    """Load an uploaded file into a Pillow image, raw bytes, and source format."""
    image_bytes = uploaded_file.getvalue()

    with Image.open(BytesIO(image_bytes)) as image:
        image.load()
        source_format = _normalize_format(image.format, getattr(uploaded_file, "name", None))
        has_transparency = "A" in image.getbands()
        rgb_image = _ensure_rgb(image)

    return rgb_image, image_bytes, source_format, has_transparency


def resize_image(image: Image.Image, max_dimension: int):
    """Resize an image to fit within max_dimension while preserving aspect ratio."""
    width, height = image.size
    largest_dimension = max(width, height)

    if largest_dimension <= max_dimension:
        return image.copy(), False

    scale = max_dimension / largest_dimension
    new_size = (
        max(1, round(width * scale)),
        max(1, round(height * scale)),
    )

    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    return resized_image, True


def pil_to_array(image: Image.Image) -> np.ndarray:
    """Convert a Pillow RGB image to a float32 NumPy array for K-Means."""
    return np.asarray(image, dtype=np.float32)


def array_to_pil(array: np.ndarray) -> Image.Image:
    """Convert a K-Means output array back to a Pillow RGB image."""
    clipped = np.clip(array, 0, 255).astype(np.uint8)
    return Image.fromarray(clipped, mode="RGB")


def encode_image(
    image: Image.Image,
    output_format: str,
    *,
    quality: int = 85,
    png_compression_level: int = 6,
    optimize: bool = True,
) -> bytes:
    """Encode a Pillow image into bytes using the requested output format."""
    buffer = BytesIO()
    normalized_format = _normalize_format(output_format)

    save_kwargs = {
        "format": normalized_format,
        "optimize": optimize,
    }

    if normalized_format == "JPEG":
        save_kwargs.update(
            {
                "quality": quality,
                "progressive": True,
            }
        )
        image = _ensure_rgb(image)
    elif normalized_format == "PNG":
        save_kwargs.update(
            {
                "compress_level": png_compression_level,
            }
        )

    image.save(buffer, **save_kwargs)
    return buffer.getvalue()


def file_size_to_string(size_bytes: int) -> str:
    """Format a byte size using a human-readable unit."""
    if size_bytes < 1024:
        return f"{size_bytes} B"

    size = float(size_bytes)
    for unit in ["KB", "MB", "GB"]:
        size /= 1024.0
        if size < 1024.0 or unit == "GB":
            return f"{size:.2f} {unit}"

    return f"{size_bytes} B"


def unique_color_count(image_array: np.ndarray) -> int:
    """Count unique RGB colors in a processed image array."""
    pixels = image_array.reshape(-1, image_array.shape[-1])
    return int(np.unique(pixels, axis=0).shape[0])


def load_image(image_path):
    """
    Load an image from disk and convert it to RGB float32 data.
    """
    with Image.open(image_path) as image:
        rgb_image = _ensure_rgb(image)

    return np.asarray(rgb_image, dtype=np.float32)


def display_image(image, title="Image"):
    """
    Display an image.
    """
    plt.figure(figsize=(6, 6))
    plt.imshow(image)
    plt.title(title)
    plt.axis("off")
    plt.show()


def compare_images(original, compressed):
    """
    Display original and compressed images side by side.
    """
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(original)
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(compressed)
    plt.title("Compressed Image")
    plt.axis("off")

    plt.tight_layout()
    plt.show()


def save_image(
    image,
    filename="compressed_image.png",
    *,
    output_format: str | None = None,
    quality: int = 85,
    png_compression_level: int = 6,
    optimize: bool = True,
):
    """
    Save a compressed image inside outputs folder using Pillow encoding.
    """
    import os

    os.makedirs("outputs", exist_ok=True)

    path = os.path.join("outputs", filename)
    pil_image = image if isinstance(image, Image.Image) else array_to_pil(np.asarray(image))
    normalized_format = _normalize_format(output_format, filename)

    encoded_bytes = encode_image(
        pil_image,
        normalized_format,
        quality=quality,
        png_compression_level=png_compression_level,
        optimize=optimize,
    )

    with open(path, "wb") as file_handle:
        file_handle.write(encoded_bytes)

    return path


def calculate_compression(original, compressed):
    """
    Calculate number of unique colors before and after compression.
    """
    original_colors = len(np.unique(original.reshape(-1, 3), axis=0))
    compressed_colors = len(np.unique(compressed.reshape(-1, 3), axis=0))

    return original_colors, compressed_colors


def execution_time(start_time, end_time):
    """
    Returns execution time.
    """
    return round(end_time - start_time, 2)
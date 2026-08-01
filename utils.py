"""Utility helpers for image loading, resizing, encoding, and metrics."""

from __future__ import annotations

import io
import os
import numpy as np
from PIL import Image
from kmeans import init_centroids, assign_clusters, update_centroids


def _normalize_format(output_format: str) -> str:
    """Normalize the image format string for Pillow compatibility."""
    normalized = output_format.strip().upper()
    if normalized in ["JPG", "JPEG"]:
        return "JPEG"
    return normalized


def load_image(source) -> tuple[Image.Image, bytes, str, bool]:
    """
    Loads an image from an uploaded file (file-like object), path, or bytes.
    Validates that the image is not corrupted and converts transparency/grayscale to RGB.
    
    Returns:
        - PIL.Image: Standardized image in RGB mode
        - bytes: The original uncompressed image bytes
        - str: Source format (e.g., 'PNG', 'JPEG', 'WEBP')
        - bool: True if the original image had a transparency layer (alpha)
    """
    if hasattr(source, "getvalue"):
        original_bytes = source.getvalue()
    elif hasattr(source, "read"):
        original_bytes = source.read()
    elif isinstance(source, bytes):
        original_bytes = source
    else:
        # Assume it's a file path
        with open(source, "rb") as f:
            original_bytes = f.read()

    if not original_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        image = Image.open(io.BytesIO(original_bytes))
        image.load()  # Verify we can load the image data to detect corruption
    except Exception as e:
        raise ValueError(f"Failed to load image. The file may be corrupted or is in an unsupported format. Details: {e}")

    source_format = _normalize_format(image.format or "PNG")
    
    # Check for transparency
    has_transparency = "A" in image.getbands() or (image.mode == "P" and "transparency" in image.info)

    # Flatten transparency onto white background or convert grayscale to RGB
    if has_transparency:
        rgba_image = image.convert("RGBA")
        background = Image.new("RGBA", rgba_image.size, (255, 255, 255, 255))
        background.alpha_composite(rgba_image)
        rgb_image = background.convert("RGB")
    else:
        rgb_image = image.convert("RGB")

    return rgb_image, original_bytes, source_format, has_transparency


def resize_image(image: Image.Image, enabled: bool, max_dimension: int) -> tuple[Image.Image, bool]:
    """
    Resizes an image so that its longest dimension fits within max_dimension.
    Preserves aspect ratio.
    
    Returns:
        - PIL.Image: Resized or copied image
        - bool: True if the image was resized, False otherwise
    """
    if not enabled:
        return image.copy(), False

    width, height = image.size
    longest_dimension = max(width, height)

    if longest_dimension <= max_dimension:
        return image.copy(), False

    scale = max_dimension / longest_dimension
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


def compress_storage(
    image: Image.Image,
    original_size_bytes: int,
    output_format: str,
    initial_quality: int = 85,
    optimize: bool = True,
    K: int = 16,
) -> tuple[bytes, int, int, bool]:
    """
    Compress the image using Pillow.
    - PNG: use palette mode (P mode) if K <= 256.
    - JPEG/WEBP: use optimize=True, progressive=True (JPEG only), and adjustable quality.
      Automatically reduce quality down to 50 if needed until compressed size < original size.
    
    Returns:
        - bytes: Compressed image bytes
        - int: Compressed file size in bytes
        - int: Final quality level used
        - bool: True if the compressed file size is smaller than the original file size
    """
    output_format = _normalize_format(output_format)
    
    if output_format == "PNG":
        buffer = io.BytesIO()
        if K <= 256:
            # PNG palette mode
            # Convert to P mode using adaptive palette with K colors
            palette_image = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=max(2, min(256, K)))
            palette_image.save(buffer, format="PNG", optimize=optimize)
        else:
            image.save(buffer, format="PNG", optimize=optimize)
            
        compressed_bytes = buffer.getvalue()
        compressed_size = len(compressed_bytes)
        was_successful = compressed_size < original_size_bytes
        return compressed_bytes, compressed_size, 85, was_successful

    # JPEG or WEBP
    quality = initial_quality
    progressive = (output_format == "JPEG")
    
    compressed_bytes = b""
    compressed_size = 0
    
    while True:
        buffer = io.BytesIO()
        save_kwargs = {
            "format": output_format,
            "quality": quality,
            "optimize": optimize,
        }
        if progressive:
            save_kwargs["progressive"] = True
            
        image.save(buffer, **save_kwargs)
        compressed_bytes = buffer.getvalue()
        compressed_size = len(compressed_bytes)
        
        # Stop loop if size is smaller than original OR we've hit minimum quality limit (50)
        if compressed_size < original_size_bytes or quality <= 50:
            break
            
        quality -= 5
        quality = max(50, quality)
        
    was_successful = compressed_size < original_size_bytes
    return compressed_bytes, compressed_size, quality, was_successful


def save_image(
    image: Image.Image,
    filename: str,
    original_size_bytes: int,
    output_format: str,
    quality: int = 85,
    optimize: bool = True,
    K: int = 16,
) -> tuple[str, bytes, int, int, bool]:
    """
    Save the compressed image to outputs directory.
    
    Returns:
        - str: Absolute path of the saved file
        - bytes: Saved image bytes
        - int: Saved size in bytes
        - int: Final quality used
        - bool: True if file size is smaller than original
    """
    os.makedirs("outputs", exist_ok=True)
    path = os.path.join("outputs", filename)

    compressed_bytes, compressed_size, final_quality, was_successful = compress_storage(
        image=image,
        original_size_bytes=original_size_bytes,
        output_format=output_format,
        initial_quality=quality,
        optimize=optimize,
        K=K,
    )

    with open(path, "wb") as f:
        f.write(compressed_bytes)

    return os.path.abspath(path), compressed_bytes, compressed_size, final_quality, was_successful


def get_unique_colors(image_array: np.ndarray) -> int:
    """Count unique RGB colors in an image array."""
    pixels = image_array.reshape(-1, image_array.shape[-1])
    # Clip and convert to uint8 for reliable color comparison
    pixels_uint8 = np.clip(pixels, 0, 255).astype(np.uint8)
    return int(np.unique(pixels_uint8, axis=0).shape[0])


def format_size(size_bytes: int) -> str:
    """Format a byte size using a human-readable unit."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    size = float(size_bytes)
    for unit in ["KB", "MB", "GB"]:
        size /= 1024.0
        if size < 1024.0 or unit == "GB":
            return f"{size:.2f} {unit}"
    return f"{size_bytes} B"


def calculate_metrics(
    original_array: np.ndarray,
    compressed_array: np.ndarray,
    original_size_bytes: int,
    compressed_size_bytes: int,
    elapsed_seconds: float,
) -> dict:
    """
    Calculate comparative compression metrics.
    """
    original_colors = get_unique_colors(original_array)
    compressed_colors = get_unique_colors(compressed_array)
    
    reduction_pct = 0.0
    if original_size_bytes > 0:
        reduction_pct = ((original_size_bytes - compressed_size_bytes) / original_size_bytes) * 100
        
    storage_saved = max(0, original_size_bytes - compressed_size_bytes)
    
    return {
        "original_size": original_size_bytes,
        "compressed_size": compressed_size_bytes,
        "reduction_pct": reduction_pct,
        "storage_saved": storage_saved,
        "original_colors": original_colors,
        "compressed_colors": compressed_colors,
        "elapsed_seconds": round(elapsed_seconds, 2),
    }


def run_kmeans_with_progress(
    image_array: np.ndarray,
    K: int,
    max_iters: int = 20,
    tolerance: float = 1e-4,
    progress_callback=None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Runs K-Means clustering step-by-step and updates a progress callback.
    Wraps the core functions of kmeans.py exactly without modifying the file.
    
    Returns:
        - np.ndarray: Final centroids
        - np.ndarray: Pixel assignment labels
        - dict: Run statistics
    """
    centroids = init_centroids(K, image_array)
    iterations = 0
    converged = False
    labels = None

    for i in range(max_iters):
        if progress_callback:
            progress_callback(i, max_iters)
            
        labels = assign_clusters(image_array, centroids)
        new_centroids = update_centroids(image_array, labels, K)
        iterations = i + 1

        if np.allclose(centroids, new_centroids, atol=tolerance):
            centroids = new_centroids
            converged = True
            break

        centroids = new_centroids

    if progress_callback:
        progress_callback(max_iters, max_iters)

    return centroids, labels, {
        "iterations": iterations,
        "converged": converged,
        "tolerance": tolerance,
    }
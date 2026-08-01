from __future__ import annotations

import hashlib
import time
from pathlib import Path

import streamlit as st

from kmeans import compress_image, kmeans
from utils import (
    array_to_pil,
    candidate_output_formats,
    encode_image,
    file_size_to_string,
    load_uploaded_image,
    pil_to_array,
    resize_image,
    unique_color_count,
)


def apply_custom_styles() -> None:
    """Apply a compact, deployment-friendly visual system."""
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(14, 165, 233, 0.14), transparent 28%),
                    radial-gradient(circle at top right, rgba(16, 185, 129, 0.12), transparent 24%),
                    linear-gradient(180deg, #f8fafc 0%, #edf2f7 100%);
                color: #0f172a;
            }

            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 2rem;
            }

            .hero {
                border-radius: 24px;
                padding: 1.4rem 1.5rem;
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.88));
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 24px 44px rgba(15, 23, 42, 0.16);
                margin-bottom: 1rem;
            }

            .hero h1 {
                margin: 0;
                font-size: clamp(2rem, 4vw, 3rem);
                line-height: 1.05;
            }

            .hero p {
                margin: 0.55rem 0 0;
                max-width: 64rem;
                color: rgba(255, 255, 255, 0.78);
                font-size: 1rem;
            }

            .eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.28rem 0.7rem;
                border-radius: 999px;
                background: rgba(59, 130, 246, 0.16);
                color: #dbeafe;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.74rem;
                font-weight: 700;
                margin-bottom: 0.65rem;
            }

            .panel {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 20px;
                padding: 1rem 1.1rem;
                box-shadow: 0 16px 32px rgba(15, 23, 42, 0.06);
            }

            .section-title {
                font-size: 1.02rem;
                font-weight: 700;
                margin-bottom: 0.3rem;
            }

            .section-copy {
                color: #64748b;
                font-size: 0.92rem;
                margin-bottom: 0;
            }

            .output-card {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(148, 163, 184, 0.24);
                border-radius: 18px;
                padding: 0.85rem;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
            }

            .stat-label {
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #64748b;
            }

            .stat-value {
                font-size: 1.25rem;
                font-weight: 700;
                color: #0f172a;
                margin-top: 0.18rem;
            }

            .stat-subtext {
                font-size: 0.88rem;
                color: #475569;
                margin-top: 0.15rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"


def format_dimensions(image_size: tuple[int, int]) -> str:
    width, height = image_size
    return f"{width} × {height}"


def build_download_name(uploaded_name: str, output_format: str) -> str:
    stem = Path(uploaded_name).stem or "compressed_image"
    extension = "jpg" if output_format == "JPEG" else output_format.lower()
    return f"{stem}_compressed.{extension}"


def get_settings_signature(upload_bytes: bytes, settings: dict[str, object]) -> str:
    digest = hashlib.sha256(upload_bytes)
    digest.update(repr(sorted(settings.items())).encode("utf-8"))
    return digest.hexdigest()


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Streamlit deployment ready</div>
            <h1>K-Means Image Compression</h1>
            <p>
                Upload a PNG or JPEG, choose an output format, and compress it with the existing K-Means
                algorithm plus a Pillow-based encoder that reports real byte savings, resize behavior, and
                palette reduction.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What this app does</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-copy">Load an image, set the compression budget, and compare the file size before and after Pillow encoding.</p>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Supported inputs", "PNG / JPEG")
    with col2:
        st.metric("Processing", "Auto-resize")
    with col3:
        st.metric("Output", "PNG / JPEG")
    st.markdown('</div>', unsafe_allow_html=True)


def process_image(
    original_image,
    original_bytes: bytes,
    uploaded_name: str,
    *,
    k: int,
    max_iters: int,
    max_dimension: int,
    output_format: str,
    jpeg_quality: int,
    png_compression_level: int,
    optimize_output: bool,
    auto_minimize_size: bool,
    has_transparency: bool,
):
    working_image, was_resized = resize_image(original_image, max_dimension)
    working_array = pil_to_array(working_image)

    pixel_count = working_array.shape[0] * working_array.shape[1]
    effective_k = min(k, pixel_count)

    start_time = time.perf_counter()
    centroids, labels, run_info = kmeans(
        working_array,
        K=effective_k,
        max_iters=max_iters,
        return_info=True,
    )
    compressed_array = compress_image(labels, centroids)
    compressed_image = array_to_pil(compressed_array)
    candidate_formats = candidate_output_formats(output_format, has_transparency)
    if auto_minimize_size:
        candidate_formats = candidate_formats + [fmt for fmt in ["JPEG", "PNG"] if fmt not in candidate_formats]

    encoded_candidates: list[tuple[str, bytes]] = []
    for candidate_format in candidate_formats:
        encoded_candidates.append(
            (
                candidate_format,
                encode_image(
                    compressed_image,
                    candidate_format,
                    quality=jpeg_quality,
                    png_compression_level=png_compression_level,
                    optimize=optimize_output,
                ),
            )
        )

    selected_format, compressed_bytes = min(encoded_candidates, key=lambda item: len(item[1]))
    elapsed_seconds = time.perf_counter() - start_time

    original_size_bytes = len(original_bytes)
    compressed_size_bytes = len(compressed_bytes)
    reduction_pct = ((original_size_bytes - compressed_size_bytes) / original_size_bytes) * 100
    compression_ratio = original_size_bytes / max(1, compressed_size_bytes)

    metrics = {
        "original_size_bytes": original_size_bytes,
        "compressed_size_bytes": compressed_size_bytes,
        "reduction_pct": reduction_pct,
        "compression_ratio": compression_ratio,
        "original_dimensions": original_image.size,
        "working_dimensions": working_image.size,
        "original_colors": unique_color_count(working_array),
        "compressed_colors": unique_color_count(compressed_array),
        "elapsed_seconds": elapsed_seconds,
        "iterations": run_info["iterations"],
        "converged": run_info["converged"],
        "was_resized": was_resized,
        "effective_k": effective_k,
        "selected_format": selected_format,
        "auto_minimize_size": auto_minimize_size,
    }

    return {
        "original_image": original_image,
        "compressed_image": compressed_image,
        "compressed_bytes": compressed_bytes,
        "metrics": metrics,
        "download_name": build_download_name(uploaded_name, selected_format),
    }


def render_results(result, *, output_format: str, optimize_output: bool, has_transparency: bool) -> None:
    metrics = result["metrics"]
    selected_format = metrics["selected_format"]

    if metrics["was_resized"]:
        st.info(
            f"Large upload detected. The image was resized from {format_dimensions(metrics['original_dimensions'])} to {format_dimensions(metrics['working_dimensions'])} before K-Means ran."
        )

    if has_transparency:
        st.info("Transparency was flattened onto a white background before RGB processing.")

    if selected_format != output_format:
        st.success(
            f"The selected {output_format} output would have been larger, so the app automatically used {selected_format} to keep the file smaller."
        )

    original_col, compressed_col = st.columns(2)
    with original_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Original upload</div>', unsafe_allow_html=True)
        st.caption(
            f"{format_dimensions(metrics['original_dimensions'])} · {file_size_to_string(metrics['original_size_bytes'])}"
        )
        st.image(result["original_image"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with compressed_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Compressed output</div>', unsafe_allow_html=True)
        st.caption(
            f"{format_dimensions(metrics['working_dimensions'])} · {selected_format} · {file_size_to_string(metrics['compressed_size_bytes'])}"
        )
        st.image(result["compressed_image"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Compression metrics")
    metric_row_1 = st.columns(4)
    with metric_row_1[0]:
        st.metric("Original size", file_size_to_string(metrics["original_size_bytes"]))
    with metric_row_1[1]:
        st.metric("Compressed size", file_size_to_string(metrics["compressed_size_bytes"]))
    with metric_row_1[2]:
        st.metric("Size reduction", format_percentage(metrics["reduction_pct"]))
    with metric_row_1[3]:
        st.metric("Compression ratio", f"{metrics['compression_ratio']:.2f}x")

    metric_row_2 = st.columns(4)
    with metric_row_2[0]:
        st.metric("Original dimensions", format_dimensions(metrics["original_dimensions"]))
    with metric_row_2[1]:
        st.metric("Working dimensions", format_dimensions(metrics["working_dimensions"]))
    with metric_row_2[2]:
        st.metric("K-Means iterations", str(metrics["iterations"]))
    with metric_row_2[3]:
        st.metric("Execution time", f"{metrics['elapsed_seconds']:.2f} sec")

    metric_row_3 = st.columns(4)
    with metric_row_3[0]:
        st.metric("Unique colors in", f"{metrics['original_colors']:,}")
    with metric_row_3[1]:
        st.metric("Unique colors out", f"{metrics['compressed_colors']:,}")
    with metric_row_3[2]:
        st.metric("Output format", selected_format)
    with metric_row_3[3]:
        st.metric("Effective K", str(metrics["effective_k"]))

    st.download_button(
        "Download compressed image",
        data=result["compressed_bytes"],
        file_name=result["download_name"],
        mime="image/jpeg" if selected_format == "JPEG" else "image/png",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="K-Means Image Compression",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_styles()
    render_hero()

    with st.sidebar:
        st.markdown("### Compression settings")
        uploaded_file = st.file_uploader(
            "Upload PNG or JPEG",
            type=["png", "jpg", "jpeg"],
        )

        k = st.slider("Number of clusters (K)", min_value=2, max_value=64, value=16, step=1)
        max_iters = st.slider("Maximum iterations", min_value=5, max_value=50, value=20, step=1)
        max_dimension = st.slider(
            "Max processing dimension",
            min_value=256,
            max_value=2048,
            value=1024,
            step=64,
            help="Images larger than this limit are resized before running K-Means.",
        )
        output_format = st.selectbox("Output format", options=["PNG", "JPEG"], index=0)
        optimize_output = st.checkbox("Optimize output file", value=True)
        auto_minimize_size = st.checkbox(
            "Automatically choose the smaller valid output",
            value=True,
            help="If your selected format would increase file size, the app will try the other supported format and keep the smaller result.",
        )

        if output_format == "JPEG":
            jpeg_quality = st.slider("JPEG quality", min_value=40, max_value=95, value=85, step=1)
            png_compression_level = 6
        else:
            png_compression_level = st.slider(
                "PNG compression level",
                min_value=0,
                max_value=9,
                value=6,
                step=1,
                help="Higher values reduce file size more slowly but usually produce smaller PNGs.",
            )
            jpeg_quality = 85

        st.caption("The algorithm is unchanged. The final compression step now uses Pillow to produce real output files.")

    if uploaded_file is None:
        render_empty_state()
        return

    original_bytes = uploaded_file.getvalue()
    signature = get_settings_signature(
        original_bytes,
        {
            "k": k,
            "max_iters": max_iters,
            "max_dimension": max_dimension,
            "output_format": output_format,
            "optimize_output": optimize_output,
            "auto_minimize_size": auto_minimize_size,
            "jpeg_quality": jpeg_quality,
            "png_compression_level": png_compression_level,
        },
    )

    original_image, _, _, has_transparency = load_uploaded_image(uploaded_file)

    if st.button("Compress image", type="primary", use_container_width=True):
        with st.spinner("Running K-Means and encoding the compressed image..."):
            processing_image, _ = resize_image(original_image, max_dimension)
            pixel_count = processing_image.size[0] * processing_image.size[1]
            effective_k = min(k, pixel_count)

            if effective_k != k:
                st.warning(
                    f"K was reduced from {k} to {effective_k} because the processed image only has {pixel_count:,} pixels."
                )

            result = process_image(
                original_image,
                original_bytes,
                uploaded_file.name,
                k=effective_k,
                max_iters=max_iters,
                max_dimension=max_dimension,
                output_format=output_format,
                jpeg_quality=jpeg_quality,
                png_compression_level=png_compression_level,
                optimize_output=optimize_output,
                auto_minimize_size=auto_minimize_size,
                has_transparency=has_transparency,
            )
            st.session_state["compression_result"] = result
            st.session_state["compression_signature"] = signature
            st.session_state["compression_transparency"] = has_transparency

    result = st.session_state.get("compression_result")
    stored_signature = st.session_state.get("compression_signature")
    stored_transparency = st.session_state.get("compression_transparency", False)

    if result is None:
        st.markdown(
            "<div class='panel'><strong>Ready when you are.</strong> Upload an image, adjust the settings, and click Compress image.</div>",
            unsafe_allow_html=True,
        )
        return

    if stored_signature != signature:
        st.info("Settings changed after the last run. Click Compress image again to refresh the output.")
        return

    render_results(
        result,
        output_format=output_format,
        optimize_output=optimize_output,
        has_transparency=stored_transparency,
    )


if __name__ == "__main__":
    main()
from __future__ import annotations

import streamlit as st
import time
from pathlib import Path
from kmeans import compress_image
from utils import (
    load_image,
    resize_image,
    pil_to_array,
    array_to_pil,
    save_image,
    calculate_metrics,
    format_size,
    run_kmeans_with_progress,
)


def apply_custom_theme() -> None:
    """Inject modern dark SaaS dashboard styles."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

            /* Global App Container Override */
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #080a10;
                color: #e2e8f0;
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background-color: #0d111c;
                border-right: 1px solid rgba(255, 255, 255, 0.06);
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
                color: #f8fafc;
                font-size: 1.1rem;
                font-weight: 600;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                margin-top: 1.5rem;
                margin-bottom: 1rem;
            }

            /* Header Section Styling */
            .header-container {
                background: linear-gradient(135deg, #1e1b4b 0%, #0d111c 100%);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 16px;
                padding: 2rem 2.5rem;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            }

            .header-title {
                font-size: 2.6rem;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(90deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.03em;
            }

            .header-subtitle {
                font-size: 1rem;
                color: #94a3b8;
                margin-top: 0.5rem;
                margin-bottom: 0;
                font-weight: 400;
            }

            /* Dashboard Cards styling */
            .dashboard-card {
                background-color: #0f1422;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 14px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            }

            .dashboard-card h3 {
                margin-top: 0;
                margin-bottom: 0.75rem;
                font-size: 1.2rem;
                font-weight: 600;
                color: #ffffff;
            }

            /* Metrics Grid Layout */
            .metrics-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 1.25rem;
                margin-top: 1rem;
                margin-bottom: 2rem;
            }

            .metric-card {
                background-color: #121829;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1.25rem 1rem;
                text-align: center;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
                transition: transform 0.2s ease, border-color 0.2s ease;
            }

            .metric-card:hover {
                transform: translateY(-2px);
                border-color: rgba(99, 102, 241, 0.4);
            }

            .metric-card-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #94a3b8;
                margin-bottom: 0.5rem;
                font-weight: 600;
            }

            .metric-card-value {
                font-size: 1.6rem;
                font-weight: 700;
                color: #ffffff;
            }

            .metric-card-sub {
                font-size: 0.85rem;
                color: #34d399;
                margin-top: 0.35rem;
                font-weight: 500;
            }

            .metric-card-sub.negative {
                color: #f87171;
            }

            /* Status Update Message Styling */
            .status-msg {
                font-size: 0.95rem;
                font-weight: 500;
                color: #818cf8;
                margin-bottom: 0.5rem;
            }

            /* Compress Trigger Button Styling */
            div.stButton > button:first-child {
                background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.75rem 2rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
                width: 100%;
            }

            div.stButton > button:first-child:hover {
                background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
            }

            /* Download Button Styling */
            div.stDownloadButton > button:first-child {
                background: linear-gradient(90deg, #10b981 0%, #059669 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.85rem 2rem;
                font-weight: 700;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
                width: 100%;
            }

            div.stDownloadButton > button:first-child:hover {
                background: linear-gradient(90deg, #059669 0%, #047857 100%);
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
            }

            /* Drag & Drop File Uploader Override */
            [data-testid="stFileUploader"] {
                background-color: #0f1422;
                border: 2px dashed rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 2rem;
                transition: border-color 0.3s ease;
            }
            [data-testid="stFileUploader"]:hover {
                border-color: #6366f1;
            }
            [data-testid="stFileUploaderDropzone"] {
                background-color: transparent !important;
            }

            /* Hide Default Streamlit Overhead Elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {background-color: transparent !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # 1. Page Configuration
    st.set_page_config(
        page_title="K-Compress - SaaS Image Optimizer",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_theme()

    # 2. Page Header
    st.markdown(
        """
        <div class="header-container">
            <h1 class="header-title">K-Compress</h1>
            <p class="header-subtitle">Production-ready vector quantization engine with advanced storage optimization</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Sidebar Configuration Layout
    with st.sidebar:
        st.markdown("### Model Configuration")
        k = st.slider(
            "Number of clusters (K)",
            min_value=2,
            max_value=256,
            value=16,
            step=1,
            help="Defines the max number of unique colors in the output image.",
        )
        max_iters = st.slider(
            "Max iterations",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            help="Maximum clustering iterations before stopping algorithm.",
        )

        st.markdown("### Image Processing")
        resize_enabled = st.checkbox(
            "Resize image",
            value=True,
            help="Auto-resize images exceeding the maximum processing dimension.",
        )
        if resize_enabled:
            max_dimension = st.slider(
                "Max dimension",
                min_value=256,
                max_value=2048,
                value=1500,
                step=64,
                help="Longest edge of the image will fit within this value.",
            )
        else:
            max_dimension = 1500

        st.markdown("### Output Storage Settings")
        output_format = st.selectbox(
            "Output format",
            options=["PNG", "JPEG", "WEBP"],
            index=1,
            help="Select the final target file format.",
        )

        if output_format in ["JPEG", "WEBP"]:
            quality_val = st.slider(
                "Quality",
                min_value=10,
                max_value=100,
                value=85,
                step=5,
                help="Starting compression quality level.",
            )
        else:
            quality_val = 85

        optimize_output = st.checkbox(
            "Optimize output",
            value=True,
            help="Applies encoder-level optimizations and progressive layouts.",
        )

    # 4. Main Panel Layout
    st.markdown("### Source File Upload")
    uploaded_file = st.file_uploader(
        "Upload image (PNG, JPEG, WEBP)",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
    )

    # State Management initialization
    if "uploaded_file_name" not in st.session_state:
        st.session_state["uploaded_file_name"] = None
        st.session_state["results"] = None
        st.session_state["last_run_params"] = None

    # Reset results if a different file is uploaded
    if uploaded_file:
        if st.session_state["uploaded_file_name"] != uploaded_file.name:
            st.session_state["uploaded_file_name"] = uploaded_file.name
            st.session_state["results"] = None
            st.session_state["last_run_params"] = None

    if not uploaded_file:
        st.markdown(
            """
            <div class="dashboard-card" style="text-align: center; padding: 3rem 2rem;">
                <h3 style="color: #818cf8; margin-bottom: 0.5rem;">Awaiting Document Upload</h3>
                <p style="color: #94a3b8; max-width: 500px; margin: 0 auto;">
                    Select an image above and configure parameter specifications in the sidebar panel to analyze the quantization system.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # User loaded an image, parse and validate it immediately
    try:
        original_image, original_bytes, source_format, has_transparency = load_image(uploaded_file)
    except Exception as e:
        st.error(f"Failed to process uploaded file: {str(e)}")
        return

    # Render manual execution button
    col_btn_l, col_btn_m, col_btn_r = st.columns([1, 2, 1])
    with col_btn_m:
        compress_clicked = st.button("Run Quantization & Compression", use_container_width=True)

    # Trigger processing sequence
    if compress_clicked:
        start_time = time.perf_counter()

        # Create status messaging placeholders
        status_placeholder = st.empty()
        progress_bar = st.progress(0.0)

        try:
            # Step 1: Loading image
            status_placeholder.markdown("<div class='status-msg'>Loading image...</div>", unsafe_allow_html=True)
            time.sleep(0.1)  # small visual delay
            progress_bar.progress(0.1)

            # Resize if toggle checked
            resized_image, was_resized = resize_image(
                original_image,
                enabled=resize_enabled,
                max_dimension=max_dimension,
            )
            image_array = pil_to_array(resized_image)

            # Cap K value to pixel counts to prevent crash
            pixel_count = image_array.shape[0] * image_array.shape[1]
            effective_k = min(k, pixel_count)

            # Step 2: Running K-Means
            status_placeholder.markdown("<div class='status-msg'>Running K-Means algorithm...</div>", unsafe_allow_html=True)

            def progress_callback(curr_iter, total_iters):
                fraction = 0.1 + (curr_iter / total_iters) * 0.7
                progress_bar.progress(fraction)
                status_placeholder.markdown(
                    f"<div class='status-msg'>Running K-Means (Iteration {curr_iter}/{total_iters})...</div>",
                    unsafe_allow_html=True,
                )

            centroids, labels, run_info = run_kmeans_with_progress(
                image_array=image_array,
                K=effective_k,
                max_iters=max_iters,
                progress_callback=progress_callback,
            )

            # Step 3: Optimizing output
            status_placeholder.markdown("<div class='status-msg'>Optimizing output and testing compression thresholds...</div>", unsafe_allow_html=True)
            compressed_array = compress_image(labels, centroids)
            compressed_image = array_to_pil(compressed_array)
            progress_bar.progress(0.9)

            # Prepare output details
            stem = Path(uploaded_file.name).stem
            ext_map = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}
            out_filename = f"{stem}_quantized.{ext_map[output_format]}"

            # Save and compress using the helper
            saved_path, compressed_bytes, compressed_size, final_quality, was_successful = save_image(
                image=compressed_image,
                filename=out_filename,
                original_size_bytes=len(original_bytes),
                output_format=output_format,
                quality=quality_val if output_format in ["JPEG", "WEBP"] else 85,
                optimize=optimize_output,
                K=effective_k,
            )
            progress_bar.progress(0.95)

            # Step 4: Preparing download
            status_placeholder.markdown("<div class='status-msg'>Preparing download packages...</div>", unsafe_allow_html=True)
            elapsed_seconds = time.perf_counter() - start_time

            metrics = calculate_metrics(
                original_array=pil_to_array(original_image),
                compressed_array=compressed_array,
                original_size_bytes=len(original_bytes),
                compressed_size_bytes=compressed_size,
                elapsed_seconds=elapsed_seconds,
            )
            progress_bar.progress(1.0)

            # Save in Streamlit Session State
            st.session_state["results"] = {
                "original_image": original_image,
                "compressed_image": compressed_image,
                "compressed_bytes": compressed_bytes,
                "metrics": metrics,
                "download_filename": out_filename,
                "was_successful": was_successful,
                "final_quality": final_quality,
                "was_resized": was_resized,
                "effective_k": effective_k,
                "original_dimensions": original_image.size,
                "compressed_dimensions": compressed_image.size,
            }
            st.session_state["last_run_params"] = {
                "k": k,
                "max_iters": max_iters,
                "resize_enabled": resize_enabled,
                "max_dimension": max_dimension,
                "output_format": output_format,
                "quality_val": quality_val,
                "optimize_output": optimize_output,
            }

            # Briefly display success status before wiping trackers
            time.sleep(0.4)
            status_placeholder.empty()
            progress_bar.empty()

        except Exception as err:
            st.error(f"Operational error occurred: {str(err)}")
            if "status_placeholder" in locals():
                status_placeholder.empty()
            if "progress_bar" in locals():
                progress_bar.empty()

    # 5. Render Results Section (if data present in state)
    results = st.session_state.get("results")
    last_params = st.session_state.get("last_run_params")

    if results:
        # Check if settings changed after run
        params_changed = False
        if last_params:
            if (
                last_params["k"] != k
                or last_params["max_iters"] != max_iters
                or last_params["resize_enabled"] != resize_enabled
                or (resize_enabled and last_params["max_dimension"] != max_dimension)
                or last_params["output_format"] != output_format
                or (output_format in ["JPEG", "WEBP"] and last_params["quality_val"] != quality_val)
                or last_params["optimize_output"] != optimize_output
            ):
                params_changed = True

        if params_changed:
            st.info("Configuration altered since last execution. Click 'Run Quantization & Compression' to synchronize.")

        # Warning/Success states
        metrics = results["metrics"]
        reduction_pct = metrics["reduction_pct"]
        saved_bytes = metrics["storage_saved"]

        if results["was_successful"]:
            st.success(
                f"Image compressed successfully. Size reduced by {format_size(saved_bytes)} ({reduction_pct:.1f}% savings)."
            )
        else:
            st.warning(
                "Compression warning: Unable to reduce file size below original without significant quality loss. "
                "Try lowering the quality slider, reducing K, or turning on resizing."
            )

        # Inform of resize behavior or transparency adjustments
        if results["was_resized"]:
            st.info(
                f"Source image dimensions exceeded the sizing threshold. "
                f"Resized from {results['original_dimensions'][0]}x{results['original_dimensions'][1]} "
                f"to {results['compressed_dimensions'][0]}x{results['compressed_dimensions'][1]} "
                f"preserving aspect ratio before quantization."
            )

        if has_transparency:
            st.info("Input transparency layers detected. Background was flattened onto white for cluster compatibility.")

        if results["effective_k"] < k:
            st.warning(
                f"Cluster count K auto-reduced to {results['effective_k']} "
                f"matching total pixel capacity."
            )

        # Image view cards side by side
        col_view_l, col_view_r = st.columns(2)

        with col_view_l:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <h3>Original</h3>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.75rem;">
                        Dimensions: {results["original_dimensions"][0]}x{results["original_dimensions"][1]} &middot; 
                        Size: {format_size(metrics["original_size"])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(results["original_image"], use_container_width=True)

        with col_view_r:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <h3>Quantized</h3>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.75rem;">
                        Dimensions: {results["compressed_dimensions"][0]}x{results["compressed_dimensions"][1]} &middot; 
                        Size: {format_size(metrics["compressed_size"])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(results["compressed_image"], use_container_width=True)

        # Comparative metric cards grid
        st.markdown("### Performance & Compression Metrics")
        
        orig_size_str = format_size(metrics["original_size"])
        comp_size_str = format_size(metrics["compressed_size"])
        reduction_str = f"{reduction_pct:.1f}%"
        saved_str = format_size(saved_bytes)
        orig_colors_str = f'{metrics["original_colors"]:,}'
        comp_colors_str = f'{metrics["compressed_colors"]:,}'
        time_str = f'{metrics["elapsed_seconds"]:.2f}s'
        
        savings_class = "metric-card-sub" if results["was_successful"] else "metric-card-sub negative"
        savings_label = "Saved" if results["was_successful"] else "Increase"
        
        # Build cards html
        metrics_html = f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-card-label">Original File Size</div>
                <div class="metric-card-value">{orig_size_str}</div>
                <div class="metric-card-sub" style="color: #94a3b8;">{orig_colors_str} colors</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Compressed File Size</div>
                <div class="metric-card-value">{comp_size_str}</div>
                <div class="metric-card-sub" style="color: #94a3b8;">{comp_colors_str} colors</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Size Savings</div>
                <div class="metric-card-value">{reduction_str}</div>
                <div class="{savings_class}">{saved_str} {savings_label}</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Engine Time</div>
                <div class="metric-card-value">{time_str}</div>
                <div class="metric-card-sub" style="color: #38bdf8;">K = {results["effective_k"]}</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # Render prominent download button
        st.download_button(
            label="Download Compressed Image",
            data=results["compressed_bytes"],
            file_name=results["download_filename"],
            mime=f"image/{output_format.lower()}",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
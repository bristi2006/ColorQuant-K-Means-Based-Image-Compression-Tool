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
    """Inject premium dark SaaS dashboard styling and layout overrides."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

            /* Global styles */
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #080a11;
                color: #e2e8f0;
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background-color: #0e1220;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
                color: #f8fafc;
                font-size: 1.15rem;
                font-weight: 700;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                margin-top: 1rem;
                margin-bottom: 1.25rem;
                letter-spacing: -0.01em;
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
                color: #f1f5f9;
                font-size: 0.95rem;
                font-weight: 600;
                margin-top: 1rem;
                margin-bottom: 0.75rem;
            }

            /* Sidebar Expander Customization */
            div[data-testid="stExpander"] {
                background-color: #12182c !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-radius: 8px !important;
                margin-top: 1rem;
            }

            /* Header Section Styling */
            .header-container {
                background: linear-gradient(135deg, #13142e 0%, #080a11 100%);
                border: 1px solid rgba(99, 102, 241, 0.12);
                border-radius: 12px;
                padding: 1.5rem 2rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 25px rgba(0, 0, 0, 0.2);
                text-align: center;
            }

            .header-title {
                font-size: 2.3rem;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(90deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.02em;
            }

            .header-subtitle {
                font-size: 0.95rem;
                color: #94a3b8;
                margin-top: 0.4rem;
                margin-bottom: 0;
                font-weight: 400;
            }

            /* Image View Cards container styling */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #0f1425 !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                border-radius: 12px !important;
                padding: 1.25rem !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
                transition: transform 0.2s ease, border-color 0.2s ease;
                min-height: 480px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                border-color: rgba(99, 102, 241, 0.3) !important;
            }

            /* Enforce maximum sizing for internal preview images */
            div[data-testid="stImage"] img {
                max-height: 320px !important;
                object-fit: contain !important;
                border-radius: 6px !important;
                border: 1px solid rgba(255, 255, 255, 0.04) !important;
                margin: 0 auto !important;
                display: block !important;
            }

            /* Metrics Grid Layout */
            .metrics-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
                margin-bottom: 1.5rem;
            }

            .metric-card {
                background-color: #12182d;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25);
                transition: transform 0.2s ease, border-color 0.2s ease;
            }

            .metric-card:hover {
                transform: translateY(-2px);
                border-color: rgba(99, 102, 241, 0.3);
            }

            .metric-card-label {
                font-size: 0.68rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #94a3b8;
                margin-bottom: 0.4rem;
                font-weight: 600;
            }

            .metric-card-value {
                font-size: 1.3rem;
                font-weight: 700;
                color: #ffffff;
            }

            .metric-card-sub {
                font-size: 0.78rem;
                color: #34d399;
                margin-top: 0.3rem;
                font-weight: 500;
            }

            .metric-card-sub.negative {
                color: #f87171;
            }

            .metric-card-sub.neutral {
                color: #64748b;
            }

            /* Status Update Message Styling */
            .status-msg {
                font-size: 0.95rem;
                font-weight: 500;
                color: #818cf8;
                margin-bottom: 0.5rem;
                text-align: center;
            }

            /* Primary Button Styling */
            div.stButton > button:first-child {
                background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.7rem 1.5rem;
                font-weight: 600;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
                width: 100%;
            }

            div.stButton > button:first-child:hover {
                background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
            }

            /* Download Button Styling */
            div.stDownloadButton > button:first-child {
                background: linear-gradient(90deg, #10b981 0%, #059669 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.8rem 2rem;
                font-weight: 700;
                font-size: 1.05rem;
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
                background-color: #0f1425;
                border: 2px dashed rgba(99, 102, 241, 0.25);
                border-radius: 12px;
                padding: 1.25rem;
                margin-bottom: 1.5rem;
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
    # 1. Page Config Setup
    st.set_page_config(
        page_title="K-Compress - Image Compression Tool",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_theme()

    # 2. Main Header
    st.markdown(
        """
        <div class="header-container">
            <h1 class="header-title">K-Compress</h1>
            <p class="header-subtitle">Optimized K-Means color quantization engine and high-efficiency image compression</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Handle File Upload immediately (Hierarchy step 3)
    uploaded_file = st.file_uploader(
        "Upload image (PNG, JPEG, WEBP)",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
    )

    # State initialization
    if "uploaded_file_name" not in st.session_state:
        st.session_state["uploaded_file_name"] = None
        st.session_state["output_format_sel"] = "JPEG"
        st.session_state["results"] = None
        st.session_state["last_run_params"] = None

    # Track upload updates to swap selected format defaults dynamically
    if uploaded_file:
        file_id = uploaded_file.name + str(uploaded_file.size)
        if st.session_state["uploaded_file_name"] != file_id:
            st.session_state["uploaded_file_name"] = file_id
            
            # Smart Default format selection based on extension
            ext = Path(uploaded_file.name).suffix.upper().lstrip(".")
            if ext in ["JPG", "JPEG"]:
                st.session_state["output_format_sel"] = "JPEG"
            elif ext == "PNG":
                st.session_state["output_format_sel"] = "PNG"
            elif ext == "WEBP":
                st.session_state["output_format_sel"] = "WEBP"
                
            # Clear previous results
            st.session_state["results"] = None
            st.session_state["last_run_params"] = None

    # 4. Sidebar configuration (Compression Settings)
    with st.sidebar:
        st.markdown("### Compression Settings")
        
        st.markdown("#### Basic Settings")
        k = st.slider(
            "Number of Clusters (K)",
            min_value=2,
            max_value=256,
            value=16,
            step=1,
            help="Number of clusters (colors) to generate.",
        )
        
        # Disabled state for sidebar button if no image uploaded
        is_disabled = (uploaded_file is None)
        compress_clicked = st.button(
            "Compress",
            type="primary",
            use_container_width=True,
            disabled=is_disabled,
            help="Upload an image to run compression." if is_disabled else "Start processing execution.",
        )

        # Advanced Settings (collapsed by default inside expander)
        with st.expander("Advanced Settings", expanded=False):
            max_iters = st.slider(
                "Maximum Iterations",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                help="Maximum clustering iterations before halting.",
            )
            resize_enabled = st.checkbox(
                "Resize Image",
                value=True,
                help="Resize large dimensions before processing.",
            )
            if resize_enabled:
                max_dimension = st.slider(
                    "Maximum Dimension",
                    min_value=256,
                    max_value=2048,
                    value=1500,
                    step=64,
                    help="Resize longest side to fit within this value.",
                )
            else:
                max_dimension = 1500

            output_format = st.selectbox(
                "Output Format",
                options=["PNG", "JPEG", "WEBP"],
                key="output_format_sel",
                help="Select target file format for output representation.",
            )

            if output_format in ["JPEG", "WEBP"]:
                quality_val = st.slider(
                    "Quality",
                    min_value=10,
                    max_value=100,
                    value=85,
                    step=5,
                    help="Compression quality level.",
                )
            else:
                quality_val = 85

            optimize_output = st.checkbox(
                "Optimize Output",
                value=True,
                help="Enables PIL optimize and JPEG progressive settings.",
            )

    # Empty State when no upload
    if not uploaded_file:
        st.markdown(
            """
            <div class="dashboard-card" style="text-align: center; padding: 3rem 2rem;">
                <h3 style="color: #818cf8; margin-bottom: 0.5rem;">Ready to Begin</h3>
                <p style="color: #94a3b8; max-width: 500px; margin: 0 auto;">
                    Select an image from your device and click "Compress" in the sidebar panel to run K-Means color quantization.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Image loading and validation
    try:
        original_image, original_bytes, source_format, has_transparency = load_image(uploaded_file)
    except Exception as e:
        st.error(f"Failed to load image: {str(e)}")
        return

    # Trigger processing sequence
    if compress_clicked:
        start_time = time.perf_counter()

        status_placeholder = st.empty()
        progress_bar = st.progress(0.0)

        try:
            # Step 1: Loading image
            status_placeholder.markdown("<div class='status-msg'>Loading image...</div>", unsafe_allow_html=True)
            time.sleep(0.05)
            progress_bar.progress(0.1)

            # Resize check
            resized_image, was_resized = resize_image(
                original_image,
                enabled=resize_enabled,
                max_dimension=max_dimension,
            )
            image_array = pil_to_array(resized_image)

            # Cap K count to total pixels
            pixel_count = image_array.shape[0] * image_array.shape[1]
            effective_k = min(k, pixel_count)

            # Step 2: Running K-Means
            status_placeholder.markdown("<div class='status-msg'>Running K-Means...</div>", unsafe_allow_html=True)

            def progress_callback(curr_iter, total_iters):
                fraction = 0.1 + (curr_iter / total_iters) * 0.7
                progress_bar.progress(fraction)
                status_placeholder.markdown(
                    f"<div class='status-msg'>Running K-Means... (Iteration {curr_iter}/{total_iters})</div>",
                    unsafe_allow_html=True,
                )

            centroids, labels, run_info = run_kmeans_with_progress(
                image_array=image_array,
                K=effective_k,
                max_iters=max_iters,
                progress_callback=progress_callback,
            )

            # Step 3: Optimizing image
            status_placeholder.markdown("<div class='status-msg'>Optimizing image...</div>", unsafe_allow_html=True)
            compressed_array = compress_image(labels, centroids)
            compressed_image = array_to_pil(compressed_array)
            progress_bar.progress(0.9)

            # Prepare output details
            stem = Path(uploaded_file.name).stem
            ext_map = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}
            out_filename = f"{stem}_quantized.{ext_map[output_format]}"

            # Save and compress
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
            status_placeholder.markdown("<div class='status-msg'>Preparing download...</div>", unsafe_allow_html=True)
            elapsed_seconds = time.perf_counter() - start_time

            metrics = calculate_metrics(
                original_array=pil_to_array(original_image),
                compressed_array=compressed_array,
                original_size_bytes=len(original_bytes),
                compressed_size_bytes=compressed_size,
                elapsed_seconds=elapsed_seconds,
            )
            progress_bar.progress(1.0)

            # Store in Session State
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

            time.sleep(0.3)
            status_placeholder.empty()
            progress_bar.empty()

        except Exception as err:
            st.error(f"Error during processing: {str(err)}")
            if "status_placeholder" in locals():
                status_placeholder.empty()
            if "progress_bar" in locals():
                progress_bar.empty()

    # 5. Render output comparison cards (Hierarchy step 4)
    results = st.session_state.get("results")
    last_params = st.session_state.get("last_run_params")

    if results:
        # Check if sidebar configurations changed
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
            st.info("Settings altered. Click the sidebar 'Compress' button to re-run and sync changes.")

        metrics = results["metrics"]
        reduction_pct = metrics["reduction_pct"]
        saved_bytes = metrics["storage_saved"]

        # Alert banners
        if results["was_successful"]:
            st.success(
                f"Compression successful. Saved {format_size(saved_bytes)} ({reduction_pct:.1f}% reduction)."
            )
        else:
            st.warning(
                "Compression warning: Unable to reduce file size below original without significant quality loss. "
                "Try lowering the quality slider, reducing K, or turning on resizing."
            )

        if results["was_resized"]:
            st.info(
                f"Image resized from {results['original_dimensions'][0]}x{results['original_dimensions'][1]} "
                f"to {results['compressed_dimensions'][0]}x{results['compressed_dimensions'][1]} before quantization."
            )

        if has_transparency:
            st.info("Transparency layers detected. Background was flattened onto white for clustering compatibility.")

        if results["effective_k"] < k:
            st.warning(
                f"Cluster count K auto-reduced to {results['effective_k']} due to total pixel capacity constraints."
            )

        # Image view cards side by side (Identical height cards)
        col_view_l, col_view_r = st.columns(2)

        with col_view_l:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; font-size: 1.05rem; color: #ffffff; text-transform: uppercase; letter-spacing: 0.05em;">Original</div>
                        <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 0.25rem;">
                            Resolution: {results['original_dimensions'][0]} × {results['original_dimensions'][1]}<br>
                            Size: {format_size(metrics["original_size"])} &middot; Format: {source_format}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.image(results["original_image"], use_container_width=True)

        with col_view_r:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; font-size: 1.05rem; color: #818cf8; text-transform: uppercase; letter-spacing: 0.05em;">Compressed</div>
                        <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 0.25rem;">
                            Resolution: {results['compressed_dimensions'][0]} × {results['compressed_dimensions'][1]}<br>
                            Size: {format_size(metrics["compressed_size"])} &middot; Format: {output_format}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.image(results["compressed_image"], use_container_width=True)

        # 6. Comparative Metric Card Grid (Hierarchy step 5)
        st.markdown("### Performance & Compression Metrics")

        orig_size_str = format_size(metrics["original_size"])
        comp_size_str = format_size(metrics["compressed_size"])
        reduction_str = f"{reduction_pct:.1f}%"
        orig_colors_str = f'{metrics["original_colors"]:,}'
        comp_colors_str = f'{metrics["compressed_colors"]:,}'
        time_str = f'{metrics["elapsed_seconds"]:.2f}s'

        if results["was_successful"]:
            saved_str = format_size(saved_bytes)
            reduction_sub = f"{reduction_pct:.1f}% savings"
            savings_class = ""
            savings_label = "Saved"
        else:
            increase_bytes = abs(metrics["original_size"] - metrics["compressed_size"])
            saved_str = format_size(increase_bytes)
            reduction_sub = f"{abs(reduction_pct):.1f}% increase"
            savings_class = "negative"
            savings_label = "Increase"

        metrics_html = f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-card-label">Original Size</div>
                <div class="metric-card-value">{orig_size_str}</div>
                <div class="metric-card-sub neutral">Input file</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Compressed Size</div>
                <div class="metric-card-value">{comp_size_str}</div>
                <div class="metric-card-sub neutral">Output file</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Compression %</div>
                <div class="metric-card-value">{reduction_str}</div>
                <div class="metric-card-sub {savings_class}">{reduction_sub}</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Storage Saved</div>
                <div class="metric-card-value">{saved_str}</div>
                <div class="metric-card-sub {savings_class}">{savings_label}</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Execution Time</div>
                <div class="metric-card-value">{time_str}</div>
                <div class="metric-card-sub neutral">Duration</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Original Colors</div>
                <div class="metric-card-value">{orig_colors_str}</div>
                <div class="metric-card-sub neutral">Before</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Compressed Colors</div>
                <div class="metric-card-value">{comp_colors_str}</div>
                <div class="metric-card-sub neutral">After (K)</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # 7. Prominent Download Button (Hierarchy step 6)
        st.download_button(
            label="Download Compressed Image",
            data=results["compressed_bytes"],
            file_name=results["download_filename"],
            mime=f"image/{output_format.lower()}",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
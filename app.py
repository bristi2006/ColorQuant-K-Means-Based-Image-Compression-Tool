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
    """Inject a warm, airy pastel theme and refreshed layout styling for the Streamlit app."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

            html, body, [data-testid="stAppViewContainer"] {
                background: linear-gradient(180deg, #fcf7ef 0%, #fdf6f0 100%);
                color: #3f342d;
                font-family: 'Nunito', 'Segoe UI', sans-serif;
            }

            [data-testid="stSidebar"] {
                background: rgba(255, 248, 239, 0.92);
                border-right: 1px solid rgba(184, 169, 227, 0.28);
                backdrop-filter: blur(8px);
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
                color: #4e3d34;
            }

            div[data-testid="stExpander"] {
                background-color: #fffdf9 !important;
                border: 1px solid rgba(184, 169, 227, 0.28) !important;
                border-radius: 16px !important;
                margin-top: 1rem;
                box-shadow: 0 8px 18px rgba(113, 92, 73, 0.05);
            }

            .hero-card {
                background: linear-gradient(135deg, rgba(255, 140, 105, 0.18), rgba(184, 169, 227, 0.16));
                border: 1px solid rgba(184, 169, 227, 0.24);
                border-radius: 24px;
                padding: 1.6rem 1.8rem;
                margin-bottom: 1.2rem;
                box-shadow: 0 12px 30px rgba(92, 76, 58, 0.08);
            }

            .hero-badge {
                display: inline-block;
                background: rgba(255, 255, 255, 0.85);
                color: #c96e4d;
                border-radius: 999px;
                padding: 0.35rem 0.75rem;
                font-size: 0.8rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.7rem;
            }

            .hero-title {
                font-size: 2.35rem;
                font-weight: 800;
                color: #4b342e;
                margin: 0 0 0.45rem 0;
                line-height: 1.1;
            }

            .hero-subtitle {
                font-size: 1rem;
                color: #5f4e44;
                margin: 0;
                max-width: 700px;
            }

            .upload-card {
                background: linear-gradient(180deg, #fffdf9 0%, #fff7ef 100%);
                border: 2px dashed rgba(255, 140, 105, 0.38);
                border-radius: 24px;
                padding: 1.2rem;
                margin-bottom: 1rem;
                box-shadow: inset 0 1px 3px rgba(92, 76, 58, 0.05);
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            }

            .upload-card:hover {
                transform: translateY(-1px);
                border-color: #ff8c69;
                box-shadow: 0 8px 18px rgba(255, 140, 105, 0.14);
            }

            .upload-title {
                font-size: 1rem;
                font-weight: 700;
                color: #a2563d;
                margin-bottom: 0.5rem;
            }

            .center-shell {
                display: flex;
                justify-content: center;
                margin: 0.2rem 0 1.2rem 0;
            }

            .center-shell > div {
                width: min(320px, 100%);
            }

            .empty-state-card {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 248, 239, 0.95));
                border: 1px solid rgba(184, 169, 227, 0.22);
                border-radius: 24px;
                padding: 2rem 2rem 2.4rem;
                text-align: center;
                box-shadow: 0 12px 30px rgba(92, 76, 58, 0.08);
            }

            .empty-illustration {
                width: 220px;
                height: 160px;
                margin: 0 auto 1rem auto;
                background: linear-gradient(135deg, rgba(255, 140, 105, 0.12), rgba(184, 169, 227, 0.18));
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4rem;
                box-shadow: inset 0 1px 2px rgba(92, 76, 58, 0.08);
            }

            .result-card {
                background: linear-gradient(180deg, #ffffff 0%, #fffaf4 100%);
                border: 1px solid rgba(184, 169, 227, 0.2);
                border-radius: 22px;
                padding: 1rem;
                box-shadow: 0 12px 24px rgba(92, 76, 58, 0.07);
                margin-bottom: 1rem;
            }

            .result-title {
                font-size: 1rem;
                font-weight: 800;
                color: #4b342e;
                margin-bottom: 0.25rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .result-meta {
                font-size: 0.88rem;
                color: #6f5d52;
                margin-bottom: 0.7rem;
                line-height: 1.5;
            }

            div[data-testid="stImage"] img {
                max-height: 320px;
                object-fit: contain;
                border-radius: 16px;
                display: block;
                margin: 0 auto;
                box-shadow: 0 8px 20px rgba(92, 76, 58, 0.12);
            }

            .metrics-shell {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 0.75rem;
                margin: 1rem 0 1.25rem 0;
            }

            .metric-pill {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(255, 248, 239, 0.95));
                border: 1px solid rgba(184, 169, 227, 0.22);
                border-radius: 16px;
                padding: 0.8rem 0.9rem;
                box-shadow: 0 8px 18px rgba(92, 76, 58, 0.06);
            }

            .metric-pill span {
                display: block;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #8d7265;
                margin-bottom: 0.3rem;
            }

            .metric-pill strong {
                display: block;
                font-size: 1.15rem;
                color: #3f342d;
                font-weight: 800;
            }

            .metric-pill em {
                display: block;
                font-size: 0.8rem;
                color: #9b7f6e;
                font-style: normal;
                margin-top: 0.2rem;
            }

            .k-display {
                background: linear-gradient(135deg, rgba(255, 140, 105, 0.16), rgba(184, 169, 227, 0.18));
                border: 1px solid rgba(184, 169, 227, 0.26);
                border-radius: 18px;
                padding: 0.95rem 1rem;
                text-align: center;
                margin-bottom: 0.6rem;
                box-shadow: 0 8px 18px rgba(92, 76, 58, 0.05);
            }

            .k-display strong {
                display: block;
                font-size: 1.8rem;
                font-weight: 800;
                color: #a2563d;
            }

            .k-display span {
                display: block;
                font-size: 0.9rem;
                color: #6f5d52;
                margin-top: 0.2rem;
            }

            .status-msg {
                font-size: 0.95rem;
                font-weight: 700;
                color: #a2563d;
                margin-bottom: 0.5rem;
                text-align: center;
            }

            div.stButton > button:first-child {
                background: linear-gradient(135deg, #ff8c69 0%, #ff7b54 100%);
                color: white;
                border: none;
                border-radius: 999px;
                padding: 0.8rem 1.7rem;
                font-weight: 800;
                font-size: 1rem;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                box-shadow: 0 10px 24px rgba(255, 140, 105, 0.28);
                width: 100%;
            }

            div.stButton > button:first-child:hover {
                transform: translateY(-2px) scale(1.01);
                box-shadow: 0 14px 28px rgba(255, 140, 105, 0.32);
            }

            div.stButton > button:first-child:disabled {
                background: linear-gradient(135deg, #efc4b2 0%, #e6d2c2 100%);
                color: #6f5d52;
                box-shadow: none;
            }

            div.stDownloadButton > button:first-child {
                background: linear-gradient(135deg, #b8a9e3 0%, #9f8dd9 100%);
                color: #3f342d;
                border: none;
                border-radius: 999px;
                padding: 0.8rem 1.7rem;
                font-weight: 800;
                font-size: 1rem;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                box-shadow: 0 10px 24px rgba(184, 169, 227, 0.2);
                width: 100%;
            }

            div.stDownloadButton > button:first-child:hover {
                transform: translateY(-2px);
                box-shadow: 0 14px 28px rgba(184, 169, 227, 0.24);
            }

            [data-testid="stFileUploader"] {
                background: linear-gradient(180deg, #fffdf9 0%, #fff7ef 100%);
                border: 2px dashed rgba(255, 140, 105, 0.38);
                border-radius: 22px;
                padding: 1rem;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }

            [data-testid="stFileUploader"]:hover {
                border-color: #ff8c69;
                box-shadow: 0 8px 18px rgba(255, 140, 105, 0.12);
            }

            [data-testid="stFileUploaderDropzone"] {
                background-color: transparent !important;
            }

            [data-testid="stAlert"] {
                border-radius: 16px;
                border: 1px solid rgba(184, 169, 227, 0.24);
                background: #fffaf4;
                box-shadow: 0 8px 18px rgba(92, 76, 58, 0.05);
            }

            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            header { background-color: transparent !important; }
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

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">🎨 K-Compress</div>
            <h1 class="hero-title">Turn bold colors into lighter files.</h1>
            <p class="hero-subtitle">Upload an image, tune the cluster count, and let K-Means keep the palette feeling vivid while trimming the footprint.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown('<div class="upload-title">Drop your image here ✨</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload image (PNG, JPEG, WEBP)",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    center_col_1, center_col_2, center_col_3 = st.columns([1, 2, 1])
    with center_col_2:
        compress_clicked = st.button(
            "Compress image",
            type="primary",
            use_container_width=True,
            disabled=uploaded_file is None,
            help="Upload an image to run compression." if uploaded_file is None else "Start processing execution.",
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
        st.markdown(f"""
        <div class="k-display">
            <strong>{k}</strong>
            <span>More clusters = closer to the original.</span>
        </div>
        """, unsafe_allow_html=True)
        
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
            <div class="empty-state-card">
                <div class="empty-illustration">🖼️</div>
                <h3 style="color: #4b342e; margin-bottom: 0.45rem;">Ready for your first compression</h3>
                <p style="color: #6f5d52; max-width: 560px; margin: 0 auto; line-height: 1.6;">
                    Choose an image to start a warm, colorful K-Means pass. The preview and stats will appear here once the compression is done.
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

        col_view_l, col_view_r = st.columns(2)

        with col_view_l:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-title">Original</div>
                    <div class="result-meta">
                        Resolution: {results['original_dimensions'][0]} × {results['original_dimensions'][1]}<br>
                        Size: {format_size(metrics["original_size"])} · Format: {source_format}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(results["original_image"], use_container_width=True)

        with col_view_r:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-title">Compressed</div>
                    <div class="result-meta">
                        Resolution: {results['compressed_dimensions'][0]} × {results['compressed_dimensions'][1]}<br>
                        Size: {format_size(metrics["compressed_size"])} · Format: {output_format}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(results["compressed_image"], use_container_width=True)

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
        <div class="metrics-shell">
            <div class="metric-pill">
                <span>Original Size</span>
                <strong>{orig_size_str}</strong>
                <em>Input file</em>
            </div>
            <div class="metric-pill">
                <span>Compressed Size</span>
                <strong>{comp_size_str}</strong>
                <em>Output file</em>
            </div>
            <div class="metric-pill">
                <span>Compression %</span>
                <strong>{reduction_str}</strong>
                <em>{reduction_sub}</em>
            </div>
            <div class="metric-pill">
                <span>Storage Saved</span>
                <strong>{saved_str}</strong>
                <em>{savings_label}</em>
            </div>
            <div class="metric-pill">
                <span>Execution Time</span>
                <strong>{time_str}</strong>
                <em>Duration</em>
            </div>
            <div class="metric-pill">
                <span>Original Colors</span>
                <strong>{orig_colors_str}</strong>
                <em>Before</em>
            </div>
            <div class="metric-pill">
                <span>Compressed Colors</span>
                <strong>{comp_colors_str}</strong>
                <em>After (K)</em>
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
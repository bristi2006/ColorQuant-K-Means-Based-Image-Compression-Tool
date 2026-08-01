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
    """Inject a light mode glassmorphism SaaS style matching Linear/Raycast/Stripe visual systems."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

            /* Global Styles Reset to Soft Light Mode Gradient */
            html, body, [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #f4f6fc 0%, #fafbff 50%, #edf1fd 100%) !important;
                color: #1e1b4b !important;
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            }

            [data-testid="stHeader"] {
                background-color: transparent !important;
            }

            /* Hide Sidebar completely to build horizontal layouts */
            [data-testid="stSidebar"] {
                display: none !important;
            }

            /* Hero Title Header Styling */
            .hero-container {
                text-align: center;
                padding: 2.5rem 1rem 1.5rem 1rem;
                margin-bottom: 1rem;
            }

            .hero-logo-box {
                display: inline-flex;
                background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
                width: 54px;
                height: 54px;
                border-radius: 16px;
                justify-content: center;
                align-items: center;
                margin-bottom: 1.25rem;
                box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
                transform: rotate(-5deg);
                transition: transform 0.3s ease;
            }
            
            .hero-logo-box:hover {
                transform: rotate(5deg) scale(1.05);
            }

            .hero-title {
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(90deg, #4f46e5, #ec4899);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.03em;
                line-height: 1.1;
            }

            .hero-subtitle {
                font-size: 1.05rem;
                color: #64748b;
                margin-top: 0.5rem;
                margin-bottom: 0;
                font-weight: 400;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }

            /* Glassmorphic border containers */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(255, 255, 255, 0.65) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                border-radius: 20px !important;
                padding: 1.5rem !important;
                box-shadow: 0 10px 30px rgba(99, 102, 241, 0.03) !important;
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 15px 35px rgba(99, 102, 241, 0.06) !important;
                border-color: rgba(99, 102, 241, 0.15) !important;
            }

            /* Custom drag & drop file uploader overrides */
            [data-testid="stFileUploader"] {
                background: rgba(255, 255, 255, 0.65) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                border-radius: 20px !important;
                padding: 1.5rem !important;
                box-shadow: 0 10px 30px rgba(99, 102, 241, 0.03) !important;
                max-width: 650px !important;
                margin: 0 auto 1.5rem auto !important;
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease !important;
            }

            [data-testid="stFileUploader"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 15px 35px rgba(99, 102, 241, 0.06) !important;
                border-color: rgba(99, 102, 241, 0.15) !important;
            }

            [data-testid="stFileUploaderDropzone"] {
                background-color: transparent !important;
            }

            /* Preview image formatting inside symmetrical cards */
            div[data-testid="stImage"] img {
                max-height: 300px !important;
                object-fit: contain !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                margin: 0 auto !important;
                display: block !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
            }

            /* Collapsible panel override (advanced settings) */
            div[data-testid="stExpander"] {
                background-color: rgba(255, 255, 255, 0.4) !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.01) !important;
                margin-top: 1rem;
            }

            /* Metric Cards Grid Layout */
            .metrics-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 1.25rem;
                margin-top: 1.5rem;
                margin-bottom: 2rem;
            }

            .metric-card {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.6);
                border-radius: 16px;
                padding: 1.25rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                box-shadow: 0 8px 24px rgba(99, 102, 241, 0.02);
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
            }

            .metric-card:hover {
                transform: translateY(-4px);
                border-color: rgba(99, 102, 241, 0.25);
                box-shadow: 0 12px 30px rgba(99, 102, 241, 0.05);
            }

            .metric-icon-box {
                width: 44px;
                height: 44px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%);
                color: #4f46e5;
                flex-shrink: 0;
            }

            .metric-info {
                display: flex;
                flex-direction: column;
                text-align: left;
            }

            .metric-value {
                font-size: 1.25rem;
                font-weight: 700;
                color: #1e1b4b;
                line-height: 1.2;
            }

            .metric-label {
                font-size: 0.72rem;
                color: #64748b;
                font-weight: 600;
                margin-top: 0.1rem;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }

            .metric-sub {
                font-size: 0.75rem;
                font-weight: 600;
                color: #10b981;
                margin-top: 0.15rem;
            }

            .metric-sub.negative {
                color: #ef4444;
            }

            .metric-sub.neutral {
                color: #8b9bb4;
            }

            /* Compress Trigger Button Styling */
            div.stButton > button:first-child {
                background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 9999px !important;
                padding: 0.75rem 2rem !important;
                font-weight: 700 !important;
                font-size: 1rem !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
                width: 100% !important;
                letter-spacing: 0.01em !important;
            }

            div.stButton > button:first-child:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45) !important;
            }

            /* Download Button Styling */
            div.stDownloadButton > button:first-child {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 9999px !important;
                padding: 0.85rem 2.5rem !important;
                font-weight: 700 !important;
                font-size: 1.05rem !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
                width: 100% !important;
            }

            div.stDownloadButton > button:first-child:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4) !important;
            }

            /* Status progress message style */
            .status-msg {
                font-size: 1rem;
                font-weight: 600;
                color: #4f46e5;
                margin-bottom: 0.5rem;
                text-align: center;
            }

            /* Footer Styling */
            .footer-container {
                text-align: center;
                padding: 2.5rem 1rem 1.5rem 1rem;
                border-top: 1px solid rgba(99, 102, 241, 0.08);
                margin-top: 4rem;
                color: #64748b;
                font-size: 0.85rem;
            }

            .footer-links {
                display: flex;
                justify-content: center;
                gap: 1.5rem;
                margin-top: 0.5rem;
            }

            .footer-links a {
                color: #4f46e5;
                text-decoration: none;
                font-weight: 500;
                transition: color 0.2s ease;
            }

            .footer-links a:hover {
                color: #ec4899;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # 1. Page Configuration (Initial sidebar state set to collapsed)
    st.set_page_config(
        page_title="K-Compress",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    apply_custom_theme()

    # 2. Hero Section (Logo, Title, Subtitle)
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-logo-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="9" cy="9" r="2"></circle>
                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
                </svg>
            </div>
            <h1 class="hero-title">K-Compress</h1>
            <p class="hero-subtitle">Modern vector quantization and image storage optimizer</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Upload Card Illustration Block & File Uploader
    st.markdown(
        """
        <div style="text-align: center; max-width: 650px; margin: 0 auto -0.5rem auto;">
            <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%); width: 70px; height: 70px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 1rem; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08);">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="url(#upload-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <defs>
                        <linearGradient id="upload-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#4f46e5" />
                            <stop offset="100%" stop-color="#ec4899" />
                        </linearGradient>
                    </defs>
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
            </div>
            <h3 style="color: #1e1b4b; font-size: 1.25rem; font-weight: 700; margin: 0 0 0.25rem 0;">Drag & drop your image here</h3>
            <p style="color: #64748b; font-size: 0.88rem; margin: 0 0 0.5rem 0;">Supported formats: PNG, JPEG, WEBP</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload image",
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

    # Empty State when no upload
    if not uploaded_file:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; max-width: 650px; margin: 1rem auto; padding: 2rem 1.5rem;">
                <h3 style="color: #4f46e5; margin-top: 0; margin-bottom: 0.5rem; font-weight: 700;">Awaiting Source File</h3>
                <p style="color: #64748b; max-width: 500px; margin: 0 auto; font-size: 0.92rem;">
                    Load an image above and configure parameters to compress your file using vector color clustering.
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

    # 4. Compression Controls - Horizontal Main Grid Section
    # Wrapped inside a native container styled as a frosted card
    with st.container(border=True):
        st.markdown("<div style='font-weight: 800; font-size: 1.15rem; color: #1e1b4b; margin-bottom: 0.8rem; letter-spacing: -0.01em;'>Compression Parameters</div>", unsafe_allow_html=True)
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
        
        with col_ctrl1:
            k = st.slider(
                "Number of Clusters (K)",
                min_value=2,
                max_value=256,
                value=16,
                step=1,
                help="Maximum unique colors in the output image.",
            )
            
        with col_ctrl2:
            output_format = st.selectbox(
                "Output Format",
                options=["PNG", "JPEG", "WEBP"],
                key="output_format_sel",
                help="Select target file format for output representation.",
            )
            
        with col_ctrl3:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            compress_clicked = st.button("Compress", type="primary", use_container_width=True)

        # Advanced settings panel collapsible inside the controls box
        with st.expander("Advanced Settings", expanded=False):
            max_iters = st.slider(
                "Maximum Iterations",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                help="Maximum iterations for K-Means iterations.",
            )
            resize_enabled = st.checkbox(
                "Resize Image",
                value=True,
                help="Auto-resize image width/height before quantizing.",
            )
            if resize_enabled:
                max_dimension = st.slider(
                    "Maximum Dimension",
                    min_value=256,
                    max_value=2048,
                    value=1500,
                    step=64,
                    help="Limit the longest side of the image to fit this boundary.",
                )
            else:
                max_dimension = 1500
                
            if output_format in ["JPEG", "WEBP"]:
                quality_val = st.slider(
                    "Quality",
                    min_value=10,
                    max_value=100,
                    value=85,
                    step=5,
                    help="Compression quality index value.",
                )
            else:
                quality_val = 85

            optimize_output = st.checkbox(
                "Optimize Output",
                value=True,
                help="Apply progressive scans and output size optimization routines.",
            )

    # Trigger processing sequence
    if compress_clicked:
        start_time = time.perf_counter()

        status_placeholder = st.empty()
        progress_bar = st.progress(0.0)

        try:
            # Step 1: Loading image...
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

            # Step 2: Running K-Means...
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

            # Step 3: Optimizing image...
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

            # Step 4: Preparing download...
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

    # 5. Render output comparison cards
    results = st.session_state.get("results")
    last_params = st.session_state.get("last_run_params")

    if results:
        # Check if configurations changed
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
            st.info("Settings changed since last execution. Click 'Compress' to synchronize new values.")

        metrics = results["metrics"]
        reduction_pct = metrics["reduction_pct"]
        saved_bytes = metrics["storage_saved"]

        # Alert state banners
        if results["was_successful"]:
            st.success(
                f"Compression successful. Size reduced by {format_size(saved_bytes)} ({reduction_pct:.1f}% savings)."
            )
        else:
            st.warning(
                "Compression warning: Unable to reduce file size below original without significant quality loss. "
                "Try lowering the quality slider, reducing K, or turning on resizing."
            )

        if results["was_resized"]:
            st.info(
                f"Image resized from {results['original_dimensions'][0]}x{results['original_dimensions'][1]} "
                f"to {results['compressed_dimensions'][0]}x{results['compressed_dimensions'][1]} before clustering."
            )

        if has_transparency:
            st.info("Transparency layers detected. Background was flattened onto white for clustering compatibility.")

        if results["effective_k"] < k:
            st.warning(
                f"Cluster count K auto-reduced to {results['effective_k']} due to pixel resolution capacity."
            )

        # Image view cards side by side (Identical height cards)
        col_view_l, col_view_r = st.columns(2)

        with col_view_l:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; font-size: 1.05rem; color: #1e1b4b; text-transform: uppercase; letter-spacing: 0.05em;">Original</div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.25rem;">
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
                        <div style="font-weight: 700; font-size: 1.05rem; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.05em;">Compressed</div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.25rem;">
                            Resolution: {results['compressed_dimensions'][0]} × {results['compressed_dimensions'][1]}<br>
                            Size: {format_size(metrics["compressed_size"])} &middot; Format: {output_format}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.image(results["compressed_image"], use_container_width=True)

        # 6. Comparative Metric Card Grid
        st.markdown("### Performance & Compression Metrics")

        orig_size_str = format_size(metrics["original_size"])
        comp_size_str = format_size(metrics["compressed_size"])
        reduction_str = f"{reduction_pct:.1f}%"
        saved_str = format_size(saved_bytes)
        orig_colors_str = f'{metrics["original_colors"]:,}'
        comp_colors_str = f'{metrics["compressed_colors"]:,}'
        time_str = f'{metrics["elapsed_seconds"]:.2f}s'
        
        orig_dims_str = f"{results['original_dimensions'][0]} × {results['original_dimensions'][1]}"
        comp_dims_str = f"{results['compressed_dimensions'][0]} × {results['compressed_dimensions'][1]}"

        savings_class = "metric-sub" if results["was_successful"] else "metric-sub negative"
        savings_label = "Saved" if results["was_successful"] else "Increase"
        
        if results["was_successful"]:
            reduction_sub = f"{reduction_pct:.1f}% savings"
        else:
            increase_bytes = abs(metrics["original_size"] - metrics["compressed_size"])
            saved_str = format_size(increase_bytes)
            reduction_sub = f"{abs(reduction_pct):.1f}% increase"

        # Grid HTML representing soft neumorphic cards with modern outline SVG icons
        metrics_html = f"""
        <div class="metrics-container">
            <!-- Card 1: Storage Saved -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                        <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                        <line x1="6" y1="6" x2="6.01" y2="6"></line>
                        <line x1="6" y1="18" x2="6.01" y2="18"></line>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{saved_str}</div>
                    <div class="metric-label">Storage Saved</div>
                    <div class="{savings_class}">{savings_label}</div>
                </div>
            </div>
            
            <!-- Card 2: Compression % -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                        <polyline points="17 18 23 18 23 12"></polyline>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{reduction_str}</div>
                    <div class="metric-label">Compression %</div>
                    <div class="{savings_class}">{reduction_sub}</div>
                </div>
            </div>
            
            <!-- Card 3: Execution Time -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{time_str}</div>
                    <div class="metric-label">Execution Time</div>
                    <div class="metric-sub neutral">Duration</div>
                </div>
            </div>
            
            <!-- Card 4: Original Colors -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 14.7255 3.09032 17.1962 4.85857 19C5.03345 19.1749 5.25367 19.3106 5.49653 19.3957C5.97839 19.5645 6.50284 19.4674 6.89949 19.14C7.5 18.64 8.5 18.64 9.10051 19.14C9.49716 19.4674 10.0216 19.5645 10.5035 19.3957C10.7463 19.3106 10.9666 19.1749 11.1414 19C11.6702 18.4712 12.3878 18.1065 13.1818 18.1065C13.9758 18.1065 14.6934 18.4712 15.2222 19L16.2929 17.9293C16.9229 17.3 17.9771 17.3 18.6071 17.9293L19.6778 19C20.6778 20 22 18 22 12"></path>
                        <circle cx="7.5" cy="10.5" r="1.5"></circle>
                        <circle cx="11.5" cy="7.5" r="1.5"></circle>
                        <circle cx="16.5" cy="9.5" r="1.5"></circle>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{orig_colors_str}</div>
                    <div class="metric-label">Original Colors</div>
                    <div class="metric-sub neutral">Before</div>
                </div>
            </div>
            
            <!-- Card 5: Compressed Colors -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M15 4V2"></path>
                        <path d="M15 16v-2"></path>
                        <path d="M8 9h2"></path>
                        <path d="M20 9h2"></path>
                        <path d="M17.8 5.2l-1.4 1.4"></path>
                        <path d="M7.6 15.4l-1.4 1.4"></path>
                        <path d="M16.4 12.6l1.4 1.4"></path>
                        <path d="M6.2 6.2l1.4-1.4"></path>
                        <path d="M14 9a5 5 0 0 1-5 5"></path>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{comp_colors_str}</div>
                    <div class="metric-label">Compressed Colors</div>
                    <div class="metric-sub neutral">After (K)</div>
                </div>
            </div>
            
            <!-- Card 6: Original Dimensions -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="15 3 21 3 21 9"></polyline>
                        <polyline points="9 21 3 21 3 15"></polyline>
                        <line x1="21" y1="3" x2="14" y2="10"></line>
                        <line x1="3" y1="21" x2="10" y2="14"></line>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{orig_dims_str}</div>
                    <div class="metric-label">Original Dims</div>
                    <div class="metric-sub neutral">Resolution</div>
                </div>
            </div>
            
            <!-- Card 7: Compressed Dimensions -->
            <div class="metric-card">
                <div class="metric-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="4 14 10 14 10 20"></polyline>
                        <polyline points="20 10 14 10 14 4"></polyline>
                        <line x1="14" y1="10" x2="21" y2="3"></line>
                        <line x1="10" y1="14" x2="3" y2="21"></line>
                    </svg>
                </div>
                <div class="metric-info">
                    <div class="metric-value">{comp_dims_str}</div>
                    <div class="metric-label">Compressed Dims</div>
                    <div class="metric-sub neutral">Output size</div>
                </div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # 7. Prominent Download Button
        st.download_button(
            label="Download Compressed Image",
            data=results["compressed_bytes"],
            file_name=results["download_filename"],
            mime=f"image/{output_format.lower()}",
            use_container_width=True,
        )

    # 8. Simple Footer
    st.markdown(
        """
        <div class="footer-container">
            <p><strong>K-Compress</strong> &middot; Optimized Image Quantization Engine</p>
            <div class="footer-links">
                <span>Version 2.1.0</span>
                <span>&middot;</span>
                <a href="https://github.com/bristi2006/ColorQuant-K-Means-Based-Image-Compression-Tool" target="_blank">GitHub Repository</a>
                <span>&middot;</span>
                <span>Author: Bristi</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
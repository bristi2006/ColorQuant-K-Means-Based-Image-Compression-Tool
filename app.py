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


# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
# Background   #FDF6F0  warm cream
# Surface      #FFF9F5  slightly brighter card surface
# Sidebar bg   #F5EDE5  warm tinted sidebar
# Primary      #E8725A  coral-peach CTA
# Primary dark #C9573F  hover state
# Accent       #B8A9E3  soft lavender labels / accents
# Success      #52C788  mint green
# Warning      #F5A623  amber
# Text main    #2D1F1A  near-black warm brown – contrast ≥ 7:1 on cream
# Text muted   #6B5047  medium warm brown – contrast ≥ 4.5:1 on cream
# Border       #E8D9CE  warm light border
# ─────────────────────────────────────────────────────────────────────────────


def apply_custom_theme() -> None:
    """Inject warm light SaaS theme — CSS only, no backend changes."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap');

        /* ── Global reset ── */
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background-color: #FDF6F0 !important;
            color: #2D1F1A;
            font-family: 'Nunito', 'Segoe UI', sans-serif;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #F5EDE5 !important;
            border-right: 1px solid #E8D9CE !important;
        }
        [data-testid="stSidebar"] * {
            color: #2D1F1A !important;
        }
        /* Sidebar heading */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            color: #2D1F1A !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 2px solid #E8D9CE !important;
            margin-bottom: 1.1rem !important;
            letter-spacing: 0.01em !important;
        }
        /* Sidebar expander */
        div[data-testid="stExpander"] {
            background-color: #FFF9F5 !important;
            border: 1px solid #E8D9CE !important;
            border-radius: 12px !important;
            margin-top: 0.75rem !important;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 700 !important;
            color: #2D1F1A !important;
        }

        /* ── Main block container ── */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 1100px !important;
        }

        /* ── Hero card ── */
        .hero-card {
            background: linear-gradient(135deg, #FFF0E8 0%, #F8E8F8 100%);
            border: 1px solid #E8D9CE;
            border-radius: 24px;
            padding: 2.25rem 2.5rem 2rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 24px rgba(232,114,90,0.10);
        }
        .hero-icon {
            font-size: 3rem;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            font-size: 2.6rem;
            font-weight: 900;
            margin: 0 0 0.3rem;
            background: linear-gradient(90deg, #E8725A, #B8A9E3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }
        .hero-tagline {
            font-size: 1.05rem;
            color: #6B5047;
            margin: 0;
            font-weight: 500;
        }

        /* ── Upload zone ── */
        [data-testid="stFileUploader"] {
            background-color: #FFF9F5 !important;
            border: 2.5px dashed #E8A090 !important;
            border-radius: 20px !important;
            padding: 1.5rem 1.5rem 1.25rem !important;
            margin-bottom: 1.25rem !important;
            transition: border-color 0.25s ease, background-color 0.25s ease !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #E8725A !important;
            background-color: #FFF3EC !important;
        }
        [data-testid="stFileUploaderDropzone"] {
            background-color: transparent !important;
        }

        /* ── CTA compress button (main area) ── */
        .compress-btn-wrapper > div > button,
        .compress-btn-wrapper button {
            background: linear-gradient(135deg, #E8725A 0%, #D45E46 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 0.85rem 2.5rem !important;
            font-family: 'Nunito', sans-serif !important;
            font-weight: 800 !important;
            font-size: 1.15rem !important;
            letter-spacing: 0.01em !important;
            box-shadow: 0 6px 22px rgba(232,114,90,0.38) !important;
            transition: transform 0.2s cubic-bezier(.34,1.56,.64,1), box-shadow 0.2s ease !important;
            width: 100% !important;
        }
        .compress-btn-wrapper > div > button:hover,
        .compress-btn-wrapper button:hover {
            transform: scale(1.04) translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(232,114,90,0.45) !important;
            background: linear-gradient(135deg, #D45E46 0%, #C04D35 100%) !important;
        }
        .compress-btn-wrapper > div > button:disabled,
        .compress-btn-wrapper button:disabled {
            background: #E8D9CE !important;
            color: #A88C82 !important;
            box-shadow: none !important;
            transform: none !important;
        }

        /* ── All other stButtons (sidebar etc.) ── */
        div.stButton > button:first-child {
            background: #E8725A !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 14px rgba(232,114,90,0.28) !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
        }
        div.stButton > button:first-child:hover {
            background: #C9573F !important;
            box-shadow: 0 6px 20px rgba(232,114,90,0.38) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Download button ── */
        div.stDownloadButton > button:first-child {
            background: linear-gradient(135deg, #52C788 0%, #3DAF6D 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 0.85rem 2.5rem !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            box-shadow: 0 6px 22px rgba(82,199,136,0.35) !important;
            transition: transform 0.2s cubic-bezier(.34,1.56,.64,1), box-shadow 0.2s ease !important;
            width: 100% !important;
        }
        div.stDownloadButton > button:first-child:hover {
            transform: scale(1.03) translateY(-2px) !important;
            box-shadow: 0 10px 28px rgba(82,199,136,0.42) !important;
        }

        /* ── Image comparison cards (st.container border=True) ── */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFF9F5 !important;
            border: 1.5px solid #E8D9CE !important;
            border-radius: 20px !important;
            padding: 1.25rem !important;
            box-shadow: 0 4px 18px rgba(45,31,26,0.07) !important;
            transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 8px 28px rgba(232,114,90,0.13) !important;
            border-color: #E8A090 !important;
        }

        /* ── Internal preview images ── */
        div[data-testid="stImage"] img {
            border-radius: 12px !important;
            border: 1px solid #E8D9CE !important;
            object-fit: contain !important;
            max-height: 320px !important;
            display: block !important;
            margin: 0 auto !important;
        }

        /* ── K slider: live number display ── */
        .k-display {
            text-align: center;
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(90deg, #E8725A, #B8A9E3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1;
            margin-bottom: 0.1rem;
        }
        .k-hint {
            text-align: center;
            font-size: 0.82rem;
            color: #6B5047;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }

        /* ── Empty state card ── */
        .empty-state {
            background: #FFF9F5;
            border: 2px dashed #E8D9CE;
            border-radius: 20px;
            padding: 3.5rem 2rem;
            text-align: center;
            margin-top: 1rem;
        }
        .empty-state-icon { font-size: 3.5rem; margin-bottom: 0.75rem; }
        .empty-state-title {
            font-size: 1.3rem;
            font-weight: 800;
            color: #2D1F1A;
            margin-bottom: 0.4rem;
        }
        .empty-state-body {
            font-size: 0.95rem;
            color: #6B5047;
            max-width: 420px;
            margin: 0 auto;
            font-weight: 500;
        }

        /* ── Metrics grid ── */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 1rem;
            margin: 1.25rem 0 2rem;
        }
        .metric-pill {
            background: #FFF9F5;
            border: 1.5px solid #E8D9CE;
            border-radius: 16px;
            padding: 1.1rem 0.75rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(45,31,26,0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-pill:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 18px rgba(232,114,90,0.14);
        }
        .metric-pill-label {
            font-size: 0.67rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #B8A9E3;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .metric-pill-value {
            font-size: 1.35rem;
            font-weight: 800;
            color: #2D1F1A;
        }
        .metric-pill-sub {
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 0.25rem;
            color: #52C788;          /* success / mint */
        }
        .metric-pill-sub.negative { color: #D9534F; }
        .metric-pill-sub.neutral  { color: #6B5047; }

        /* ── Status message ── */
        .status-msg {
            font-size: 0.95rem;
            font-weight: 700;
            color: #E8725A;
            text-align: center;
            margin-bottom: 0.4rem;
        }

        /* ── Section divider ── */
        .warm-divider {
            border: none;
            border-top: 1.5px solid #E8D9CE;
            margin: 1.75rem 0;
        }

        /* ── Card label for image cards ── */
        .img-card-badge {
            display: inline-block;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }
        .img-card-badge.original {
            background: #FFF0EB;
            color: #C9573F;
            border: 1px solid #F5C4B8;
        }
        .img-card-badge.compressed {
            background: #EEE9FA;
            color: #7B6DBF;
            border: 1px solid #D1C7F0;
        }
        .img-card-meta {
            font-size: 0.82rem;
            color: #6B5047;
            font-weight: 500;
            margin-bottom: 0.6rem;
        }

        /* ── Streamlit native overrides ── */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
        header     { background-color: transparent !important; }

        /* Slider track colour (best-effort) */
        [data-testid="stSlider"] [class*="thumb"] {
            background-color: #E8725A !important;
        }

        /* Progress bar */
        [data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, #E8725A, #B8A9E3) !important;
            border-radius: 999px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # ── Page config ──────────────────────────────────────────────────────────
    st.set_page_config(
        page_title="K-Compress — Image Compression",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_theme()

    # ── Session state init ────────────────────────────────────────────────────
    if "uploaded_file_name" not in st.session_state:
        st.session_state["uploaded_file_name"] = None
        st.session_state["output_format_sel"] = "JPEG"
        st.session_state["results"] = None
        st.session_state["last_run_params"] = None

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Compression Settings")

        # Live K display
        k = st.slider(
            "Number of Colors (K)",
            min_value=2,
            max_value=256,
            value=16,
            step=1,
            help="Number of unique colors in the output image.",
        )
        st.markdown(
            f'<div class="k-display">{k}</div>'
            f'<div class="k-hint">{"More colors = closer to original" if k > 32 else "Fewer colors = smaller file"}</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Advanced Settings", expanded=False):
            max_iters = st.slider(
                "Max Iterations",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                help="K-Means stops early if it converges.",
            )
            resize_enabled = st.checkbox(
                "Auto-resize Large Images",
                value=True,
                help="Recommended — shrinks huge images before processing.",
            )
            if resize_enabled:
                max_dimension = st.slider(
                    "Max Dimension (px)",
                    min_value=256,
                    max_value=2048,
                    value=1500,
                    step=64,
                )
            else:
                max_dimension = 1500

            output_format = st.selectbox(
                "Output Format",
                options=["PNG", "JPEG", "WEBP"],
                key="output_format_sel",
            )
            if output_format in ["JPEG", "WEBP"]:
                quality_val = st.slider(
                    "Quality",
                    min_value=10,
                    max_value=100,
                    value=85,
                    step=5,
                )
            else:
                quality_val = 85

            optimize_output = st.checkbox("Optimize Output", value=True)

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-icon">🎨</div>
            <h1 class="hero-title">K-Compress</h1>
            <p class="hero-tagline">
                Shrink your images with K-Means color magic — fewer colors, smaller files, beautiful results.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Upload zone ───────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Drop your image here ✨  (PNG, JPEG, WEBP)",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="visible",
    )

    # Smart format default on new upload
    if uploaded_file:
        file_id = uploaded_file.name + str(uploaded_file.size)
        if st.session_state["uploaded_file_name"] != file_id:
            st.session_state["uploaded_file_name"] = file_id
            ext = Path(uploaded_file.name).suffix.upper().lstrip(".")
            if ext in ["JPG", "JPEG"]:
                st.session_state["output_format_sel"] = "JPEG"
            elif ext == "PNG":
                st.session_state["output_format_sel"] = "PNG"
            elif ext == "WEBP":
                st.session_state["output_format_sel"] = "WEBP"
            st.session_state["results"] = None
            st.session_state["last_run_params"] = None

    # ── CTA compress button (centered, main area) ─────────────────────────────
    col_l, col_c, col_r = st.columns([1.2, 2, 1.2])
    with col_c:
        st.markdown('<div class="compress-btn-wrapper">', unsafe_allow_html=True)
        compress_clicked = st.button(
            "Compress Image" if uploaded_file else "Upload an image first",
            disabled=(uploaded_file is None),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Empty state ───────────────────────────────────────────────────────────
    if not uploaded_file:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🖼️</div>
                <div class="empty-state-title">No image yet</div>
                <div class="empty-state-body">
                    Upload a PNG, JPEG or WEBP above, pick your K value in the sidebar,
                    then hit <strong>Compress Image</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Load & validate ───────────────────────────────────────────────────────
    try:
        original_image, original_bytes, source_format, has_transparency = load_image(uploaded_file)
    except Exception as e:
        st.error(f"Could not read image: {e}")
        return

    # ── Processing pipeline ───────────────────────────────────────────────────
    if compress_clicked:
        start_time = time.perf_counter()
        status_ph = st.empty()
        prog = st.progress(0.0)

        try:
            status_ph.markdown("<div class='status-msg'>Loading image...</div>", unsafe_allow_html=True)
            time.sleep(0.05)
            prog.progress(0.1)

            resized_image, was_resized = resize_image(
                original_image, enabled=resize_enabled, max_dimension=max_dimension
            )
            image_array = pil_to_array(resized_image)

            pixel_count = image_array.shape[0] * image_array.shape[1]
            effective_k = min(k, pixel_count)

            status_ph.markdown("<div class='status-msg'>Running K-Means...</div>", unsafe_allow_html=True)

            def progress_callback(curr_iter, total_iters):
                frac = 0.1 + (curr_iter / total_iters) * 0.7
                prog.progress(frac)
                status_ph.markdown(
                    f"<div class='status-msg'>Running K-Means... iteration {curr_iter}/{total_iters}</div>",
                    unsafe_allow_html=True,
                )

            centroids, labels, run_info = run_kmeans_with_progress(
                image_array=image_array,
                K=effective_k,
                max_iters=max_iters,
                progress_callback=progress_callback,
            )

            status_ph.markdown("<div class='status-msg'>Optimizing image...</div>", unsafe_allow_html=True)
            compressed_array = compress_image(labels, centroids)
            compressed_image  = array_to_pil(compressed_array)
            prog.progress(0.9)

            stem        = Path(uploaded_file.name).stem
            ext_map     = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}
            out_filename = f"{stem}_kcompress.{ext_map[output_format]}"

            saved_path, compressed_bytes, compressed_size, final_quality, was_successful = save_image(
                image=compressed_image,
                filename=out_filename,
                original_size_bytes=len(original_bytes),
                output_format=output_format,
                quality=quality_val if output_format in ["JPEG", "WEBP"] else 85,
                optimize=optimize_output,
                K=effective_k,
            )
            prog.progress(0.95)

            status_ph.markdown("<div class='status-msg'>Preparing download...</div>", unsafe_allow_html=True)
            elapsed_seconds = time.perf_counter() - start_time

            metrics = calculate_metrics(
                original_array=pil_to_array(original_image),
                compressed_array=compressed_array,
                original_size_bytes=len(original_bytes),
                compressed_size_bytes=compressed_size,
                elapsed_seconds=elapsed_seconds,
            )
            prog.progress(1.0)

            st.session_state["results"] = {
                "original_image":      original_image,
                "compressed_image":    compressed_image,
                "compressed_bytes":    compressed_bytes,
                "metrics":             metrics,
                "download_filename":   out_filename,
                "was_successful":      was_successful,
                "final_quality":       final_quality,
                "was_resized":         was_resized,
                "effective_k":         effective_k,
                "original_dimensions": original_image.size,
                "compressed_dimensions": compressed_image.size,
            }
            st.session_state["last_run_params"] = {
                "k": k, "max_iters": max_iters,
                "resize_enabled": resize_enabled,
                "max_dimension": max_dimension,
                "output_format": output_format,
                "quality_val": quality_val,
                "optimize_output": optimize_output,
            }

            time.sleep(0.3)
            status_ph.empty()
            prog.empty()

        except Exception as err:
            st.error(f"Processing error: {err}")
            if "status_ph" in locals(): status_ph.empty()
            if "prog"      in locals(): prog.empty()

    # ── Results ───────────────────────────────────────────────────────────────
    results    = st.session_state.get("results")
    last_params = st.session_state.get("last_run_params")

    if not results:
        return

    # Stale-settings notice
    if last_params:
        changed = (
            last_params["k"] != k
            or last_params["max_iters"] != max_iters
            or last_params["resize_enabled"] != resize_enabled
            or (resize_enabled and last_params["max_dimension"] != max_dimension)
            or last_params["output_format"] != output_format
            or (output_format in ["JPEG", "WEBP"] and last_params["quality_val"] != quality_val)
            or last_params["optimize_output"] != optimize_output
        )
        if changed:
            st.info("Settings changed — click **Compress Image** again to update results.")

    metrics      = results["metrics"]
    reduction_pct = metrics["reduction_pct"]
    saved_bytes  = metrics["storage_saved"]

    # ── Alert banners ─────────────────────────────────────────────────────────
    if results["was_successful"]:
        st.success(
            f"Compressed successfully — saved {format_size(saved_bytes)} ({reduction_pct:.1f}% smaller)."
        )
    else:
        st.warning(
            "Could not reduce file size below the original. "
            "Try a lower K, enable resizing, or choose JPEG/WEBP output."
        )

    if results["was_resized"]:
        ow, oh = results["original_dimensions"]
        cw, ch = results["compressed_dimensions"]
        st.info(f"Image resized from {ow}×{oh} to {cw}×{ch} before processing.")

    if has_transparency:
        st.info("Transparency flattened onto white background for colour clustering.")

    if results["effective_k"] < k:
        st.warning(f"K reduced to {results['effective_k']} (image has fewer pixels than requested).")

    # ── Before / After image cards ────────────────────────────────────────────
    st.markdown('<hr class="warm-divider">', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        with st.container(border=True):
            ow, oh = results["original_dimensions"]
            st.markdown(
                f"""
                <div style="text-align:center; margin-bottom:0.6rem;">
                    <span class="img-card-badge original">Original</span><br>
                    <span class="img-card-meta">
                        {ow} × {oh} &nbsp;·&nbsp; {format_size(metrics["original_size"])} &nbsp;·&nbsp; {source_format}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(results["original_image"], use_container_width=True)

    with col_r:
        with st.container(border=True):
            cw, ch = results["compressed_dimensions"]
            st.markdown(
                f"""
                <div style="text-align:center; margin-bottom:0.6rem;">
                    <span class="img-card-badge compressed">Compressed</span><br>
                    <span class="img-card-meta">
                        {cw} × {ch} &nbsp;·&nbsp; {format_size(metrics["compressed_size"])} &nbsp;·&nbsp; {output_format}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(results["compressed_image"], use_container_width=True)

    # ── Metrics pill grid ─────────────────────────────────────────────────────
    st.markdown('<hr class="warm-divider">', unsafe_allow_html=True)
    st.markdown(
        "<h3 style='font-weight:800; font-size:1.15rem; color:#2D1F1A; margin-bottom:0;'>Compression Results</h3>",
        unsafe_allow_html=True,
    )

    orig_size_str  = format_size(metrics["original_size"])
    comp_size_str  = format_size(metrics["compressed_size"])
    reduction_str  = f"{reduction_pct:.1f}%"
    orig_colors_str = f'{metrics["original_colors"]:,}'
    comp_colors_str = f'{metrics["compressed_colors"]:,}'
    time_str       = f'{metrics["elapsed_seconds"]:.2f}s'

    if results["was_successful"]:
        saved_str    = format_size(saved_bytes)
        red_sub      = f"{reduction_pct:.1f}% savings"
        sav_class    = ""
        sav_label    = "Saved"
    else:
        increase_bytes = abs(metrics["original_size"] - metrics["compressed_size"])
        saved_str    = format_size(increase_bytes)
        red_sub      = f"{abs(reduction_pct):.1f}% increase"
        sav_class    = "negative"
        sav_label    = "Increase"

    st.markdown(
        f"""
        <div class="metrics-grid">
            <div class="metric-pill">
                <div class="metric-pill-label">Original Size</div>
                <div class="metric-pill-value">{orig_size_str}</div>
                <div class="metric-pill-sub neutral">Input</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">Compressed</div>
                <div class="metric-pill-value">{comp_size_str}</div>
                <div class="metric-pill-sub neutral">Output</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">Compression</div>
                <div class="metric-pill-value">{reduction_str}</div>
                <div class="metric-pill-sub {sav_class}">{red_sub}</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">Storage Saved</div>
                <div class="metric-pill-value">{saved_str}</div>
                <div class="metric-pill-sub {sav_class}">{sav_label}</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">Time</div>
                <div class="metric-pill-value">{time_str}</div>
                <div class="metric-pill-sub neutral">Duration</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">Colors Before</div>
                <div class="metric-pill-value">{orig_colors_str}</div>
                <div class="metric-pill-sub neutral">Unique</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">Colors After</div>
                <div class="metric-pill-value">{comp_colors_str}</div>
                <div class="metric-pill-sub neutral">K = {results["effective_k"]}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Download ──────────────────────────────────────────────────────────────
    col_dl_l, col_dl_c, col_dl_r = st.columns([1, 2, 1])
    with col_dl_c:
        st.download_button(
            label="Download Compressed Image",
            data=results["compressed_bytes"],
            file_name=results["download_filename"],
            mime=f"image/{output_format.lower()}",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
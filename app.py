import os
from typing import Any

import streamlit as st
from markitdown import MarkItDown, __version__ as markitdown_version

from converter import ConversionResult, build_zip, convert_bytes


MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
PREVIEW_CHAR_LIMIT = int(os.getenv("PREVIEW_CHAR_LIMIT", "50000"))
ENABLE_PLUGINS = os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


st.set_page_config(
    page_title="MarkItDown GUI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container { max-width: 1180px; padding-top: 2.2rem; }
      [data-testid="stFileUploader"] { padding: .35rem 0; }
      .small-muted { color: #687076; font-size: .92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_engine(enable_plugins: bool) -> MarkItDown:
    return MarkItDown(enable_plugins=enable_plugins)


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def reset_results() -> None:
    st.session_state["results"] = []
    st.session_state["errors"] = []


if "results" not in st.session_state:
    reset_results()

with st.sidebar:
    st.header("MarkItDown GUI")
    st.caption(f"Engine: Microsoft MarkItDown {markitdown_version}")
    st.metric("Max file size", f"{MAX_FILE_SIZE_MB} MB")
    st.write(
        "Files are converted from an in-memory upload stream. "
        "This app does not accept arbitrary remote URLs."
    )
    if ENABLE_PLUGINS:
        st.warning(
            "Third-party MarkItDown plugins are enabled by environment configuration."
        )
    st.divider()
    st.caption(
        "Common formats include PDF, DOCX, PPTX, XLSX/XLS, HTML, CSV, JSON, XML, "
        "plain text, images, audio, EPUB, ZIP, IPYNB, and Outlook MSG."
    )

st.title("Turn documents into Markdown")
st.write(
    "A lightweight web interface powered by Microsoft's "
    "[MarkItDown](https://github.com/microsoft/markitdown). "
    "Upload one or more files, preview the converted Markdown, then download the results."
)

uploaded_files = st.file_uploader(
    "Drop files here",
    accept_multiple_files=True,
    help=f"Each file is limited to {MAX_FILE_SIZE_MB} MB by this application.",
)

left, right = st.columns([1, 4])
with left:
    convert_clicked = st.button(
        "Convert files",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files,
    )
with right:
    if uploaded_files:
        total_size = sum(file.size for file in uploaded_files)
        st.markdown(
            f'<div class="small-muted">{len(uploaded_files)} file(s) · '
            f"{human_size(total_size)} selected</div>",
            unsafe_allow_html=True,
        )

if convert_clicked:
    reset_results()
    engine = get_engine(ENABLE_PLUGINS)
    progress = st.progress(0, text="Preparing conversion...")

    for index, uploaded in enumerate(uploaded_files):
        progress.progress(
            index / max(len(uploaded_files), 1),
            text=f"Converting {uploaded.name}...",
        )

        if uploaded.size > MAX_FILE_SIZE_BYTES:
            st.session_state["errors"].append(
                (
                    uploaded.name,
                    f"File is {human_size(uploaded.size)}; limit is {MAX_FILE_SIZE_MB} MB.",
                )
            )
            continue

        try:
            result = convert_bytes(engine, uploaded.name, uploaded.getvalue())
            st.session_state["results"].append(result)
        except Exception as exc:  # MarkItDown exposes multiple format/dependency exceptions.
            st.session_state["errors"].append((uploaded.name, str(exc)))

    progress.progress(1.0, text="Conversion complete.")
    progress.empty()

results: list[ConversionResult] = st.session_state.get("results", [])
errors: list[tuple[str, str]] = st.session_state.get("errors", [])

if errors:
    st.subheader("Could not convert")
    for filename, message in errors:
        st.error(f"**{filename}** — {message}")

if results:
    st.divider()
    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.subheader(f"Converted {len(results)} file(s)")
    with header_right:
        if len(results) > 1:
            st.download_button(
                "Download all (.zip)",
                data=build_zip(results),
                file_name="markitdown-output.zip",
                mime="application/zip",
                use_container_width=True,
            )

    for index, result in enumerate(results):
        label = (
            f"{result.original_name} → {result.output_name} "
            f"({result.elapsed_seconds:.2f}s)"
        )
        with st.expander(label, expanded=index == 0):
            preview = result.markdown[:PREVIEW_CHAR_LIMIT]
            was_truncated = len(result.markdown) > PREVIEW_CHAR_LIMIT

            rendered_tab, source_tab = st.tabs(["Rendered preview", "Markdown source"])
            with rendered_tab:
                st.markdown(preview)
                if was_truncated:
                    st.info(
                        f"Preview truncated after {PREVIEW_CHAR_LIMIT:,} characters. "
                        "The download contains the complete output."
                    )
            with source_tab:
                st.code(preview, language="markdown", wrap_lines=True)
                if was_truncated:
                    st.caption("Source preview is truncated; download contains full Markdown.")

            st.download_button(
                "Download Markdown",
                data=result.markdown.encode("utf-8"),
                file_name=result.output_name,
                mime="text/markdown; charset=utf-8",
                key=f"download-{index}-{result.output_name}",
            )
elif not errors:
    st.info("Upload files and press **Convert files** to begin.")

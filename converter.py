from __future__ import annotations

import io
import mimetypes
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from markitdown import MarkItDown, StreamInfo


class ConverterEngine(Protocol):
    def convert_stream(self, stream, *, stream_info: StreamInfo): ...


@dataclass(frozen=True)
class ConversionResult:
    original_name: str
    output_name: str
    markdown: str
    elapsed_seconds: float


def safe_filename(filename: str) -> str:
    normalized = (filename or "document").replace("\\", "/")
    return Path(normalized).name or "document"


def markdown_filename(filename: str) -> str:
    clean_name = safe_filename(filename)
    stem = Path(clean_name).stem or "document"
    return f"{stem}.md"


def convert_bytes(
    engine: ConverterEngine | MarkItDown,
    filename: str,
    data: bytes,
) -> ConversionResult:
    clean_name = safe_filename(filename)
    extension = Path(clean_name).suffix.lower() or None
    mimetype, _ = mimetypes.guess_type(clean_name)

    stream_info = StreamInfo(
        filename=clean_name,
        extension=extension,
        mimetype=mimetype,
    )

    started = time.perf_counter()
    result = engine.convert_stream(
        io.BytesIO(data),
        stream_info=stream_info,
    )
    elapsed = time.perf_counter() - started

    return ConversionResult(
        original_name=clean_name,
        output_name=markdown_filename(clean_name),
        markdown=result.markdown,
        elapsed_seconds=elapsed,
    )


def build_zip(results: list[ConversionResult]) -> bytes:
    buffer = io.BytesIO()
    used_names: set[str] = set()

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for result in results:
            base = result.output_name
            candidate = base
            counter = 2

            while candidate.lower() in used_names:
                path = Path(base)
                candidate = f"{path.stem}-{counter}{path.suffix}"
                counter += 1

            used_names.add(candidate.lower())
            archive.writestr(candidate, result.markdown.encode("utf-8"))

    return buffer.getvalue()

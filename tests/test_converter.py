from types import SimpleNamespace
import zipfile
import io

from converter import ConversionResult, build_zip, convert_bytes, markdown_filename, safe_filename


class FakeEngine:
    def convert_stream(self, stream, *, stream_info):
        assert stream_info.filename == "notes.txt"
        assert stream_info.extension == ".txt"
        assert stream_info.mimetype == "text/plain"
        return SimpleNamespace(markdown=stream.read().decode("utf-8"))


def test_safe_filename_strips_paths():
    assert safe_filename("../../secret/report.pdf") == "report.pdf"
    assert safe_filename(r"C:\\Users\\demo\\notes.txt") == "notes.txt"


def test_markdown_filename():
    assert markdown_filename("report.final.pdf") == "report.final.md"


def test_convert_bytes_uses_stream_only():
    result = convert_bytes(FakeEngine(), "notes.txt", b"# Hello\n")
    assert result.original_name == "notes.txt"
    assert result.output_name == "notes.md"
    assert result.markdown == "# Hello\n"
    assert result.elapsed_seconds >= 0


def test_build_zip_deduplicates_output_names():
    results = [
        ConversionResult("a/report.pdf", "report.md", "one", 0.1),
        ConversionResult("b/report.docx", "report.md", "two", 0.2),
    ]

    payload = build_zip(results)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert archive.namelist() == ["report.md", "report-2.md"]
        assert archive.read("report.md") == b"one"
        assert archive.read("report-2.md") == b"two"

# MarkItDown GUI

A small, self-hostable web GUI for [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

The upstream MarkItDown project intentionally focuses on the Python library and CLI rather than end-user web applications. This repository keeps the GUI separate and uses the official `markitdown` package as its conversion engine.

## Features

- Drag-and-drop browser UI.
- Multiple file uploads.
- Rendered Markdown preview plus raw Markdown view.
- Download each conversion as `.md`.
- Download batch results as a ZIP.
- In-memory upload processing; no application-level document persistence.
- Uses `convert_stream()` rather than arbitrary URL conversion.
- Docker and Docker Compose support.
- Configurable per-file size limit.
- Optional third-party MarkItDown plugins via environment variable.

Common MarkItDown formats include PDF, DOCX, PPTX, XLSX/XLS, HTML, CSV, JSON, XML, plain text, images, audio, EPUB, ZIP, IPYNB, and Outlook MSG. Actual conversion support depends on the installed MarkItDown version and its optional dependencies.

## Quick start with Docker Compose

~~~bash
git clone https://github.com/yusufbayuw/markitdown-gui.git
cd markitdown-gui
docker compose up --build
~~~

Open:

~~~text
http://localhost:8501
~~~

To stop it:

~~~bash
docker compose down
~~~

## Run locally with Python

Python 3.10-3.14 is supported by MarkItDown 0.1.8. Python 3.13 is used by the Docker image.

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
~~~

On Windows PowerShell:

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
~~~

## Configuration

| Variable | Default | Purpose |
| --- | ---: | --- |
| `MAX_FILE_SIZE_MB` | `50` | Application-level limit for each uploaded file |
| `PREVIEW_CHAR_LIMIT` | `50000` | Maximum characters rendered in each on-screen preview |
| `MARKITDOWN_ENABLE_PLUGINS` | `false` | Load installed third-party MarkItDown plugins |

The Streamlit transport upload limit is set to 200 MB in `.streamlit/config.toml`. Keep the application-level file limit lower unless the server has enough memory.

## Docker without Compose

~~~bash
docker build -t markitdown-gui .
docker run --rm -p 8501:8501 -e MAX_FILE_SIZE_MB=50 markitdown-gui
~~~

## Architecture

~~~text
Browser
  |
  v
Streamlit UI (app.py)
  |
  v
Safe upload adapter (converter.py)
  |
  v
MarkItDown.convert_stream()
  |
  v
Markdown preview / .md download / ZIP
~~~

There is intentionally no database, persistent upload directory, or arbitrary URL-fetch endpoint. This keeps the default deployment small and reduces the attack surface.

## Tests

~~~bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
~~~

GitHub Actions also runs the test suite on pushes and pull requests.

## Production notes

Before exposing the app publicly, put authentication and rate limiting in front of it and enforce container CPU/memory limits. Document conversion libraries parse complex, potentially hostile files; see [SECURITY.md](SECURITY.md).

A typical reverse-proxy setup can route a domain such as `markdown.example.com` to port 8501 while terminating HTTPS at Nginx, Caddy, Traefik, Cloudflare Tunnel, or your hosting platform.

## Relationship to Microsoft MarkItDown

This is an independent GUI project and is not an official Microsoft product. MarkItDown is maintained by Microsoft and is licensed separately under the MIT License. This repository depends on the published MarkItDown package rather than copying its source code.

## License

MIT. See [LICENSE](LICENSE).

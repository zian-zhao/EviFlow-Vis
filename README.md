# EviFlow-Vis: Evidence-Centered Chart Authoring Workbench

EviFlow-Vis is a Django-based prototype for evidence-centered text-to-chart authoring in long-document reporting workflows.
It helps users extract chart-worthy evidence from text, generate editable ECharts visualizations, inspect chart-type recommendations, validate generated values against source evidence, repair layout issues, and export chart-enhanced reports.

The current implementation exposes the main workbench under the `/cs-workbench/` URL prefix.

## Core Features

- Evidence segment extraction from long-form text and common document formats.
- Source-linked chart generation from selected text spans.
- Chart-type recommendation with LLM-assisted reasoning and heuristic fallback.
- Editable ECharts configuration, including chart type switching, JSON editing, and data-level edits.
- Batch chart generation for multiple evidence segments.
- Evidence-aware quality control for unsupported numeric values and layout overlap/clutter.
- Report layout board for assembling generated charts with source excerpts.
- DOCX export for chart-enhanced analytical reports.

## Quick Start

Create and activate a Python environment, then install the required dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Initialize the local SQLite database if needed.

```bash
python manage.py migrate
```

Start the development server.

```bash
python manage.py runserver 0.0.0.0:8000
```

Open the main workbench in a browser.

```text
http://127.0.0.1:8000/cs-workbench/
```

## Main Pages

| Page | URL | Purpose |
| --- | --- | --- |
| Chart authoring workbench | `/cs-workbench/` | Upload or paste text, extract evidence spans, generate and edit charts. |
| Layout board | `/cs-workbench/layout-board/` | Assemble chart cards and source evidence into an exportable report. |
| Django admin | `/admin/` | Default Django admin entry, if enabled and configured. |

## API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/cs-workbench/api/render-chart/` | `POST` | Generate or regenerate chart configurations from text or edited settings. |
| `/cs-workbench/api/chart-type-scores/` | `POST` | Return ranked chart-type recommendations and rationales. |
| `/cs-workbench/api/layout-overlap/` | `POST` | Diagnose chart layout overlap or clutter and optionally apply repairs. |
| `/cs-workbench/api/extract-segments/` | `POST` | Extract candidate chart-worthy text spans from uploaded content. |
| `/cs-workbench/layout-board/export-docx/` | `POST` | Export the assembled report as a DOCX file. |

## Supported Inputs

The evidence extraction endpoint currently accepts the following document types:

- `.txt`
- `.md`
- `.csv`
- `.docx`
- `.pdf`

## Project Structure

```text
.
├── manage.py                  # Django command-line entrypoint
├── requirements.txt           # Python dependencies
├── vizforge/                  # Django settings, URL routing, WSGI/ASGI entrypoints
├── eviflow_vis/               # Main application, views, agents, prompts, and chart logic
├── eviflow_vis/agents/        # Evidence, recommendation, visualization, QC, and report agents
├── templates/viz_lab/         # Workbench and layout-board HTML templates
├── static/                    # Static assets served by Django
├── .env.example               # Optional environment configuration template
└── start.sh                   # Convenience development-server launcher
```

## Configuration

The project reads optional Django-related environment variables from a local `.env` file when `manage.py` runs.
Copy `.env.example` to `.env` if you need to override local defaults.

```bash
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Overrides the Django secret key. Set this for any shared or public deployment. |
| `DJANGO_DEBUG` | Set to `False` or `0` for non-local deployments. Defaults to local development mode. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host allow-list, for example `127.0.0.1,localhost,your.domain`. |
| `DJANGO_ALLOW_ALL_HOSTS` | Set to `1` only when wildcard host access is truly required. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins when using stricter CORS settings. |
| `DEEPSEEK_API_KEY` | API key for the DeepSeek-compatible LLM backend used by chart generation and recommendation. |
| `DEEPSEEK_API_URL` | Chat-completions endpoint. Defaults to `https://api.deepseek.com/v1/chat/completions`. |
| `VIZ_HTTP_PROXY_RECOVERY_CMD` | Optional command used for best-effort proxy recovery after upstream API connection failures. |

LLM credentials are read from environment variables in `eviflow_vis/config.py`.
Keep real API keys in a local `.env` file or deployment secrets, never in source code.

## Runtime Notes

- The default database is SQLite at `db.sqlite3`, generated locally after migration.
- Generated Matplotlib assets are written to `static/viz_matplotlib_exports/` when the legacy image-generation path is used.
- The primary browser workflow uses ECharts on the frontend and returns machine-readable chart options from the backend.
- The Channels/Redis settings are present for a websocket-capable stack, but the main HTTP workbench can be run with Django's development server.

## Development Workflow

Run the development server with:

```bash
python manage.py runserver 0.0.0.0:8000
```

Or use the convenience script:

```bash
bash start.sh
```

If dependencies are missing, reinstall them inside your active environment:

```bash
pip install -r requirements.txt
```

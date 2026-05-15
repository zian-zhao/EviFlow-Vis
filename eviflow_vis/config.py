import os

# DeepSeek-compatible HTTP API (OpenAI-style chat completions).
# Keep real keys in local environment variables or .env, never in source code.
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_API_URL = os.environ.get(
    "DEEPSEEK_API_URL",
    "https://api.deepseek.com/v1/chat/completions",
).strip()

# Default ECharts presentation hints passed into chart prompts.
DEFAULT_CHART_THEME = "default"
CHART_ANIMATION_DURATION = 1000
CHART_ANIMATION_EASING = "cubicInOut"

# Dataset size / string guards for chart prompts.
MAX_DATA_POINTS = 1000
MIN_DATA_POINTS = 2
MAX_STRING_LENGTH = 100

# Matplotlib scratch PNGs (relative to process cwd, usually repo root).
MATPLOTLIB_EXPORT_REL_PATH = "static/viz_matplotlib_exports"

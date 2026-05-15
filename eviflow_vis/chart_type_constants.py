"""Canonical chart type codes for the generation pipeline (single + combo)."""
from __future__ import annotations

from typing import Optional

# Types the backend may select or accept as client override.
PIPELINE_CHART_TYPES = frozenset(
    {"line", "bar", "scatter", "pie", "radar", "funnel", "tree", "gantt", "combo"}
)

_ZH_TO_CODE = {
    "折线图": "line",
    "柱状图": "bar",
    "条形图": "bar",
    "散点图": "scatter",
    "饼图": "pie",
    "雷达图": "radar",
    "漏斗图": "funnel",
    "树形图": "tree",
    "甘特图": "gantt",
    "组合图": "combo",
    "复合图": "combo",
    "混合图": "combo",
}


def normalize_chart_type_code(raw: Optional[str]) -> str:
    """
    Map LLM / UI / Chinese labels to a canonical code in PIPELINE_CHART_TYPES.
    Returns "" if unknown (caller should fall back to automatic selection).
    """
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if s in _ZH_TO_CODE:
        return _ZH_TO_CODE[s]
    tl = s.lower().replace(" ", "").replace("_", "-")
    if any(k in tl for k in ("combo", "mixed", "composite", "combination", "dual-axis", "dualaxis")):
        return "combo"
    if any(z in s for z in ("复合", "组合", "混合")):
        return "combo"
    if tl in PIPELINE_CHART_TYPES:
        return tl
    return ""

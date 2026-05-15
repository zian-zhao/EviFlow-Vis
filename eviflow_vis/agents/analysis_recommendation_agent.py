import re
from typing import Any, Dict, Tuple

from eviflow_vis.chart_type_constants import normalize_chart_type_code

from .data_analysis_agent import DataAnalysisAgent
from .logger import Logger

NUMERIC_EVIDENCE_PATTERN = re.compile(
    r"(?:(?:\$|€|£|¥)\s*)?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:%|[kKmMbB]|万|亿)?|-?\d+(?:\.\d+)?%"
)


class AnalysisRecommendationAgent:
    """Analyze evidence text and stabilize chart-type recommendation."""

    def __init__(self):
        self.logger = Logger("AnalysisRecommendationAgent")
        self.data_analysis_agent = DataAnalysisAgent()

    def analyze(self, description: str) -> Dict[str, Any]:
        self.logger.log_interaction("开始数据语义分析", "start")
        analysis_result = self.data_analysis_agent.analyze_data(description)
        if analysis_result.get("status") == "error":
            self.logger.log_interaction("数据语义分析失败", "error", analysis_result)
            return analysis_result
        self.logger.log_interaction(
            "完成数据语义分析",
            "complete",
            {"chart_type": analysis_result.get("chart_type")},
        )
        return analysis_result

    def choose_chart_type(self, description: str, llm_type: str) -> Tuple[str, Dict[str, float]]:
        scores = self._infer_chart_type_scores(description)
        llm_code = normalize_chart_type_code(llm_type or "")
        if llm_code in scores:
            scores[llm_code] += 12
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        if ranked:
            top = ranked[0][0]
        else:
            top = llm_code if llm_code else "bar"
        return (top, dict(ranked))

    def _infer_chart_type_scores(self, description: str) -> Dict[str, float]:
        text = description or ""
        lower = text.lower()
        numeric_count = len(NUMERIC_EVIDENCE_PATTERN.findall(text))
        has_time = bool(
            re.search(r"\b(q[1-4]|week\s*\d+|month|year|daily|weekly|monthly|quarter|timeline)\b", lower)
            or re.search(r"(月|周|年|季度|时间线|趋势)", text)
        )
        has_compare = bool(
            re.search(r"\b(compare|versus|rank|higher|lower|top|bottom)\b", lower)
            or re.search(r"(对比|比较|排名|高于|低于|最多|最少)", text)
        )
        has_share = bool(
            re.search(r"\b(share|ratio|proportion|percentage|percent)\b", lower)
            or re.search(r"(占比|比例|构成|份额|百分比)", text)
        )
        has_relation = bool(
            re.search(r"\b(correlation|relationship|association)\b", lower)
            or re.search(r"(相关|关系|关联)", text)
        )

        scores = {
            "line": 0.0,
            "bar": 0.0,
            "scatter": 0.0,
            "pie": 0.0,
            "radar": 0.0,
            "funnel": 0.0,
            "tree": 0.0,
            "gantt": 0.0,
            "combo": 0.0,
        }
        if has_time:
            scores["line"] += 30
            scores["bar"] += 10
        if has_compare:
            scores["bar"] += 28
            scores["line"] += 12
        if has_share:
            scores["pie"] += 26
            scores["bar"] += 12
        if has_relation:
            scores["scatter"] += 24
        if numeric_count >= 3:
            scores["bar"] += 14
            scores["line"] += 14
        elif numeric_count <= 1:
            scores["tree"] += 8
            scores["radar"] += 6
        # Composite chart: trend + comparison + several numbers (typical ops report).
        if has_time and has_compare:
            scores["combo"] += 26
        if numeric_count >= 4 and (has_time or has_compare):
            scores["combo"] += 10
        scores["bar"] += 4
        scores["line"] += 4
        return scores

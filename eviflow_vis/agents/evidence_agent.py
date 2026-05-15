from typing import Any, Dict

from .logger import Logger
from .text_chart_agent import TextChartAgent


class EvidenceAgent:
    """Evidence-oriented wrapper around text segment extraction."""

    def __init__(self):
        self.logger = Logger("EvidenceAgent")
        self.text_chart_agent = TextChartAgent()

    def extract_segments(self, text: str, profile: str = "balanced") -> Dict[str, Any]:
        """Extract chartable evidence spans from source text."""
        self.logger.log_interaction("开始证据片段抽取", "start", {"profile": profile})
        result = self.text_chart_agent.extract_segments(text or "", profile=profile)
        segments = result.get("segments", []) if isinstance(result, dict) else []
        self.logger.log_interaction(
            "完成证据片段抽取",
            "complete",
            {"profile": profile, "segments_count": len(segments)},
        )
        return {"segments": segments}

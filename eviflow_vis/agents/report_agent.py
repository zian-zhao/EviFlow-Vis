from typing import Any, Dict, List

from .logger import Logger


class ReportAgent:
    """
    Lightweight export-oriented helper.
    Kept intentionally simple to avoid changing current export behavior.
    """

    def __init__(self):
        self.logger = Logger("ReportAgent")

    def build_layout_payload(
        self,
        uploaded_text: str,
        segments: List[Dict[str, Any]],
        charts: List[Dict[str, Any]],
        manual_layout_parts: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "uploadedText": uploaded_text,
            "extractedSegments": segments,
            "charts": charts,
            "manualLayoutParts": manual_layout_parts or [],
        }
        self.logger.log_interaction(
            "构建报告布局载荷",
            "complete",
            {"segments_count": len(segments), "charts_count": len(charts)},
        )
        return payload

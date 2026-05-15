from typing import Any, Callable, Dict, Optional

from openai import APIConnectionError, AuthenticationError, RateLimitError

from eviflow_vis.chart_type_constants import PIPELINE_CHART_TYPES, normalize_chart_type_code

from .analysis_recommendation_agent import AnalysisRecommendationAgent
from .base_agent import BaseAgent
from .evidence_agent import EvidenceAgent
from .graph_agent import GraphAgent
from .image_agent import ImageAgent
from .logger import agent_logger
from .quality_control_agent import QualityControlAgent
from .visualization_agent import VisualizationAgent


class MasterAgent(BaseAgent):
    """
    Lightweight orchestrator:
    - keeps current behavior stable
    - exposes explicit multi-agent coordination entrypoints for views
    """

    def __init__(self):
        super().__init__()
        self.image_agent = ImageAgent()
        # Legacy compatibility path. Main web flow does not depend on this branch.
        self.graph_agent = GraphAgent()
        self.evidence_agent = EvidenceAgent()
        self.analysis_recommendation_agent = AnalysisRecommendationAgent()
        self.visualization_agent = VisualizationAgent()
        self.quality_control_agent = QualityControlAgent()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward-compatible async entry for legacy task dispatch."""
        try:
            self.update_status("processing")
            task_type = data.get("type", "")
            description = data.get("description", "")
            agent_logger.log_interaction(
                source_agent="user",
                target_agent="master",
                action="request_received",
                data={"task_type": task_type, "description": description},
            )

            if task_type == "image":
                result = await self.image_agent.process({"description": description})
            elif task_type == "graph":
                result = await self.graph_agent.process({"description": description})
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            agent_logger.log_interaction(
                source_agent="master",
                target_agent="user",
                action="task_completed",
                data={"result": result},
            )
            self.update_status("completed")
            return result
        except Exception as e:
            agent_logger.log_interaction(
                source_agent="master",
                target_agent="system",
                action="error_occurred",
                data={"error": str(e)},
                status="error",
            )
            return await self.handle_error(e)

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Unified error shape for API-level reliability."""
        error_response = {
            "error": True,
            "message": str(error),
            "type": error.__class__.__name__,
        }
        if isinstance(error, APIConnectionError):
            error_response["message"] = "API连接错误，请稍后重试"
        elif isinstance(error, RateLimitError):
            error_response["message"] = "API调用次数超限，请稍后重试"
        elif isinstance(error, AuthenticationError):
            error_response["message"] = "API认证错误，请检查配置"
        self.update_status("error")
        return error_response

    def orchestrate_segment_extraction(self, content: str, profile: str = "balanced") -> Dict[str, Any]:
        """EvidenceAgent wrapper used by text extraction endpoint."""
        self.update_status("processing")
        result = self.evidence_agent.extract_segments(content, profile=profile)
        self.update_status("completed")
        return result

    def orchestrate_graph_generation(
        self,
        description: str,
        language: str,
        generate_chart_config_fn: Callable[[str, str, Dict[str, Any], str], Dict[str, Any]],
        enforce_chart_type_consistency_fn: Callable[[Dict[str, Any], str], Dict[str, Any]],
        sanitize_chart_config_by_evidence_fn: Callable[[Dict[str, Any], str], Any],
        chart_type_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main chart workflow with minimal behavior changes:
        analysis -> type selection -> config generation -> evidence gate -> layout QC.
        """
        self.update_status("processing")

        analysis_result = self.analysis_recommendation_agent.analyze(description)
        if analysis_result.get("status") == "error":
            self.update_status("error")
            return {"error": analysis_result.get("error", "数据分析失败")}

        override_code = normalize_chart_type_code(chart_type_override or "")
        if override_code in PIPELINE_CHART_TYPES:
            selected_chart_type = override_code
            _, type_scores = self.analysis_recommendation_agent.choose_chart_type(
                description, analysis_result.get("chart_type")
            )
        else:
            selected_chart_type, type_scores = self.analysis_recommendation_agent.choose_chart_type(
                description, analysis_result.get("chart_type")
            )

        chart_config = self.visualization_agent.generate_chart_config(
            description,
            selected_chart_type,
            analysis_result["analysis_result"],
            language,
            generate_chart_config_fn,
        )
        if not chart_config:
            self.update_status("error")
            return {"error": "图表配置生成失败"}

        chart_config = enforce_chart_type_consistency_fn(chart_config, selected_chart_type)

        chart_config, evidence_report = sanitize_chart_config_by_evidence_fn(chart_config, description)
        if evidence_report.get("source_numeric_count", 0) >= 2:
            total_points = evidence_report.get("total_numeric_points", 0)
            kept_points = evidence_report.get("kept_numeric_points", 0)
            drop_ratio = evidence_report.get("drop_ratio", 0.0)
            if total_points > 0 and (kept_points == 0 or drop_ratio >= 0.65):
                self.update_status("error")
                return {
                    "error": (
                        "Evidence check failed: chart data is not supported by the source text. "
                        "Please provide more explicit numeric values."
                    )
                }

        try:
            layout_result = self.quality_control_agent.check_layout_overlaps_sync(chart_config, description)
            if layout_result.get("has_overlaps", False):
                fix_result = self.quality_control_agent.auto_fix_overlaps_sync(
                    chart_config, layout_result.get("issues", [])
                )
                chart_config = fix_result["fixed_config"]
                layout_analysis = {
                    "issues_detected": layout_result.get("issues", []),
                    "fixes_applied": fix_result["fixes_applied"],
                    "overlap_score": layout_result.get("overlap_score", 0),
                    "suggestions": layout_result.get("suggestions", []),
                }
            else:
                layout_analysis = {
                    "issues_detected": [],
                    "fixes_applied": [],
                    "overlap_score": 0,
                    "suggestions": ["布局检测通过，无需修复"],
                }
        except Exception:
            layout_analysis = {
                "issues_detected": [],
                "fixes_applied": [],
                "overlap_score": 0,
                "suggestions": ["布局检测过程中出现错误，使用原始配置"],
            }

        self.update_status("completed")
        return {
            "error": False,
            "chart_config": chart_config,
            "chart_type": selected_chart_type,
            "analysis": analysis_result["analysis_result"],
            "layout_analysis": layout_analysis,
            "evidence_report": evidence_report,
            "chart_type_scores": type_scores,
        }

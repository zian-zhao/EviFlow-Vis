from typing import Any, Callable, Dict

from .logger import Logger


class VisualizationAgent:
    """
    Dedicated visualization agent for chart-option generation.
    It intentionally wraps existing generation logic to keep behavior stable.
    """

    def __init__(self):
        self.logger = Logger("VisualizationAgent")

    def generate_chart_config(
        self,
        description: str,
        chart_type: str,
        analysis_result: Dict[str, Any],
        language: str,
        generate_chart_config_fn: Callable[[str, str, Dict[str, Any], str], Dict[str, Any]],
    ) -> Dict[str, Any]:
        self.logger.log_interaction(
            "开始可视化配置生成",
            "start",
            {"chart_type": chart_type, "language": language},
        )
        chart_config = generate_chart_config_fn(
            description,
            chart_type,
            analysis_result,
            language=language,
        )
        if not chart_config:
            self.logger.log_interaction("可视化配置生成失败", "error")
            return {}
        self.logger.log_interaction("完成可视化配置生成", "complete")
        return chart_config

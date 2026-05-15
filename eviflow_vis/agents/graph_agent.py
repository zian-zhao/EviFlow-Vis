from typing import Any, Dict
from .base_agent import BaseAgent
from eviflow_vis import echarts_llm_gateway as llm_viz_bridge
import subprocess
from openai import APIConnectionError, RateLimitError, AuthenticationError
import binascii
from .logger import agent_logger
from .logger import AgentLogger

class DataAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            description = data.get('description', '')
            if not description:
                return {"error": "No description provided"}

            agent_logger.log_interaction(
                source_agent="DataAnalysisAgent",
                target_agent="System",
                action="开始数据分析",
                data={"description": description}
            )

            analysis_result = llm_viz_bridge.extract_structured_data_profile(user_brief=description)
            
            agent_logger.log_interaction(
                source_agent="DataAnalysisAgent",
                target_agent="System",
                action="完成数据分析",
                data={"analysis_result": analysis_result}
            )

            return {
                "error": False,
                "analysis_result": analysis_result
            }
        except Exception as e:
            error_result = await self.handle_error(e)
            agent_logger.log_interaction(
                source_agent="DataAnalysisAgent",
                target_agent="System",
                action="数据分析失败",
                data={"error": str(e)}
            )
            return error_result

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误"""
        error_response = {
            "error": True,
            "message": str(error),
            "type": error.__class__.__name__
        }
        self.update_status("error")
        return error_response

class VisualizationAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            description = data.get('description', '')
            analysis_result = data.get('analysis_result', {})
            if not description:
                return {"error": "No description provided"}

            agent_logger.log_interaction(
                source_agent="VisualizationAgent",
                target_agent="System",
                action="开始图表设计",
                data={"description": description, "analysis_result": analysis_result}
            )

            script = llm_viz_bridge.synthesize_echarts_init_block(user_brief=description)
            
            agent_logger.log_interaction(
                source_agent="VisualizationAgent",
                target_agent="System",
                action="完成图表设计",
                data={"script": script[:100] + "..."}
            )

            return {
                "error": False,
                "script": script
            }
        except Exception as e:
            error_result = await self.handle_error(e)
            agent_logger.log_interaction(
                source_agent="VisualizationAgent",
                target_agent="System",
                action="图表设计失败",
                data={"error": str(e)}
            )
            return error_result

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误"""
        error_response = {
            "error": True,
            "message": str(error),
            "type": error.__class__.__name__
        }
        self.update_status("error")
        return error_response

class QualityControlAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            description = data.get('description', '')
            analysis_result = data.get('analysis_result', {})
            design_result = data.get('design_result', {})
            if not description or not design_result:
                return {"error": "Missing required data"}

            agent_logger.log_interaction(
                source_agent="QualityControlAgent",
                target_agent="System",
                action="开始质量检查",
                data={"description": description, "analysis_result": analysis_result, "design_result": design_result}
            )

            script = design_result.get('script', '')
            optimized_script = llm_viz_bridge.polish_echarts_init_block(
                user_brief=description, existing_script=script
            )
            
            agent_logger.log_interaction(
                source_agent="QualityControlAgent",
                target_agent="System",
                action="完成质量检查",
                data={"optimized_script": optimized_script[:100] + "..."}
            )

            return {
                "error": False,
                "script": optimized_script
            }
        except Exception as e:
            error_result = await self.handle_error(e)
            agent_logger.log_interaction(
                source_agent="QualityControlAgent",
                target_agent="System",
                action="质量检查失败",
                data={"error": str(e)}
            )
            return error_result

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误"""
        error_response = {
            "error": True,
            "message": str(error),
            "type": error.__class__.__name__
        }
        self.update_status("error")
        return error_response

class GraphAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.data_analysis_agent = DataAnalysisAgent()
        self.visualization_agent = VisualizationAgent()
        self.quality_control_agent = QualityControlAgent()
        self.cache = {}

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            description = data.get('description', '')
            if not description:
                return {"error": "No description provided"}

            # 记录GraphAgent开始处理
            agent_logger.log_interaction(
                source_agent="GraphAgent",
                target_agent="User",
                action="开始处理图表生成请求",
                data={"description": description}
            )

            # 1. 数据分析阶段
            agent_logger.log_interaction(
                source_agent="GraphAgent",
                target_agent="DataAnalysisAgent",
                action="请求数据分析",
                data={"description": description}
            )
            analysis_result = await self.data_analysis_agent.process({"description": description})
            agent_logger.log_interaction(
                source_agent="DataAnalysisAgent",
                target_agent="GraphAgent",
                action="返回数据分析结果",
                data={"analysis_result": analysis_result}
            )

            # 2. 可视化设计阶段
            agent_logger.log_interaction(
                source_agent="GraphAgent",
                target_agent="VisualizationAgent",
                action="请求图表设计",
                data={"description": description, "analysis_result": analysis_result}
            )
            design_result = await self.visualization_agent.process({
                "description": description,
                "analysis_result": analysis_result
            })
            agent_logger.log_interaction(
                source_agent="VisualizationAgent",
                target_agent="GraphAgent",
                action="返回图表设计结果",
                data={"design_result": design_result}
            )

            # 3. 质量控制阶段
            agent_logger.log_interaction(
                source_agent="GraphAgent",
                target_agent="QualityControlAgent",
                action="请求质量检查",
                data={"description": description, "analysis_result": analysis_result, "design_result": design_result}
            )
            quality_result = await self.quality_control_agent.process({
                "description": description,
                "analysis_result": analysis_result,
                "design_result": design_result
            })
            agent_logger.log_interaction(
                source_agent="QualityControlAgent",
                target_agent="GraphAgent",
                action="返回质量检查结果",
                data={"quality_result": quality_result}
            )

            # 记录最终结果
            agent_logger.log_interaction(
                source_agent="GraphAgent",
                target_agent="User",
                action="完成图表生成",
                data={"final_result": quality_result}
            )

            return quality_result

        except Exception as e:
            error_result = await self.handle_error(e)
            agent_logger.log_interaction(
                source_agent="GraphAgent",
                target_agent="User",
                action="处理失败",
                data={"error": str(e)}
            )
            return error_result

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误"""
        error_message = str(error)
        if isinstance(error, APIConnectionError):
            error_message = "API连接错误，请检查网络连接"
        elif isinstance(error, RateLimitError):
            error_message = "API请求频率超限，请稍后重试"
        elif isinstance(error, AuthenticationError):
            error_message = "API认证失败，请检查API密钥"

        agent_logger.log_interaction(
            source_agent="GraphAgent",
            target_agent="System",
            action="error",
            data={"error": error_message}
        )

        self.update_status("error")
        return {
            "error": True,
            "message": error_message
        }

    def clear_cache(self):
        """清除缓存"""
        self.cache = {} 
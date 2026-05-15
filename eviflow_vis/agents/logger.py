import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

class Logger:
    def __init__(self, name: str):
        self.name = name
        self.logs: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def log_interaction(self, 
                       message: str,
                       status: str,
                       data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """记录交互日志"""
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time": round(time.time() - self.start_time, 2),
            "agent": self.name,
            "message": message,
            "status": status,
            "data": data or {}
        }
        self.logs.append(log_entry)
        return log_entry

    def get_logs(self) -> List[Dict[str, Any]]:
        """获取所有日志"""
        return self.logs

    def clear_logs(self):
        """清除所有日志"""
        self.logs = []
        self.start_time = time.time()

class AgentLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLogger, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.start_time = time.time()
            cls._instance.action_descriptions = {
                'request_received': '收到新的请求',
                'task_assigned': '分配任务',
                'task_started': '开始任务',
                'task_completed': '完成任务',
                'error_occurred': '发生错误',
                'status_check': '检查状态',
                'analysis_started': '开始数据分析',
                'analysis_completed': '完成数据分析',
                'design_started': '开始可视化设计',
                'design_completed': '完成可视化设计',
                'quality_check_started': '开始质量控制',
                'quality_check_completed': '完成质量控制'
            }
            cls._instance.agent_names = {
                'master': '主控智能体',
                'image': '图像智能体',
                'graph': '图表智能体',
                'data_analysis': '数据分析智能体',
                'visualization': '可视化设计智能体',
                'quality_control': '质量控制智能体',
                'user': '用户',
                'system': '系统'
            }
        return cls._instance

    def log_interaction(self, 
                       source_agent: str,
                       target_agent: str,
                       action: str,
                       data: Dict[str, Any],
                       status: str = "success"):
        """记录智能体之间的交互"""
        # 转换动作描述
        action_desc = self.action_descriptions.get(action, action)
        
        # 转换智能体名称
        source_name = self.agent_names.get(source_agent.lower(), source_agent)
        target_name = self.agent_names.get(target_agent.lower(), target_agent)
        
        # 转换状态描述
        status_desc = "成功" if status == "success" else "失败"

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time": round(time.time() - self.start_time, 2),
            "source_agent": source_name,
            "target_agent": target_name,
            "action": action_desc,
            "data": data,
            "status": status_desc
        }
        self.logs.append(log_entry)
        return log_entry

    def get_logs(self) -> list:
        """获取所有日志"""
        return self.logs

    def clear_logs(self):
        """清除所有日志"""
        self.logs = []
        self.start_time = time.time()

# 创建全局日志记录器实例
agent_logger = AgentLogger() 
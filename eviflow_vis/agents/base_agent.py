from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        self.status = "idle"
        self.error_count = 0
        self.max_retries = 3

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务的主要方法"""
        pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误的方法"""
        pass

    def update_status(self, status: str):
        """更新智能体状态"""
        self.status = status

    def reset_error_count(self):
        """重置错误计数"""
        self.error_count = 0

    def increment_error_count(self):
        """增加错误计数"""
        self.error_count += 1
        return self.error_count >= self.max_retries 
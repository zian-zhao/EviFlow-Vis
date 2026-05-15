from typing import Any, Dict
from .base_agent import BaseAgent
from eviflow_vis import echarts_llm_gateway as llm_viz_bridge
from eviflow_vis.config import MATPLOTLIB_EXPORT_REL_PATH
from eviflow_vis.proxy_recovery import run_proxy_recovery_after_proxy_error
from openai import APIConnectionError, RateLimitError, AuthenticationError

class ImageAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.cache = {}  # naive in-memory memo keyed by prompt text

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run matplotlib synthesis for a natural-language brief."""
        try:
            self.update_status("processing")
            description = data.get("description", "")

            if description in self.cache:
                return self.cache[description]

            filename = llm_viz_bridge.synthesize_matplotlib_asset(user_prompt=description)
            image_path = f'{MATPLOTLIB_EXPORT_REL_PATH}/{filename}.png'

            self.cache[description] = {
                "image_path": image_path,
                "error": ""
            }

            self.update_status("completed")
            return self.cache[description]

        except Exception as e:
            return await self.handle_error(e)

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Normalize errors for the async agent façade."""
        error_response = {
            "error": True,
            "message": str(error),
            "type": error.__class__.__name__
        }

        if isinstance(error, APIConnectionError):
            if str(error).find("Caused by ProxyError") >= 0:
                run_proxy_recovery_after_proxy_error()
                error_response["message"] = "Proxy recovery attempted; retry the request."
            else:
                error_response["message"] = "Upstream API connection error; retry later."
        elif isinstance(error, RateLimitError):
            error_response["message"] = "Rate limit exceeded; retry later."
        elif isinstance(error, AuthenticationError):
            error_response["message"] = "Authentication failed; check API keys in settings."
        else:
            error_response["message"] = "Generation failed; try a different prompt."

        self.update_status("error")
        return error_response

    def clear_cache(self):
        """Drop memoized matplotlib outputs."""
        self.cache.clear()

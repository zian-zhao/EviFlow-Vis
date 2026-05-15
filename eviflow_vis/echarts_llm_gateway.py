"""
LLM bridge for legacy matplotlib art + optional ECharts script helpers.

Prompts and entrypoint names are intentionally distinct from earlier demo projects.
"""
from __future__ import annotations

import json
import re
import uuid

from langchain.chat_models import ChatOpenAI
from langchain.globals import set_verbose
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from eviflow_vis.config import DEEPSEEK_API_KEY, MATPLOTLIB_EXPORT_REL_PATH

set_verbose(True)

_DEEPSEEK_BASE = "https://api.deepseek.com/v1"
_DEFAULT_MODEL = "deepseek-chat"


def _uuid_asset_stem() -> str:
    return str(uuid.uuid1())


def _openai_compatible_client(api_key: str | None) -> ChatOpenAI:
    key = api_key or DEEPSEEK_API_KEY
    return ChatOpenAI(
        model=_DEFAULT_MODEL,
        openai_api_key=key,
        temperature=0.0,
        request_timeout=120,
        max_retries=1,
        base_url=_DEEPSEEK_BASE,
    )


def synthesize_matplotlib_asset(user_prompt: str, api_key: str | None = None) -> str:
    """
    Ask the model for a single matplotlib script (no def), executed via exec after extraction.
    Saves under MATPLOTLIB_EXPORT_REL_PATH/<stem>.png — stem is returned.
    """
    system = (
        "You are a matplotlib technician. Produce ONE Python script for Linux, matplotlib only. "
        "Hard rules: never define functions (no def, no lambda assignments). "
        "Return exactly one Markdown fenced block ```python ... ``` and nothing outside it. "
        "Never call plt.show(). If you use pyplot, end with plt.clf() after saving."
    )
    human = "{payload}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    def _run_extracted_code(raw: str):
        print(raw)
        blocks = re.findall(r"```python(.*)```", raw, re.M | re.S)
        code = blocks[0] if blocks else raw
        code = code.replace("plt.show()", "")
        if "plt." in code:
            code += "\nplt.clf()"
        print(code)
        return exec(code)

    stem = _uuid_asset_stem()
    payload = (
        user_prompt
        + f' — Save the figure exactly to path "{MATPLOTLIB_EXPORT_REL_PATH}/{stem}.png" (create dirs if needed).'
    )
    chain = prompt | _openai_compatible_client(api_key) | StrOutputParser() | _run_extracted_code
    chain.invoke({"payload": payload})
    print("matplotlib pipeline finished")
    return stem


def synthesize_echarts_init_block(user_brief: str, api_key: str | None = None) -> str:
    """
    Returns raw JS that configures ECharts on the DOM node whose id is 'chart'.
    """
    system = (
        "You emit browser-side JavaScript that builds an Apache ECharts chart. "
        "Assume `echarts` is already loaded. Target container id must be exactly: chart "
        "(use echarts.init(document.getElementById('chart'))). "
        "Output a single ```javascript ... ``` fence; no prose outside the fence."
    )
    human = "User brief:\n{payload}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    def _strip_fence(raw: str) -> str:
        blocks = re.findall(r"```(?:javascript|js)?(.*)```", raw, re.M | re.S)
        return blocks[0].strip() if blocks else raw.strip()

    chain = prompt | _openai_compatible_client(api_key) | StrOutputParser() | _strip_fence
    out = chain.invoke({"payload": user_brief})
    print("ECharts block generated (truncated log)")
    return out


def extract_structured_data_profile(user_brief: str, api_key: str | None = None) -> dict:
    """Lightweight structured profile used by exploratory agents."""
    system = (
        "Read the user's quantitative description. Reply with strict JSON only (no markdown) "
        "matching this schema keys: data_type (string), dimensions (array of strings), "
        "ranges (object mapping dimension to [min,max]), relationships (array of strings), "
        "visualization_suggestions (array of strings)."
    )
    human = "{payload}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    def _parse_json(raw: str) -> dict:
        try:
            fenced = re.findall(r"```(?:json)?(.*)```", raw, re.M | re.S)
            blob = fenced[0] if fenced else raw
            return json.loads(blob)
        except Exception:
            return {
                "data_type": "unknown",
                "dimensions": [],
                "ranges": {},
                "relationships": [],
                "visualization_suggestions": [],
            }

    chain = prompt | _openai_compatible_client(api_key) | StrOutputParser() | _parse_json
    return chain.invoke({"payload": user_brief})


def polish_echarts_init_block(user_brief: str, existing_script: str, api_key: str | None = None) -> str:
    """Style / readability pass on an existing ECharts init snippet."""
    system = (
        "Improve the supplied ECharts JavaScript for clarity, labels, and responsive layout. "
        "Keep the same container id `chart`. Return only ```javascript ... ``` fenced code."
    )
    human = "Requirements:\n{user_brief}\n\nCurrent script:\n{existing_script}\n"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    def _strip_fence(raw: str) -> str:
        blocks = re.findall(r"```(?:javascript|js)?(.*)```", raw, re.M | re.S)
        return blocks[0].strip() if blocks else raw.strip()

    chain = prompt | _openai_compatible_client(api_key) | StrOutputParser() | _strip_fence
    return chain.invoke({"user_brief": user_brief, "existing_script": existing_script})

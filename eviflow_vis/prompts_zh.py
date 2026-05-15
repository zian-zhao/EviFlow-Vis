"""Large Chinese LLM prompt bodies (kept out of ``views.py`` for readability)."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def analyze_data_description_user_zh(
    description: str,
    theme: str,
    anim_ms: int,
    easing: str,
    min_points: int,
    max_points: int,
    max_str_len: int,
) -> str:
    return f"""请分析以下数据描述，并生成适合的图表类型和数据结构。
数据描述：{description}

请以JSON格式返回以下信息：
1. chart_type: 推荐的图表类型（line, bar, scatter, pie, radar, funnel, tree, gantt）
2. data_structure: 适合的数据结构
3. chart_config: 完整的ECharts配置，包括以下要求：
   - 使用主题：{theme}
   - 动画持续时间：{anim_ms}ms
   - 动画缓动效果：{easing}
   - 数据点数量限制：{min_points}到{max_points}
   - 字符串长度限制：{max_str_len}
4. title: 图表标题
5. description: 图表说明

请确保返回的是有效的JSON格式。"""


def analyze_data_description_system_zh() -> str:
    return "你是一个专业的数据可视化专家，擅长分析数据并生成合适的图表配置。"


def generate_chart_config_user_zh(
    description: str,
    chart_type: str,
    analysis_result: Dict[str, Any],
    theme: str,
    anim_ms: int,
    easing: str,
    min_points: int,
    max_points: int,
    max_str_len: int,
    is_combo: bool,
    combo_rules_zh: str,
    single_type_rule_zh: str,
) -> str:
    tail = (
        combo_rules_zh
        if is_combo
        else single_type_rule_zh + "\n- 尽可能充分利用原文中的有效数值，不要无故丢点"
    )
    analysis_blob = json.dumps(analysis_result, ensure_ascii=False)
    return f"""请根据以下信息生成ECharts图表配置：

数据描述：{description}
图表类型：{chart_type}
分析结果：{analysis_blob}

请生成完整的ECharts配置，包括：
1. 标题和副标题
2. 坐标轴配置（如果需要）
3. 数据系列配置
4. 图例配置
5. 提示框配置
6. 主题和样式配置

要求：
- 使用主题：{theme}
- 动画持续时间：{anim_ms}ms
- 动画缓动效果：{easing}
- 数据点数量限制：{min_points}到{max_points}
- 字符串长度限制：{max_str_len}
- 零幻觉要求：不得编造、补全、外推原文未出现的数值
- 若原文缺失某值，请省略该数据点或设为null，不得猜测
- 仅保留可由原文直接支撑的数据值
{tail}

请确保返回的是有效的JSON格式的ECharts配置。"""


def generate_chart_config_system_zh() -> str:
    return "你是一个专业的数据可视化专家，擅长生成优化的ECharts配置。"


def generate_chart_config_fix_system_zh() -> str:
    return "你是一个专业的数据可视化专家，只能输出JSON。"


def chart_type_recommendation_user_zh(description: str, backend_analysis: Dict[str, Any]) -> str:
    blob = json.dumps(backend_analysis, ensure_ascii=False)
    return f"""请分析以下数据描述，并推荐最适合的图表类型。

数据描述：{description}

后端分析结果：{blob}

请考虑以下因素：
1. 数据的特点和目的
2. 需要展示的关系类型
3. 数据的维度
4. 目标受众的需求
5. 数据可视化的最佳实践

请以JSON格式返回以下信息：
{{
    "recommendations": [
        {{
            "type": "图表类型代码",
            "name": "图表类型中文名称",
            "confidence": 置信度百分比(0-100),
            "reason": "推荐理由",
            "matched_keywords": ["匹配的关键词1", "关键词2"],
            "suitability_score": 适用性评分(0-100)
        }},
        // ... 最多4个推荐
    ],
    "analysis_summary": {{
        "data_characteristics": "数据特征描述",
        "visualization_goals": "可视化目标",
        "recommended_approach": "推荐的可视化方法"
    }}
}}

可选的图表类型代码：
- line: 折线图（适合展示趋势和变化）
- bar: 柱状图（适合比较和排名）
- scatter: 散点图（适合展示相关性）
- pie: 饼图（适合展示占比）
- radar: 雷达图（适合多维度对比）
- funnel: 漏斗图（适合展示转化流程）
- tree: 树形图（适合展示层级关系）
- gantt: 甘特图（适合展示时间进度）
- area: 面积图（适合展示累积数据）
- heatmap: 热力图（适合展示密度分布）
- bubble: 气泡图（适合展示三维数据）
- candlestick: K线图（适合展示金融数据）
- combo: 复合图（同一坐标系内多种 series.type，如柱+折线，可双 Y 轴）

重要要求：
1. 置信度必须基于数据特征和用户需求的真实匹配程度
2. 所有推荐的置信度总和必须等于100%
3. 推荐理由要具体且专业，基于实际分析
4. 按置信度从高到低排序
5. 返回有效的JSON格式
6. 置信度不能是随机编造的，必须反映真实的适用性评估"""


def chart_type_recommendation_system_zh() -> str:
    return (
        "你是一个专业的数据可视化专家，擅长根据数据特点选择最合适的图表类型。"
        "你必须确保推荐的置信度总和为100%，并且基于真实的数据分析，不能编造数值。"
    )


def enrich_recommendation_reasons_user_zh(desc_short: str, rows: List[Dict[str, Any]], n: int) -> str:
    rows_blob = json.dumps(rows, ensure_ascii=False)
    return f"""以下为数据摘录（可能含无关叙述）：
---
{desc_short}
---

下列图表类型排序已由服务器最终确定（第 1 名即当前已出图类型）。请为每一行各写**一句**中文（≤45 字），从“读者想从数据里看出什么关系”解释该图式为何合适；各行开头和句式必须明显不同，禁止复制粘贴式雷同。不要否定排序、不要建议改类型、不要提“置信度百分之”。

行数据：
{rows_blob}

仅返回 JSON；`reasons` 数组必须恰好包含 {n} 个字符串，例如 {{"reasons": ["…", "…"]}}。"""


def enrich_recommendation_reasons_system_zh() -> str:
    return "你是数据可视化文案编辑，只输出合法 JSON，不要用 Markdown 围栏。"


def semantic_fallback_label_zh() -> str:
    return "语义线索"

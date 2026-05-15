"""
Chinese UI / API copy and static localization tables for EviFlow-Vis.

Views import from here so ``views.py`` stays mostly logic; language tier stays zh for product copy.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# --- API JSON errors (user-visible) ---
ERR_PROVIDE_DATA_DESCRIPTION = "请提供数据描述"
ERR_INVALID_JSON = "无效的JSON数据"
ERR_POST_ONLY = "仅支持 POST"
ERR_INVALID_JSON_BODY = "无效的 JSON"
ERR_MERGED_PARTS_NOT_ARRAY = "mergedParts 须为数组"
ERR_POST_ONLY_ALT = "仅支持POST请求"
ERR_UPLOAD_TEXT_FILE = "请上传文本文件"
ERR_UNSUPPORTED_TEXT_EXT = "仅支持 .txt/.md/.csv/.docx/.pdf 文本文件"
ERR_EMPTY_FILE = "文件内容为空，无法提取可视化片段"
ERR_LLM_ANALYSIS_FAILED = "LLM分析失败"
ERR_CHART_CONFIG_REQUIRED = "请提供有效的chart_config"

ERR_TEXT_PARSE_PREFIX = "文本解析失败:"


def err_text_parse_failed(exc: Exception) -> str:
    return f"{ERR_TEXT_PARSE_PREFIX} {exc}"


# --- Default chart title when LLM omits one ---
UI_DEFAULT_CHART_TITLE_ZH = "数据可视化"

# --- Layout QC: zh -> en for EN UI tier ---
LAYOUT_ZH_TO_EN: Dict[str, str] = {
    "标题与图例重叠": "Title overlaps legend.",
    "x轴标签过长，可能导致重叠": "X-axis labels are long and may overlap.",
    "y轴标签过长，可能导致重叠": "Y-axis labels are long and may overlap.",
    "水平图例项较多，极易与标题或标签重叠": "Too many horizontal legend items; overlap risk with title/labels is high.",
    "图例位置未明确设置，极易与标题或标签重叠": "Legend position is not explicitly set; overlap risk with title/labels is high.",
    "图例与标题距离过近，极易重叠": "Legend is too close to the title and may overlap.",
    "图例项文字过长，易导致重叠": "Legend item text is too long and may overlap.",
    "标题或副标题与图表主体区域(grid)重叠": "Title/subtitle overlaps the chart plotting area (grid).",
    "标题或副标题与雷达图指示器重叠": "Title/subtitle overlaps radar indicators.",
    "标题或副标题与饼图重叠": "Title/subtitle overlaps the pie chart.",
    "标题或副标题与树图节点重叠": "Title/subtitle overlaps tree nodes.",
    "数据点较多且启用标签，极易重叠": "Many data points with labels enabled; overlap risk is high.",
    "数据标签内容过长，极易重叠": "Data-label text is too long and may overlap.",
    "未设置图表边距，可能导致文字与边缘重叠": "Grid margins are not set; text may overlap chart edges.",
    "布局良好": "Layout is good.",
    "检测过程中出现错误，建议手动检查布局": "An error occurred during layout QC; please review layout manually.",
    "建议旋转x轴标签45度或90度": "Rotate x-axis labels by 45° or 90°.",
    "考虑减少标签显示间隔": "Increase label interval / reduce displayed labels.",
    "建议将图例放置在图表外部": "Move legend outside the main plotting area.",
    "考虑使用垂直图例布局": "Use a vertical legend layout.",
    "建议缩短标题长度": "Shorten the title/subtitle text.",
    "考虑调整标题位置": "Adjust title position.",
    "建议减少数据标签显示": "Reduce visible data labels.",
    "考虑使用交互式显示标签": "Use interaction-based label display.",
    "建议增加图表边距": "Increase chart margins.",
    "考虑调整图表容器大小": "Adjust chart container size.",
    "自动调整坐标轴标签避免重叠": "Auto-fix: adjusted axis labels to reduce overlap.",
    "自动调整图例位置避免与标题重叠": "Auto-fix: adjusted legend position to avoid title overlap.",
    "自动缩小雷达图为标题让出空间": "Auto-fix: reduced radar footprint to free title space.",
    "自动调整图表边距为标题让出空间": "Auto-fix: adjusted chart margins to free title space.",
    "自动调整树图布局为标题让出空间": "Auto-fix: adjusted tree layout to free title space.",
    "自动调整标题位置": "Auto-fix: adjusted title position.",
    "自动优化数据标签显示": "Auto-fix: optimized data-label display.",
    "自动调整图表边距": "Auto-fix: adjusted chart margins.",
    "树状图布局智能优化": "Auto-fix: optimized tree layout.",
}

LAYOUT_ZH_FALLBACK_PAIRS: List[Tuple[str, str]] = [
    ("标题", "title"),
    ("副标题", "subtitle"),
    ("图例", "legend"),
    ("重叠", "overlap"),
    ("坐标轴", "axis"),
    ("标签", "label"),
    ("边距", "margin"),
    ("建议", "suggestion"),
]

# --- LLM / validation errors ---
ERR_CANNOT_EXTRACT_JSON_FROM_LLM = "无法从LLM响应中提取有效的JSON数据"
ERR_LLM_RESULT_SHAPE_INVALID = "LLM返回的结果格式不正确"

# --- Heuristic scoring (Chinese substrings in excerpt) ---
HEURISTIC_ZH_TIME = r"(月|周|年|季度|时间线|趋势)"
HEURISTIC_ZH_COMPARE = r"(对比|比较|排名|高于|低于|最多|最少)"
HEURISTIC_ZH_SHARE = r"(占比|比例|构成|份额|百分比)"
HEURISTIC_ZH_RELATION = r"(相关|关系|关联)"

# --- Chart-type display names ---
CHART_TYPE_NAMES_ZH: Dict[str, str] = {
    "line": "折线图",
    "bar": "柱状图",
    "scatter": "散点图",
    "pie": "饼图",
    "radar": "雷达图",
    "funnel": "漏斗图",
    "tree": "树形图",
    "gantt": "甘特图",
    "area": "面积图",
    "heatmap": "热力图",
    "bubble": "气泡图",
    "candlestick": "K线图",
    "combo": "复合图",
}

CHART_TYPE_NAMES_EN: Dict[str, str] = {
    "line": "Line chart",
    "bar": "Bar chart",
    "scatter": "Scatter chart",
    "pie": "Pie chart",
    "radar": "Radar chart",
    "funnel": "Funnel chart",
    "tree": "Tree chart",
    "gantt": "Gantt chart",
    "area": "Area chart",
    "heatmap": "Heatmap",
    "bubble": "Bubble chart",
    "candlestick": "Candlestick chart",
    "combo": "Composite chart",
}

# --- Keyword hints for matched_keywords ---
KEYWORD_MAP_BY_CHART_TYPE: Dict[str, List[str]] = {
    "line": ["trend", "time", "increase", "decrease", "趋势", "时间", "增长", "下降"],
    "bar": ["compare", "rank", "category", "比较", "对比", "排名", "分类"],
    "scatter": ["correlation", "relationship", "distribution", "相关", "关系", "分布"],
    "pie": ["share", "ratio", "percentage", "占比", "比例", "百分比"],
    "radar": ["dimension", "multi-metric", "多维", "能力", "评估"],
    "funnel": ["conversion", "stage", "pipeline", "转化", "阶段", "流程"],
    "tree": ["hierarchy", "structure", "nested", "层级", "结构", "树形"],
    "gantt": ["timeline", "schedule", "milestone", "时间线", "进度", "里程碑"],
    "area": ["cumulative", "stacked", "累积", "堆积"],
    "heatmap": ["density", "intensity", "热力", "密度"],
    "bubble": ["third variable", "size encoding", "气泡", "三维"],
    "candlestick": ["open", "close", "high", "low", "开盘", "收盘", "最高", "最低"],
    "combo": [
        "composite",
        "dual axis",
        "two metrics",
        "bar and line",
        "组合",
        "复合",
        "双轴",
        "柱线",
        "多指标",
    ],
}

DEFAULT_MATCHED_KEYWORDS_ZH = ["时间趋势", "数值序列"]
DEFAULT_MATCHED_KEYWORDS_EN = ["time trend", "numeric sequence"]

# --- LLM reason hygiene ---
SPURIOUS_REASON_PHRASE_ZH = "基于数据分析"

# --- UI copy when LLM path is skipped ---
ANALYSIS_SUMMARY_UI_ZH: Dict[str, str] = {
    "data_characteristics": "系统会从摘录里抓取数值与语义线索，夹杂无关叙述是正常的。",
    "visualization_goals": "首张卡片对应已渲染的图；其余条目是对同一段文字的不同读图视角。",
    "recommended_approach": "点 Apply type 可换类型重新生成；每条说明会尽量写得自然，但排序仍与后端打分一致。",
}

# --- Diverse non-LLM rationales (zh) ---
RUNNER_OPENING_ZH: Tuple[str, ...] = (
    "换一种读法时，",
    "作为备选也说得通：",
    "次要视角下，",
    "若想做对照解读，",
)

REASON_POOL_ZH: Dict[str, Tuple[str, ...]] = {
    "line": (
        "数字沿顺序展开，更像在问“走势如何”——折线突出拐点与交叉，而不是强调离散桶宽。",
        "若关心阶段之间的起伏而非名次本身，用折线串起来比柱状更不容易误读成无关类别。",
        "多组读数沿同一时间或步骤对齐时，折线用最少笔墨交代“往哪跑、何时掉头”。",
    ),
    "bar": (
        "若干独立类目各有一个主指标时，柱形把“谁高谁低”变成一眼可比的线段长度。",
        "若重点是横向对比而非连续走势，柱图避免把本不连续的点连成假趋势。",
        "排名或分组对比场景下，等宽柱+统一基线让两两比较更直观。",
    ),
    "scatter": (
        "两个数值维度可能共同变化时，散点云能同时暴露聚集、离群和弱相关趋势。",
        "没有强时间先后、却想观察成对关系时，用点云比硬连线更不容易虚构序列。",
        "若关心联合分布而非排序，散点把每对观测当作独立样本呈现。",
    ),
    "pie": (
        "文本在讲构成、份额或“整体中的部分”时，饼/环图把占比关系转成角度直觉。",
        "当各部分应加总为一个有意义整体，扇区强调组成结构而非精确差值。",
        "类别不多且读者偏业务口径时，占比叙事与扇区隐喻更贴近口头表达。",
    ),
    "radar": (
        "同一对象上多指标并列评估时，雷达把“偏科/短板”折成一张轮廓。",
        "维度多但量纲可比时，折叠到一张蛛网图比拆多张迷你图更省认知负担。",
        "若要做能力矩阵或评分卡式对比，多轴闭合线适合展示形状差异。",
    ),
    "funnel": (
        "按阶段递减的转化/留存数字，漏斗自上而下天然对应“越往后越少”的叙事。",
        "流程闸门逐个筛掉流量时，锥形带宽比零散柱更贴合漏斗心智模型。",
        "若强调每关流失而非精确差值，阶段式收窄更利于讲清瓶颈。",
    ),
    "tree": (
        "文本呈现层级、父子或嵌套归属时，树状结构优先交代包含关系而非单点大小。",
        "当“谁属于谁”比数值更重要，分支布局避免把兄弟类目误读成时间顺序。",
        "多层分类rollup时，树/矩形树图能一次展开路径而不打乱层级。",
    ),
    "gantt": (
        "带起止跨度、并行任务或里程碑的叙述，更适合横条贴在时间轴上看重叠与空档。",
        "若关心工期占用与并发，甘特式条带比孤立点更能表达持续区间。",
        "项目排期类信息里，显式时长条帮助比较谁在何时占用资源。",
    ),
    "combo": (
        "同一类目上两个量级差很大的指标，常用双轴+混合几何避免把细信号压扁。",
        "若一条序列像“量”、另一条像“率/占比”，复合图让读者留在同一画布上对照。",
        "需要柱看体量、线看变化节奏时，组合编码比两张独立截图更易对照。",
    ),
}

# --- generate_chart_config (zh tier) ---
COMBO_RULES_ZH = """
- 复合图（combo）：由你完整设计 option；多个 series 的 type 可分别为 line、bar、scatter、area，并共享同一类目轴或时间轴。
- 当同一组年份/类目上有两个及以上不同数值指标时，至少使用两种不同的 series.type（推荐：销售额等主量级用 bar，利润等次指标用 line；或 bar + scatter）。不要默认把两条系列都做成同一种 area/折线叠涂，除非原文明确要求该样式。
- 若两类指标量级差异大，可使用 yAxis 数组并为各 series 设置 yAxisIndex 实现双 Y 轴。
- 同一图中不要混用 pie / radar / funnel / tree / gantt 与直角坐标系系列。
- 每个 series 设置清晰 name；配色区分明显。
- 充分利用原文中的有效数值，不要无故丢点。
"""


def single_series_type_rule_zh(chart_type: str) -> str:
    return (
        f'- series[].type 必须与指定图表类型 "{chart_type}" 保持一致（数据结构完全不支持时除外）'
    )


def fmt_recommendation_reason_zh(chart_name: str, kw: str, numeric_count: int, confidence: float) -> str:
    return (
        f"推荐{chart_name}，因为命中线索[{kw}]与该图类型匹配；"
        f"检测到数值证据{numeric_count}处；当前置信度{round(confidence, 1)}%。"
    )


def fmt_reason_body_hook_zh(clip: str) -> str:
    return f"（线索：{clip}。）"

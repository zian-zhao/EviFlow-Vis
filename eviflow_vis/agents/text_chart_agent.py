import json
import re
from typing import Any, Dict, List

import requests

from eviflow_vis.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL


class TextChartAgent:
    """识别文本中适合图表化的片段。"""

    PROFILE_CONFIG = {
        "strict": {
            "extract_limit": 20,
            "candidate_limit": 50,
            "min_score": 80,
            "min_numbers": 2,
            "min_keywords": 1,
            "label": "严格",
            # Strict: merge near-duplicate spans (high overlap) into one segment instead of keeping two.
            "overlap_merge_iou": 0.50,
            "overlap_merge_min_intersection_ratio": 0.72,
        },
        "balanced": {"extract_limit": 30, "candidate_limit": 70, "min_score": 66, "min_numbers": 1, "min_keywords": 1, "label": "平衡"},
        "loose": {"extract_limit": 45, "candidate_limit": 100, "min_score": 54, "min_numbers": 1, "min_keywords": 0, "label": "宽松"},
    }

    ZH_KEYWORDS = [
        "增长", "下降", "同比", "环比", "占比", "比例", "趋势", "对比", "时间", "月份", "年度", "季度",
        "排名", "平均", "中位数", "波动", "峰值", "低谷", "分布", "相关", "回归", "转化", "留存",
        "从", "到", "由", "较", "提升", "减少", "上升", "下滑", "累计",
    ]
    EN_KEYWORDS = [
        "increase", "decrease", "growth", "decline", "trend", "compare", "comparison", "versus",
        "share", "ratio", "proportion", "percentage", "distribution", "correlation", "regression",
        "from", "to", "between", "by", "quarter", "q1", "q2", "q3", "q4", "month", "year",
        "yoy", "mom", "rank", "ranking", "average", "median", "conversion", "retention", "rate",
        "rose", "fell", "improved", "dropped", "peak", "low",
    ]

    NUMERIC_PATTERN = re.compile(
        r"(?:(?:\$|€|£|¥)\s*)?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:%|[kKmMbB]|万|亿)?|-?\d+(?:\.\d+)?%"
    )
    YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")
    MAX_SEGMENT_CHARS = 280
    PARAGRAPH_KEEP_CHARS = 360
    META_LINE_PATTERN = re.compile(
        r"^\s*(date:|attendees:|confidential|meeting minutes|action items?|next review|owner:|due:)",
        re.IGNORECASE,
    )

    def extract_segments(self, text: str, profile: str = "balanced") -> Dict[str, Any]:
        text = (text or "").strip()
        if not text:
            return {"segments": []}

        config = self.PROFILE_CONFIG.get(profile, self.PROFILE_CONFIG["balanced"])
        # 阶段1：规则召回（快）
        rule_candidates = self._extract_with_rules(text, config)

        # 阶段2：LLM召回（单次调用，失败即回退）
        llm_candidates = self._extract_with_llm(text, config["extract_limit"])

        merged = self._merge_candidates(
            rule_candidates + llm_candidates,
            limit=config.get("candidate_limit", 70),
        )
        reranked = self._rerank_candidates(merged, text, config)
        return {"segments": self._normalize_segments(text, reranked, config, profile=profile)}

    def _extract_with_llm(self, text: str, max_segments: int) -> List[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        prompt = f"""你是数据可视化预处理智能体。请从文本中找出最适合生成图表的1-{max_segments}个片段（支持中文与英文）。

要求：
1) 片段必须是原文中的连续文本，并且满足“可量化且可比较”标准。
2) 优先选择包含多个数字、对比关系、趋势描述、时间维度或比例关系的句段。
3) 对于过于泛泛、没有明确数据结构的句段，不要返回。
3.1) 不要直接返回整段长文本；优先返回最小可解释的句段或相邻句组。
3.2) 只有当整段都围绕同一组指标且数据非常密集时，才允许返回较长片段。
4) 返回JSON数组，每个元素格式为：
{{
  "text": "原文片段",
  "reason": "为什么适合画图",
  "score": 0-100,
  "intent": "trend|comparison|composition|distribution|relationship"
}}
5) 只返回JSON，不要markdown。

原文：
{text}
"""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你擅长从长文本中提取可视化价值最高的片段。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
        }
        try:
            resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=18)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            start = content.find("[")
            end = content.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
                return data if isinstance(data, list) else []
        except Exception:
            return []
        return []

    def _extract_with_rules(self, text: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        blocks = self._build_candidate_blocks(text)
        scored: List[Dict[str, Any]] = []
        for block in blocks:
            if self._is_meta_or_header_text(block):
                continue
            score = self._score_candidate(block)
            if self._passes_structural_filter(block, score, config):
                scored.append(
                    {
                        "text": block,
                        "reason": "Contains quantifiable and comparable signals",
                        "score": score,
                        "intent": self._infer_intent(block),
                    }
                )

        scored.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
        return scored

    def _build_candidate_blocks(self, text: str) -> List[str]:
        paragraphs = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        if not paragraphs:
            paragraphs = [line.strip() for line in text.splitlines() if line.strip()]

        candidates: List[str] = []
        for para in paragraphs:
            if len(para) < 24:
                continue
            # 英文/中文混合句切分
            sentences = [s.strip() for s in re.split(r"(?<=[。！？!?\.])\s+|(?<=[；;])\s*", para) if s.strip()]
            if len(sentences) <= 1:
                sentences = [s.strip() for s in re.split(r"[，,]", para) if s.strip()]

            # 控制复杂度：保留长度适中的句段
            for sent in sentences:
                if 18 <= len(sent) <= 320:
                    candidates.append(sent)

            # 句对窗口：保留本应一起画图的相邻信息（避免被硬拆）
            if len(sentences) >= 2:
                for i in range(len(sentences) - 1):
                    pair = f"{sentences[i]} {sentences[i + 1]}".strip()
                    if 30 <= len(pair) <= self.MAX_SEGMENT_CHARS:
                        candidates.append(pair)

            # 仅在段落本身“高密度、单主题”时，才保留整段候选
            if self._should_keep_full_paragraph(para):
                candidates.append(para)

        # 去重
        dedup = list(dict.fromkeys(candidates))
        return dedup

    def _should_keep_full_paragraph(self, para: str) -> bool:
        if len(para) > self.PARAGRAPH_KEEP_CHARS:
            return False
        score = self._score_candidate(para)
        number_count = len(self.NUMERIC_PATTERN.findall(para))
        relation_hits = sum(
            1
            for token in ["同比", "环比", "对比", "占比", "趋势", "comparison", "versus", "trend", "share", "ratio"]
            if token in para.lower() or token in para
        )
        return score >= 78 and number_count >= 3 and relation_hits >= 2

    def _score_candidate(self, block: str) -> float:
        lower = block.lower()
        number_count = len(self.NUMERIC_PATTERN.findall(block))
        zh_kw_count = sum(1 for kw in self.ZH_KEYWORDS if kw in block)
        en_kw_count = sum(1 for kw in self.EN_KEYWORDS if kw in lower)
        keyword_count = zh_kw_count + en_kw_count
        year_hits = len(self.YEAR_PATTERN.findall(block))

        structure_bonus = 0
        if (("从" in block and "到" in block) or ("from" in lower and "to" in lower)) and number_count >= 2:
            structure_bonus += 14
        if any(token in lower for token in ["yoy", "mom", "versus", "compare", "compared"]) or any(
            token in block for token in ["同比", "环比", "对比", "占比"]
        ):
            structure_bonus += 12
        if year_hits > 0:
            structure_bonus += min(10, year_hits * 3)

        # 惩罚：过长且数据密度低
        density_penalty = 0
        if len(block) > 260 and number_count <= 1 and keyword_count <= 2:
            density_penalty = 16
        # 惩罚：纯描述无数据
        if number_count == 0:
            density_penalty += 10

        score = number_count * 14 + keyword_count * 8 + structure_bonus - density_penalty
        return float(max(0, min(100, score)))

    def _infer_intent(self, text: str) -> str:
        lower = text.lower()
        if any(t in lower for t in ["trend", "growth", "decline", "yoy", "mom"]) or any(t in text for t in ["趋势", "增长", "下降"]):
            return "trend"
        if any(t in lower for t in ["compare", "versus", "rank"]) or any(t in text for t in ["对比", "排名"]):
            return "comparison"
        if any(t in lower for t in ["share", "ratio", "proportion", "percentage"]) or any(t in text for t in ["占比", "比例"]):
            return "composition"
        if any(t in lower for t in ["distribution", "spread"]) or "分布" in text:
            return "distribution"
        if any(t in lower for t in ["correlation", "relationship"]) or any(t in text for t in ["相关", "关系"]):
            return "relationship"
        return "general"

    def _merge_candidates(self, candidates: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []
        seen = set()
        for item in candidates:
            txt = str(item.get("text", "")).strip()
            if not txt:
                continue
            if self._is_meta_or_header_text(txt):
                continue
            key = self._canonical_text(txt)
            if key in seen:
                continue
            seen.add(key)
            merged.append(
                {
                    "text": txt,
                    "reason": str(item.get("reason", "Contains chartable signals")),
                    "score": float(item.get("score", 60)),
                    "intent": str(item.get("intent", self._infer_intent(txt))),
                }
            )
            if len(merged) >= limit:
                break
        return merged

    def _rerank_candidates(self, candidates: List[Dict[str, Any]], source_text: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        reranked = []
        for c in candidates:
            txt = c.get("text", "")
            base = float(c.get("score", 0))
            rule_score = self._score_candidate(txt)
            # 融合LLM分和规则分，减轻单侧偏差
            fused = round(0.45 * base + 0.55 * rule_score, 2)
            if self._passes_structural_filter(txt, fused, config):
                reranked.append({**c, "score": fused})
        reranked.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
        return reranked[: int(config.get("extract_limit", 30))]

    def _canonical_text(self, text: str) -> str:
        return re.sub(r"\s+", "", text).strip().lower()

    def _normalize_segments(
        self,
        source_text: str,
        segments: List[Dict[str, Any]],
        config: Dict[str, Any],
        profile: str = "balanced",
    ) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        used_ranges = set()
        for idx, item in enumerate(segments):
            seg_text = str(item.get("text", "")).strip()
            if not seg_text:
                continue
            if self._is_meta_or_header_text(seg_text):
                continue

            # 软拆分：仅对“超长且低密度”的片段拆分；高密度片段保持整体
            refined_texts = self._refine_granularity(seg_text)
            if not refined_texts:
                refined_texts = [seg_text]

            for refined in refined_texts:
                if self._is_meta_or_header_text(refined):
                    continue

                start, end = self._locate_exact_span(source_text, refined)
                if start < 0 or end <= start:
                    # 严格边界命中失败：回退到原子句，避免整块错误高亮
                    fallback_units = self._to_atomic_units(refined)
                    for unit in fallback_units:
                        s2, e2 = self._locate_exact_span(source_text, unit)
                        if s2 < 0 or e2 <= s2:
                            continue
                        key2 = (s2, e2)
                        if key2 in used_ranges:
                            continue
                        used_ranges.add(key2)
                        normalized.append(
                            {
                                "id": f"seg_{idx + 1}",
                                "text": unit,
                                "start": s2,
                                "end": e2,
                                "reason": str(item.get("reason", "Contains chartable information")),
                                "score": max(50.0, float(item.get("score", 60)) * 0.92),
                            }
                        )
                    continue

                key = (start, end)
                if key in used_ranges:
                    continue
                used_ranges.add(key)
                normalized.append(
                    {
                        "id": f"seg_{idx + 1}",
                        "text": refined,
                        "start": start,
                        "end": end,
                        "reason": str(item.get("reason", "Contains chartable information")),
                        "score": float(item.get("score", 60)),
                    }
                )
        normalized.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
        filtered = [item for item in normalized if self._passes_structural_filter(item.get("text", ""), float(item.get("score", 0)), config)]
        filtered = self._prune_redundant_segments(filtered)
        if profile == "strict":
            filtered = self._merge_strict_high_overlap_segments(source_text, filtered, config)
        return filtered

    def _strict_pair_should_merge(
        self,
        seg_a: Dict[str, Any],
        seg_b: Dict[str, Any],
        config: Dict[str, Any],
    ) -> bool:
        """True if two located spans are near-duplicates by overlap (strict mode only)."""
        a1 = int(seg_a.get("start", -1))
        a2 = int(seg_a.get("end", -1))
        b1 = int(seg_b.get("start", -1))
        b2 = int(seg_b.get("end", -1))
        if a1 < 0 or a2 <= a1 or b1 < 0 or b2 <= b1:
            return False
        inter = max(0, min(a2, b2) - max(a1, b1))
        if inter <= 0:
            return False
        len_a = a2 - a1
        len_b = b2 - b1
        union_span = max(a2, b2) - min(a1, b1)
        if union_span <= 0:
            return False
        iou = inter / float(union_span)
        min_len = max(1, min(len_a, len_b))
        intersection_ratio = inter / float(min_len)

        iou_th = float(config.get("overlap_merge_iou", 0.50))
        ratio_th = float(config.get("overlap_merge_min_intersection_ratio", 0.72))
        if iou >= iou_th:
            return True
        if intersection_ratio >= ratio_th:
            return True
        return False

    def _merge_strict_high_overlap_segments(
        self,
        source_text: str,
        segments: List[Dict[str, Any]],
        config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        In strict profile, cluster segments that overlap heavily and replace each cluster
        with a single span [min(start), max(end)) in the source text.
        """
        if len(segments) <= 1:
            return segments

        n = len(segments)
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: int, y: int) -> None:
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx

        for i in range(n):
            for j in range(i + 1, n):
                if self._strict_pair_should_merge(segments[i], segments[j], config):
                    union(i, j)

        clusters: Dict[int, List[int]] = {}
        for i in range(n):
            r = find(i)
            clusters.setdefault(r, []).append(i)

        merged: List[Dict[str, Any]] = []
        for root in sorted(clusters.keys()):
            idxs = clusters[root]
            if len(idxs) == 1:
                merged.append(dict(segments[idxs[0]]))
                continue

            sts = [int(segments[k]["start"]) for k in idxs]
            eds = [int(segments[k]["end"]) for k in idxs]
            s_min = max(0, min(sts))
            e_max = min(len(source_text), max(eds))
            if e_max <= s_min:
                continue
            new_text = source_text[s_min:e_max]

            best_k = max(idxs, key=lambda k: float(segments[k].get("score", 0)))
            best_score = float(segments[best_k].get("score", 60))
            reasons: List[str] = []
            for k in sorted(idxs, key=lambda x: int(segments[x].get("start", 0))):
                rtxt = str(segments[k].get("reason", "")).strip()
                if rtxt and rtxt not in reasons:
                    reasons.append(rtxt)
            if len(reasons) <= 1:
                reason = reasons[0] if reasons else "Contains chartable information"
            else:
                reason = " | ".join(reasons[:3])

            merged.append(
                {
                    "id": "temp",
                    "text": new_text,
                    "start": s_min,
                    "end": e_max,
                    "reason": reason[:500] if len(reason) > 500 else reason,
                    "score": best_score,
                }
            )

        merged.sort(key=lambda x: (int(x.get("start", 0)), int(x.get("end", 0))))
        for idx, seg in enumerate(merged):
            seg["id"] = f"seg_{idx + 1}"
        return merged

    def _prune_redundant_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicated / nested segments to avoid generating near-identical charts.
        Keep the more informative parent segment when child is highly contained.
        """
        if not segments:
            return []

        # Prefer higher score first, and for close scores prefer longer context (composite-friendly).
        ranked = sorted(
            segments,
            key=lambda s: (float(s.get("score", 0)), len(str(s.get("text", "")))),
            reverse=True
        )
        kept: List[Dict[str, Any]] = []
        kept_norm_texts: List[str] = []

        for seg in ranked:
            st = int(seg.get("start", -1))
            ed = int(seg.get("end", -1))
            txt = str(seg.get("text", "")).strip()
            if st < 0 or ed <= st or not txt:
                continue

            norm_txt = self._canonical_text(txt)
            seg_len = max(1, ed - st)
            redundant = False

            for i, ex in enumerate(kept):
                ex_st = int(ex.get("start", -1))
                ex_ed = int(ex.get("end", -1))
                if ex_st < 0 or ex_ed <= ex_st:
                    continue
                ex_len = max(1, ex_ed - ex_st)
                ex_norm_txt = kept_norm_texts[i]

                # 1) Exact or near-exact textual duplicate
                if norm_txt == ex_norm_txt:
                    redundant = True
                    break

                # 2) Heavy containment in span space + textual inclusion -> drop child
                inter = max(0, min(ed, ex_ed) - max(st, ex_st))
                if inter <= 0:
                    continue

                contain_by_ex = inter / float(seg_len)     # seg covered by existing
                contain_ex_by_seg = inter / float(ex_len)  # existing covered by seg
                text_inclusion = norm_txt and (norm_txt in ex_norm_txt or ex_norm_txt in norm_txt)

                # If current segment is mostly inside an existing one and semantically same, drop it.
                if contain_by_ex >= 0.85 and (text_inclusion or abs(seg_len - ex_len) <= 12):
                    redundant = True
                    break

                # If almost identical ranges, keep only one (already ranked by score/length).
                if contain_by_ex >= 0.92 and contain_ex_by_seg >= 0.92:
                    redundant = True
                    break

            if not redundant:
                kept.append(seg)
                kept_norm_texts.append(norm_txt)

        # Return in reading order for stable IDs in frontend
        kept.sort(key=lambda s: (int(s.get("start", 0)), int(s.get("end", 0))))
        for idx, seg in enumerate(kept):
            seg["id"] = f"seg_{idx + 1}"
        return kept

    def _refine_granularity(self, seg_text: str) -> List[str]:
        seg_text = (seg_text or "").strip()
        if len(seg_text) <= self.MAX_SEGMENT_CHARS:
            return [seg_text]

        # 高密度长段落：保留整体，避免把本可一图表达的内容硬拆
        if self._should_keep_full_paragraph(seg_text):
            return [seg_text]

        # 低密度超长片段：拆成句段，再尝试保留相邻句对
        parts = [s.strip() for s in re.split(r"(?<=[。！？!?\.])\s+|(?<=[；;])\s*|(?<=[，,])\s*", seg_text) if s.strip()]
        if len(parts) <= 1:
            return [seg_text[: self.MAX_SEGMENT_CHARS]]

        out: List[str] = []
        for p in parts:
            if 18 <= len(p) <= self.MAX_SEGMENT_CHARS:
                out.append(p)
        for i in range(len(parts) - 1):
            pair = f"{parts[i]} {parts[i + 1]}".strip()
            if 35 <= len(pair) <= self.MAX_SEGMENT_CHARS and self._score_candidate(pair) >= self._score_candidate(parts[i]):
                out.append(pair)

        dedup = list(dict.fromkeys(out))
        return dedup[:4] if dedup else [seg_text[: self.MAX_SEGMENT_CHARS]]

    def _passes_structural_filter(self, text: str, score: float, config: Dict[str, Any]) -> bool:
        if self._is_meta_or_header_text(text):
            return False
        min_score = float(config.get("min_score", 60))
        min_numbers = int(config.get("min_numbers", 1))
        min_keywords = int(config.get("min_keywords", 0))
        numbers = len(self.NUMERIC_PATTERN.findall(text or ""))
        lower = (text or "").lower()
        keywords = sum(
            1
            for kw in self.ZH_KEYWORDS
            if kw in (text or "")
        )
        keywords += sum(1 for kw in self.EN_KEYWORDS if kw in lower)
        return score >= min_score and numbers >= min_numbers and keywords >= min_keywords

    def _locate_exact_span(self, source_text: str, seg_text: str) -> (int, int):
        """Prefer exact contiguous match to avoid oversized highlight spans."""
        seg_text = (seg_text or "").strip()
        if not seg_text:
            return -1, -1

        start = source_text.find(seg_text)
        if start >= 0:
            return start, start + len(seg_text)

        # 容忍末尾标点差异，但仍要求连续命中
        relaxed = seg_text.strip(" .,:;!?，。；：！？\"'")
        if relaxed and len(relaxed) >= 12:
            s2 = source_text.find(relaxed)
            if s2 >= 0:
                return s2, s2 + len(relaxed)
        return -1, -1

    def _to_atomic_units(self, text: str) -> List[str]:
        parts = [
            p.strip()
            for p in re.split(r"(?<=[。！？!?\.])\s+|(?<=[；;])\s*|(?<=[，,])\s*", text or "")
            if p and p.strip()
        ]
        out: List[str] = []
        for p in parts:
            if 18 <= len(p) <= self.MAX_SEGMENT_CHARS and not self._is_meta_or_header_text(p):
                out.append(p)
        return list(dict.fromkeys(out))[:5]

    def _is_meta_or_header_text(self, text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return True
        if self.META_LINE_PATTERN.match(t):
            return True
        # 会议标题、章节标题、格式化标题等
        if t.startswith("**") and t.endswith("**"):
            return True
        if re.match(r"^(Q\d|Week\s*\d+|Version\s*[A-Z]\b)\s*[:\-]?$", t, re.IGNORECASE):
            return True
        # 只有时间/日期/名单字段，通常不直接画图
        if re.match(r"^\s*\d{1,2}:\d{2}\s*(AM|PM)\.?\s*$", t, re.IGNORECASE):
            return True
        if re.match(r"^\s*(date|time|attendees?)\s*[:：]", t, re.IGNORECASE):
            return True
        return False

    def _normalize_with_map(self, text: str) -> (str, List[int]):
        chars: List[str] = []
        idx_map: List[int] = []
        for i, ch in enumerate(text):
            if ch.isspace():
                continue
            # 统一常见中英文标点
            repl = {
                "，": ",",
                "。": ".",
                "：": ":",
                "；": ";",
                "（": "(",
                "）": ")",
                "“": "\"",
                "”": "\"",
                "‘": "'",
                "’": "'",
            }.get(ch, ch)
            chars.append(repl.lower())
            idx_map.append(i)
        return "".join(chars), idx_map


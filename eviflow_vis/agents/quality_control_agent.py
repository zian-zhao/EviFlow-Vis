from typing import Dict, List, Any, Optional, Union
import json
import re
from .logger import AgentLogger

class QualityControlAgent:
    def __init__(self):
        self.logger = AgentLogger()
        self.data_quality_checker = DataQualityChecker()
        self.visualization_quality_checker = VisualizationQualityChecker()
        self.performance_checker = PerformanceChecker()
        self.accessibility_checker = AccessibilityChecker()
        self.usability_checker = UsabilityChecker()
        self.optimization_suggester = OptimizationSuggester()
        self.error_detector = ErrorDetector()
        self.quality_improver = QualityImprover()
        self.layout_overlap_detector = LayoutOverlapDetector()
        self.auto_layout_fixer = AutoLayoutFixer()

    async def check_quality(self, data: Dict, visualization: Dict) -> Dict:
        """检查质量"""
        try:
            # 1. 检查数据质量
            data_quality_result = await self.data_quality_checker.check_data_quality(data)
            if not data_quality_result['is_acceptable']:
                return {
                    'error': f"数据质量不达标: {data_quality_result['message']}",
                    'suggestions': data_quality_result['suggestions']
                }

            # 2. 检查可视化质量
            visualization_quality_result = await self.visualization_quality_checker.check_visualization_quality(
                visualization
            )
            if not visualization_quality_result['is_acceptable']:
                return {
                    'error': f"可视化质量不达标: {visualization_quality_result['message']}",
                    'suggestions': visualization_quality_result['suggestions']
                }

            # 3. 检查性能
            performance_result = await self.performance_checker.check_performance(visualization)
            if not performance_result['is_acceptable']:
                return {
                    'error': f"性能不达标: {performance_result['message']}",
                    'suggestions': performance_result['suggestions']
                }

            # 4. 检查可访问性
            accessibility_result = await self.accessibility_checker.check_accessibility(visualization)
            if not accessibility_result['is_acceptable']:
                return {
                    'error': f"可访问性不达标: {accessibility_result['message']}",
                    'suggestions': accessibility_result['suggestions']
                }

            # 5. 检查可用性
            usability_result = await self.usability_checker.check_usability(visualization)
            if not usability_result['is_acceptable']:
                return {
                    'error': f"可用性不达标: {usability_result['message']}",
                    'suggestions': usability_result['suggestions']
                }

            # 6. 检测错误
            error_result = await self.error_detector.detect_errors(data, visualization)
            if error_result['has_errors']:
                return {
                    'error': f"发现错误: {error_result['message']}",
                    'suggestions': error_result['suggestions']
                }

            # 7. 检测布局重叠问题（新增）
            layout_result = await self.layout_overlap_detector.detect_overlaps(visualization)
            if layout_result['has_overlaps']:
                # 自动修复布局问题
                fixed_visualization = await self.auto_layout_fixer.fix_overlaps(
                    visualization, layout_result['issues']
                )
                visualization = fixed_visualization
                
                # 记录布局修复
                self.logger.log_interaction(
                    'quality_control',
                    'layout_fixer',
                    '布局重叠问题已自动修复',
                    {
                        'original_issues': layout_result['issues'],
                        'fixes_applied': layout_result['fixes_applied']
                    },
                    'success'
                )

            # 8. 获取优化建议
            optimization_suggestions = await self.optimization_suggester.get_suggestions(
                data, visualization
            )

            # 9. 改进质量
            improved_result = await self.quality_improver.improve_quality(
                data, visualization, optimization_suggestions
            )

            # 记录质量检查过程
            self.logger.log_interaction(
                'quality_control',
                'master',
                '质量检查完成',
                {
                    'data_quality_score': data_quality_result['score'],
                    'visualization_quality_score': visualization_quality_result['score'],
                    'performance_score': performance_result['score'],
                    'accessibility_score': accessibility_result['score'],
                    'usability_score': usability_result['score'],
                    'layout_issues_fixed': layout_result.get('has_overlaps', False)
                },
                'success'
            )

            return {
                'is_acceptable': True,
                'quality_metrics': {
                    'data_quality': data_quality_result['score'],
                    'visualization_quality': visualization_quality_result['score'],
                    'performance': performance_result['score'],
                    'accessibility': accessibility_result['score'],
                    'usability': usability_result['score']
                },
                'layout_analysis': layout_result,
                'improvements': improved_result['improvements'],
                'suggestions': optimization_suggestions,
                'optimized_visualization': visualization
            }

        except Exception as e:
            self.logger.log_interaction(
                'quality_control',
                'master',
                '质量检查失败',
                {'error': str(e)},
                'error'
            )
            return {'error': f"质量检查失败: {str(e)}"}

    async def check_layout_overlaps(self, chart_config: Dict, description: str = "") -> Dict:
        """专门检查布局重叠问题"""
        try:
            layout_result = await self.layout_overlap_detector.detect_overlaps(chart_config)
            return layout_result
        except Exception as e:
            self.logger.log_interaction(
                'quality_control',
                'layout_detector',
                '布局检测失败',
                {'error': str(e)},
                'error'
            )
            return {'error': f"布局检测失败: {str(e)}"}

    async def auto_fix_overlaps(self, chart_config: Dict, issues: List[str]) -> Dict:
        """自动修复布局重叠问题"""
        try:
            fixed_config = await self.auto_layout_fixer.fix_overlaps(chart_config, issues)
            return fixed_config
        except Exception as e:
            self.logger.log_interaction(
                'quality_control',
                'layout_fixer',
                '布局修复失败',
                {'error': str(e)},
                'error'
            )
            return chart_config  # 返回原始配置

    def check_layout_overlaps_sync(self, chart_config: Dict, description: str = "") -> Dict:
        """同步版本：专门检查布局重叠问题"""
        try:
            layout_result = self.layout_overlap_detector.detect_overlaps_sync(chart_config)
            return layout_result
        except Exception as e:
            self.logger.log_interaction(
                'quality_control',
                'layout_detector',
                '布局检测失败',
                {'error': str(e)},
                'error'
            )
            return {'error': f"布局检测失败: {str(e)}"}

    def auto_fix_overlaps_sync(self, chart_config: Dict, issues: List[str]) -> Dict:
        """同步版本：自动修复布局重叠问题"""
        try:
            fix_result = self.auto_layout_fixer.fix_overlaps_sync(chart_config, issues)
            return fix_result
        except Exception as e:
            self.logger.log_interaction(
                'quality_control',
                'layout_fixer',
                '布局修复失败',
                {'error': str(e)},
                'error'
            )
            return {"fixed_config": chart_config, "fixes_applied": []}

    def parse_llm_chart_config(self, llm_response, call_llm_func=None, max_fix_rounds=2):
        """
        智能解析LLM输出的ECharts配置：
        1. 直接解析
        2. 正则/替换修复
        3. LLM自我修正（多轮）
        4. 兜底用户提示
        call_llm_func: 可选，传入一个函数用于再次调用LLM自我修正
        """
        # 1. 直接解析
        try:
            return json.loads(llm_response)
        except Exception:
            pass
        # 2. 去除代码块标记、正则提取
        import re
        cleaned = re.sub(r'```[a-zA-Z]*', '', llm_response).strip()
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        # 3. 替换单引号为双引号再试
        try:
            fixed = cleaned.replace("'", '"')
            return json.loads(fixed)
        except Exception:
            pass
        # 4. LLM自我修正
        if call_llm_func is not None:
            for _ in range(max_fix_rounds):
                fix_prompt = (
                    "你刚才的输出不是合法JSON。请你只返回合法的JSON对象，不要有任何解释或代码块标记。"
                    f"原始内容如下：\n{llm_response}"
                )
                llm_response = call_llm_func(fix_prompt)
                try:
                    return json.loads(llm_response)
                except Exception:
                    continue
        # 5. 兜底：用户提示
        self.logger.log_interaction(
            'quality_control',
            'llm_fix',
            'LLM输出格式异常',
            {'raw_llm_output': llm_response},
            'error'
        )
        return {
            "error": "AI输出格式有误，已自动反馈。请简化描述或稍后重试。",
            "raw_llm_output": llm_response
        }

class DataQualityChecker:
    """数据质量检查器"""
    async def check_data_quality(self, data: Dict) -> Dict:
        """检查数据质量"""
        return {
            'is_acceptable': self._check_data_validity(data),
            'score': self._calculate_data_quality_score(data),
            'message': self._get_data_quality_message(data),
            'suggestions': self._get_data_quality_suggestions(data)
        }

    def _check_data_validity(self, data: Dict) -> bool:
        """检查数据有效性"""
        # 实现数据有效性检查逻辑
        pass

    def _calculate_data_quality_score(self, data: Dict) -> float:
        """计算数据质量分数"""
        # 实现数据质量分数计算逻辑
        pass

    def _get_data_quality_message(self, data: Dict) -> str:
        """获取数据质量消息"""
        # 实现数据质量消息生成逻辑
        pass

    def _get_data_quality_suggestions(self, data: Dict) -> List[str]:
        """获取数据质量建议"""
        # 实现数据质量建议生成逻辑
        pass

class VisualizationQualityChecker:
    """可视化质量检查器"""
    async def check_visualization_quality(self, visualization: Dict) -> Dict:
        """检查可视化质量"""
        return {
            'is_acceptable': self._check_visualization_validity(visualization),
            'score': self._calculate_visualization_quality_score(visualization),
            'message': self._get_visualization_quality_message(visualization),
            'suggestions': self._get_visualization_quality_suggestions(visualization)
        }

    def _check_visualization_validity(self, visualization: Dict) -> bool:
        """检查可视化有效性"""
        # 实现可视化有效性检查逻辑
        pass

    def _calculate_visualization_quality_score(self, visualization: Dict) -> float:
        """计算可视化质量分数"""
        # 实现可视化质量分数计算逻辑
        pass

    def _get_visualization_quality_message(self, visualization: Dict) -> str:
        """获取可视化质量消息"""
        # 实现可视化质量消息生成逻辑
        pass

    def _get_visualization_quality_suggestions(self, visualization: Dict) -> List[str]:
        """获取可视化质量建议"""
        # 实现可视化质量建议生成逻辑
        pass

class PerformanceChecker:
    """性能检查器"""
    async def check_performance(self, visualization: Dict) -> Dict:
        """检查性能"""
        return {
            'is_acceptable': self._check_performance_validity(visualization),
            'score': self._calculate_performance_score(visualization),
            'message': self._get_performance_message(visualization),
            'suggestions': self._get_performance_suggestions(visualization)
        }

    def _check_performance_validity(self, visualization: Dict) -> bool:
        """检查性能有效性"""
        # 实现性能有效性检查逻辑
        pass

    def _calculate_performance_score(self, visualization: Dict) -> float:
        """计算性能分数"""
        # 实现性能分数计算逻辑
        pass

    def _get_performance_message(self, visualization: Dict) -> str:
        """获取性能消息"""
        # 实现性能消息生成逻辑
        pass

    def _get_performance_suggestions(self, visualization: Dict) -> List[str]:
        """获取性能建议"""
        # 实现性能建议生成逻辑
        pass

class AccessibilityChecker:
    """可访问性检查器"""
    async def check_accessibility(self, visualization: Dict) -> Dict:
        """检查可访问性"""
        return {
            'is_acceptable': self._check_accessibility_validity(visualization),
            'score': self._calculate_accessibility_score(visualization),
            'message': self._get_accessibility_message(visualization),
            'suggestions': self._get_accessibility_suggestions(visualization)
        }

    def _check_accessibility_validity(self, visualization: Dict) -> bool:
        """检查可访问性有效性"""
        # 实现可访问性有效性检查逻辑
        pass

    def _calculate_accessibility_score(self, visualization: Dict) -> float:
        """计算可访问性分数"""
        # 实现可访问性分数计算逻辑
        pass

    def _get_accessibility_message(self, visualization: Dict) -> str:
        """获取可访问性消息"""
        # 实现可访问性消息生成逻辑
        pass

    def _get_accessibility_suggestions(self, visualization: Dict) -> List[str]:
        """获取可访问性建议"""
        # 实现可访问性建议生成逻辑
        pass

class UsabilityChecker:
    """可用性检查器"""
    async def check_usability(self, visualization: Dict) -> Dict:
        """检查可用性"""
        return {
            'is_acceptable': self._check_usability_validity(visualization),
            'score': self._calculate_usability_score(visualization),
            'message': self._get_usability_message(visualization),
            'suggestions': self._get_usability_suggestions(visualization)
        }

    def _check_usability_validity(self, visualization: Dict) -> bool:
        """检查可用性有效性"""
        # 实现可用性有效性检查逻辑
        pass

    def _calculate_usability_score(self, visualization: Dict) -> float:
        """计算可用性分数"""
        # 实现可用性分数计算逻辑
        pass

    def _get_usability_message(self, visualization: Dict) -> str:
        """获取可用性消息"""
        # 实现可用性消息生成逻辑
        pass

    def _get_usability_suggestions(self, visualization: Dict) -> List[str]:
        """获取可用性建议"""
        # 实现可用性建议生成逻辑
        pass

class OptimizationSuggester:
    """优化建议器"""
    async def get_suggestions(self, data: Dict, visualization: Dict) -> List[str]:
        """获取优化建议"""
        return {
            'data_suggestions': self._get_data_suggestions(data),
            'visualization_suggestions': self._get_visualization_suggestions(visualization),
            'performance_suggestions': self._get_performance_suggestions(visualization),
            'accessibility_suggestions': self._get_accessibility_suggestions(visualization),
            'usability_suggestions': self._get_usability_suggestions(visualization)
        }

    def _get_data_suggestions(self, data: Dict) -> List[str]:
        """获取数据建议"""
        # 实现数据建议生成逻辑
        pass

    def _get_visualization_suggestions(self, visualization: Dict) -> List[str]:
        """获取可视化建议"""
        # 实现可视化建议生成逻辑
        pass

    def _get_performance_suggestions(self, visualization: Dict) -> List[str]:
        """获取性能建议"""
        # 实现性能建议生成逻辑
        pass

    def _get_accessibility_suggestions(self, visualization: Dict) -> List[str]:
        """获取可访问性建议"""
        # 实现可访问性建议生成逻辑
        pass

    def _get_usability_suggestions(self, visualization: Dict) -> List[str]:
        """获取可用性建议"""
        # 实现可用性建议生成逻辑
        pass

class ErrorDetector:
    """错误检测器"""
    async def detect_errors(self, data: Dict, visualization: Dict) -> Dict:
        """检测错误"""
        return {
            'has_errors': self._check_for_errors(data, visualization),
            'message': self._get_error_message(data, visualization),
            'suggestions': self._get_error_suggestions(data, visualization)
        }

    def _check_for_errors(self, data: Dict, visualization: Dict) -> bool:
        """检查错误"""
        # 实现错误检查逻辑
        pass

    def _get_error_message(self, data: Dict, visualization: Dict) -> str:
        """获取错误消息"""
        # 实现错误消息生成逻辑
        pass

    def _get_error_suggestions(self, data: Dict, visualization: Dict) -> List[str]:
        """获取错误建议"""
        # 实现错误建议生成逻辑
        pass

class QualityImprover:
    """质量改进器"""
    async def improve_quality(self, data: Dict, visualization: Dict, suggestions: List[str]) -> Dict:
        """改进质量"""
        return {
            'improvements': self._apply_improvements(data, visualization, suggestions),
            'quality_metrics': self._calculate_improved_metrics(data, visualization),
            'suggestions': self._get_improvement_suggestions(data, visualization)
        }

    def _apply_improvements(self, data: Dict, visualization: Dict, suggestions: List[str]) -> Dict:
        """应用改进"""
        # 实现改进应用逻辑
        pass

    def _calculate_improved_metrics(self, data: Dict, visualization: Dict) -> Dict:
        """计算改进指标"""
        # 实现改进指标计算逻辑
        pass

    def _get_improvement_suggestions(self, data: Dict, visualization: Dict) -> List[str]:
        """获取改进建议"""
        # 实现改进建议生成逻辑
        pass

class LayoutOverlapDetector:
    """布局重叠检测器"""
    
    def __init__(self):
        self.logger = AgentLogger()
    
    async def detect_overlaps(self, chart_config: Dict) -> Dict:
        """检测布局重叠问题"""
        try:
            issues = []
            fixes_applied = []
            
            # 1. 检测坐标轴标签重叠
            axis_issues = self._check_axis_label_overlap(chart_config)
            if axis_issues:
                issues.extend(axis_issues)
                fixes_applied.append("坐标轴标签优化")
            
            # 2. 检测图例位置问题
            legend_issues = self._check_legend_overlap(chart_config)
            if legend_issues:
                issues.extend(legend_issues)
                fixes_applied.append("图例位置优化")
            
            # 3. 检查标题位置问题
            title_issues = self._check_title_overlap(chart_config)
            if title_issues:
                issues.extend(title_issues)
                fixes_applied.append("标题位置优化")
            
            # 4. 检测数据标签重叠
            data_label_issues = self._check_data_label_overlap(chart_config)
            if data_label_issues:
                issues.extend(data_label_issues)
                fixes_applied.append("数据标签优化")
            
            # 5. 检测容器边距问题
            margin_issues = self._check_margin_issues(chart_config)
            if margin_issues:
                issues.extend(margin_issues)
                fixes_applied.append("边距优化")
            
            # 6. 检查与树图的重叠
            tree_series = [s for s in chart_config.get('series', []) if s.get('type') == 'tree']
            if tree_series:
                tree_config = tree_series[0]
                tree_top_px = self._convert_to_px(tree_config.get('top', '5%'), 600)
                if tree_top_px > 0 and title_bottom_px > tree_top_px:
                    issues.append("标题或副标题与树图节点重叠")
            
            has_overlaps = len(issues) > 0
            
            # 记录检测结果
            self.logger.log_interaction(
                'layout_detector',
                'master',
                '布局重叠检测完成',
                {
                    'has_overlaps': has_overlaps,
                    'issues_count': len(issues),
                    'issues': issues
                },
                'success' if not has_overlaps else 'warning'
            )
            
            return {
                'has_overlaps': has_overlaps,
                'issues': issues,
                'fixes_applied': fixes_applied,
                'overlap_score': self._calculate_overlap_score(issues),
                'suggestions': self._get_overlap_suggestions(issues)
            }
            
        except Exception as e:
            self.logger.log_interaction(
                'layout_detector',
                'master',
                '布局重叠检测失败',
                {'error': str(e)},
                'error'
            )
            return {
                'has_overlaps': False,
                'issues': [],
                'fixes_applied': [],
                'overlap_score': 100,
                'suggestions': ['检测过程中出现错误，建议手动检查布局']
            }
    
    def _check_axis_label_overlap(self, chart_config: Dict) -> List[str]:
        """检查坐标轴标签重叠"""
        issues = []
        
        # 检查x轴标签
        if 'xAxis' in chart_config:
            x_axis = chart_config['xAxis']
            if isinstance(x_axis, list):
                for axis in x_axis:
                    if self._has_long_labels(axis):
                        issues.append("x轴标签过长，可能导致重叠")
            else:
                if self._has_long_labels(x_axis):
                    issues.append("x轴标签过长，可能导致重叠")
        
        # 检查y轴标签
        if 'yAxis' in chart_config:
            y_axis = chart_config['yAxis']
            if isinstance(y_axis, list):
                for axis in y_axis:
                    if self._has_long_labels(axis):
                        issues.append("y轴标签过长，可能导致重叠")
            else:
                if self._has_long_labels(y_axis):
                    issues.append("y轴标签过长，可能导致重叠")
        
        return issues
    
    def _check_legend_overlap(self, chart_config: Dict) -> List[str]:
        """增强版：检查图例重叠问题，包括与标题、标签的空间关系"""
        issues = []
        if 'legend' in chart_config:
            legend = chart_config['legend']
            legend_data = legend.get('data', [])
            position = legend.get('orient', 'horizontal')
            # 1. 水平图例项过多
            if position == 'horizontal' and len(legend_data) > 3:
                issues.append("水平图例项较多，极易与标题或标签重叠")
            # 2. 图例未设置明确位置
            if 'left' not in legend and 'right' not in legend and 'top' not in legend and 'bottom' not in legend:
                issues.append("图例位置未明确设置，极易与标题或标签重叠")
            # 3. 图例与标题距离过近
            if 'top' in legend and 'title' in chart_config:
                legend_top = legend.get('top')
                title_top = chart_config['title'].get('top', 0)
                # 只要都设置了top且距离小于60像素/百分比很近就判为高风险
                if isinstance(legend_top, (int, float)) and isinstance(title_top, (int, float)):
                    if abs(legend_top - title_top) < 60:
                        issues.append("图例与标题距离过近，极易重叠")
                elif isinstance(legend_top, str) and isinstance(title_top, str):
                    if legend_top.endswith('%') and title_top.endswith('%'):
                        try:
                            if abs(float(legend_top.strip('%')) - float(title_top.strip('%'))) < 8:
                                issues.append("图例与标题距离过近，极易重叠")
                        except Exception:
                            pass
            # 4. 图例项文字过长
            for item in legend_data:
                if isinstance(item, str) and len(item) > 8:
                    issues.append("图例项文字过长，易导致重叠")
        return issues
    
    def _check_title_overlap(self, chart_config: Dict) -> List[str]:
        """检查标题和副标题是否与其他图表元素重叠"""
        issues = []
        title_config = chart_config.get('title', {})
        
        if isinstance(title_config, list):
            title_config = title_config[0] if title_config else {}

        if not title_config or not title_config.get('show', True):
            return issues

        # 1. 估算标题区域的底部位置 (单位: 像素)
        chart_height = 600  # 假设图表高度为600px
        title_bottom_px = 0
        try:
            title_top = title_config.get('top', 'auto')
            title_text_lines = len(str(title_config.get('text', '')).split('\n'))
            subtext_lines = len(str(title_config.get('subtext', '')).split('\n'))
            title_height_px = (title_text_lines * 1.2 + subtext_lines * 1) * (title_config.get('textStyle',{}).get('fontSize', 18) * 1.2)

            if title_top == 'auto' or title_top == 'top':
                title_bottom_px = (title_config.get('padding', [5,5,5,5])[0] or 5) + title_height_px
            elif isinstance(title_top, (int, float)):
                title_bottom_px = title_top + title_height_px
            elif isinstance(title_top, str) and '%' in title_top:
                title_bottom_px = (float(title_top.strip('%')) / 100 * chart_height) + title_height_px
        except Exception:
            # 如果估算失败，提前返回
            return issues

        if title_bottom_px <= 0:
            return issues

        # 2. 检查与 grid 的重叠 (适用于柱状图、折线图等)
        grid_config = chart_config.get('grid', {})
        if isinstance(grid_config, list):
            grid_config = grid_config[0] if grid_config else {}
        if grid_config:
            grid_top_px = self._convert_to_px(grid_config.get('top', 60), chart_height)
            if grid_top_px > 0 and title_bottom_px > grid_top_px:
                issues.append("标题或副标题与图表主体区域(grid)重叠")

        # 3. 检查与雷达图的重叠
        radar_config = chart_config.get('radar')
        if radar_config:
            if isinstance(radar_config, list):
                radar_config = radar_config[0] if radar_config else {}
            
            if radar_config and radar_config.get('indicator'):
                center_y = self._convert_to_px(radar_config.get('center', ['50%', '50%'])[1], chart_height)
                radius = self._convert_to_px(radar_config.get('radius', '75%'), min(chart_height, 800)) # 假设宽度最大800
                if center_y > 0 and radius > 0 and title_bottom_px > (center_y - radius):
                    issues.append("标题或副标题与雷达图指示器重叠")
                        
        # 4. 检查与饼图的重叠
        pie_series = [s for s in chart_config.get('series', []) if s.get('type') == 'pie']
        if pie_series:
            pie_config = pie_series[0]
            center_y = self._convert_to_px(pie_config.get('center', ['50%', '50%'])[1], chart_height)
            radius_str = pie_config.get('radius', '75%')
            outer_radius_str = radius_str[1] if isinstance(radius_str, list) else radius_str
            radius = self._convert_to_px(outer_radius_str, min(chart_height, 800) * 0.5)
            if center_y > 0 and radius > 0 and title_bottom_px > (center_y - radius):
                issues.append("标题或副标题与饼图重叠")

        # 5. 检查与树图的重叠
        tree_series = [s for s in chart_config.get('series', []) if s.get('type') == 'tree']
        if tree_series:
            tree_config = tree_series[0]
            tree_top_px = self._convert_to_px(tree_config.get('top', '5%'), chart_height)
            if tree_top_px > 0 and title_bottom_px > tree_top_px:
                issues.append("标题或副标题与树图节点重叠")

        return issues
    
    def _check_data_label_overlap(self, chart_config: Dict) -> List[str]:
        """增强版：检查数据标签重叠，包括标签内容长度和数量"""
        issues = []
        if 'series' in chart_config:
            series = chart_config['series']
            if isinstance(series, list):
                for s in series:
                    if s.get('label', {}).get('show', False):
                        data = s.get('data', [])
                        # 数据点过多
                        if len(data) > 10:
                            issues.append("数据点较多且启用标签，极易重叠")
                        # 标签内容过长
                        for item in data:
                            if isinstance(item, str) and len(item) > 8:
                                issues.append("数据标签内容过长，极易重叠")
        return issues
    
    def _check_margin_issues(self, chart_config: Dict) -> List[str]:
        """检查边距问题"""
        issues = []
        
        # 检查是否设置了grid边距
        if 'grid' not in chart_config:
            issues.append("未设置图表边距，可能导致文字与边缘重叠")
        else:
            grid = chart_config['grid']
            # 检查边距是否合理
            if grid.get('left', '10%') == '10%' and grid.get('right', '10%') == '10%':
                # 默认边距可能不够
                pass
        
        return issues
    
    def _has_long_labels(self, axis: Dict) -> bool:
        """检查轴是否有长标签"""
        if 'data' in axis:
            data = axis['data']
            if isinstance(data, list):
                label_values = [str(item) for item in data if isinstance(item, str) and item.strip()]
                if not label_values:
                    return False
                count = len(label_values)
                max_len = max(len(v) for v in label_values)
                avg_len = sum(len(v) for v in label_values) / count

                axis_label = axis.get('axisLabel', {}) if isinstance(axis.get('axisLabel', {}), dict) else {}
                rotate = axis_label.get('rotate', 0)
                has_formatter = callable(axis_label.get('formatter')) or ('formatter' in axis_label and axis_label.get('formatter') is not None)
                hide_overlap = bool(axis_label.get('hideOverlap', False))

                # If mitigation exists, use stricter threshold to avoid false positives.
                if rotate and abs(float(rotate)) >= 30:
                    return count >= 14 and max_len >= 20
                if has_formatter or hide_overlap:
                    return (count >= 12 and max_len >= 18) or (count >= 16 and avg_len >= 11)

                # Default risk threshold: many categories + long labels.
                return (count >= 8 and max_len >= 16) or (count >= 12 and avg_len >= 11)
        return False
    
    def _calculate_overlap_score(self, issues: List[str]) -> float:
        """计算重叠问题严重程度分数（0-100，0为最好）"""
        if not issues:
            return 0
        
        # 根据问题类型和数量计算分数
        score = 0
        for issue in issues:
            if "坐标轴标签" in issue:
                score += 20
            elif "图例" in issue:
                score += 15
            elif "标题" in issue:
                score += 10
            elif "数据标签" in issue:
                score += 25
            elif "边距" in issue:
                score += 15
            else:
                score += 10
        
        return min(score, 100)
    
    def _get_overlap_suggestions(self, issues: List[str]) -> List[str]:
        """获取重叠问题的解决建议"""
        suggestions = []
        
        for issue in issues:
            if "坐标轴标签" in issue:
                suggestions.append("建议旋转x轴标签45度或90度")
                suggestions.append("考虑减少标签显示间隔")
            elif "图例" in issue:
                suggestions.append("建议将图例放置在图表外部")
                suggestions.append("考虑使用垂直图例布局")
            elif "标题" in issue:
                suggestions.append("建议缩短标题长度")
                suggestions.append("考虑调整标题位置")
            elif "数据标签" in issue:
                suggestions.append("建议减少数据标签显示")
                suggestions.append("考虑使用交互式显示标签")
            elif "边距" in issue:
                suggestions.append("建议增加图表边距")
                suggestions.append("考虑调整图表容器大小")
        
        return list(set(suggestions))  # 去重

    def _get_element_rect(self, config: Dict, element: str, chart_width: int, chart_height: int) -> Optional[Dict[str, float]]:
        """估算图表元素的矩形边界 (top, right, bottom, left) in pixels."""
        if element == 'title':
            title_config = config.get('title', {})
            if isinstance(title_config, list):
                title_config = title_config[0] if title_config else {}
            if not title_config.get('show', True): return None

            top = self._convert_to_px(title_config.get('top', 'auto'), chart_height)
            left = self._convert_to_px(title_config.get('left', 'auto'), chart_width)
            if top == 0 and (title_config.get('top') == 'auto' or title_config.get('top') == 'top'): top = 10 # default top margin
            if left == 0 and (title_config.get('left') == 'auto' or title_config.get('left') == 'center'): left = chart_width * 0.1 
            
            width = chart_width * 0.8
            height = (len(str(title_config.get('text', '')).split('\n')) * 1.2 + len(str(title_config.get('subtext', '')).split('\n')) * 1) * (title_config.get('textStyle',{}).get('fontSize', 18) * 1.2)
            return {'top': top, 'right': left + width, 'bottom': top + height, 'left': left}

        if element == 'legend':
            legend_config = config.get('legend', {})
            if isinstance(legend_config, list):
                legend_config = legend_config[0] if legend_config else {}
            if not legend_config.get('show', True): return None

            top = self._convert_to_px(legend_config.get('top', 'auto'), chart_height)
            left = self._convert_to_px(legend_config.get('left', 'auto'), chart_width)
            if top == 0 and (legend_config.get('top') == 'auto' or legend_config.get('top') == 'top'): top = 10
            if left == 0 and (legend_config.get('left') == 'auto' or legend_config.get('left') == 'center'): left = chart_width * 0.2
                
            width = legend_config.get('width', chart_width * 0.6)
            height = legend_config.get('height', 30) # rough estimate
            return {'top': top, 'right': left + width, 'bottom': top + height, 'left': left}
        
        return None

    def _rects_overlap(self, rect1: Dict[str, float], rect2: Dict[str, float]) -> bool:
        """检查两个矩形是否重叠"""
        if not rect1 or not rect2:
            return False
        return not (rect1['right'] < rect2['left'] or rect1['left'] > rect2['right'] or rect1['bottom'] < rect2['top'] or rect1['top'] > rect2['bottom'])

    def detect_overlaps_sync(self, chart_config: Dict) -> Dict:
        """同步版本：使用边界框检测所有潜在的布局重叠问题"""
        issues = []
        chart_width, chart_height = 800, 600 # 假设图表尺寸

        # 1. 检测标题和图例的重叠
        title_rect = self._get_element_rect(chart_config, 'title', chart_width, chart_height)
        legend_rect = self._get_element_rect(chart_config, 'legend', chart_width, chart_height)

        if self._rects_overlap(title_rect, legend_rect):
            issues.append("标题与图例重叠")

        # Align with async detector: include axis/legend/title/data-label/margin checks.
        issues.extend(self._check_axis_label_overlap(chart_config))
        issues.extend(self._check_legend_overlap(chart_config))
        issues.extend(self._check_title_overlap(chart_config))
        issues.extend(self._check_data_label_overlap(chart_config))
        issues.extend(self._check_margin_issues(chart_config))

        has_overlaps = len(issues) > 0
        score = self._calculate_overlap_score(issues)
        suggestions = self._get_overlap_suggestions(issues) if has_overlaps else ["布局良好"]

        return {
            'has_overlaps': has_overlaps,
            'issues': list(set(issues)),
            'overlap_score': score,
            'suggestions': suggestions
        }

    def _convert_to_px(self, value: Union[str, int, float], total_pixels: int) -> float:
        """将echarts的单位（如'%'）统一转换为像素值"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            if '%' in value:
                return float(value.strip('%')) / 100 * total_pixels
            elif 'px' in value:
                return float(value.strip('px'))
        return 0

class AutoLayoutFixer:
    """自动布局修复器"""
    
    def __init__(self):
        self.logger = AgentLogger()
    
    async def fix_overlaps(self, chart_config: Dict, issues: List[str]) -> Dict:
        """自动修复布局重叠问题"""
        try:
            fixed_config = chart_config.copy()
            fixes_applied = []
            
            for issue in issues:
                if "坐标轴标签" in issue:
                    fixed_config = self._fix_axis_labels(fixed_config)
                    fixes_applied.append("坐标轴标签优化")
                
                elif "图例" in issue:
                    fixed_config = self._fix_legend_position(fixed_config)
                    fixes_applied.append("图例位置优化")
                
                elif "标题" in issue:
                    fixed_config = self._fix_title_position(fixed_config)
                    fixes_applied.append("标题位置优化")
                
                elif "数据标签" in issue:
                    fixed_config = self._fix_data_labels(fixed_config)
                    fixes_applied.append("数据标签优化")
                
                elif "边距" in issue:
                    fixed_config = self._fix_margins(fixed_config)
                    fixes_applied.append("边距优化")
            
            # 记录修复结果
            self.logger.log_interaction(
                'layout_fixer',
                'master',
                '布局修复完成',
                {
                    'issues_fixed': len(issues),
                    'fixes_applied': fixes_applied
                },
                'success'
            )
            
            return fixed_config
            
        except Exception as e:
            self.logger.log_interaction(
                'layout_fixer',
                'master',
                '布局修复失败',
                {'error': str(e)},
                'error'
            )
            return chart_config  # 返回原始配置
    
    def _fix_axis_labels(self, config: Dict) -> Dict:
        """修复坐标轴标签"""
        # 修复x轴标签
        if 'xAxis' in config:
            x_axis = config['xAxis']
            if isinstance(x_axis, list):
                for axis in x_axis:
                    axis['axisLabel'] = {
                        'rotate': 45,
                        'interval': 'auto',
                        'textStyle': {
                            'fontSize': 12
                        }
                    }
            else:
                x_axis['axisLabel'] = {
                    'rotate': 45,
                    'interval': 'auto',
                    'textStyle': {
                        'fontSize': 12
                    }
                }
        
        # 修复y轴标签
        if 'yAxis' in config:
            y_axis = config['yAxis']
            if isinstance(y_axis, list):
                for axis in y_axis:
                    axis['axisLabel'] = {
                        'interval': 'auto',
                        'textStyle': {
                            'fontSize': 12
                        }
                    }
            else:
                y_axis['axisLabel'] = {
                    'interval': 'auto',
                    'textStyle': {
                        'fontSize': 12
                    }
                }
        
        return config
    
    def _fix_legend_position(self, config: Dict) -> Dict:
        """修复图例位置重叠问题"""
        if 'legend' in config:
            if isinstance(config['legend'], list):
                if config['legend']:
                    config['legend'][0]['top'] = 'bottom'
                    config['legend'][0]['left'] = 'center'
            else:
                config['legend']['top'] = 'bottom'
                config['legend']['left'] = 'center'
        return config
    
    def _fix_title_position(self, config: Dict) -> Dict:
        """修复标题位置重叠问题（通用后备方案）"""
        if 'title' in config:
            # 默认调整标题位置到底部
            if isinstance(config['title'], list):
                if config['title']:
                    config['title'][0]['top'] = 'bottom'
                    config['title'][0]['left'] = 'center'
            else:
                config['title']['top'] = 'bottom'
                config['title']['left'] = 'center'
        return config
    
    def _fix_data_labels(self, config: Dict) -> Dict:
        """修复数据标签"""
        if 'series' in config:
            series = config['series']
            if isinstance(series, list):
                for s in series:
                    if 'label' in s:
                        # 优化数据标签显示
                        s['label'].update({
                            'show': False,  # 默认不显示
                            'position': 'top',
                            'fontSize': 10,
                            'formatter': '{c}'
                        })
        
        return config
    
    def _fix_margins(self, config: Dict) -> Dict:
        """修复边距"""
        # 设置合理的边距
        config['grid'] = {
            'left': '10%',
            'right': '15%',
            'top': '15%',
            'bottom': '15%',
            'containLabel': True
        }
        
        return config
    
    def _fix_radar_for_title(self, config: Dict) -> Dict:
        """为标题和副标题调整雷达图，避免重叠（更激进再加强）"""
        # 1. 获取副标题内容和字体大小
        subtext = ''
        subtext_fontsize = 14
        if 'title' in config:
            title = config['title']
            if isinstance(title, list):
                title = title[0] if title else {}
            subtext = title.get('subtext', '')
            if 'subtextStyle' in title and 'fontSize' in title['subtextStyle']:
                subtext_fontsize = title['subtextStyle']['fontSize']
            # 自动截断副标题
            if len(subtext) > 18:
                title['subtext'] = subtext[:18] + '...'
                subtext = title['subtext']
            # 自动多行换行（每8个字换行）
            if len(subtext) > 8:
                lines = [subtext[i:i+8] for i in range(0, len(subtext), 8)]
                title['subtext'] = '\n'.join(lines)
                subtext = title['subtext']
            # 增加title.padding，下方空间更大
            title['padding'] = [0, 0, 120, 0]
        # 2. 计算副标题高度（估算：字体大小*1.7*行数）
        subtext_lines = subtext.count('\n') + 1 if subtext else 1
        subtext_height = subtext_fontsize * 1.7 * subtext_lines

        # 3. 调整radar.top和radius
        if 'radar' in config:
            radar = config.get('radar')
            if isinstance(radar, list):
                radar = radar[0] if radar else {}
            if radar:
                radar['top'] = int(150 + subtext_height)
                radar['radius'] = '40%'
        return config

    def _fix_grid_for_title(self, config: Dict) -> Dict:
        """为标题调整grid"""
        if 'grid' in config:
            grid = config.get('grid')
            if isinstance(grid, list):
                grid = grid[0] if grid else {}

            if grid:
                current_top = grid.get('top', 60)
                if isinstance(current_top, (int, float)):
                    grid['top'] = current_top + 40
                elif isinstance(current_top, str) and '%' in current_top:
                    grid['top'] = f"{min(90, int(current_top.strip('%')) + 10)}%"
        return config

    def _fix_tree_for_title(self, config: Dict) -> Dict:
        """为标题调整树图"""
        tree_series = [s for s in config.get('series', []) if s.get('type') == 'tree']
        if tree_series:
            tree_config = tree_series[0]
            current_top = tree_config.get('top', '5%')
            
            if isinstance(current_top, (int, float)):
                tree_config['top'] = current_top + 60
            elif isinstance(current_top, str) and '%' in current_top:
                tree_config['top'] = f"{min(90, int(current_top.strip('%')) + 15)}%"
        return config

    def fix_overlaps_sync(self, chart_config: Dict, issues: List[str]) -> Dict:
        """同步版本：自动修复布局重叠问题"""
        config = chart_config.copy()
        fixes_applied = []

        for issue in issues:
            if ("坐标轴标签重叠" in issue) or ("x轴标签过长" in issue) or ("y轴标签过长" in issue) or ("坐标轴标签" in issue):
                config = self._fix_axis_labels(config)
                fixes_applied.append("自动调整坐标轴标签避免重叠")
            elif "图例重叠" in issue or "标题与图例重叠" in issue:
                config = self._fix_legend_position(config)
                fixes_applied.append("自动调整图例位置避免与标题重叠")
            elif "标题或副标题与雷达图指示器重叠" in issue:
                config = self._fix_radar_for_title(config)
                fixes_applied.append("自动缩小雷达图为标题让出空间")
            elif "标题或副标题与图表主体区域(grid)重叠" in issue:
                config = self._fix_grid_for_title(config)
                fixes_applied.append("自动调整图表边距为标题让出空间")
            elif "标题或副标题与树图节点重叠" in issue:
                config = self._fix_tree_for_title(config)
                fixes_applied.append("自动调整树图布局为标题让出空间")
            elif "标题" in issue:  # 通用标题问题作为后备
                config = self._fix_title_position(config)
                fixes_applied.append("自动调整标题位置")
            elif ("数据标签重叠" in issue) or ("数据点较多且启用标签" in issue) or ("数据标签内容过长" in issue):
                config = self._fix_data_labels(config)
                fixes_applied.append("自动优化数据标签显示")
            elif ("边距不足" in issue) or ("边距" in issue):
                config = self._fix_margins(config)
                fixes_applied.append("自动调整图表边距")

        # --- 树状图专用增强修复 ---
        tree_series = [s for s in config.get('series', []) if s.get('type') == 'tree']
        if tree_series:
            tree = tree_series[0]
            # 自动调整节点大小
            tree['symbolSize'] = 14
            # 自动调整层间距和节点间距
            tree['nodePadding'] = 40
            tree['layerPadding'] = 80
            # 节点数多时自动横向布局
            def count_nodes(node):
                if not node: return 0
                count = 1
                for child in node.get('children', []):
                    count += count_nodes(child)
                return count
            total_nodes = 0
            for node in tree.get('data', []):
                total_nodes += count_nodes(node)
            if total_nodes > 8:
                tree['orient'] = 'LR'
                tree['top'] = 60
                tree['left'] = 80
                tree['right'] = 80
                tree['bottom'] = 40
            # 自动缩小字体
            tree['label'] = tree.get('label', {})
            tree['label']['fontSize'] = 12 if total_nodes <= 10 else 10
            # 自动截断过长内容
            def truncate(node, maxlen=8):
                if 'name' in node and len(node['name']) > maxlen:
                    node['name'] = node['name'][:maxlen] + '...'
                for child in node.get('children', []):
                    truncate(child, maxlen)
            for node in tree.get('data', []):
                truncate(node)
            fixes_applied.append("树状图布局智能优化")

        return {"fixed_config": config, "fixes_applied": list(set(fixes_applied))} 

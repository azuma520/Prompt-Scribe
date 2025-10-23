#!/usr/bin/env python3
"""
應用測試場景（E1）
測試實際應用場景
"""

import sqlite3
import time
from typing import List, Dict, Tuple

from .base import BaseTestScenario, TestResult, QualityIssue


class ScenarioE1_PromptGeneration(BaseTestScenario):
    """場景 E1: Prompt 生成流程測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'E1'
    
    @property
    def name(self) -> str:
        return 'Prompt 生成流程測試'
    
    @property
    def dimension(self) -> str:
        return 'Application'
    
    @property
    def description(self) -> str:
        return '模擬完整的 AI 繪圖 Prompt 生成流程'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # 6 個 Prompt 維度查詢
        dimensions = [
            ('角色數量', 'CHARACTER_RELATED', 'CHARACTER_COUNT', 100000, 5),
            ('髮型髮色', 'CHARACTER_RELATED', 'HAIR', 50000, 15),
            ('服裝配飾', 'CHARACTER_RELATED', 'CLOTHING', 50000, 20),
            ('姿態表情', 'ACTION_POSE', None, 30000, 15),
            ('場景環境', 'ENVIRONMENT', None, 20000, 10),
            ('藝術風格', 'ART_STYLE', None, 10000, 8)
        ]
        
        query_results = []
        dimension_stats = []
        
        for dim_name, main_cat, sub_cat, min_usage, min_options in dimensions:
            if sub_cat:
                sql = f"""
                SELECT name, post_count, classification_confidence
                FROM tags_final
                WHERE main_category = '{main_cat}'
                  AND sub_category = '{sub_cat}'
                  AND post_count > {min_usage}
                ORDER BY post_count DESC
                LIMIT 50
                """
            else:
                sql = f"""
                SELECT name, post_count, classification_confidence
                FROM tags_final
                WHERE main_category = '{main_cat}'
                  AND post_count > {min_usage}
                ORDER BY post_count DESC
                LIMIT 50
                """
            
            results = self._execute_query(cursor, sql)
            
            # 統計這個維度
            avg_conf = sum(r['classification_confidence'] for r in results if r['classification_confidence']) / len(results) if results else 0
            
            dimension_stats.append({
                'dimension': dim_name,
                'available_options': len(results),
                'min_required': min_options,
                'avg_confidence': round(avg_conf, 3),
                'status': 'PASS' if len(results) >= min_options else 'FAIL'
            })
            
            query_results.extend(results)
        
        # 驗證結果
        passed, issues = self.validate_results(dimension_stats)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            'Prompt維度數': len(dimension_stats),
            '通過維度數': len([d for d in dimension_stats if d['status'] == 'PASS']),
            '總可用選項': len(query_results),
            '平均信心度': f"{sum(d['avg_confidence'] for d in dimension_stats) / len(dimension_stats):.3f}" if dimension_stats else "0"
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=dimension_stats,  # 返回統計數據而非原始結果
            issues=issues,
            metrics=metrics
        )
    
    def validate_results(self, dimension_stats: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查每個維度的選項充足性
        for stat in dimension_stats:
            if stat['status'] == 'FAIL':
                issues.append(QualityIssue(
                    issue_type='INSUFFICIENT_OPTIONS',
                    severity='P1',
                    description=f'{stat["dimension"]} 維度選項不足: {stat["available_options"]} (需要: {stat["min_required"]})',
                    affected_tags=[],
                    recommendation=f'增加 {stat["dimension"]} 相關標籤的分類',
                    scenario_id=self.scenario_id
                ))
            
            # 檢查信心度
            if stat['avg_confidence'] < 0.80:
                issues.append(QualityIssue(
                    issue_type='LOW_DIMENSION_CONFIDENCE',
                    severity='P2',
                    description=f'{stat["dimension"]} 維度平均信心度較低: {stat["avg_confidence"]:.3f}',
                    affected_tags=[],
                    recommendation='審查該維度標籤的分類品質',
                    scenario_id=self.scenario_id
                ))
        
        passed = len([i for i in issues if i.severity in ['P0', 'P1']]) == 0
        return passed, issues


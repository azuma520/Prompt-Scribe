#!/usr/bin/env python3
"""
性能測試場景（D1）
測試查詢效率
"""

import sqlite3
import time
from typing import List, Dict, Tuple

from .base import BaseTestScenario, TestResult, QualityIssue


class ScenarioD1_QueryPerformance(BaseTestScenario):
    """場景 D1: 複雜查詢效率測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'D1'
    
    @property
    def name(self) -> str:
        return '複雜查詢效率測試'
    
    @property
    def dimension(self) -> str:
        return 'Performance'
    
    @property
    def description(self) -> str:
        return '確保實際應用查詢的響應速度'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        query_results = []
        performance_data = []
        
        # 測試查詢列表
        test_queries = [
            ('單條件查詢', """
                SELECT name, post_count, classification_confidence
                FROM tags_final
                WHERE main_category = 'CHARACTER_RELATED'
                  AND sub_category = 'CLOTHING'
                ORDER BY post_count DESC
                LIMIT 100
            """, 50),  # 目標 <50ms
            
            ('多條件組合查詢', """
                SELECT name, main_category, sub_category, post_count
                FROM tags_final
                WHERE (
                    (main_category = 'CHARACTER_RELATED' AND sub_category IN ('HAIR', 'CLOTHING', 'ACCESSORIES'))
                    OR (main_category = 'ACTION_POSE' AND sub_category = 'EXPRESSION')
                    OR (main_category = 'ENVIRONMENT')
                )
                AND post_count > 10000
                ORDER BY post_count DESC
                LIMIT 50
            """, 200),  # 目標 <200ms
            
            ('聚合查詢', """
                SELECT 
                    main_category,
                    sub_category,
                    COUNT(*) as count,
                    AVG(post_count) as avg_usage
                FROM tags_final
                WHERE post_count > 1000
                GROUP BY main_category, sub_category
                ORDER BY count DESC
            """, 100),  # 目標 <100ms
            
            ('全文搜索', """
                SELECT name, main_category, sub_category, post_count
                FROM tags_final
                WHERE name LIKE '%blue%'
                  AND main_category IS NOT NULL
                ORDER BY post_count DESC
                LIMIT 20
            """, 500)  # 目標 <500ms
        ]
        
        # 執行並測量每個查詢
        for query_name, sql, target_ms in test_queries:
            exec_time = self._measure_query(cursor, sql)
            exec_ms = exec_time * 1000
            
            # 獲取查詢計劃
            plan = self._get_query_plan(cursor, sql)
            
            performance_data.append({
                'query_name': query_name,
                'execution_time_ms': round(exec_ms, 2),
                'target_ms': target_ms,
                'status': 'PASS' if exec_ms < target_ms else 'FAIL',
                'query_plan': plan
            })
        
        query_results = performance_data
        
        # 驗證結果
        passed, issues = self.validate_results(performance_data)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            '測試查詢數': len(performance_data),
            '通過查詢數': len([p for p in performance_data if p['status'] == 'PASS']),
            '平均執行時間': f"{sum(p['execution_time_ms'] for p in performance_data) / len(performance_data):.2f}ms",
            '最慢查詢': max((p['execution_time_ms'] for p in performance_data))
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics
        )
    
    def _measure_query(self, cursor: sqlite3.Cursor, sql: str, runs: int = 3) -> float:
        """測量查詢性能
        
        Args:
            cursor: 資料庫游標
            sql: SQL 查詢
            runs: 執行次數（取平均）
            
        Returns:
            平均執行時間（秒）
        """
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            cursor.execute(sql)
            cursor.fetchall()
            times.append(time.perf_counter() - start)
        
        # 排除第一次（冷啟動），取平均
        return sum(times[1:]) / (runs - 1) if runs > 1 else times[0]
    
    def _get_query_plan(self, cursor: sqlite3.Cursor, sql: str) -> str:
        """獲取查詢計劃
        
        Args:
            cursor: 資料庫游標
            sql: SQL 查詢
            
        Returns:
            查詢計劃字符串
        """
        try:
            cursor.execute(f"EXPLAIN QUERY PLAN {sql}")
            plan_rows = cursor.fetchall()
            return "; ".join([str(row) for row in plan_rows])
        except Exception:
            return "無法獲取查詢計劃"
    
    def validate_results(self, performance_data: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查每個查詢是否達標
        for perf in performance_data:
            if perf['status'] == 'FAIL':
                exec_time = perf['execution_time_ms']
                target = perf['target_ms']
                
                severity = 'P1' if exec_time < target * 2 else 'P0'
                issues.append(QualityIssue(
                    issue_type='SLOW_QUERY',
                    severity=severity,
                    description=f'{perf["query_name"]} 執行過慢: {exec_time:.2f}ms (目標: <{target}ms)',
                    affected_tags=[],
                    recommendation='考慮添加索引或優化查詢',
                    scenario_id=self.scenario_id
                ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


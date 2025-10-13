#!/usr/bin/env python3
"""
一致性測試場景（C1-C2）
測試分類邏輯的一致性
"""

import sqlite3
import time
from typing import List, Dict, Tuple

from .base import BaseTestScenario, TestResult, QualityIssue


class ScenarioC1_PatternConsistency(BaseTestScenario):
    """場景 C1: 同類標籤一致性測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'C1'
    
    @property
    def name(self) -> str:
        return '同類標籤一致性測試'
    
    @property
    def dimension(self) -> str:
        return 'Consistency'
    
    @property
    def description(self) -> str:
        return '確保相似模式的標籤分類一致'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # 查詢 1: 眼睛標籤一致性
        sql_eyes = """
        WITH eye_tags AS (
            SELECT name, main_category, sub_category, post_count
            FROM tags_final
            WHERE name LIKE '%_eyes'
              AND main_category IS NOT NULL
        )
        SELECT 
            main_category,
            sub_category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM eye_tags), 2) as consistency_rate
        FROM eye_tags
        GROUP BY main_category, sub_category
        ORDER BY count DESC
        """
        
        # 查詢 2: 頭髮標籤一致性
        sql_hair = """
        WITH hair_tags AS (
            SELECT name, main_category, sub_category, post_count
            FROM tags_final
            WHERE name LIKE '%_hair'
              AND main_category IS NOT NULL
        )
        SELECT 
            main_category,
            sub_category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM hair_tags), 2) as consistency_rate
        FROM hair_tags
        GROUP BY main_category, sub_category
        ORDER BY count DESC
        """
        
        # 執行查詢
        eyes_consistency = self._execute_query(cursor, sql_eyes)
        hair_consistency = self._execute_query(cursor, sql_hair)
        
        query_results = eyes_consistency + hair_consistency
        
        # 驗證結果
        passed, issues = self.validate_results(eyes_consistency, hair_consistency)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            '眼睛標籤一致性': f"{eyes_consistency[0]['consistency_rate']:.2f}%" if eyes_consistency else "0%",
            '頭髮標籤一致性': f"{hair_consistency[0]['consistency_rate']:.2f}%" if hair_consistency else "0%",
            '眼睛標籤分類數': len(eyes_consistency),
            '頭髮標籤分類數': len(hair_consistency)
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics
        )
    
    def validate_results(self, eyes: List[Dict], hair: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查眼睛標籤一致性
        if eyes:
            top_consistency = eyes[0]['consistency_rate']
            if top_consistency < 95:
                issues.append(QualityIssue(
                    issue_type='PATTERN_INCONSISTENCY',
                    severity='P1',
                    description=f'眼睛標籤一致性不足: {top_consistency:.2f}% (目標: >95%)',
                    affected_tags=[],
                    recommendation='統一眼睛標籤的分類到 CHARACTER_RELATED/BODY_PARTS',
                    scenario_id=self.scenario_id
                ))
            
            if len(eyes) > 2:
                issues.append(QualityIssue(
                    issue_type='PATTERN_INCONSISTENCY',
                    severity='P2',
                    description=f'眼睛標籤有 {len(eyes)} 種不同分類',
                    affected_tags=[],
                    recommendation='檢查並統一眼睛標籤的分類',
                    scenario_id=self.scenario_id
                ))
        
        # 檢查頭髮標籤一致性
        if hair:
            top_consistency = hair[0]['consistency_rate']
            if top_consistency < 95:
                issues.append(QualityIssue(
                    issue_type='PATTERN_INCONSISTENCY',
                    severity='P1',
                    description=f'頭髮標籤一致性不足: {top_consistency:.2f}% (目標: >95%)',
                    affected_tags=[],
                    recommendation='統一頭髮標籤的分類到 CHARACTER_RELATED/HAIR',
                    scenario_id=self.scenario_id
                ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


class ScenarioC2_SourceQuality(BaseTestScenario):
    """場景 C2: 分類來源品質對比測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'C2'
    
    @property
    def name(self) -> str:
        return '分類來源品質對比測試'
    
    @property
    def dimension(self) -> str:
        return 'Consistency'
    
    @property
    def description(self) -> str:
        return '比較不同分類方法的品質差異'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # 查詢: 各分類來源品質統計
        sql = """
        SELECT 
            classification_source,
            COUNT(*) as tag_count,
            ROUND(AVG(CASE WHEN classification_confidence IS NOT NULL THEN classification_confidence ELSE 0 END), 3) as avg_confidence,
            ROUND(MIN(CASE WHEN classification_confidence IS NOT NULL THEN classification_confidence ELSE 0 END), 3) as min_confidence,
            ROUND(MAX(CASE WHEN classification_confidence IS NOT NULL THEN classification_confidence ELSE 1 END), 3) as max_confidence
        FROM tags_final
        WHERE classification_source IS NOT NULL
        GROUP BY classification_source
        ORDER BY tag_count DESC
        """
        
        # 執行查詢
        query_results = self._execute_query(cursor, sql)
        
        # 驗證結果
        passed, issues = self.validate_results(query_results)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        llm_sources = [r for r in query_results if 'batch' in r['classification_source'].lower() or 'llm' in r['classification_source'].lower()]
        llm_avg_conf = sum(r['avg_confidence'] for r in llm_sources) / len(llm_sources) if llm_sources else 0
        
        metrics = {
            '分類來源數': len(query_results),
            'LLM來源數': len(llm_sources),
            'LLM平均信心度': f"{llm_avg_conf:.3f}",
            '最低平均信心度來源': query_results[-1]['classification_source'] if query_results else 'N/A'
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics
        )
    
    def validate_results(self, query_results: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查 LLM 來源的平均信心度
        llm_sources = [r for r in query_results if 'batch' in r['classification_source'].lower() or 'llm' in r['classification_source'].lower()]
        
        for source in llm_sources:
            if source['avg_confidence'] < 0.85:
                issues.append(QualityIssue(
                    issue_type='LOW_SOURCE_QUALITY',
                    severity='P1',
                    description=f'{source["classification_source"]} 平均信心度過低: {source["avg_confidence"]:.3f} (目標: >0.85)',
                    affected_tags=[],
                    recommendation='審查該來源的分類品質',
                    scenario_id=self.scenario_id
                ))
        
        # 檢查是否有來源信心度過低
        low_quality_sources = [r for r in query_results if r['avg_confidence'] < 0.70]
        if low_quality_sources:
            issues.append(QualityIssue(
                issue_type='VERY_LOW_SOURCE_QUALITY',
                severity='P0',
                description=f'{len(low_quality_sources)} 個來源平均信心度 <0.70',
                affected_tags=[],
                recommendation='審查並可能重新分類這些來源的標籤',
                scenario_id=self.scenario_id
            ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


#!/usr/bin/env python3
"""
完整性測試場景（A1-A3）
測試數據覆蓋的完整性
"""

import sqlite3
import time
from typing import List, Dict, Tuple

from .base import BaseTestScenario, TestResult, QualityIssue


class ScenarioA1_MainCategoryCoverage(BaseTestScenario):
    """場景 A1: 主分類覆蓋度測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'A1'
    
    @property
    def name(self) -> str:
        return '主分類覆蓋度測試'
    
    @property
    def dimension(self) -> str:
        return 'Completeness'
    
    @property
    def description(self) -> str:
        return '驗證所有主分類都有合理的標籤分布'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # SQL 查詢
        sql = """
        SELECT 
            main_category,
            COUNT(*) as tag_count,
            SUM(post_count) as total_usage,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL), 2) as tag_percentage,
            ROUND(SUM(post_count) * 100.0 / (SELECT SUM(post_count) FROM tags_final WHERE main_category IS NOT NULL), 2) as usage_percentage
        FROM tags_final
        WHERE main_category IS NOT NULL
        GROUP BY main_category
        ORDER BY tag_count DESC
        """
        
        # 執行查詢
        query_results = self._execute_query(cursor, sql)
        
        # 驗證結果
        passed, issues = self.validate_results(query_results)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            '主分類數量': len(query_results),
            '預期數量': 17,
            '最大標籤占比': f"{max([r['tag_percentage'] for r in query_results]):.2f}%" if query_results else "0%"
        }
        
        # 確定狀態
        status = 'PASS' if passed and not issues else ('WARN' if issues else 'FAIL')
        
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
        
        # 檢查 1: 是否有 17 個主分類
        category_count = len(query_results)
        if category_count < 17:
            issues.append(QualityIssue(
                issue_type='MISSING_CATEGORIES',
                severity='P0',
                description=f'主分類數量不足: {category_count}/17',
                affected_tags=[],
                recommendation='檢查分類系統定義，確保所有主分類都有標籤',
                scenario_id=self.scenario_id
            ))
        
        # 檢查 2: 分布是否過於集中
        if query_results:
            max_percentage = max([r['tag_percentage'] for r in query_results])
            if max_percentage > 60:
                dominant_cat = next(r['main_category'] for r in query_results 
                                  if r['tag_percentage'] == max_percentage)
                issues.append(QualityIssue(
                    issue_type='DISTRIBUTION_IMBALANCE',
                    severity='P1',
                    description=f'分類分布過於集中: {dominant_cat} 占 {max_percentage:.2f}%',
                    affected_tags=[],
                    recommendation='檢查是否有過度分類或分類錯誤',
                    scenario_id=self.scenario_id
                ))
        
        passed = category_count >= 17 and len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


class ScenarioA2_FrequencyCoverage(BaseTestScenario):
    """場景 A2: 頻率段覆蓋度測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'A2'
    
    @property
    def name(self) -> str:
        return '頻率段覆蓋度測試'
    
    @property
    def dimension(self) -> str:
        return 'Completeness'
    
    @property
    def description(self) -> str:
        return '確保各頻率段達到目標覆蓋率'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # SQL 查詢
        sql = """
        SELECT 
            CASE 
                WHEN post_count >= 1000000 THEN '1. 超高頻 (>=1M)'
                WHEN post_count >= 100000 THEN '2. 極高頻 (100K-1M)'
                WHEN post_count >= 50000 THEN '3. 高頻 (50K-100K)'
                WHEN post_count >= 10000 THEN '4. 中高頻 (10K-50K)'
                WHEN post_count >= 5000 THEN '5. 中頻 (5K-10K)'
                WHEN post_count >= 1000 THEN '6. 中低頻 (1K-5K)'
                WHEN post_count >= 100 THEN '7. 低頻 (100-1K)'
                ELSE '8. 極低頻 (<100)'
            END as frequency_range,
            COUNT(*) as total_tags,
            SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified_tags,
            COUNT(*) - SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as unclassified_tags,
            ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage_rate
        FROM tags_final
        GROUP BY 
            CASE 
                WHEN post_count >= 1000000 THEN 1
                WHEN post_count >= 100000 THEN 2
                WHEN post_count >= 50000 THEN 3
                WHEN post_count >= 10000 THEN 4
                WHEN post_count >= 5000 THEN 5
                WHEN post_count >= 1000 THEN 6
                WHEN post_count >= 100 THEN 7
                ELSE 8
            END
        ORDER BY frequency_range
        """
        
        # 執行查詢
        query_results = self._execute_query(cursor, sql)
        
        # 驗證結果
        passed, issues = self.validate_results(query_results)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            '頻率段數量': len(query_results),
            '100%覆蓋的頻率段': len([r for r in query_results if r['coverage_rate'] == 100]),
            '最低覆蓋率': f"{min([r['coverage_rate'] for r in query_results]):.2f}%" if query_results else "0%"
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
        
        # 定義各頻率段的目標覆蓋率
        targets = {
            '1. 超高頻 (>=1M)': 100.0,
            '2. 極高頻 (100K-1M)': 100.0,
            '3. 高頻 (50K-100K)': 100.0,
            '4. 中高頻 (10K-50K)': 99.0,
            '5. 中頻 (5K-10K)': 99.0,
            '6. 中低頻 (1K-5K)': 99.0,
            '7. 低頻 (100-1K)': 90.0
        }
        
        # 檢查每個頻率段
        for result in query_results:
            freq_range = result['frequency_range']
            coverage = result['coverage_rate']
            target = targets.get(freq_range, 0)
            
            if coverage < target:
                severity = 'P0' if coverage < target - 5 else 'P1'
                issues.append(QualityIssue(
                    issue_type='INSUFFICIENT_COVERAGE',
                    severity=severity,
                    description=f'{freq_range} 覆蓋率不足: {coverage:.2f}% (目標: {target}%)',
                    affected_tags=[],
                    recommendation=f'處理 {result["unclassified_tags"]} 個待分類標籤',
                    scenario_id=self.scenario_id
                ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


class ScenarioA3_DanbooruMapping(BaseTestScenario):
    """場景 A3: Danbooru 轉換完整性測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'A3'
    
    @property
    def name(self) -> str:
        return 'Danbooru 轉換完整性測試'
    
    @property
    def dimension(self) -> str:
        return 'Completeness'
    
    @property
    def description(self) -> str:
        return '驗證 Danbooru 原生分類 100% 正確轉換'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # SQL 查詢
        sql = """
        SELECT 
            danbooru_cat,
            CASE danbooru_cat
                WHEN 0 THEN '一般標籤 (General)'
                WHEN 1 THEN '藝術家 (Artist)'
                WHEN 3 THEN '版權 (Copyright)'
                WHEN 4 THEN '角色 (Character)'
                WHEN 5 THEN '元標籤 (Meta)'
                ELSE '未知類別'
            END as category_name,
            COUNT(*) as total_tags,
            SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified_tags,
            COUNT(*) - SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as unclassified_tags,
            ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage_rate,
            SUM(CASE 
                WHEN danbooru_cat = 1 AND main_category = 'ARTIST' THEN 1
                WHEN danbooru_cat = 3 AND main_category = 'COPYRIGHT' THEN 1
                WHEN danbooru_cat = 4 AND main_category = 'CHARACTER' THEN 1
                WHEN danbooru_cat = 5 AND main_category IN ('TECHNICAL', 'QUALITY') THEN 1
                WHEN danbooru_cat = 0 THEN 1
                ELSE 0
            END) as correct_mapping
        FROM tags_final
        GROUP BY danbooru_cat
        ORDER BY danbooru_cat
        """
        
        # 執行查詢
        query_results = self._execute_query(cursor, sql)
        
        # 驗證結果
        passed, issues = self.validate_results(query_results)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            'Danbooru分類數': len(query_results),
            'ARTIST覆蓋率': next((r['coverage_rate'] for r in query_results if r['danbooru_cat'] == 1), 0),
            'COPYRIGHT覆蓋率': next((r['coverage_rate'] for r in query_results if r['danbooru_cat'] == 3), 0),
            'CHARACTER覆蓋率': next((r['coverage_rate'] for r in query_results if r['danbooru_cat'] == 4), 0),
            'GENERAL覆蓋率': next((r['coverage_rate'] for r in query_results if r['danbooru_cat'] == 0), 0)
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
        
        # Danbooru 分類轉換目標
        targets = {
            1: ('ARTIST', 100.0),      # Artist 應 100% 轉換
            3: ('COPYRIGHT', 100.0),   # Copyright 應 100% 轉換
            4: ('CHARACTER', 100.0),   # Character 應 100% 轉換
            5: ('TECHNICAL', 100.0),   # Meta 應 100% 轉換
            0: ('GENERAL', 84.0)       # General 目標 84%+
        }
        
        for result in query_results:
            cat = result['danbooru_cat']
            coverage = result['coverage_rate']
            
            if cat in targets:
                target_cat, target_coverage = targets[cat]
                
                if coverage < target_coverage:
                    severity = 'P0' if cat in [1, 3, 4, 5] else 'P1'
                    issues.append(QualityIssue(
                        issue_type='DANBOORU_MAPPING_INCOMPLETE',
                        severity=severity,
                        description=f'{result["category_name"]} 覆蓋率不足: {coverage:.2f}% (目標: {target_coverage}%)',
                        affected_tags=[],
                        recommendation=f'檢查 danbooru_cat={cat} 的轉換邏輯',
                        scenario_id=self.scenario_id
                    ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


#!/usr/bin/env python3
"""
準確性測試場景（B1-B3）
測試分類的準確性和信心度
"""

import sqlite3
import time
from typing import List, Dict, Tuple

from .base import BaseTestScenario, TestResult, QualityIssue


class ScenarioB1_SubcategoryAccuracy(BaseTestScenario):
    """場景 B1: 副分類邏輯準確性測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'B1'
    
    @property
    def name(self) -> str:
        return '副分類邏輯準確性測試'
    
    @property
    def dimension(self) -> str:
        return 'Accuracy'
    
    @property
    def description(self) -> str:
        return '驗證副分類規則的正確執行'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # 查詢 1: 眼睛標籤檢查
        sql_eyes = """
        SELECT '眼睛顏色標籤檢查' as test_name,
               COUNT(*) as total_tags,
               SUM(CASE WHEN main_category = 'CHARACTER_RELATED' AND sub_category = 'BODY_PARTS' THEN 1 ELSE 0 END) as correct_tags,
               COUNT(*) - SUM(CASE WHEN main_category = 'CHARACTER_RELATED' AND sub_category = 'BODY_PARTS' THEN 1 ELSE 0 END) as incorrect_tags,
               ROUND(SUM(CASE WHEN main_category = 'CHARACTER_RELATED' AND sub_category = 'BODY_PARTS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as accuracy_rate
        FROM tags_final
        WHERE name LIKE '%_eyes' OR name LIKE '%_eye'
        """
        
        # 查詢 2: 頭髮標籤檢查
        sql_hair = """
        SELECT '頭髮標籤檢查' as test_name,
               COUNT(*) as total_tags,
               SUM(CASE WHEN main_category = 'CHARACTER_RELATED' AND sub_category = 'HAIR' THEN 1 ELSE 0 END) as correct_tags,
               COUNT(*) - SUM(CASE WHEN main_category = 'CHARACTER_RELATED' AND sub_category = 'HAIR' THEN 1 ELSE 0 END) as incorrect_tags,
               ROUND(SUM(CASE WHEN main_category = 'CHARACTER_RELATED' AND sub_category = 'HAIR' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as accuracy_rate
        FROM tags_final
        WHERE name LIKE '%_hair' OR name LIKE '%_bangs' OR name LIKE '%_ponytail'
        """
        
        # 查詢 3: 列出誤分類案例
        sql_misclassified = """
        SELECT name, main_category, sub_category, post_count, classification_confidence
        FROM tags_final
        WHERE (
            (name LIKE '%_eyes' AND (main_category != 'CHARACTER_RELATED' OR sub_category != 'BODY_PARTS'))
            OR
            (name LIKE '%_hair' AND (main_category != 'CHARACTER_RELATED' OR sub_category != 'HAIR'))
        )
        AND main_category IS NOT NULL
        ORDER BY post_count DESC
        LIMIT 50
        """
        
        # 執行所有查詢
        eyes_result = self._execute_query(cursor, sql_eyes)
        hair_result = self._execute_query(cursor, sql_hair)
        misclassified = self._execute_query(cursor, sql_misclassified)
        
        query_results = eyes_result + hair_result + misclassified
        
        # 驗證結果
        passed, issues = self.validate_results(eyes_result + hair_result, misclassified)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            '眼睛標籤準確率': f"{eyes_result[0]['accuracy_rate']:.2f}%" if eyes_result else "0%",
            '頭髮標籤準確率': f"{hair_result[0]['accuracy_rate']:.2f}%" if hair_result else "0%",
            '誤分類數量': len(misclassified),
            '高頻誤分類': len([m for m in misclassified if m['post_count'] > 10000])
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics
        )
    
    def validate_results(self, stats: List[Dict], misclassified: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查準確率
        for stat in stats:
            accuracy = stat['accuracy_rate']
            test_name = stat['test_name']
            
            if accuracy < 95:
                issues.append(QualityIssue(
                    issue_type='LOW_SUBCATEGORY_ACCURACY',
                    severity='P0' if accuracy < 90 else 'P1',
                    description=f'{test_name} 準確率過低: {accuracy:.2f}% (目標: >95%)',
                    affected_tags=[],
                    recommendation='檢查副分類規則，修正誤分類標籤',
                    scenario_id=self.scenario_id
                ))
        
        # 檢查高頻誤分類
        high_freq_errors = [m for m in misclassified if m['post_count'] > 10000]
        if high_freq_errors:
            issues.append(QualityIssue(
                issue_type='HIGH_FREQ_MISCLASSIFICATION',
                severity='P0',
                description=f'發現 {len(high_freq_errors)} 個高頻誤分類標籤',
                affected_tags=[m['name'] for m in high_freq_errors],
                recommendation='優先修復高頻標籤的分類',
                scenario_id=self.scenario_id
            ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


class ScenarioB2_ConfidenceDistribution(BaseTestScenario):
    """場景 B2: 信心度分布驗證測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'B2'
    
    @property
    def name(self) -> str:
        return '信心度分布驗證測試'
    
    @property
    def dimension(self) -> str:
        return 'Accuracy'
    
    @property
    def description(self) -> str:
        return '確保分類品質穩定且可靠'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # 查詢 1: 各主分類信心度統計
        sql_by_category = """
        SELECT 
            main_category,
            COUNT(*) as total_tags,
            ROUND(AVG(classification_confidence), 3) as avg_confidence,
            ROUND(MIN(classification_confidence), 3) as min_confidence,
            ROUND(MAX(classification_confidence), 3) as max_confidence,
            SUM(CASE WHEN classification_confidence < 0.75 THEN 1 ELSE 0 END) as low_conf_count,
            ROUND(SUM(CASE WHEN classification_confidence < 0.75 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as low_conf_rate
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
        GROUP BY main_category
        ORDER BY avg_confidence DESC
        """
        
        # 查詢 2: 整體信心度分布
        sql_distribution = """
        SELECT 
            CASE 
                WHEN classification_confidence >= 0.95 THEN '極高 (>=0.95)'
                WHEN classification_confidence >= 0.90 THEN '高 (0.90-0.95)'
                WHEN classification_confidence >= 0.85 THEN '中高 (0.85-0.90)'
                WHEN classification_confidence >= 0.80 THEN '中等 (0.80-0.85)'
                WHEN classification_confidence >= 0.75 THEN '中低 (0.75-0.80)'
                WHEN classification_confidence >= 0.60 THEN '低 (0.60-0.75)'
                ELSE '極低 (<0.60)'
            END as confidence_level,
            COUNT(*) as tag_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final WHERE classification_confidence IS NOT NULL), 2) as percentage
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
        GROUP BY confidence_level
        ORDER BY MIN(classification_confidence) DESC
        """
        
        # 執行查詢
        by_category = self._execute_query(cursor, sql_by_category)
        distribution = self._execute_query(cursor, sql_distribution)
        
        query_results = by_category + distribution
        
        # 驗證結果
        passed, issues = self.validate_results(by_category, distribution)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算整體平均信心度
        cursor.execute("SELECT AVG(classification_confidence) FROM tags_final WHERE classification_confidence IS NOT NULL")
        overall_avg = cursor.fetchone()[0] or 0
        
        # 計算指標
        metrics = {
            '整體平均信心度': f"{overall_avg:.3f}",
            '高信心度標籤占比': next((r['percentage'] for r in distribution if '極高' in r['confidence_level'] or '高' in r['confidence_level']), 0),
            '低信心度標籤占比': sum(r['percentage'] for r in distribution if '低' in r['confidence_level'] or '極低' in r['confidence_level']),
            '最低平均信心度分類': by_category[-1]['main_category'] if by_category else 'N/A'
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics
        )
    
    def validate_results(self, by_category: List[Dict], distribution: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查各主分類平均信心度
        for cat in by_category:
            avg_conf = cat['avg_confidence']
            if avg_conf and avg_conf < 0.70:
                issues.append(QualityIssue(
                    issue_type='LOW_CATEGORY_CONFIDENCE',
                    severity='P0',
                    description=f'{cat["main_category"]} 平均信心度過低: {avg_conf:.3f} (目標: >0.70)',
                    affected_tags=[],
                    recommendation=f'審查 {cat["main_category"]} 分類的低信心度標籤',
                    scenario_id=self.scenario_id
                ))
        
        # 檢查低信心度標籤占比
        low_conf_percentage = sum(r['percentage'] for r in distribution if '低' in r['confidence_level'] or '極低' in r['confidence_level'])
        if low_conf_percentage > 10:
            issues.append(QualityIssue(
                issue_type='HIGH_LOW_CONFIDENCE_RATE',
                severity='P1',
                description=f'低信心度標籤占比過高: {low_conf_percentage:.2f}% (目標: <10%)',
                affected_tags=[],
                recommendation='審查並重新分類低信心度標籤',
                scenario_id=self.scenario_id
            ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


class ScenarioB3_EdgeCases(BaseTestScenario):
    """場景 B3: 邊界案例處理測試"""
    
    @property
    def scenario_id(self) -> str:
        return 'B3'
    
    @property
    def name(self) -> str:
        return '邊界案例處理測試'
    
    @property
    def dimension(self) -> str:
        return 'Accuracy'
    
    @property
    def description(self) -> str:
        return '驗證模糊和特殊案例的處理正確性'
    
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試"""
        start_time = time.perf_counter()
        
        # 查詢 1: NULL 字符串檢查
        sql_null = """
        SELECT name, main_category, sub_category, post_count
        FROM tags_final
        WHERE main_category = 'null' OR sub_category = 'null'
        ORDER BY post_count DESC
        LIMIT 50
        """
        
        # 查詢 2: 成人內容分類檢查
        sql_adult = """
        SELECT name, main_category, sub_category, post_count, classification_confidence
        FROM tags_final
        WHERE (name LIKE '%nude%' OR name LIKE '%naked%' OR name LIKE '%nsfw%' 
           OR name LIKE '%sex%' OR name LIKE '%penis%' OR name LIKE '%vagina%')
        AND main_category IS NOT NULL
        ORDER BY post_count DESC
        LIMIT 30
        """
        
        # 查詢 3: 極低信心度標籤
        sql_low_conf = """
        SELECT name, main_category, sub_category, post_count, classification_confidence
        FROM tags_final
        WHERE classification_confidence IS NOT NULL
          AND classification_confidence < 0.60
          AND post_count > 10000
        ORDER BY post_count DESC
        """
        
        # 執行查詢
        null_tags = self._execute_query(cursor, sql_null)
        adult_tags = self._execute_query(cursor, sql_adult)
        low_conf_tags = self._execute_query(cursor, sql_low_conf)
        
        query_results = null_tags + adult_tags + low_conf_tags
        
        # 驗證結果
        passed, issues = self.validate_results(null_tags, adult_tags, low_conf_tags)
        
        execution_time = time.perf_counter() - start_time
        
        # 計算指標
        metrics = {
            'NULL字符串標籤': len(null_tags),
            '成人內容標籤數': len(adult_tags),
            '極低信心度高頻標籤': len(low_conf_tags),
            '成人內容正確率': f"{sum(1 for t in adult_tags if t['main_category'] == 'ADULT_CONTENT') / len(adult_tags) * 100:.2f}%" if adult_tags else "N/A"
        }
        
        status = 'PASS' if passed else ('WARN' if issues else 'FAIL')
        
        return self._create_result(
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics
        )
    
    def validate_results(self, null_tags: List[Dict], adult_tags: List[Dict], low_conf_tags: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證結果"""
        issues = []
        
        # 檢查 NULL 字符串
        if len(null_tags) > 20:
            issues.append(QualityIssue(
                issue_type='NULL_STRING',
                severity='P0',
                description=f'發現 {len(null_tags)} 個 NULL 字符串標籤 (目標: <20)',
                affected_tags=[t['name'] for t in null_tags],
                recommendation='運行 quality_optimizer.py 修復 NULL 字符串問題',
                scenario_id=self.scenario_id
            ))
        elif len(null_tags) > 0:
            issues.append(QualityIssue(
                issue_type='NULL_STRING',
                severity='P1',
                description=f'發現 {len(null_tags)} 個 NULL 字符串標籤',
                affected_tags=[t['name'] for t in null_tags],
                recommendation='建議修復 NULL 字符串問題',
                scenario_id=self.scenario_id
            ))
        
        # 檢查成人內容分類
        adult_incorrect = [t for t in adult_tags if t['main_category'] != 'ADULT_CONTENT']
        if adult_incorrect:
            issues.append(QualityIssue(
                issue_type='ADULT_CONTENT_MISCLASSIFICATION',
                severity='P0',
                description=f'{len(adult_incorrect)} 個成人內容標籤未正確分類',
                affected_tags=[t['name'] for t in adult_incorrect],
                recommendation='將這些標籤重新分類到 ADULT_CONTENT',
                scenario_id=self.scenario_id
            ))
        
        # 檢查極低信心度標籤
        if len(low_conf_tags) > 10:
            issues.append(QualityIssue(
                issue_type='VERY_LOW_CONFIDENCE',
                severity='P1',
                description=f'發現 {len(low_conf_tags)} 個極低信心度高頻標籤 (目標: <10)',
                affected_tags=[t['name'] for t in low_conf_tags],
                recommendation='審查並重新分類這些標籤',
                scenario_id=self.scenario_id
            ))
        
        passed = len([i for i in issues if i.severity == 'P0']) == 0
        return passed, issues


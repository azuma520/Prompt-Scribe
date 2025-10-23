#!/usr/bin/env python3
"""
測試場景基礎模組
定義所有測試場景和結果的核心數據結構
"""

import sqlite3
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
from datetime import datetime


@dataclass
class TestScenario:
    """測試場景數據模型"""
    id: str                           # 場景 ID (如 'A1', 'B2')
    name: str                         # 場景名稱
    dimension: str                    # 測試維度 (Completeness/Accuracy/...)
    description: str                  # 測試描述
    sql_queries: List[str]            # SQL 查詢列表
    success_criteria: Dict            # 成功標準
    priority: str                     # 優先級 (P0/P1/P2)


@dataclass
class QualityIssue:
    """品質問題數據模型"""
    issue_type: str                   # 問題類型
    severity: str                     # 嚴重程度 (P0/P1/P2)
    description: str                  # 問題描述
    affected_tags: List[str]          # 受影響的標籤
    recommendation: str               # 修復建議
    scenario_id: str                  # 發現問題的場景
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.severity}] {self.issue_type}: {self.description}"


@dataclass
class TestResult:
    """測試結果數據模型"""
    scenario_id: str                  # 關聯的場景 ID
    status: str                       # 狀態 (PASS/FAIL/WARN/ERROR)
    execution_time: float             # 執行時間（秒）
    query_results: List[Dict]         # 查詢結果
    issues: List[QualityIssue]        # 發現的問題
    metrics: Dict                     # 測試指標
    timestamp: str                    # 執行時間戳
    error: str = ""                   # 錯誤訊息（若有）
    
    def __post_init__(self):
        """後初始化處理"""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == 'PASS'
    
    def has_warnings(self) -> bool:
        """是否有警告"""
        return self.status == 'WARN' or len(self.issues) > 0
    
    def get_p0_issues(self) -> List[QualityIssue]:
        """獲取 P0 級別問題"""
        return [issue for issue in self.issues if issue.severity == 'P0']
    
    def get_p1_issues(self) -> List[QualityIssue]:
        """獲取 P1 級別問題"""
        return [issue for issue in self.issues if issue.severity == 'P1']


class BaseTestScenario(ABC):
    """測試場景抽象基類
    
    所有測試場景都應繼承此類並實現抽象方法
    """
    
    @property
    @abstractmethod
    def scenario_id(self) -> str:
        """場景 ID（如 'A1', 'B2'）"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """場景名稱"""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> str:
        """測試維度（Completeness/Accuracy/Consistency/Performance/Application）"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """測試描述"""
        pass
    
    @abstractmethod
    def execute(self, cursor: sqlite3.Cursor) -> TestResult:
        """執行測試場景
        
        Args:
            cursor: 資料庫游標
            
        Returns:
            測試結果
        """
        pass
    
    @abstractmethod
    def validate_results(self, query_results: List[Dict]) -> Tuple[bool, List[QualityIssue]]:
        """驗證測試結果
        
        Args:
            query_results: 查詢結果列表
            
        Returns:
            (是否通過, 問題清單)
        """
        pass
    
    def _execute_query(self, cursor: sqlite3.Cursor, sql: str) -> List[Dict]:
        """執行 SQL 查詢並返回字典格式結果
        
        Args:
            cursor: 資料庫游標
            sql: SQL 查詢語句
            
        Returns:
            查詢結果列表（字典格式）
        """
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def _create_result(self, 
                      status: str, 
                      execution_time: float,
                      query_results: List[Dict],
                      issues: List[QualityIssue],
                      metrics: Dict,
                      error: str = "") -> TestResult:
        """創建測試結果對象
        
        Args:
            status: 測試狀態
            execution_time: 執行時間
            query_results: 查詢結果
            issues: 問題清單
            metrics: 測試指標
            error: 錯誤訊息
            
        Returns:
            測試結果對象
        """
        return TestResult(
            scenario_id=self.scenario_id,
            status=status,
            execution_time=execution_time,
            query_results=query_results,
            issues=issues,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            error=error
        )
    
    def get_info(self) -> TestScenario:
        """獲取場景資訊
        
        Returns:
            場景數據對象
        """
        return TestScenario(
            id=self.scenario_id,
            name=self.name,
            dimension=self.dimension,
            description=self.description,
            sql_queries=[],  # 由子類填充
            success_criteria={},  # 由子類填充
            priority='P0'
        )


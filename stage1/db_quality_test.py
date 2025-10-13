#!/usr/bin/env python3
"""
資料庫品質測試主腳本
執行所有測試場景並生成報告
"""

import sqlite3
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from test_scenarios.base import BaseTestScenario, TestResult, QualityIssue
from report_generator import ReportGenerator
from config import DB_PATH, OUTPUT_DIR


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseQualityTest:
    """資料庫品質測試主類別"""
    
    def __init__(self, db_path: str = None):
        """初始化測試器
        
        Args:
            db_path: 資料庫路徑（默認使用 config.DB_PATH）
        """
        self.db_path = db_path or DB_PATH
        self.scenarios: List[BaseTestScenario] = []
        self.results: Dict[str, TestResult] = {}
        self.report_generator = ReportGenerator()
        
        # 驗證資料庫存在
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"資料庫文件不存在: {self.db_path}")
    
    def load_scenarios(self) -> None:
        """載入所有測試場景"""
        logger.info("載入測試場景...")
        
        try:
            # 動態導入測試場景模組
            from test_scenarios import completeness_tests
            from test_scenarios import accuracy_tests
            from test_scenarios import consistency_tests
            from test_scenarios import performance_tests
            from test_scenarios import application_tests
            
            # 收集所有場景實例
            for module in [completeness_tests, accuracy_tests, consistency_tests, 
                          performance_tests, application_tests]:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseTestScenario) and 
                        attr != BaseTestScenario):
                        try:
                            scenario = attr()
                            self.scenarios.append(scenario)
                        except Exception as e:
                            logger.warning(f"無法實例化場景 {attr_name}: {e}")
            
            logger.info(f"成功載入 {len(self.scenarios)} 個測試場景")
            
        except ImportError as e:
            logger.error(f"載入測試場景失敗: {e}")
            logger.info("部分測試場景可能尚未實現")
    
    def run_all_tests(self) -> Dict[str, TestResult]:
        """執行所有測試場景
        
        Returns:
            場景 ID -> 測試結果的字典
        """
        logger.info("="*80)
        logger.info("開始執行資料庫品質測試")
        logger.info("="*80)
        
        if not self.scenarios:
            logger.warning("未找到任何測試場景")
            return {}
        
        # 連接資料庫
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            total = len(self.scenarios)
            for i, scenario in enumerate(sorted(self.scenarios, key=lambda s: s.scenario_id), 1):
                logger.info(f"\n[{i}/{total}] 執行場景 {scenario.scenario_id}: {scenario.name}")
                logger.info("-" * 60)
                
                try:
                    result = scenario.execute(cursor)
                    self.results[scenario.scenario_id] = result
                    
                    # 輸出結果
                    status_str = f"[{result.status}]"
                    logger.info(f"結果: {status_str} (執行時間: {result.execution_time:.3f}s)")
                    
                    if result.issues:
                        logger.warning(f"發現 {len(result.issues)} 個問題")
                        for issue in result.issues[:3]:  # 只顯示前 3 個
                            logger.warning(f"  - [{issue.severity}] {issue.description}")
                    
                except Exception as e:
                    logger.error(f"場景 {scenario.scenario_id} 執行失敗: {e}")
                    self.results[scenario.scenario_id] = TestResult(
                        scenario_id=scenario.scenario_id,
                        status='ERROR',
                        execution_time=0.0,
                        query_results=[],
                        issues=[],
                        metrics={},
                        timestamp=datetime.now().isoformat(),
                        error=str(e)
                    )
                    continue
            
            logger.info("\n" + "="*80)
            logger.info("所有測試執行完成")
            logger.info("="*80)
            
            return self.results
            
        finally:
            conn.close()
    
    def run_scenario(self, scenario_id: str) -> Optional[TestResult]:
        """執行單一測試場景
        
        Args:
            scenario_id: 場景 ID（如 'A1', 'B2'）
            
        Returns:
            測試結果，若場景不存在則返回 None
        """
        scenario = next((s for s in self.scenarios if s.scenario_id == scenario_id), None)
        
        if not scenario:
            logger.error(f"場景 {scenario_id} 不存在")
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            logger.info(f"執行場景 {scenario_id}: {scenario.name}")
            result = scenario.execute(cursor)
            self.results[scenario_id] = result
            return result
        finally:
            conn.close()
    
    def run_dimension(self, dimension: str) -> Dict[str, TestResult]:
        """執行特定維度的所有場景
        
        Args:
            dimension: 維度名稱（如 'Completeness', 'Accuracy'）
            
        Returns:
            場景 ID -> 測試結果的字典
        """
        dimension_scenarios = [s for s in self.scenarios if s.dimension == dimension]
        
        if not dimension_scenarios:
            logger.error(f"維度 {dimension} 沒有測試場景")
            return {}
        
        logger.info(f"執行 {dimension} 維度的 {len(dimension_scenarios)} 個場景")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        dimension_results = {}
        try:
            for scenario in dimension_scenarios:
                try:
                    result = scenario.execute(cursor)
                    self.results[scenario.scenario_id] = result
                    dimension_results[scenario.scenario_id] = result
                except Exception as e:
                    logger.error(f"場景 {scenario.scenario_id} 執行失敗: {e}")
                    continue
        finally:
            conn.close()
        
        return dimension_results
    
    def generate_reports(self, format_type: str = 'markdown') -> None:
        """生成測試報告
        
        Args:
            format_type: 報告格式（markdown/json/both）
        """
        if not self.results:
            logger.warning("沒有測試結果，無法生成報告")
            return
        
        # 收集所有問題
        all_issues = []
        for result in self.results.values():
            all_issues.extend(result.issues)
        
        # 生成報告
        if format_type in ['markdown', 'both']:
            self.report_generator.generate_markdown_report(
                self.results, 
                all_issues,
                f"{OUTPUT_DIR}/DB_QUALITY_TEST_REPORT.md"
            )
        
        if format_type in ['json', 'both']:
            self.report_generator.generate_json_report(
                self.results,
                f"{OUTPUT_DIR}/test_results.json"
            )


def safe_print(text: str) -> None:
    """Unicode 安全的輸出函數
    
    Args:
        text: 要輸出的文本
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # 移除無法編碼的字符
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='資料庫品質測試工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python db_quality_test.py                    # 執行所有測試
  python db_quality_test.py --scenario A1      # 執行特定場景
  python db_quality_test.py --dimension Completeness  # 執行特定維度
  python db_quality_test.py --format both      # 生成 Markdown 和 JSON 報告
        """
    )
    
    parser.add_argument('--scenario', type=str, help='執行特定場景（如 A1, B2）')
    parser.add_argument('--dimension', type=str, help='執行特定維度（如 Completeness）')
    parser.add_argument('--format', type=str, default='markdown',
                       choices=['markdown', 'json', 'both'],
                       help='報告格式（默認: markdown）')
    parser.add_argument('--verbose', action='store_true', help='詳細輸出模式')
    parser.add_argument('--output', type=str, help='輸出目錄（默認: output/）')
    parser.add_argument('--db', type=str, help='資料庫路徑（默認: output/tags.db）')
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化測試器
        db_path = args.db if args.db else None
        tester = DatabaseQualityTest(db_path=db_path)
        
        # 載入測試場景
        tester.load_scenarios()
        
        if not tester.scenarios:
            safe_print("錯誤: 未找到任何測試場景")
            safe_print("提示: 請確保已實現測試場景模組")
            sys.exit(1)
        
        # 執行測試
        if args.scenario:
            # 執行單一場景
            result = tester.run_scenario(args.scenario)
            if not result:
                sys.exit(1)
        elif args.dimension:
            # 執行特定維度
            tester.run_dimension(args.dimension)
        else:
            # 執行所有測試
            tester.run_all_tests()
        
        # 生成報告
        logger.info("\n生成測試報告...")
        tester.generate_reports(format_type=args.format)
        
        # 顯示摘要
        summary = tester.report_generator.generate_summary(tester.results)
        safe_print("\n" + "="*80)
        safe_print("測試摘要")
        safe_print("="*80)
        safe_print(f"總場景: {summary['total']}")
        safe_print(f"通過: {summary['passed']}")
        safe_print(f"警告: {summary['warned']}")
        safe_print(f"失敗: {summary['failed']}")
        safe_print(f"錯誤: {summary['errors']}")
        safe_print(f"總問題數: {summary['total_issues']}")
        safe_print(f"執行時間: {summary['total_time']:.2f} 秒")
        safe_print("="*80)
        
        # 退出碼
        if summary['errors'] > 0 or summary['failed'] > 0:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"測試執行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


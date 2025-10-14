#!/usr/bin/env python3
"""
測試報告生成器
生成 Markdown 和 JSON 格式的測試報告
"""

from typing import Dict, List
from datetime import datetime
from pathlib import Path
import json


class ReportGenerator:
    """測試報告生成器"""
    
    def __init__(self):
        """初始化報告生成器"""
        self.timestamp = datetime.now()
    
    def generate_markdown_report(self, 
                                results: Dict,
                                issues: List,
                                output_path: str = "output/DB_QUALITY_TEST_REPORT.md") -> None:
        """生成 Markdown 格式報告
        
        Args:
            results: 測試結果字典 {scenario_id: TestResult}
            issues: 所有問題清單
            output_path: 輸出路徑
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 標題
            f.write("# 資料庫品質測試報告\n\n")
            f.write(f"**執行日期**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**資料庫**: output/tags.db (Plan C Phase 3 Complete)\n")
            f.write(f"**測試版本**: v1.0\n\n")
            f.write("---\n\n")
            
            # 執行摘要
            f.write("## 📊 執行摘要\n\n")
            summary = self.generate_summary(results)
            f.write(f"- **總場景**: {summary['total']}\n")
            f.write(f"- **通過**: {summary['passed']} ✅\n")
            f.write(f"- **警告**: {summary['warned']} ⚠️\n")
            f.write(f"- **失敗**: {summary['failed']} ❌\n")
            f.write(f"- **錯誤**: {summary['errors']}\n")
            f.write(f"- **執行時間**: {summary['total_time']:.2f} 秒\n\n")
            
            # 詳細結果
            f.write("---\n\n")
            f.write("## 📝 詳細結果\n\n")
            
            # 按維度組織結果
            by_dimension = {}
            for scenario_id, result in results.items():
                dimension = self._get_dimension_from_id(scenario_id)
                if dimension not in by_dimension:
                    by_dimension[dimension] = []
                by_dimension[dimension].append((scenario_id, result))
            
            dimension_names = {
                'A': 'A 組: 數據完整性 (Completeness)',
                'B': 'B 組: 分類準確性 (Accuracy)',
                'C': 'C 組: 數據一致性 (Consistency)',
                'D': 'D 組: 查詢性能 (Performance)',
                'E': 'E 組: 實際應用 (Application)'
            }
            
            for dim in ['A', 'B', 'C', 'D', 'E']:
                if dim in by_dimension:
                    f.write(f"### {dimension_names[dim]}\n\n")
                    
                    for scenario_id, result in sorted(by_dimension[dim]):
                        status_icon = self._get_status_icon(result.status)
                        f.write(f"#### {scenario_id}: {self._get_scenario_name(scenario_id)} {status_icon}\n\n")
                        f.write(f"- **狀態**: {result.status}\n")
                        f.write(f"- **執行時間**: {result.execution_time:.3f} 秒\n")
                        
                        # 關鍵指標
                        if result.metrics:
                            f.write(f"- **關鍵指標**:\n")
                            for key, value in result.metrics.items():
                                f.write(f"  - {key}: {value}\n")
                        
                        # 發現的問題
                        if result.issues:
                            f.write(f"- **發現問題**: {len(result.issues)} 個\n")
                        
                        # 錯誤訊息
                        if result.error:
                            f.write(f"- **錯誤**: {result.error}\n")
                        
                        f.write("\n")
            
            # 問題總結
            f.write("---\n\n")
            f.write("## ⚠️ 問題總結\n\n")
            
            if not issues:
                f.write("✅ **未發現品質問題**\n\n")
            else:
                # 按嚴重程度分組
                p0_issues = [i for i in issues if i.severity == 'P0']
                p1_issues = [i for i in issues if i.severity == 'P1']
                p2_issues = [i for i in issues if i.severity == 'P2']
                
                if p0_issues:
                    f.write("### P0 問題（必須修復）\n\n")
                    for i, issue in enumerate(p0_issues, 1):
                        f.write(f"{i}. **[{issue.scenario_id}] {issue.issue_type}**\n")
                        f.write(f"   - 描述: {issue.description}\n")
                        if issue.affected_tags:
                            f.write(f"   - 受影響標籤: {len(issue.affected_tags)} 個\n")
                        f.write(f"   - 修復建議: {issue.recommendation}\n\n")
                
                if p1_issues:
                    f.write("### P1 問題（建議修復）\n\n")
                    for i, issue in enumerate(p1_issues, 1):
                        f.write(f"{i}. **[{issue.scenario_id}] {issue.issue_type}**\n")
                        f.write(f"   - 描述: {issue.description}\n")
                        if issue.affected_tags:
                            f.write(f"   - 受影響標籤: {len(issue.affected_tags)} 個\n")
                        f.write(f"   - 修復建議: {issue.recommendation}\n\n")
                
                if p2_issues:
                    f.write("### P2 問題（可選優化）\n\n")
                    for i, issue in enumerate(p2_issues, 1):
                        f.write(f"{i}. **[{issue.scenario_id}] {issue.issue_type}**\n")
                        f.write(f"   - 描述: {issue.description}\n\n")
            
            # 修復建議總結
            f.write("---\n\n")
            f.write("## 🔧 修復建議\n\n")
            self._write_recommendations(f, issues)
            
            # 結論
            f.write("---\n\n")
            f.write("## 🎯 結論\n\n")
            if summary['passed'] >= summary['total'] * 0.9:
                f.write("✅ **資料庫品質優秀！** 大部分測試通過，可以進入 Stage 2。\n\n")
            elif summary['passed'] >= summary['total'] * 0.7:
                f.write("⚠️ **資料庫品質良好** 部分問題需要關注，建議修復後再進入 Stage 2。\n\n")
            else:
                f.write("❌ **資料庫品質需要改善** 發現多個問題，建議先進行品質優化。\n\n")
        
        print(f"Markdown 報告已生成: {output_file}")
    
    def generate_json_report(self, 
                            results: Dict,
                            output_path: str = "output/test_results.json") -> None:
        """生成 JSON 格式報告
        
        Args:
            results: 測試結果字典
            output_path: 輸出路徑
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 轉換為可序列化的格式
        json_data = {
            'timestamp': self.timestamp.isoformat(),
            'summary': self.generate_summary(results),
            'results': {}
        }
        
        for scenario_id, result in results.items():
            json_data['results'][scenario_id] = {
                'status': result.status,
                'execution_time': result.execution_time,
                'metrics': result.metrics,
                'issues_count': len(result.issues),
                'issues': [
                    {
                        'type': issue.issue_type,
                        'severity': issue.severity,
                        'description': issue.description,
                        'affected_count': len(issue.affected_tags),
                        'recommendation': issue.recommendation
                    }
                    for issue in result.issues
                ],
                'error': result.error
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"JSON 報告已生成: {output_file}")
    
    def generate_summary(self, results: Dict) -> Dict:
        """生成執行摘要
        
        Args:
            results: 測試結果字典
            
        Returns:
            摘要統計
        """
        summary = {
            'total': len(results),
            'passed': sum(1 for r in results.values() if r.status == 'PASS'),
            'warned': sum(1 for r in results.values() if r.status == 'WARN'),
            'failed': sum(1 for r in results.values() if r.status == 'FAIL'),
            'errors': sum(1 for r in results.values() if r.status == 'ERROR'),
            'total_time': sum(r.execution_time for r in results.values()),
            'total_issues': sum(len(r.issues) for r in results.values())
        }
        return summary
    
    def format_table(self, data: List[Dict], columns: List[str] = None) -> str:
        """格式化表格
        
        Args:
            data: 數據列表
            columns: 欄位列表（若無則使用第一行的 keys）
            
        Returns:
            Markdown 表格字符串
        """
        if not data:
            return ""
        
        if columns is None:
            columns = list(data[0].keys())
        
        # 表頭
        lines = []
        lines.append("| " + " | ".join(str(col) for col in columns) + " |")
        lines.append("|" + "|".join("---" for _ in columns) + "|")
        
        # 數據行
        for row in data:
            values = [str(row.get(col, '')) for col in columns]
            lines.append("| " + " | ".join(values) + " |")
        
        return "\n".join(lines)
    
    def _get_dimension_from_id(self, scenario_id: str) -> str:
        """從場景 ID 獲取維度"""
        return scenario_id[0] if scenario_id else 'Unknown'
    
    def _get_status_icon(self, status: str) -> str:
        """獲取狀態圖標"""
        icons = {
            'PASS': '✅',
            'WARN': '⚠️',
            'FAIL': '❌',
            'ERROR': '🔴'
        }
        return icons.get(status, '❓')
    
    def _get_scenario_name(self, scenario_id: str) -> str:
        """獲取場景名稱"""
        names = {
            'A1': '主分類覆蓋度測試',
            'A2': '頻率段覆蓋度測試',
            'A3': 'Danbooru 轉換完整性測試',
            'B1': '副分類邏輯準確性測試',
            'B2': '信心度分布驗證測試',
            'B3': '邊界案例處理測試',
            'C1': '同類標籤一致性測試',
            'C2': '分類來源品質對比測試',
            'D1': '複雜查詢效率測試',
            'E1': 'Prompt 生成流程測試'
        }
        return names.get(scenario_id, scenario_id)
    
    def _write_recommendations(self, f, issues: List) -> None:
        """寫入修復建議
        
        Args:
            f: 文件對象
            issues: 問題清單
        """
        if not issues:
            f.write("✅ 無需修復建議\n\n")
            return
        
        # 按問題類型分組建議
        by_type = {}
        for issue in issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)
        
        for issue_type, issue_list in by_type.items():
            f.write(f"### {issue_type}\n\n")
            f.write(f"發現 {len(issue_list)} 個相關問題\n\n")
            f.write(f"**建議**:\n")
            # 使用第一個問題的建議（同類型問題建議通常相似）
            f.write(f"{issue_list[0].recommendation}\n\n")


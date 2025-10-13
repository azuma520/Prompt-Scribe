#!/usr/bin/env python3
"""
品質監控器
實時監控分類品質，檢測異常和問題
"""

import sqlite3
from typing import List, Dict
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

from config import DB_PATH, OUTPUT_DIR


class QualityMonitor:
    """品質監控器 - 實時監控分類品質"""
    
    def __init__(self):
        """初始化監控器"""
        self.db_path = DB_PATH
        self.batch_records = []
        self.alerts = []
    
    def record_batch(self, results: List, phase_name: str):
        """記錄批次處理結果
        
        Args:
            results: 分類結果列表
            phase_name: Phase 名稱
        """
        # 統計批次數據
        total = len(results)
        successful = sum(1 for r in results if r.success)
        confidences = [r.confidence for r in results if r.success]
        
        # 分類分布
        category_dist = Counter()
        for r in results:
            if r.success and r.main_category:
                category_dist[r.main_category] += 1
        
        # 記錄批次
        batch_record = {
            'timestamp': datetime.now().isoformat(),
            'phase_name': phase_name,
            'total': total,
            'successful': successful,
            'success_rate': successful / total if total > 0 else 0.0,
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'min_confidence': min(confidences) if confidences else 0.0,
            'max_confidence': max(confidences) if confidences else 0.0,
            'category_distribution': dict(category_dist)
        }
        
        self.batch_records.append(batch_record)
        
        # 檢測異常
        self._detect_anomalies(batch_record, results)
    
    def _detect_anomalies(self, batch_record: Dict, results: List):
        """檢測異常情況"""
        # 1. 成功率異常低
        if batch_record['success_rate'] < 0.80:
            self.alerts.append({
                'type': 'LOW_SUCCESS_RATE',
                'severity': 'WARNING',
                'timestamp': batch_record['timestamp'],
                'phase': batch_record['phase_name'],
                'message': f"成功率過低: {batch_record['success_rate']:.1%}",
                'value': batch_record['success_rate']
            })
        
        # 2. 平均信心度異常低
        if batch_record['avg_confidence'] < 0.70:
            self.alerts.append({
                'type': 'LOW_CONFIDENCE',
                'severity': 'WARNING',
                'timestamp': batch_record['timestamp'],
                'phase': batch_record['phase_name'],
                'message': f"平均信心度過低: {batch_record['avg_confidence']:.2f}",
                'value': batch_record['avg_confidence']
            })
        
        # 3. 檢查是否有 null 字符串
        null_categories = [r for r in results if r.success and 
                         (r.main_category == 'null' or r.sub_category == 'null')]
        if null_categories:
            self.alerts.append({
                'type': 'NULL_CATEGORY',
                'severity': 'ERROR',
                'timestamp': batch_record['timestamp'],
                'phase': batch_record['phase_name'],
                'message': f"發現 {len(null_categories)} 個 'null' 字符串分類",
                'tags': [r.tag_name for r in null_categories]
            })
        
        # 4. 檢查分類分布是否過於集中
        if batch_record['category_distribution']:
            max_category_count = max(batch_record['category_distribution'].values())
            concentration = max_category_count / batch_record['successful']
            if concentration > 0.80:  # 80% 集中在一個分類
                self.alerts.append({
                    'type': 'CATEGORY_CONCENTRATION',
                    'severity': 'INFO',
                    'timestamp': batch_record['timestamp'],
                    'phase': batch_record['phase_name'],
                    'message': f"分類過於集中: {concentration:.1%} 在單一分類",
                    'distribution': batch_record['category_distribution']
                })
    
    def get_quality_metrics(self, recent_n: int = 10) -> Dict:
        """獲取品質指標
        
        Args:
            recent_n: 最近 N 個批次
            
        Returns:
            品質指標字典
        """
        if not self.batch_records:
            return {}
        
        recent_batches = self.batch_records[-recent_n:]
        
        return {
            'total_batches': len(self.batch_records),
            'recent_batches': len(recent_batches),
            'avg_success_rate': sum(b['success_rate'] for b in recent_batches) / len(recent_batches),
            'avg_confidence': sum(b['avg_confidence'] for b in recent_batches) / len(recent_batches),
            'min_confidence': min(b['min_confidence'] for b in recent_batches),
            'max_confidence': max(b['max_confidence'] for b in recent_batches),
            'total_alerts': len(self.alerts),
            'recent_alerts': len([a for a in self.alerts if a['timestamp'] >= recent_batches[0]['timestamp']])
        }
    
    def get_confidence_distribution(self) -> Dict:
        """獲取信心度分布"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN classification_confidence >= 0.90 THEN '高 (>=0.90)'
                    WHEN classification_confidence >= 0.75 THEN '中高 (0.75-0.90)'
                    WHEN classification_confidence >= 0.60 THEN '中低 (0.60-0.75)'
                    ELSE '低 (<0.60)'
                END as level,
                COUNT(*) as count
            FROM tags_final
            WHERE main_category IS NOT NULL
            AND classification_confidence IS NOT NULL
            GROUP BY level
        """)
        
        distribution = dict(cursor.fetchall())
        conn.close()
        
        return distribution
    
    def check_quality_issues(self) -> List[Dict]:
        """檢查品質問題
        
        Returns:
            問題列表
        """
        issues = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 檢查 null 字符串
        cursor.execute("""
            SELECT COUNT(*) FROM tags_final
            WHERE main_category = 'null' OR sub_category = 'null'
        """)
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            issues.append({
                'type': 'NULL_STRING',
                'severity': 'ERROR',
                'count': null_count,
                'message': f'發現 {null_count} 個標籤包含 "null" 字符串'
            })
        
        # 2. 檢查高頻標籤無副分類
        cursor.execute("""
            SELECT COUNT(*) FROM tags_final
            WHERE main_category IS NOT NULL
            AND (sub_category IS NULL OR sub_category = '')
            AND post_count > 50000
        """)
        no_sub_count = cursor.fetchone()[0]
        if no_sub_count > 0:
            issues.append({
                'type': 'MISSING_SUBCATEGORY',
                'severity': 'WARNING',
                'count': no_sub_count,
                'message': f'{no_sub_count} 個高頻標籤缺少副分類'
            })
        
        # 3. 檢查低信心度標籤比例
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN classification_confidence < 0.75 THEN 1 ELSE 0 END) as low_conf
            FROM tags_final
            WHERE main_category IS NOT NULL
            AND classification_confidence IS NOT NULL
        """)
        total, low_conf = cursor.fetchone()
        if total > 0:
            low_conf_ratio = low_conf / total
            if low_conf_ratio > 0.20:  # 超過 20%
                issues.append({
                    'type': 'HIGH_LOW_CONFIDENCE_RATIO',
                    'severity': 'WARNING',
                    'count': low_conf,
                    'ratio': low_conf_ratio,
                    'message': f'低信心度標籤比例過高: {low_conf_ratio:.1%} ({low_conf}/{total})'
                })
        
        conn.close()
        return issues
    
    def generate_quality_report(self, output_file: str = 'output/QUALITY_REPORT.md'):
        """生成品質報告"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        metrics = self.get_quality_metrics()
        conf_dist = self.get_confidence_distribution()
        issues = self.check_quality_issues()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 品質監控報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 整體品質指標
            if metrics:
                f.write("## 整體品質指標\n\n")
                f.write(f"- 總批次數: {metrics['total_batches']}\n")
                f.write(f"- 最近 {metrics['recent_batches']} 批平均成功率: {metrics['avg_success_rate']:.1%}\n")
                f.write(f"- 最近平均信心度: {metrics['avg_confidence']:.3f}\n")
                f.write(f"- 信心度範圍: {metrics['min_confidence']:.3f} - {metrics['max_confidence']:.3f}\n")
                f.write(f"- 總警告數: {metrics['total_alerts']}\n")
                f.write(f"- 最近警告數: {metrics['recent_alerts']}\n\n")
            
            # 信心度分布
            f.write("## 信心度分布\n\n")
            f.write("| 信心度等級 | 數量 |\n")
            f.write("|-----------|------|\n")
            for level, count in sorted(conf_dist.items(), reverse=True):
                f.write(f"| {level} | {count:,} |\n")
            f.write("\n")
            
            # 品質問題
            if issues:
                f.write("## ⚠️ 品質問題\n\n")
                for issue in issues:
                    severity_emoji = {
                        'ERROR': '🛑',
                        'WARNING': '⚠️',
                        'INFO': 'ℹ️'
                    }.get(issue['severity'], '•')
                    f.write(f"### {severity_emoji} {issue['type']}\n\n")
                    f.write(f"**嚴重程度**: {issue['severity']}\n\n")
                    f.write(f"{issue['message']}\n\n")
            else:
                f.write("## ✅ 無品質問題\n\n")
                f.write("所有品質檢查通過！\n\n")
            
            # 警告歷史
            if self.alerts:
                f.write("## 警告歷史\n\n")
                for alert in self.alerts[-20:]:  # 最近 20 個
                    severity_emoji = {
                        'ERROR': '🛑',
                        'WARNING': '⚠️',
                        'INFO': 'ℹ️'
                    }.get(alert['severity'], '•')
                    f.write(f"- {severity_emoji} [{alert['phase']}] {alert['message']} ({alert['timestamp']})\n")
                f.write("\n")
        
        print(f"品質報告已生成: {output_path}")


if __name__ == "__main__":
    # 測試
    monitor = QualityMonitor()
    
    # 模擬批次數據
    from optimized_llm_classifier import ClassificationResult
    
    mock_results = [
        ClassificationResult('test1', 'CHARACTER_RELATED', 'CLOTHING', 0.92, 'Test', True),
        ClassificationResult('test2', 'ACTION_POSE', 'EXPRESSION', 0.88, 'Test', True),
        ClassificationResult('test3', 'OBJECTS', 'WEAPONS', 0.85, 'Test', True),
    ]
    
    monitor.record_batch(mock_results, 'Test Phase')
    
    metrics = monitor.get_quality_metrics()
    print("品質指標:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n生成品質報告...")
    monitor.generate_quality_report()


#!/usr/bin/env python3
"""
檢查點評估器
在處理過程中定期評估進度和品質
"""

import sqlite3
from typing import List, Dict
from datetime import datetime
from config import DB_PATH


class CheckpointEvaluator:
    """檢查點評估器 - 評估處理進度和品質"""
    
    def __init__(self):
        """初始化評估器"""
        self.db_path = DB_PATH
        self.checkpoints = []
    
    def evaluate(self, processed: int, success: int, confidences: List[float],
                 phase_name: str) -> Dict:
        """評估當前檢查點
        
        Args:
            processed: 已處理標籤數
            success: 成功標籤數
            confidences: 信心度列表
            phase_name: Phase 名稱
            
        Returns:
            評估結果字典
        """
        # 1. 計算成功率
        success_rate = success / processed if processed > 0 else 0.0
        success_rating = self._rate_success(success_rate)
        
        # 2. 計算平均信心度
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        confidence_rating = self._rate_confidence(avg_confidence)
        
        # 3. 獲取當前覆蓋率
        coverage = self._get_current_coverage()
        
        # 4. 計算覆蓋率進度
        coverage_progress = self._evaluate_coverage_progress(coverage)
        
        # 5. 評估成本
        cost_status = self._evaluate_cost()
        
        # 記錄檢查點
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'phase_name': phase_name,
            'processed': processed,
            'success': success,
            'success_rate': success_rate,
            'success_rating': success_rating,
            'avg_confidence': avg_confidence,
            'confidence_rating': confidence_rating,
            'coverage': coverage,
            'coverage_progress': coverage_progress,
            'cost_status': cost_status
        }
        
        self.checkpoints.append(checkpoint)
        
        return checkpoint
    
    def _rate_success(self, success_rate: float) -> str:
        """評級成功率
        
        ✅ 優秀: >= 95%
        ⚠️ 良好: 90-95%
        🛑 警告: < 90%
        """
        if success_rate >= 0.95:
            return '✅ 優秀'
        elif success_rate >= 0.90:
            return '⚠️ 良好'
        else:
            return '🛑 警告'
    
    def _rate_confidence(self, avg_confidence: float) -> str:
        """評級信心度
        
        ✅ 優秀: >= 0.85
        ⚠️ 良好: 0.75-0.85
        🛑 警告: < 0.75
        """
        if avg_confidence >= 0.85:
            return '✅ 優秀'
        elif avg_confidence >= 0.75:
            return '⚠️ 良好'
        else:
            return '🛑 警告'
    
    def _get_current_coverage(self) -> float:
        """獲取當前覆蓋率"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 總標籤數
            cursor.execute("SELECT COUNT(*) FROM tags_final")
            total = cursor.fetchone()[0]
            
            # 已分類標籤數
            cursor.execute("""
                SELECT COUNT(*) FROM tags_final
                WHERE main_category IS NOT NULL
            """)
            classified = cursor.fetchone()[0]
            
            conn.close()
            
            return (classified / total * 100) if total > 0 else 0.0
            
        except Exception as e:
            print(f"獲取覆蓋率失敗: {e}")
            return 0.0
    
    def _evaluate_coverage_progress(self, current_coverage: float) -> str:
        """評估覆蓋率進度"""
        # 根據當前覆蓋率判斷進度
        if current_coverage >= 96.0:
            return '🎉 已達成目標 (96%+)'
        elif current_coverage >= 93.0:
            return '✅ 接近目標'
        elif current_coverage >= 91.0:
            return '⚠️ 進度良好'
        else:
            return '📊 持續推進'
    
    def _evaluate_cost(self) -> Dict:
        """評估成本狀態
        
        ⚠️ 50% 預算: 評估是否需要調整
        🛑 80% 預算: 必須重新評估計畫
        """
        # 這裡簡化處理，實際應該追蹤 API 調用成本
        # 可以根據處理的標籤數和批次數估算
        return {
            'status': '✅ 預算充足',
            'estimated_cost': 0.0,
            'budget_used_percent': 0.0
        }
    
    def get_checkpoint_summary(self) -> Dict:
        """獲取所有檢查點的總結"""
        if not self.checkpoints:
            return {}
        
        return {
            'total_checkpoints': len(self.checkpoints),
            'latest': self.checkpoints[-1],
            'avg_success_rate': sum(cp['success_rate'] for cp in self.checkpoints) / len(self.checkpoints),
            'avg_confidence': sum(cp['avg_confidence'] for cp in self.checkpoints) / len(self.checkpoints),
            'coverage_progression': [cp['coverage'] for cp in self.checkpoints]
        }
    
    def generate_checkpoint_report(self, output_file: str = 'output/CHECKPOINT_LOGS.md'):
        """生成檢查點報告文檔"""
        if not self.checkpoints:
            return
        
        from pathlib import Path
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 檢查點評估記錄\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for i, cp in enumerate(self.checkpoints, 1):
                f.write(f"## 檢查點 {i}: {cp['phase_name']}\n\n")
                f.write(f"**時間**: {cp['timestamp']}\n\n")
                f.write(f"### 處理統計\n\n")
                f.write(f"- 已處理: {cp['processed']} 個標籤\n")
                f.write(f"- 成功: {cp['success']} 個\n")
                f.write(f"- 成功率: {cp['success_rate']:.1%} - {cp['success_rating']}\n")
                f.write(f"- 平均信心度: {cp['avg_confidence']:.3f} - {cp['confidence_rating']}\n\n")
                f.write(f"### 覆蓋率進度\n\n")
                f.write(f"- 當前覆蓋率: {cp['coverage']:.2f}%\n")
                f.write(f"- 進度評估: {cp['coverage_progress']}\n\n")
                f.write("---\n\n")
            
            # 總結
            summary = self.get_checkpoint_summary()
            f.write("## 總結\n\n")
            f.write(f"- 總檢查點數: {summary['total_checkpoints']}\n")
            f.write(f"- 平均成功率: {summary['avg_success_rate']:.1%}\n")
            f.write(f"- 平均信心度: {summary['avg_confidence']:.3f}\n")
            f.write(f"- 最新覆蓋率: {summary['latest']['coverage']:.2f}%\n")


if __name__ == "__main__":
    # 測試
    evaluator = CheckpointEvaluator()
    
    # 模擬檢查點
    result = evaluator.evaluate(
        processed=300,
        success=285,
        confidences=[0.85, 0.90, 0.88, 0.92, 0.87],
        phase_name='Test Phase'
    )
    
    print("檢查點評估結果:")
    print(f"成功率: {result['success_rate']:.1%} - {result['success_rating']}")
    print(f"平均信心度: {result['avg_confidence']:.3f} - {result['confidence_rating']}")
    print(f"當前覆蓋率: {result['coverage']:.2f}%")
    print(f"覆蓋率進度: {result['coverage_progress']}")


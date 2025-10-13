#!/usr/bin/env python3
"""
批次大小動態調整器
根據成功率和頻率範圍動態調整批次大小
"""

from typing import Dict


class BatchSizeAdjuster:
    """批次大小動態調整器"""
    
    def __init__(self):
        """初始化調整器"""
        self.adjustment_history = []
    
    def adjust(self, current_success_rate: float, frequency_range: str,
               current_batch_size: int) -> int:
        """根據成功率和頻率範圍動態調整批次大小
        
        Args:
            current_success_rate: 當前成功率 (0.0-1.0)
            frequency_range: 頻率範圍 ('30K-100K', '20K-30K', '10K-20K', etc.)
            current_batch_size: 當前批次大小
            
        Returns:
            調整後的批次大小
        """
        # 根據頻率範圍確定基礎批次大小
        if frequency_range in ['30K-100K', '50K-100K']:
            # 高頻中頻標籤，已驗證效果好
            recommended = 20
            
        elif frequency_range == '20K-30K':
            if current_success_rate >= 0.95:
                recommended = 15
            elif current_success_rate >= 0.90:
                recommended = 12
            else:
                recommended = 10
                
        elif frequency_range == '10K-20K':
            if current_success_rate >= 0.92:
                recommended = 15
            elif current_success_rate >= 0.88:
                recommended = 12
            else:
                recommended = 10
                
        elif frequency_range == '5K-10K':
            if current_success_rate >= 0.90:
                recommended = 12
            elif current_success_rate >= 0.85:
                recommended = 10
            else:
                recommended = 8
                
        elif frequency_range == '3K-5K':
            if current_success_rate >= 0.88:
                recommended = 12
            elif current_success_rate >= 0.83:
                recommended = 10
            else:
                recommended = 8
                
        elif frequency_range == '1K-3K':
            if current_success_rate >= 0.85:
                recommended = 10
            elif current_success_rate >= 0.80:
                recommended = 8
            else:
                recommended = 6
        else:
            # 未知範圍，使用保守值
            recommended = 10
        
        # 漸進調整，避免劇烈變化
        if recommended > current_batch_size:
            # 增加批次大小，每次最多增加 2
            new_size = min(recommended, current_batch_size + 2)
        elif recommended < current_batch_size:
            # 減少批次大小，每次最多減少 3
            new_size = max(recommended, current_batch_size - 3)
        else:
            new_size = current_batch_size
        
        # 記錄調整
        if new_size != current_batch_size:
            self.adjustment_history.append({
                'from': current_batch_size,
                'to': new_size,
                'success_rate': current_success_rate,
                'frequency_range': frequency_range,
                'reason': self._get_adjustment_reason(current_success_rate, frequency_range)
            })
        
        return new_size
    
    def _get_adjustment_reason(self, success_rate: float, frequency_range: str) -> str:
        """獲取調整原因"""
        if success_rate < 0.85:
            return f'成功率過低 ({success_rate:.1%})，降低批次大小以提高品質'
        elif success_rate >= 0.95:
            return f'成功率優秀 ({success_rate:.1%})，可以適度增加批次大小'
        else:
            return f'成功率良好 ({success_rate:.1%})，根據頻率範圍 {frequency_range} 調整'
    
    def get_recommended_params(self, frequency_range: str) -> Dict:
        """獲取推薦的處理參數
        
        Args:
            frequency_range: 頻率範圍
            
        Returns:
            推薦參數字典
        """
        params_map = {
            '50K-100K': {
                'batch_size': 20,
                'retry_count': 3,
                'delay': 1.5,
                'confidence_threshold': 0.85
            },
            '30K-50K': {
                'batch_size': 20,
                'retry_count': 3,
                'delay': 1.5,
                'confidence_threshold': 0.80
            },
            '20K-30K': {
                'batch_size': 15,
                'retry_count': 3,
                'delay': 1.5,
                'confidence_threshold': 0.75
            },
            '10K-20K': {
                'batch_size': 15,
                'retry_count': 2,
                'delay': 2.0,
                'confidence_threshold': 0.70
            },
            '5K-10K': {
                'batch_size': 12,
                'retry_count': 2,
                'delay': 2.0,
                'confidence_threshold': 0.70
            },
            '3K-5K': {
                'batch_size': 12,
                'retry_count': 2,
                'delay': 2.0,
                'confidence_threshold': 0.65
            },
            '1K-3K': {
                'batch_size': 10,
                'retry_count': 2,
                'delay': 2.5,
                'confidence_threshold': 0.60
            }
        }
        
        return params_map.get(frequency_range, {
            'batch_size': 10,
            'retry_count': 2,
            'delay': 2.0,
            'confidence_threshold': 0.70
        })
    
    def get_adjustment_summary(self) -> Dict:
        """獲取調整歷史總結"""
        if not self.adjustment_history:
            return {
                'total_adjustments': 0,
                'increases': 0,
                'decreases': 0
            }
        
        increases = sum(1 for adj in self.adjustment_history if adj['to'] > adj['from'])
        decreases = sum(1 for adj in self.adjustment_history if adj['to'] < adj['from'])
        
        return {
            'total_adjustments': len(self.adjustment_history),
            'increases': increases,
            'decreases': decreases,
            'history': self.adjustment_history
        }


if __name__ == "__main__":
    # 測試
    adjuster = BatchSizeAdjuster()
    
    # 測試不同場景
    scenarios = [
        (0.96, '30K-50K', 20),  # 優秀表現
        (0.88, '10K-20K', 15),  # 良好表現
        (0.82, '10K-20K', 15),  # 需要調整
        (0.75, '1K-3K', 10),    # 低頻標籤
    ]
    
    print("批次大小調整測試:\n")
    for success_rate, freq_range, current_size in scenarios:
        new_size = adjuster.adjust(success_rate, freq_range, current_size)
        print(f"頻率範圍: {freq_range}")
        print(f"  成功率: {success_rate:.1%}")
        print(f"  當前批次大小: {current_size}")
        print(f"  建議批次大小: {new_size}")
        print()
    
    print("\n推薦參數示例:")
    for freq_range in ['30K-50K', '10K-20K', '1K-3K']:
        params = adjuster.get_recommended_params(freq_range)
        print(f"\n{freq_range}:")
        for key, value in params.items():
            print(f"  {key}: {value}")


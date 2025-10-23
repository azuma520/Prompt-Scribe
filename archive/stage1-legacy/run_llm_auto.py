#!/usr/bin/env python3
"""
LLM 增強自動執行腳本（無互動）
直接處理超高頻未分類標籤
"""

import sys
import logging
from pathlib import Path

from qwen_classifier import QwenClassifier
from llm_config import validate_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """主函數"""
    print("="*80)
    print("LLM 增強 - 自動批次處理（超高頻標籤）")
    print("="*80)
    print()
    
    # 驗證配置
    if not validate_config():
        print("\n[ERROR] 配置驗證失敗")
        return 1
    
    # 檢查數據庫
    db_path = "output/tags.db"
    if not Path(db_path).exists():
        print(f"\n[ERROR] 資料庫不存在: {db_path}")
        return 1
    
    print(f"\n[OK] 資料庫找到: {db_path}")
    
    # 初始化分類器
    try:
        classifier = QwenClassifier()
        print("[OK] 分類器初始化成功\n")
    except Exception as e:
        print(f"\n[ERROR] 分類器初始化失敗: {e}")
        return 1
    
    # 設定參數
    MIN_POST_COUNT = 1000000  # 1M
    
    print("[INFO] 處理設定:")
    print(f"  最小使用次數: {MIN_POST_COUNT:,}")
    print(f"  預估標籤數: ~114 個")
    print(f"  預估時間: 2-3 小時")
    print(f"  預估成本: $2-5")
    
    # 執行處理
    print("\n" + "="*80)
    print("開始批次處理...")
    print("="*80)
    print()
    
    try:
        results = classifier.process_unclassified_tags(
            db_path=db_path,
            min_post_count=MIN_POST_COUNT,
            limit=None
        )
        
        # 顯示結果
        print("\n" + "="*80)
        print("處理完成")
        print("="*80)
        print(f"總處理: {results['total']} 個標籤")
        print(f"成功: {results['success']} ({results['success']/results['total']*100:.1f}%)")
        print(f"失敗: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
        
        if results['success'] > 0:
            print("\n下一步:")
            print("  1. 執行審查: python review_llm_results.py")
            print("  2. 查看統計: python quick_stats.py")
            print("  3. 生成最終報告")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n[INFO] 使用者中斷處理")
        print("已處理的結果已保存到資料庫")
        return 1
        
    except Exception as e:
        logger.error(f"處理失敗: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


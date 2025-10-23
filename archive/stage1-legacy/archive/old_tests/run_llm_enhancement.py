#!/usr/bin/env python3
"""
LLM 增強主執行腳本
自動執行完整的 LLM 增強流程
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
    print("LLM 增強 - 批次處理未分類標籤")
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
    
    # 詢問處理範圍
    print("請選擇處理範圍:")
    print("  1. 超高頻標籤 (post_count >= 1M, ~114 個標籤)")
    print("  2. 高頻標籤 (post_count >= 100K, ~150 個標籤)")
    print("  3. 中高頻標籤 (post_count >= 10K, ~3,200 個標籤)")
    print("  4. 測試模式 (前 20 個標籤)")
    
    try:
        choice = input("\n請輸入選項 (1-4) [1]: ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        choice = "1"
        print("1 (使用預設)")
    
    # 設定閾值
    threshold_map = {
        "1": 1000000,
        "2": 100000,
        "3": 10000,
        "4": 1000000  # 測試模式也用高頻但限制數量
    }
    
    limit_map = {
        "1": None,
        "2": None,
        "3": None,
        "4": 20
    }
    
    threshold = threshold_map.get(choice, 1000000)
    limit = limit_map.get(choice)
    
    print(f"\n[INFO] 處理設定:")
    print(f"  最小使用次數: {threshold:,}")
    if limit:
        print(f"  限制數量: {limit} 個標籤")
    
    # 確認
    print("\n" + "="*80)
    print("準備開始批次處理")
    print("="*80)
    print("注意：")
    print("  - 這可能需要 2-3 小時")
    print("  - 請確保網路連接穩定")
    print("  - 預估成本: $2-5 (依實際標籤數量)")
    print()
    
    try:
        confirm = input("確認開始處理？(y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        confirm = 'n'
        print("n")
    
    if confirm != 'y':
        print("\n取消處理")
        return 0
    
    # 執行處理
    print("\n" + "="*80)
    print("開始批次處理...")
    print("="*80)
    print()
    
    try:
        results = classifier.process_unclassified_tags(
            db_path=db_path,
            min_post_count=threshold,
            limit=limit
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


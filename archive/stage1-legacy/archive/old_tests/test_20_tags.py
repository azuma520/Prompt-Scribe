#!/usr/bin/env python3
"""
測試模式：處理 20 個超高頻未分類標籤
用於驗證效果和估算成本
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
    print("LLM 增強 - 測試模式（20 個標籤）")
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
    LIMIT = 20  # 只處理前 20 個
    
    print("[INFO] 測試設定:")
    print(f"  最小使用次數: {MIN_POST_COUNT:,}")
    print(f"  處理數量: {LIMIT} 個標籤")
    print(f"  預估時間: 3-5 分鐘")
    print(f"  預估成本: $0.20-0.50")
    
    # 執行處理
    print("\n" + "="*80)
    print("開始測試處理...")
    print("="*80)
    print()
    
    try:
        results = classifier.process_unclassified_tags(
            db_path=db_path,
            min_post_count=MIN_POST_COUNT,
            limit=LIMIT
        )
        
        # 顯示結果
        print("\n" + "="*80)
        print("測試完成")
        print("="*80)
        print(f"總處理: {results['total']} 個標籤")
        print(f"成功: {results['success']} ({results['success']/results['total']*100:.1f}%)")
        print(f"失敗: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
        
        # 成本估算
        # Gemini 2.5 Flash Lite 價格較低
        # 假設每個標籤約 150 tokens input + 100 tokens output = 250 tokens
        # 20 個標籤 = 5,000 tokens
        # Gemini Flash Lite 約 $0.075 / 1M input tokens, $0.30 / 1M output tokens
        total_tokens = results['total'] * 250
        est_cost = (total_tokens * 0.075) / 1000000 + (total_tokens * 0.3) / 1000000
        
        print(f"\n成本估算:")
        print(f"  預估總 tokens: ~{total_tokens:,}")
        print(f"  預估成本: ${est_cost:.4f}")
        
        if results['success'] > 0:
            print("\n如果效果滿意，執行完整處理:")
            print("  python run_llm_auto.py")
            print("\n或先審查這 20 個結果:")
            print("  python review_llm_results.py")
        
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


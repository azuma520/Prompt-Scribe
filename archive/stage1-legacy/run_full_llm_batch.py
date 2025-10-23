#!/usr/bin/env python3
"""
執行完整的 LLM 批量處理（自動化版本）
"""

from optimized_llm_classifier import batch_process_medium_frequency_tags

if __name__ == "__main__":
    print("開始完整的 LLM 批量處理...")
    print("目標: 處理所有中高頻未分類標籤 (100K-1M)")
    print("")
    
    batch_process_medium_frequency_tags(batch_size=20)

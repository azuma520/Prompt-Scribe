#!/usr/bin/env python3
"""
Qwen3 分類器小規模測試
測試 10 個標籤的分類效果
"""

import sqlite3
import json
import logging
from pathlib import Path

from llm_config import TEST_TAGS, validate_config
from qwen_classifier import QwenClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_classification():
    """測試分類功能"""
    
    print("="*80)
    print("Qwen3 分類器小規模測試")
    print("="*80)
    print()
    
    # 驗證配置
    if not validate_config():
        print("\n[FAIL] 配置驗證失敗，請設定 API Key")
        return False
    
    # 初始化分類器
    try:
        classifier = QwenClassifier()
        print("\n[OK] 分類器初始化成功")
    except Exception as e:
        print(f"\n[FAIL] 分類器初始化失敗: {e}")
        return False
    
    # 從資料庫獲取測試標籤的資訊
    db_path = "output/tags.db"
    if not Path(db_path).exists():
        print(f"\n[FAIL] 資料庫不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    
    try:
        # 獲取測試標籤資訊
        placeholders = ','.join(['?' for _ in TEST_TAGS])
        query = f"""
            SELECT name, post_count, main_category, sub_category
            FROM tags_final
            WHERE name IN ({placeholders})
        """
        cursor = conn.execute(query, TEST_TAGS)
        db_tags = {row[0]: row for row in cursor.fetchall()}
        
        print(f"\n測試標籤列表 ({len(TEST_TAGS)} 個):")
        print("-" * 80)
        for i, tag in enumerate(TEST_TAGS, 1):
            if tag in db_tags:
                _, post_count, main_cat, sub_cat = db_tags[tag]
                status = f"已分類: {main_cat}" if main_cat else "未分類"
                print(f"{i:2}. {tag:20} - 使用次數: {post_count:>10,} - {status}")
            else:
                print(f"{i:2}. {tag:20} - 不在資料庫中")
        
        # 執行分類
        print("\n" + "="*80)
        print("開始分類...")
        print("="*80)
        
        results = classifier.classify_batch(TEST_TAGS)
        
        # 顯示結果
        print("\n" + "="*80)
        print("分類結果")
        print("="*80)
        
        success_count = 0
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.tag_name}")
            if result.success:
                print(f"   主分類: {result.main_category}")
                print(f"   副分類: {result.sub_category or 'None'}")
                print(f"   置信度: {result.confidence:.2f}")
                print(f"   理由: {result.reasoning}")
                success_count += 1
            else:
                print(f"   [FAIL] 失敗: {result.error}")
        
        # 統計
        print("\n" + "="*80)
        print("統計結果")
        print("="*80)
        print(f"總標籤數: {len(results)}")
        print(f"成功: {success_count} ({success_count/len(results)*100:.1f}%)")
        print(f"失敗: {len(results)-success_count}")
        
        # 分類分佈
        if success_count > 0:
            main_cats = {}
            sub_cats = {}
            confidences = []
            
            for result in results:
                if result.success:
                    main_cats[result.main_category] = main_cats.get(result.main_category, 0) + 1
                    if result.sub_category:
                        sub_cats[result.sub_category] = sub_cats.get(result.sub_category, 0) + 1
                    confidences.append(result.confidence)
            
            print("\n主分類分佈:")
            for cat, count in sorted(main_cats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")
            
            if sub_cats:
                print("\n副分類分佈:")
                for cat, count in sorted(sub_cats.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {cat}: {count}")
            
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                min_conf = min(confidences)
                max_conf = max(confidences)
                print(f"\n置信度統計:")
                print(f"  平均: {avg_conf:.3f}")
                print(f"  最小: {min_conf:.3f}")
                print(f"  最大: {max_conf:.3f}")
        
        # 詢問是否保存結果
        print("\n" + "="*80)
        save = input("是否將這些結果保存到資料庫？(y/N): ").strip().lower()
        
        if save == 'y':
            success, failed = classifier.save_results(conn, results)
            print(f"[OK] 已保存 {success} 個結果到資料庫")
            if failed > 0:
                print(f"[WARN] {failed} 個結果保存失敗")
        else:
            print("結果未保存")
        
        return success_count == len(results)
        
    except Exception as e:
        logger.error(f"測試失敗: {e}", exc_info=True)
        return False
        
    finally:
        conn.close()


def main():
    """主函數"""
    success = test_classification()
    
    print("\n" + "="*80)
    if success:
        print("[SUCCESS] 測試通過")
        print("\n下一步：")
        print("  1. 確認分類結果是否合理")
        print("  2. 如果滿意，執行完整批次處理:")
        print("     python qwen_classifier.py")
    else:
        print("[FAILED] 測試失敗")
        print("\n請檢查：")
        print("  1. API Key 是否正確設定")
        print("  2. 網路連接是否正常")
        print("  3. API 是否有額度")
    print("="*80)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())


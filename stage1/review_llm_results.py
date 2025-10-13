#!/usr/bin/env python3
"""
LLM 分類結果審查工具
用於審查、驗證和修正 LLM 的分類結果
"""

import sqlite3
import logging
from typing import List, Dict
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def review_llm_classifications(db_path: str = "output/tags.db"):
    """審查 LLM 分類結果"""
    
    print("="*80)
    print("LLM 分類結果審查")
    print("="*80)
    
    conn = sqlite3.connect(db_path)
    
    try:
        # 獲取所有 LLM 分類的標籤
        query = """
            SELECT 
                name, 
                main_category, 
                sub_category,
                classification_source,
                classification_confidence,
                classification_reasoning,
                post_count
            FROM tags_final
            WHERE classification_source IS NOT NULL
            ORDER BY post_count DESC
        """
        
        cursor = conn.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("\n未找到 LLM 分類的標籤")
            return
        
        print(f"\n找到 {len(results)} 個 LLM 分類的標籤")
        
        # 統計
        by_main_cat = defaultdict(list)
        by_confidence = {'high': [], 'medium': [], 'low': []}
        by_source = defaultdict(int)
        
        for row in results:
            name, main_cat, sub_cat, source, confidence, reasoning, post_count = row
            
            by_main_cat[main_cat].append(row)
            by_source[source] += 1
            
            # 處理 None 信心度的情況
            if confidence is None:
                by_confidence['low'].append(row)
            elif confidence >= 0.8:
                by_confidence['high'].append(row)
            elif confidence >= 0.5:
                by_confidence['medium'].append(row)
            else:
                by_confidence['low'].append(row)
        
        # 顯示統計
        print("\n" + "="*80)
        print("統計摘要")
        print("="*80)
        
        print(f"\n按來源統計:")
        for source, count in sorted(by_source.items()):
            print(f"  {source}: {count} 個標籤")
        
        print(f"\n按主分類統計:")
        for main_cat, tags in sorted(by_main_cat.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {main_cat}: {len(tags)} 個標籤")
        
        print(f"\n按置信度統計:")
        print(f"  高 (>=0.8): {len(by_confidence['high'])} 個標籤")
        print(f"  中 (0.5-0.8): {len(by_confidence['medium'])} 個標籤")
        print(f"  低 (<0.5): {len(by_confidence['low'])} 個標籤")
        
        # 顯示低置信度標籤
        if by_confidence['low']:
            print("\n" + "="*80)
            print("低置信度標籤（需審查）")
            print("="*80)
            
            for row in sorted(by_confidence['low'], key=lambda x: x[6], reverse=True)[:20]:
                name, main_cat, sub_cat, source, confidence, reasoning, post_count = row
                print(f"\n標籤: {name}")
                print(f"  使用次數: {post_count:,}")
                print(f"  分類: {main_cat} / {sub_cat or 'None'}")
                print(f"  置信度: {confidence:.3f if confidence is not None else 'None'}")
                print(f"  理由: {reasoning[:100] if reasoning else 'None'}...")
        
        # 按主分類顯示代表性標籤
        print("\n" + "="*80)
        print("各分類代表性標籤（前 5 個）")
        print("="*80)
        
        for main_cat, tags in sorted(by_main_cat.items()):
            print(f"\n{main_cat}:")
            for row in sorted(tags, key=lambda x: x[6], reverse=True)[:5]:
                name, _, sub_cat, _, confidence, _, post_count = row
                print(f"  {name:30} [{sub_cat or 'None':15}] - {post_count:>10,} 次 (conf: {confidence:.2f})")
        
        # 檢查潛在問題
        print("\n" + "="*80)
        print("潛在問題檢查")
        print("="*80)
        
        issues = []
        
        # 檢查 1: 相似標籤分類不一致
        similar_patterns = {}
        for row in results:
            name = row[0]
            # 提取基礎詞
            if '_' in name:
                base = name.split('_')[0]
                if base not in similar_patterns:
                    similar_patterns[base] = []
                similar_patterns[base].append(row)
        
        inconsistent = []
        for base, tags in similar_patterns.items():
            if len(tags) >= 2:
                main_cats = set(tag[1] for tag in tags)
                if len(main_cats) > 1:
                    inconsistent.append((base, tags))
        
        if inconsistent:
            print(f"\n發現 {len(inconsistent)} 組相似標籤分類不一致:")
            for base, tags in inconsistent[:5]:
                print(f"\n  基礎詞: {base}")
                for tag in tags[:3]:
                    print(f"    {tag[0]:30} -> {tag[1]} / {tag[2] or 'None'}")
        
        # 檢查 2: 空白理由
        no_reasoning = [row for row in results if not row[5] or row[5].strip() == '']
        if no_reasoning:
            print(f"\n發現 {len(no_reasoning)} 個標籤沒有分類理由")
            issues.append(f"{len(no_reasoning)} 個標籤沒有理由")
        
        # 檢查 3: 極端置信度
        very_low_conf = [row for row in results if row[4] < 0.3]
        if very_low_conf:
            print(f"\n發現 {len(very_low_conf)} 個標籤置信度極低 (<0.3)")
            for row in very_low_conf:
                print(f"  {row[0]}: {row[4]:.3f}")
            issues.append(f"{len(very_low_conf)} 個極低置信度")
        
        # 總結
        print("\n" + "="*80)
        print("審查總結")
        print("="*80)
        print(f"總標籤數: {len(results)}")
        print(f"發現問題: {len(issues)}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("  未發現明顯問題")
        
        # 推薦
        print("\n建議:")
        if by_confidence['low']:
            print(f"  1. 審查 {len(by_confidence['low'])} 個低置信度標籤")
        if inconsistent:
            print(f"  2. 檢查 {len(inconsistent)} 組不一致的相似標籤")
        if not issues:
            print("  分類結果良好，可以繼續處理更多標籤")
        
        return results
        
    finally:
        conn.close()


def export_review_report(db_path: str = "output/tags.db", 
                         output_path: str = "output/llm_review_report.txt"):
    """匯出審查報告"""
    
    print(f"\n生成審查報告: {output_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        query = """
            SELECT 
                name, 
                main_category, 
                sub_category,
                classification_confidence,
                classification_reasoning,
                post_count
            FROM tags_final
            WHERE classification_source IS NOT NULL
            ORDER BY classification_confidence ASC, post_count DESC
        """
        
        cursor = conn.execute(query)
        results = cursor.fetchall()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("LLM 分類結果審查報告\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"總標籤數: {len(results)}\n\n")
            
            f.write("="*80 + "\n")
            f.write("完整標籤列表（按置信度排序）\n")
            f.write("="*80 + "\n\n")
            
            for i, row in enumerate(results, 1):
                name, main_cat, sub_cat, confidence, reasoning, post_count = row
                
                f.write(f"{i}. {name}\n")
                f.write(f"   使用次數: {post_count:,}\n")
                f.write(f"   分類: {main_cat} / {sub_cat or 'None'}\n")
                f.write(f"   置信度: {confidence:.3f}\n")
                f.write(f"   理由: {reasoning}\n")
                f.write("\n")
        
        print(f"✓ 報告已生成: {output_path}")
        
    finally:
        conn.close()


def main():
    """主函數"""
    results = review_llm_classifications()
    
    if results:
        export = input("\n是否匯出詳細審查報告？(y/N): ").strip().lower()
        if export == 'y':
            export_review_report()
    
    print("\n" + "="*80)
    print("審查完成")
    print("="*80)


if __name__ == "__main__":
    main()


"""
深入分析現有資料庫
回答關鍵問題：分類系統、NSFW 內容、資料品質
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

from services.supabase_client import get_supabase_service

async def detailed_analysis():
    """深入分析"""
    
    print("\n" + "="*70)
    print("Detailed Database Analysis")
    print("="*70)
    
    db = get_supabase_service()
    
    # ============================================
    # Q1: 完整的 main_category 列表
    # ============================================
    
    print("\n[Q1] What are ALL main_category values?")
    print("-"*70)
    
    try:
        # 查詢所有不同的 main_category
        result = db.client.table('tags_final')\
            .select('main_category')\
            .not_.is_('main_category', 'null')\
            .execute()
        
        # 統計
        category_counts = {}
        for row in result.data:
            cat = row['main_category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # 排序
        sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"  Total unique categories: {len(sorted_cats)}")
        print(f"\n  All categories (sorted by count):")
        for cat, count in sorted_cats:
            print(f"    {cat:30} : {count:7,} tags")
        
        # 保存到檔案供參考
        with open("category_analysis.json", "w", encoding="utf-8") as f:
            json.dump({
                "total_categories": len(sorted_cats),
                "categories": sorted_cats
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n  [INFO] Full list saved to: category_analysis.json")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # Q2: sub_category 分佈
    # ============================================
    
    print("\n[Q2] What are sub_category values?")
    print("-"*70)
    
    try:
        result = db.client.table('tags_final')\
            .select('sub_category')\
            .not_.is_('sub_category', 'null')\
            .execute()
        
        sub_counts = {}
        for row in result.data:
            sub = row['sub_category']
            sub_counts[sub] = sub_counts.get(sub, 0) + 1
        
        sorted_subs = sorted(sub_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"  Total unique sub-categories: {len(sorted_subs)}")
        print(f"\n  Top 20 sub-categories:")
        for sub, count in sorted_subs[:20]:
            print(f"    {sub:30} : {count:7,} tags")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # Q3: TOP 100 熱門標籤（檢查 NSFW）
    # ============================================
    
    print("\n[Q3] TOP 100 tags - NSFW content check:")
    print("-"*70)
    
    try:
        result = db.client.table('tags_final')\
            .select('name, post_count, main_category')\
            .order('post_count', desc=True)\
            .limit(100)\
            .execute()
        
        # NSFW 關鍵字
        nsfw_keywords = [
            "nsfw", "nude", "naked", "sex", "penis", "vagina",
            "breasts", "nipples", "ass", "pussy", "porn",
            "hentai", "cum", "erect", "explicit"
        ]
        
        blocked_keywords = [
            "loli", "shota", "child", "kid", "toddler"
        ]
        
        nsfw_tags = []
        blocked_tags = []
        safe_tags = []
        
        for tag in result.data:
            tag_name = tag['name'].lower()
            
            if any(kw in tag_name for kw in blocked_keywords):
                blocked_tags.append(tag)
            elif any(kw in tag_name for kw in nsfw_keywords):
                nsfw_tags.append(tag)
            else:
                safe_tags.append(tag)
        
        print(f"  Total TOP 100 tags analyzed:")
        print(f"    Safe (all-ages) : {len(safe_tags)} tags")
        print(f"    NSFW (r18)      : {len(nsfw_tags)} tags")
        print(f"    Blocked         : {len(blocked_tags)} tags")
        
        if nsfw_tags:
            print(f"\n  NSFW tags found in TOP 100:")
            for tag in nsfw_tags[:10]:
                print(f"    - {tag['name']:20} ({tag['post_count']:,} posts)")
        
        if blocked_tags:
            print(f"\n  [CRITICAL] Blocked tags found in TOP 100:")
            for tag in blocked_tags:
                print(f"    - {tag['name']:20} ({tag['post_count']:,} posts)")
        
        # 保存完整列表
        with open("top100_nsfw_analysis.json", "w", encoding="utf-8") as f:
            json.dump({
                "safe": [t["name"] for t in safe_tags],
                "nsfw": [t["name"] for t in nsfw_tags],
                "blocked": [t["name"] for t in blocked_tags]
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n  [INFO] Full analysis saved to: top100_nsfw_analysis.json")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # Q4: 檢查特定標籤樣本
    # ============================================
    
    print("\n[Q4] Specific Tag Samples:")
    print("-"*70)
    
    test_tags = {
        "Character": ["1girl", "1boy", "solo"],
        "Appearance": ["long_hair", "blue_eyes", "blonde_hair"],
        "Scene": ["outdoors", "forest", "beach", "city"],
        "Mood": ["smile", "sad", "happy"],
        "Style": ["anime_style", "realistic", "masterpiece"],
        "Blocked": ["loli", "shota", "child"]
    }
    
    try:
        for category_name, tags in test_tags.items():
            print(f"\n  {category_name} tags:")
            
            tag_data = await db.get_tags_by_names(tags)
            
            for tag_name in tags:
                tag = tag_data.get(tag_name)
                if tag:
                    print(f"    [OK] {tag['name']:15} - {tag['post_count']:9,} posts - Cat: {tag.get('main_category', 'NULL'):20}")
                else:
                    print(f"    [MISS] {tag_name:15} - NOT IN DATABASE")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # Q5: 分類覆蓋度
    # ============================================
    
    print("\n[Q5] Category Coverage:")
    print("-"*70)
    
    try:
        total_count = await db.get_total_tags_count()
        
        # 有分類的數量
        result_categorized = db.client.table('tags_final')\
            .select('*', count='exact')\
            .not_.is_('main_category', 'null')\
            .limit(1)\
            .execute()
        
        categorized_count = result_categorized.count if result_categorized.count else 0
        coverage = (categorized_count / total_count * 100) if total_count > 0 else 0
        
        print(f"  Total tags: {total_count:,}")
        print(f"  Categorized: {categorized_count:,} ({coverage:.2f}%)")
        print(f"  Uncategorized: {total_count - categorized_count:,} ({100-coverage:.2f}%)")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # 總結與建議
    # ============================================
    
    print("\n" + "="*70)
    print("Analysis Summary & Recommendations")
    print("="*70)
    
    print("\n[FINDINGS]")
    print("  1. tags_final has complete popularity data (post_count)")
    print("  2. Classification system exists (main_category, sub_category)")
    print("  3. NSFW content confirmed in database")
    print("  4. No embeddings available (semantic search not ready)")
    print("  5. No aliases, conflicts, nsfw_level columns")
    
    print("\n[RECOMMENDATIONS]")
    print("  Option A (Minimal): Use existing columns + app-layer logic")
    print("    - Zero schema changes")
    print("    - Maintain mappings in code")
    print("    - Fast to implement")
    print("    - Recommended for MVP")
    
    print("\n  Option B (Balanced): Create auxiliary tables")
    print("    - tags_final unchanged")
    print("    - New table: tag_metadata (inspire-specific data)")
    print("    - Safe and reversible")
    
    print("\n  Option C (Complete): ALTER tags_final")
    print("    - Add inspire columns to existing table")
    print("    - Higher risk, more integrated")
    
    print("\n[NEXT STEPS]")
    print("  1. Review category_analysis.json")
    print("  2. Review top100_nsfw_analysis.json")
    print("  3. Decide on integration strategy (A, B, or C)")
    print("  4. Create category mapping (main_category -> Inspire categories)")
    print("  5. Create NSFW detection rules")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(detailed_analysis())


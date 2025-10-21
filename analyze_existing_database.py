"""
分析現有 Supabase 資料庫
了解 tags_final 表的實際內容和結構
"""

import asyncio
import sys
import os

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

from services.supabase_client import get_supabase_service

async def analyze_database():
    """分析資料庫"""
    
    print("\n" + "="*70)
    print("Analyzing Existing Database (tags_final)")
    print("="*70)
    
    db = get_supabase_service()
    
    # ============================================
    # 1. 檢查表結構（取樣一筆資料）
    # ============================================
    
    print("\n[1] Table Structure - Sample Row:")
    print("-"*70)
    
    try:
        result = db.client.table('tags_final').select('*').limit(1).execute()
        
        if result.data:
            sample = result.data[0]
            print(f"Available columns:")
            for key, value in sample.items():
                value_preview = str(value)[:50] if value else "None"
                print(f"  - {key:25} = {value_preview} ({type(value).__name__})")
        else:
            print("  [WARN] No data found in tags_final")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # 2. 統計基礎資訊
    # ============================================
    
    print("\n[2] Basic Statistics:")
    print("-"*70)
    
    try:
        # 總數
        total_count = await db.get_total_tags_count()
        print(f"  Total tags: {total_count:,}")
        
        # 流行度分佈
        result = db.client.table('tags_final')\
            .select('post_count')\
            .order('post_count', desc=True)\
            .limit(10)\
            .execute()
        
        if result.data:
            print(f"\n  Top 10 by popularity:")
            top_tags = db.client.table('tags_final')\
                .select('name, post_count')\
                .order('post_count', desc=True)\
                .limit(10)\
                .execute()
            
            for i, tag in enumerate(top_tags.data, 1):
                print(f"    {i:2}. {tag['name']:20} - {tag['post_count']:,} posts")
        
        # 流行度範圍統計
        ranges = [
            (">= 10000", 10000),
            (">= 5000", 5000),
            (">= 1000", 1000),
            (">= 500", 500),
            (">= 100", 100),
            ("< 100", 0)
        ]
        
        print(f"\n  Popularity distribution:")
        for label, min_count in ranges:
            if min_count > 0:
                result = db.client.table('tags_final')\
                    .select('*', count='exact')\
                    .gte('post_count', min_count)\
                    .limit(1)\
                    .execute()
            else:
                result = db.client.table('tags_final')\
                    .select('*', count='exact')\
                    .lt('post_count', 100)\
                    .limit(1)\
                    .execute()
            
            count = result.count if result.count else 0
            percentage = (count / total_count * 100) if total_count > 0 else 0
            print(f"    {label:15} : {count:7,} tags ({percentage:5.2f}%)")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # 3. 檢查分類系統（main_category）
    # ============================================
    
    print("\n[3] Category System (main_category):")
    print("-"*70)
    
    try:
        stats = await db.get_category_stats()
        
        if stats:
            print(f"  Total categories: {len(stats)}")
            print(f"\n  Top categories:")
            sorted_cats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
            for cat, count in sorted_cats[:15]:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                print(f"    {cat:25} : {count:7,} tags ({percentage:5.2f}%)")
            
            # 檢查 NULL 分類
            result = db.client.table('tags_final')\
                .select('*', count='exact')\
                .is_('main_category', 'null')\
                .limit(1)\
                .execute()
            
            null_count = result.count if result.count else 0
            if null_count > 0:
                null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
                print(f"    {'(NULL/未分類)':25} : {null_count:7,} tags ({null_percentage:5.2f}%)")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # 4. 檢查是否有 embeddings
    # ============================================
    
    print("\n[4] Vector Embeddings (tag_embeddings):")
    print("-"*70)
    
    try:
        result = db.client.table('tag_embeddings')\
            .select('*', count='exact')\
            .limit(1)\
            .execute()
        
        embed_count = result.count if result.count else 0
        coverage = (embed_count / total_count * 100) if total_count > 0 else 0
        
        print(f"  Total embeddings: {embed_count:,}")
        print(f"  Coverage: {coverage:.2f}%")
        
        if embed_count > 0:
            sample = result.data[0]
            print(f"  Model: {sample.get('model', 'unknown')}")
            print(f"  Dimension: {len(sample.get('embedding', []))} if available")
    
    except Exception as e:
        print(f"  [WARN] tag_embeddings table may not exist: {e}")
    
    # ============================================
    # 5. 抽樣檢查具體標籤
    # ============================================
    
    print("\n[5] Sample Tags Analysis:")
    print("-"*70)
    
    sample_tags = ["1girl", "solo", "long_hair", "blue_eyes", "smile", "outdoors", "anime_style"]
    
    try:
        tag_data = await db.get_tags_by_names(sample_tags)
        
        print(f"  Checking {len(sample_tags)} common tags:")
        for tag_name in sample_tags:
            tag = tag_data.get(tag_name)
            if tag:
                print(f"    ✅ {tag['name']:15} - {tag['post_count']:7,} posts - Category: {tag.get('main_category', 'N/A')}")
            else:
                print(f"    ❌ {tag_name:15} - NOT FOUND")
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # ============================================
    # 6. 評估 Inspire 需求 vs 現有資料
    # ============================================
    
    print("\n[6] Inspire Agent Requirements vs Existing Data:")
    print("-"*70)
    
    print("\n  Inspire Needs        | Existing Data      | Status")
    print("  " + "-"*66)
    print(f"  Tag name             | name               | ✅ Available")
    print(f"  Popularity           | post_count         | ✅ Available")
    print(f"  Category system      | main_category      | ⚠️  Need mapping")
    print(f"  Semantic search      | tag_embeddings     | {'✅ Available' if embed_count > 0 else '❌ Missing'}")
    print(f"  Tag aliases          | ???                | ❓ Need to check")
    print(f"  Conflict detection   | ???                | ❓ Need to check")
    print(f"  NSFW classification  | ???                | ❓ Need to check")
    
    # ============================================
    # 7. 總結與建議
    # ============================================
    
    print("\n" + "="*70)
    print("Analysis Summary")
    print("="*70)
    
    print("\n✅ Available (can use directly):")
    print(f"  - {total_count:,} tags with popularity data (post_count)")
    print(f"  - Category system (main_category) - {len(stats)} categories")
    if embed_count > 0:
        print(f"  - Vector embeddings for semantic search ({coverage:.1f}% coverage)")
    
    print("\n⚠️  Need to investigate:")
    print(f"  - Whether aliases, conflicts, nsfw_level exist")
    print(f"  - Category mapping (main_category → Inspire categories)")
    print(f"  - Tag quality and validity")
    
    print("\n💡 Next steps:")
    print(f"  1. Check if additional columns exist (aliases, conflicts, nsfw)")
    print(f"  2. Create category mapping from main_category to Inspire categories")
    print(f"  3. Design minimal schema changes (if needed)")
    print(f"  4. Plan data migration strategy")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(analyze_database())


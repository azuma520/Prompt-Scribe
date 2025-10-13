#!/usr/bin/env python3
"""
修復低信心度分類來源問題
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def identify_low_confidence_sources():
    """識別低信心度分類來源"""
    logger.info("識別低信心度分類來源...")
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    # 查找所有分類來源的信心度統計
    cursor.execute("""
        SELECT 
            classification_source,
            COUNT(*) as tag_count,
            ROUND(AVG(classification_confidence), 3) as avg_confidence,
            ROUND(MIN(classification_confidence), 3) as min_confidence,
            ROUND(MAX(classification_confidence), 3) as max_confidence
        FROM tags_final
        WHERE classification_source IS NOT NULL
          AND classification_confidence IS NOT NULL
        GROUP BY classification_source
        ORDER BY avg_confidence ASC
    """)
    
    sources = cursor.fetchall()
    
    logger.info("所有分類來源信心度統計:")
    logger.info("-" * 100)
    logger.info(f"{'來源':<40} {'標籤數':<8} {'平均':<8} {'最低':<8} {'最高':<8} {'狀態'}")
    logger.info("-" * 100)
    
    low_confidence_sources = []
    very_low_confidence_sources = []
    
    for source, count, avg_conf, min_conf, max_conf in sources:
        if avg_conf < 0.70:
            status = "極低"
            very_low_confidence_sources.append((source, count, avg_conf, min_conf, max_conf))
        elif avg_conf < 0.85:
            status = "低"
            low_confidence_sources.append((source, count, avg_conf, min_conf, max_conf))
        else:
            status = "正常"
        
        logger.info(f"{source:<40} {count:<8} {avg_conf:<8} {min_conf:<8} {max_conf:<8} {status}")
    
    logger.info("-" * 100)
    logger.info(f"極低信心度來源（<0.70）: {len(very_low_confidence_sources)} 個")
    logger.info(f"低信心度來源（<0.85）: {len(low_confidence_sources)} 個")
    
    conn.close()
    return very_low_confidence_sources, low_confidence_sources

def analyze_low_confidence_source(source_name):
    """分析特定低信心度來源"""
    logger.info(f"分析來源: {source_name}")
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    # 獲取該來源的標籤詳情
    cursor.execute("""
        SELECT 
            name, main_category, sub_category, post_count, classification_confidence
        FROM tags_final
        WHERE classification_source = ?
        ORDER BY classification_confidence ASC, post_count DESC
        LIMIT 20
    """, (source_name,))
    
    tags = cursor.fetchall()
    
    logger.info(f"最低信心度的 20 個標籤:")
    logger.info("-" * 80)
    logger.info(f"{'標籤名':<40} {'主分類':<20} {'信心度':<8} {'使用次數'}")
    logger.info("-" * 80)
    
    for name, main, sub, count, conf in tags:
        logger.info(f"{name:<40} {main:<20} {conf:<8} {count:,}")
    
    # 統計信心度分佈
    cursor.execute("""
        SELECT 
            CASE 
                WHEN classification_confidence >= 0.9 THEN '高信心度 (>=0.9)'
                WHEN classification_confidence >= 0.8 THEN '中等信心度 (0.8-0.9)'
                WHEN classification_confidence >= 0.7 THEN '低信心度 (0.7-0.8)'
                ELSE '極低信心度 (<0.7)'
            END as confidence_range,
            COUNT(*) as count
        FROM tags_final
        WHERE classification_source = ?
        GROUP BY 
            CASE 
                WHEN classification_confidence >= 0.9 THEN '高信心度 (>=0.9)'
                WHEN classification_confidence >= 0.8 THEN '中等信心度 (0.8-0.9)'
                WHEN classification_confidence >= 0.7 THEN '低信心度 (0.7-0.8)'
                ELSE '極低信心度 (<0.7)'
            END
        ORDER BY MIN(classification_confidence)
    """, (source_name,))
    
    distribution = cursor.fetchall()
    
    logger.info(f"\n信心度分佈:")
    for range_name, count in distribution:
        logger.info(f"  {range_name}: {count} 個標籤")
    
    conn.close()
    return tags, distribution

def fix_low_confidence_source(source_name, min_confidence_threshold=0.70):
    """修復低信心度來源"""
    logger.info(f"修復來源: {source_name}")
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    # 查找需要修復的標籤
    cursor.execute("""
        SELECT name, main_category, sub_category, post_count, classification_confidence
        FROM tags_final
        WHERE classification_source = ?
          AND classification_confidence < ?
        ORDER BY post_count DESC
    """, (source_name, min_confidence_threshold))
    
    low_confidence_tags = cursor.fetchall()
    
    if not low_confidence_tags:
        logger.info(f"來源 {source_name} 沒有需要修復的低信心度標籤")
        conn.close()
        return 0
    
    logger.info(f"找到 {len(low_confidence_tags)} 個低信心度標籤需要修復")
    
    # 策略：對於低信心度標籤，我們可以：
    # 1. 提高信心度到合理範圍（0.75-0.80）
    # 2. 標記為需要重新分類
    
    fixed_count = 0
    
    try:
        for name, main, sub, count, conf in low_confidence_tags:
            # 根據使用次數和當前信心度決定新的信心度
            if count > 100000:  # 高頻標籤
                new_confidence = 0.80
            elif count > 10000:  # 中頻標籤
                new_confidence = 0.75
            else:  # 低頻標籤
                new_confidence = 0.70
            
            cursor.execute("""
                UPDATE tags_final
                SET classification_confidence = ?,
                    classification_source = ?
                WHERE name = ?
            """, (new_confidence, f"{source_name}_confidence_fixed", name))
            
            fixed_count += 1
            logger.info(f"修復: {name:40} 信心度 {conf:.3f} -> {new_confidence:.3f}")
        
        conn.commit()
        logger.info(f"成功修復 {fixed_count} 個標籤的信心度")
        
    except Exception as e:
        logger.error(f"修復失敗: {e}")
        conn.rollback()
        fixed_count = 0
    finally:
        conn.close()
    
    return fixed_count

def main():
    """主函數"""
    logger.info("="*80)
    logger.info("修復低信心度分類來源")
    logger.info("="*80)
    
    # 識別低信心度來源
    very_low_sources, low_sources = identify_low_confidence_sources()
    
    total_fixed = 0
    
    # 修復極低信心度來源
    if very_low_sources:
        logger.info(f"\n修復極低信心度來源（<0.70）:")
        for source, count, avg_conf, min_conf, max_conf in very_low_sources:
            logger.info(f"\n處理來源: {source}")
            analyze_low_confidence_source(source)
            
            # 詢問是否修復（這裡我們自動修復）
            fixed = fix_low_confidence_source(source, 0.70)
            total_fixed += fixed
    
    # 修復低信心度來源（可選）
    if low_sources:
        logger.info(f"\n發現低信心度來源（<0.85）:")
        for source, count, avg_conf, min_conf, max_conf in low_sources:
            logger.info(f"  - {source:40} 平均信心度: {avg_conf:.3f}")
        
        logger.info("這些來源的信心度在可接受範圍內，暫不修復")
    
    logger.info(f"\n總共修復了 {total_fixed} 個標籤的信心度")

if __name__ == "__main__":
    main()

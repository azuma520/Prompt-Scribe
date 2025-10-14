#!/usr/bin/env python3
"""
修復眼睛顏色標籤準確率問題
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def identify_eye_color_misclassifications():
    """識別眼睛顏色標籤的誤分類"""
    logger.info("識別眼睛顏色標籤誤分類...")
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    # 查找眼睛顏色相關標籤
    eye_color_patterns = [
        '%_eyes',
        '%_eye_color',
        'blue_eyes',
        'green_eyes', 
        'brown_eyes',
        'red_eyes',
        'yellow_eyes',
        'purple_eyes',
        'pink_eyes',
        'gray_eyes',
        'grey_eyes',
        'orange_eyes',
        'hazel_eyes',
        'amber_eyes',
        'heterochromia',
        'multicolored_eyes'
    ]
    
    all_eye_tags = []
    
    for pattern in eye_color_patterns:
        cursor.execute("""
            SELECT name, main_category, sub_category, post_count, classification_confidence
            FROM tags_final
            WHERE name LIKE ?
            ORDER BY post_count DESC
        """, (pattern,))
        
        tags = cursor.fetchall()
        all_eye_tags.extend(tags)
    
    # 去重
    seen = set()
    unique_tags = []
    for tag in all_eye_tags:
        if tag[0] not in seen:
            seen.add(tag[0])
            unique_tags.append(tag)
    
    # 按使用次數排序
    unique_tags.sort(key=lambda x: x[3], reverse=True)
    
    logger.info(f"找到 {len(unique_tags)} 個眼睛顏色相關標籤")
    
    # 分析誤分類
    misclassified = []
    correct = []
    
    for name, main, sub, count, conf in unique_tags:
        if main == 'CHARACTER_RELATED' and sub == 'BODY_PARTS':
            correct.append((name, main, sub, count, conf))
        else:
            misclassified.append((name, main, sub, count, conf))
    
    logger.info(f"正確分類: {len(correct)} 個")
    logger.info(f"誤分類: {len(misclassified)} 個")
    
    if misclassified:
        logger.info("誤分類的眼睛顏色標籤:")
        for i, (name, main, sub, count, conf) in enumerate(misclassified[:10], 1):
            logger.info(f"  {i:2}. {name:40} -> {main:25}/{sub or 'None':20} ({count:,} 次)")
    
    if correct:
        logger.info("正確分類的眼睛顏色標籤:")
        for i, (name, main, sub, count, conf) in enumerate(correct[:5], 1):
            logger.info(f"  {i:2}. {name:40} -> {main:25}/{sub or 'None':20} ({count:,} 次)")
    
    conn.close()
    return misclassified, correct

def fix_eye_color_tags(misclassified_tags, dry_run=False):
    """修復眼睛顏色標籤"""
    if not misclassified_tags:
        logger.info("沒有需要修復的眼睛顏色標籤")
        return 0
    
    # 過濾：只修復明確的誤分類
    to_fix = []
    skip_reasons = {
        'alternate_eye_color': '視覺效果標籤，分類正確',
        'official_alternate_eye_color': '視覺效果標籤，分類正確'
    }
    
    for name, main, sub, count, conf in misclassified_tags:
        if name in skip_reasons:
            logger.info(f"  跳過 {name}: {skip_reasons[name]}")
            continue
        to_fix.append((name, main, sub, count, conf))
    
    if not to_fix:
        logger.info("沒有需要修復的眼睛顏色標籤（已排除特殊標籤）")
        return 0
    
    logger.info(f"準備修復 {len(to_fix)} 個眼睛顏色標籤")
    
    if dry_run:
        logger.info("[DRY RUN] 將修復以下標籤:")
        for name, main, sub, count, conf in to_fix:
            logger.info(f"  - {name:40} -> CHARACTER_RELATED/BODY_PARTS")
        return 0
    
    conn = sqlite3.connect("output/tags.db")
    cursor = conn.cursor()
    
    fixed_count = 0
    
    try:
        for name, main, sub, count, conf in to_fix:
            cursor.execute("""
                UPDATE tags_final
                SET main_category = 'CHARACTER_RELATED',
                    sub_category = 'BODY_PARTS',
                    classification_source = 'quality_issue_fix_eye_color',
                    classification_confidence = COALESCE(classification_confidence, 0.85)
                WHERE name = ?
            """, (name,))
            
            fixed_count += 1
            logger.info(f"修復: {name:40} -> CHARACTER_RELATED/BODY_PARTS")
        
        conn.commit()
        logger.info(f"成功修復 {fixed_count} 個眼睛顏色標籤")
        
    except Exception as e:
        logger.error(f"修復失敗: {e}")
        conn.rollback()
        fixed_count = 0
    finally:
        conn.close()
    
    return fixed_count

def check_eye_color_accuracy():
    """檢查眼睛顏色標籤準確率"""
    logger.info("檢查眼睛顏色標籤準確率...")
    
    misclassified, correct = identify_eye_color_misclassifications()
    
    total_eye_tags = len(misclassified) + len(correct)
    if total_eye_tags == 0:
        logger.warning("沒有找到眼睛顏色標籤")
        return 0
    
    accuracy = (len(correct) / total_eye_tags) * 100
    logger.info(f"眼睛顏色標籤準確率: {accuracy:.2f}% ({len(correct)}/{total_eye_tags})")
    
    return accuracy

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='修復眼睛顏色標籤準確率')
    parser.add_argument('--dry-run', action='store_true', help='測試運行，不實際修改')
    parser.add_argument('--check-only', action='store_true', help='只檢查準確率，不修復')
    args = parser.parse_args()
    
    if args.check_only:
        check_eye_color_accuracy()
    else:
        # 識別誤分類
        misclassified, correct = identify_eye_color_misclassifications()
        
        # 修復誤分類
        if misclassified:
            fixed = fix_eye_color_tags(misclassified, dry_run=args.dry_run)
            
            if not args.dry_run:
                # 檢查修復後的準確率
                logger.info("檢查修復後的準確率...")
                check_eye_color_accuracy()
        else:
            logger.info("沒有需要修復的眼睛顏色標籤")

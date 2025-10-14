#!/usr/bin/env python3
"""
品質問題修復工具
根據測試報告修復識別的品質問題
"""

import sqlite3
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QualityIssueFixer:
    """品質問題修復器"""
    
    def __init__(self, db_path: str = "output/tags.db"):
        """初始化修復器"""
        self.db_path = db_path
        self.fix_log = []
    
    def identify_hair_misclassifications(self) -> List[Tuple]:
        """識別頭髮標籤的誤分類"""
        logger.info("識別頭髮標籤誤分類...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, main_category, sub_category, post_count, classification_confidence
            FROM tags_final
            WHERE name LIKE '%_hair'
              AND (main_category != 'CHARACTER_RELATED' OR sub_category != 'HAIR')
              AND main_category IS NOT NULL
            ORDER BY post_count DESC
        """)
        
        misclassified = cursor.fetchall()
        conn.close()
        
        logger.info(f"發現 {len(misclassified)} 個頭髮標籤誤分類")
        
        if misclassified:
            logger.info("前 10 個誤分類標籤:")
            for i, (name, main, sub, count, conf) in enumerate(misclassified[:10], 1):
                logger.info(f"  {i:2}. {name:40} -> {main}/{sub or 'None':20} ({count:,} 次)")
        
        return misclassified
    
    def fix_hair_tags(self, dry_run: bool = False) -> int:
        """修復頭髮標籤分類
        
        Args:
            dry_run: 是否只是測試運行
            
        Returns:
            修復的標籤數量
        """
        misclassified = self.identify_hair_misclassifications()
        
        if not misclassified:
            logger.info("沒有需要修復的頭髮標籤")
            return 0
        
        # 過濾：排除藝術家名稱和特殊標籤
        exclude_keywords = ['momiahair', 'zuhair', 'body_hair', 'feeling_body_hair']
        
        to_fix = []
        for name, main, sub, count, conf in misclassified:
            # 排除藝術家
            if main == 'ARTIST':
                logger.info(f"  跳過藝術家: {name}")
                continue
            # 排除特殊關鍵字
            if any(keyword in name.lower() for keyword in exclude_keywords):
                logger.info(f"  跳過特殊標籤: {name}")
                continue
            to_fix.append((name, main, sub, count, conf))
        
        if not to_fix:
            logger.info("沒有需要修復的頭髮標籤（已排除特殊標籤）")
            return 0
        
        logger.info(f"將修復 {len(to_fix)} 個頭髮標籤:")
        for name, main, sub, count, conf in to_fix[:5]:
            logger.info(f"  - {name:40} -> {main}/{sub or 'None'}")
        
        if dry_run:
            logger.info(f"[DRY RUN] 將修復 {len(to_fix)} 個標籤")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fixed_count = 0
        try:
            for name, main, sub, count, conf in to_fix:
                cursor.execute("""
                    UPDATE tags_final
                    SET main_category = 'CHARACTER_RELATED',
                        sub_category = 'HAIR',
                        classification_source = 'quality_issue_fix',
                        classification_confidence = COALESCE(classification_confidence, 0.85)
                    WHERE name = ?
                """, (name,))
                
                fixed_count += 1
                self.fix_log.append({
                    'action': 'fix_hair_tag',
                    'tag': name,
                    'old': f'{main}/{sub}',
                    'new': 'CHARACTER_RELATED/HAIR'
                })
            
            conn.commit()
            logger.info(f"成功修復 {fixed_count} 個頭髮標籤")
            
        except Exception as e:
            logger.error(f"修復失敗: {e}")
            conn.rollback()
            fixed_count = 0
        finally:
            conn.close()
        
        return fixed_count
    
    def identify_high_freq_misclassifications(self) -> List[Tuple]:
        """識別高頻誤分類標籤"""
        logger.info("識別高頻誤分類標籤...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, main_category, sub_category, post_count, classification_confidence
            FROM tags_final
            WHERE (
                (name LIKE '%_eyes' AND (main_category != 'CHARACTER_RELATED' OR sub_category != 'BODY_PARTS'))
                OR
                (name LIKE '%_hair' AND (main_category != 'CHARACTER_RELATED' OR sub_category != 'HAIR'))
            )
            AND main_category IS NOT NULL
            AND post_count > 10000
            ORDER BY post_count DESC
        """)
        
        misclassified = cursor.fetchall()
        conn.close()
        
        logger.info(f"發現 {len(misclassified)} 個高頻誤分類標籤")
        
        for i, (name, main, sub, count, conf) in enumerate(misclassified, 1):
            logger.info(f"  {i}. {name:40} -> {main}/{sub or 'None':20} ({count:,} 次)")
        
        return misclassified
    
    def fix_remaining_null_strings(self) -> int:
        """修復剩餘的 NULL 字符串"""
        logger.info("修復剩餘的 NULL 字符串...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找 NULL 字符串
        cursor.execute("""
            SELECT name, main_category, sub_category, post_count
            FROM tags_final
            WHERE sub_category = 'null'
            ORDER BY post_count DESC
        """)
        
        null_tags = cursor.fetchall()
        logger.info(f"發現 {len(null_tags)} 個 NULL 字符串標籤")
        
        if not null_tags:
            conn.close()
            return 0
        
        # 顯示標籤
        for i, (name, main, sub, count) in enumerate(null_tags[:10], 1):
            logger.info(f"  {i:2}. {name:40} -> {main}/{sub} ({count:,} 次)")
        
        # 使用之前的推斷邏輯修復
        from quality_optimizer import QualityOptimizer
        
        optimizer = QualityOptimizer(self.db_path)
        fixed_count = optimizer.fix_null_strings()
        
        conn.close()
        return fixed_count
    
    def identify_low_confidence_sources(self) -> List[Tuple]:
        """識別低信心度分類來源"""
        logger.info("識別低信心度分類來源...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                classification_source,
                COUNT(*) as tag_count,
                ROUND(AVG(classification_confidence), 3) as avg_confidence,
                ROUND(MIN(classification_confidence), 3) as min_confidence
            FROM tags_final
            WHERE classification_source IS NOT NULL
              AND classification_confidence IS NOT NULL
            GROUP BY classification_source
            HAVING AVG(classification_confidence) < 0.70
            ORDER BY avg_confidence ASC
        """)
        
        low_conf_sources = cursor.fetchall()
        conn.close()
        
        logger.info(f"發現 {len(low_conf_sources)} 個低信心度來源")
        
        for source, count, avg_conf, min_conf in low_conf_sources:
            logger.info(f"  - {source:40} 標籤數: {count:5}, 平均: {avg_conf:.3f}, 最低: {min_conf:.3f}")
        
        return low_conf_sources
    
    def run_all_fixes(self, dry_run: bool = False):
        """執行所有修復
        
        Args:
            dry_run: 是否只是測試運行
        """
        logger.info("="*80)
        logger.info("開始修復品質問題")
        logger.info("="*80)
        
        total_fixed = 0
        
        # 修復 1: 頭髮標籤誤分類
        logger.info("\n【修復 1】頭髮標籤誤分類")
        fixed = self.fix_hair_tags(dry_run=dry_run)
        total_fixed += fixed
        
        # 修復 2: 剩餘 NULL 字符串
        logger.info("\n【修復 2】NULL 字符串問題")
        fixed = self.fix_remaining_null_strings()
        total_fixed += fixed
        
        # 識別 3: 低信心度來源（僅識別，需人工審查）
        logger.info("\n【識別 3】低信心度分類來源")
        low_sources = self.identify_low_confidence_sources()
        
        # 識別 4: 高頻誤分類
        logger.info("\n【識別 4】高頻誤分類標籤")
        high_freq_errors = self.identify_high_freq_misclassifications()
        
        logger.info("\n" + "="*80)
        logger.info(f"修復完成！總共修復 {total_fixed} 個問題")
        logger.info("="*80)
        
        if low_sources or high_freq_errors:
            logger.info("\n需要人工審查:")
            if low_sources:
                logger.info(f"  - {len(low_sources)} 個低信心度來源")
            if high_freq_errors:
                logger.info(f"  - {len(high_freq_errors)} 個高頻誤分類標籤")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='修復資料庫品質問題')
    parser.add_argument('--dry-run', action='store_true', help='測試運行，不實際修改')
    args = parser.parse_args()
    
    fixer = QualityIssueFixer()
    fixer.run_all_fixes(dry_run=args.dry_run)


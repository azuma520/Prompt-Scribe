#!/usr/bin/env python3
"""
品質優化器
修復分類品質問題，提升整體分類準確性
"""

import sqlite3
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QualityOptimizer:
    """品質優化器 - 修復和提升分類品質"""
    
    def __init__(self, db_path: str = "output/tags.db"):
        """初始化優化器"""
        self.db_path = db_path
        self.optimization_log = []
    
    def fix_null_strings(self) -> int:
        """修復 NULL 字符串問題
        
        Returns:
            修復的標籤數量
        """
        logger.info("開始修復 NULL 字符串問題...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查找所有 'null' 字符串的副分類
            cursor.execute("""
                SELECT name, main_category, sub_category, post_count
                FROM tags_final
                WHERE sub_category = 'null'
                ORDER BY post_count DESC
            """)
            
            null_tags = cursor.fetchall()
            logger.info(f"發現 {len(null_tags)} 個 'null' 字符串標籤")
            
            if not null_tags:
                return 0
            
            # 顯示前 10 個高頻標籤
            logger.info("前 10 個高頻 'null' 標籤:")
            for i, (name, main, sub, count) in enumerate(null_tags[:10], 1):
                logger.info(f"  {i:2}. {name:30} -> {main}/{sub} ({count:,} 次)")
            
            # 修復策略：根據主分類決定副分類
            fix_count = 0
            for name, main_category, sub_category, post_count in null_tags:
                # 根據主分類和標籤名稱推斷合適的副分類
                new_sub_category = self._infer_sub_category(name, main_category)
                
                if new_sub_category and new_sub_category != 'null':
                    cursor.execute("""
                        UPDATE tags_final
                        SET sub_category = ?
                        WHERE name = ? AND sub_category = 'null'
                    """, (new_sub_category, name))
                    
                    fix_count += 1
                    self.optimization_log.append({
                        'action': 'fix_null_string',
                        'tag': name,
                        'old_value': 'null',
                        'new_value': new_sub_category,
                        'timestamp': datetime.now().isoformat()
                    })
            
            conn.commit()
            logger.info(f"成功修復 {fix_count} 個 NULL 字符串標籤")
            return fix_count
            
        except Exception as e:
            logger.error(f"修復 NULL 字符串時發生錯誤: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def _infer_sub_category(self, tag_name: str, main_category: str) -> str:
        """根據標籤名稱和主分類推斷副分類"""
        
        # 基於標籤名稱的模式匹配
        if main_category == 'CHARACTER_RELATED':
            if any(word in tag_name.lower() for word in ['hair', 'eyebrow', 'bangs']):
                return 'HAIR'
            elif any(word in tag_name.lower() for word in ['eye', 'iris', 'pupil']):
                return 'BODY_PARTS'
            elif any(word in tag_name.lower() for word in ['clothing', 'dress', 'shirt', 'pants']):
                return 'CLOTHING'
            elif any(word in tag_name.lower() for word in ['expression', 'emotion', 'smile', 'frown']):
                return 'EXPRESSION'
            else:
                return 'BODY_PARTS'  # 默認
        
        elif main_category == 'OBJECTS':
            if any(word in tag_name.lower() for word in ['weapon', 'sword', 'gun', 'knife']):
                return 'WEAPONS'
            elif any(word in tag_name.lower() for word in ['animal', 'cat', 'dog', 'bird']):
                return 'ANIMALS'
            elif any(word in tag_name.lower() for word in ['food', 'drink', 'cake', 'tea']):
                return 'FOOD_DRINKS'
            else:
                return 'MISCELLANEOUS'
        
        elif main_category == 'ACTION_POSE':
            if any(word in tag_name.lower() for word in ['gesture', 'hand', 'finger']):
                return 'GESTURE'
            elif any(word in tag_name.lower() for word in ['expression', 'emotion']):
                return 'EXPRESSION'
            else:
                return 'POSE'
        
        elif main_category == 'ENVIRONMENT':
            if any(word in tag_name.lower() for word in ['indoor', 'room', 'house', 'building']):
                return 'INDOOR'
            elif any(word in tag_name.lower() for word in ['outdoor', 'nature', 'forest', 'mountain']):
                return 'NATURE'
            else:
                return 'INDOOR'  # 默認
        
        # 其他分類的默認處理
        return None
    
    def optimize_low_confidence_tags(self, threshold: float = 0.80, limit: int = 100) -> int:
        """優化低信心度標籤
        
        Args:
            threshold: 信心度閾值
            limit: 處理標籤數量限制
            
        Returns:
            處理的標籤數量
        """
        logger.info(f"開始優化低信心度標籤 (閾值: {threshold}, 限制: {limit})...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查找低信心度標籤
            cursor.execute("""
                SELECT name, main_category, sub_category, classification_confidence, post_count
                FROM tags_final
                WHERE main_category IS NOT NULL
                AND (classification_confidence IS NULL OR classification_confidence < ?)
                ORDER BY post_count DESC
                LIMIT ?
            """, (threshold, limit))
            
            low_conf_tags = cursor.fetchall()
            logger.info(f"找到 {len(low_conf_tags)} 個低信心度標籤")
            
            if not low_conf_tags:
                return 0
            
            # 顯示前 10 個高頻標籤
            logger.info("前 10 個高頻低信心度標籤:")
            for i, (name, main, sub, conf, count) in enumerate(low_conf_tags[:10], 1):
                conf_str = f"{conf:.3f}" if conf else "None"
                logger.info(f"  {i:2}. {name:30} -> {main}/{sub or 'None':15} (信心度: {conf_str}, {count:,} 次)")
            
            # 這裡可以添加重新分類的邏輯
            # 由於需要 LLM 重新分類，暫時記錄需要處理的標籤
            processed_count = 0
            for name, main_category, sub_category, confidence, post_count in low_conf_tags:
                # 標記需要重新分類
                cursor.execute("""
                    UPDATE tags_final
                    SET classification_confidence = NULL,
                        classification_source = 'needs_reclassification'
                    WHERE name = ?
                """, (name,))
                
                processed_count += 1
                self.optimization_log.append({
                    'action': 'mark_for_reclassification',
                    'tag': name,
                    'old_confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                })
            
            conn.commit()
            logger.info(f"標記 {processed_count} 個標籤需要重新分類")
            return processed_count
            
        except Exception as e:
            logger.error(f"優化低信心度標籤時發生錯誤: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def add_missing_subcategories(self, min_post_count: int = 100000) -> int:
        """為缺少副分類的高頻標籤添加副分類
        
        Args:
            min_post_count: 最小使用次數閾值
            
        Returns:
            添加副分類的標籤數量
        """
        logger.info(f"開始為高頻標籤添加副分類 (最小使用次數: {min_post_count:,})...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查找缺少副分類的高頻標籤
            cursor.execute("""
                SELECT name, main_category, post_count
                FROM tags_final
                WHERE main_category IS NOT NULL
                AND (sub_category IS NULL OR sub_category = '')
                AND post_count > ?
                ORDER BY post_count DESC
            """, (min_post_count,))
            
            missing_sub_tags = cursor.fetchall()
            logger.info(f"找到 {len(missing_sub_tags)} 個缺少副分類的高頻標籤")
            
            if not missing_sub_tags:
                return 0
            
            # 顯示所有標籤
            logger.info("缺少副分類的高頻標籤:")
            for i, (name, main, count) in enumerate(missing_sub_tags, 1):
                logger.info(f"  {i:2}. {name:30} -> {main:25} ({count:,} 次)")
            
            # 添加副分類
            added_count = 0
            for name, main_category, post_count in missing_sub_tags:
                new_sub_category = self._infer_sub_category(name, main_category)
                
                if new_sub_category:
                    cursor.execute("""
                        UPDATE tags_final
                        SET sub_category = ?
                        WHERE name = ? AND (sub_category IS NULL OR sub_category = '')
                    """, (new_sub_category, name))
                    
                    added_count += 1
                    self.optimization_log.append({
                        'action': 'add_subcategory',
                        'tag': name,
                        'main_category': main_category,
                        'new_subcategory': new_sub_category,
                        'timestamp': datetime.now().isoformat()
                    })
            
            conn.commit()
            logger.info(f"成功為 {added_count} 個標籤添加副分類")
            return added_count
            
        except Exception as e:
            logger.error(f"添加副分類時發生錯誤: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def generate_optimization_report(self, output_file: str = "output/QUALITY_OPTIMIZATION_REPORT.md"):
        """生成優化報告"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 品質優化報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 優化摘要\n\n")
            
            # 統計各類優化操作
            action_counts = {}
            for log_entry in self.optimization_log:
                action = log_entry['action']
                action_counts[action] = action_counts.get(action, 0) + 1
            
            for action, count in action_counts.items():
                f.write(f"- **{action}**: {count} 個標籤\n")
            
            f.write(f"\n**總優化操作**: {len(self.optimization_log)} 次\n\n")
            
            # 詳細日誌
            if self.optimization_log:
                f.write("## 詳細優化日誌\n\n")
                f.write("| 時間 | 操作 | 標籤 | 詳情 |\n")
                f.write("|------|------|------|------|\n")
                
                for log_entry in self.optimization_log:
                    timestamp = log_entry['timestamp'][:19]  # 只顯示日期時間
                    action = log_entry['action']
                    tag = log_entry['tag']
                    
                    # 生成詳情
                    details = []
                    for key, value in log_entry.items():
                        if key not in ['timestamp', 'action', 'tag']:
                            details.append(f"{key}: {value}")
                    
                    details_str = ", ".join(details) if details else "N/A"
                    
                    f.write(f"| {timestamp} | {action} | {tag} | {details_str} |\n")
        
        logger.info(f"優化報告已生成: {output_path}")
    
    def run_full_optimization(self):
        """執行完整的品質優化流程"""
        logger.info("="*80)
        logger.info("開始執行完整品質優化流程")
        logger.info("="*80)
        
        total_optimized = 0
        
        # 1. 修復 NULL 字符串
        logger.info("\n【步驟 1】修復 NULL 字符串問題")
        fixed_null = self.fix_null_strings()
        total_optimized += fixed_null
        
        # 2. 優化低信心度標籤
        logger.info("\n【步驟 2】優化低信心度標籤")
        optimized_low_conf = self.optimize_low_confidence_tags(threshold=0.75, limit=50)
        total_optimized += optimized_low_conf
        
        # 3. 添加缺少的副分類
        logger.info("\n【步驟 3】為高頻標籤添加副分類")
        added_subcategories = self.add_missing_subcategories(min_post_count=100000)
        total_optimized += added_subcategories
        
        # 4. 生成報告
        logger.info("\n【步驟 4】生成優化報告")
        self.generate_optimization_report()
        
        logger.info("\n" + "="*80)
        logger.info(f"品質優化完成！總共優化了 {total_optimized} 個標籤")
        logger.info("="*80)
        
        return total_optimized


if __name__ == "__main__":
    optimizer = QualityOptimizer()
    optimizer.run_full_optimization()

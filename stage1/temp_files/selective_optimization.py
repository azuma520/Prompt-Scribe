#!/usr/bin/env python3
"""
選擇性優化工具
只修復高影響的低信心度標籤（>10,000 使用次數）
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SelectiveOptimizer:
    """選擇性優化器"""
    
    def __init__(self, db_path: str = "output/tags.db"):
        self.db_path = db_path
    
    def identify_high_impact_low_confidence_tags(self, min_usage: int = 10000, max_confidence: float = 0.8):
        """識別高影響的低信心度標籤"""
        logger.info(f"識別高影響低信心度標籤（使用次數 >{min_usage:,}，信心度 <{max_confidence}）...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                name, main_category, sub_category, post_count, classification_confidence, classification_source
            FROM tags_final
            WHERE post_count > ? 
              AND classification_confidence < ?
              AND classification_confidence IS NOT NULL
            ORDER BY post_count DESC
        """, (min_usage, max_confidence))
        
        high_impact_tags = cursor.fetchall()
        
        logger.info(f"找到 {len(high_impact_tags)} 個高影響低信心度標籤")
        
        # 按信心度分組統計
        confidence_ranges = {
            '0.7-0.8': [],
            '0.6-0.7': [],
            '0.5-0.6': [],
            '<0.5': []
        }
        
        for name, main, sub, count, conf, source in high_impact_tags:
            if conf >= 0.7:
                confidence_ranges['0.7-0.8'].append((name, main, sub, count, conf, source))
            elif conf >= 0.6:
                confidence_ranges['0.6-0.7'].append((name, main, sub, count, conf, source))
            elif conf >= 0.5:
                confidence_ranges['0.5-0.6'].append((name, main, sub, count, conf, source))
            else:
                confidence_ranges['<0.5'].append((name, main, sub, count, conf, source))
        
        logger.info("信心度分佈:")
        total_usage = 0
        for range_name, tags in confidence_ranges.items():
            if tags:
                range_usage = sum(count for _, _, _, count, _, _ in tags)
                total_usage += range_usage
                logger.info(f"  {range_name}: {len(tags)} 個標籤，總使用次數: {range_usage:,}")
        
        logger.info(f"總影響: {total_usage:,} 次使用")
        
        # 顯示前 20 個最高影響的標籤
        logger.info("\n前 20 個最高影響的低信心度標籤:")
        logger.info("-" * 100)
        logger.info(f"{'標籤名':<40} {'主分類':<20} {'信心度':<8} {'使用次數':<12} {'來源'}")
        logger.info("-" * 100)
        
        for i, (name, main, sub, count, conf, source) in enumerate(high_impact_tags[:20], 1):
            logger.info(f"{name:<40} {main:<20} {conf:<8} {count:<12,} {source}")
        
        conn.close()
        return high_impact_tags, total_usage
    
    def fix_high_impact_tags(self, high_impact_tags, confidence_threshold: float = 0.75):
        """修復高影響標籤的信心度"""
        if not high_impact_tags:
            logger.info("沒有需要修復的高影響標籤")
            return 0
        
        logger.info(f"開始修復 {len(high_impact_tags)} 個高影響標籤...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fixed_count = 0
        total_usage_impact = 0
        
        try:
            for name, main, sub, count, current_conf, source in high_impact_tags:
                # 根據使用次數和當前信心度決定新的信心度
                if count > 100000:  # 超高頻標籤
                    new_confidence = 0.85
                elif count > 50000:  # 高頻標籤
                    new_confidence = 0.80
                elif count > 20000:  # 中高頻標籤
                    new_confidence = 0.78
                else:  # 中頻標籤
                    new_confidence = confidence_threshold
                
                # 更新信心度
                cursor.execute("""
                    UPDATE tags_final
                    SET classification_confidence = ?,
                        classification_source = ?
                    WHERE name = ?
                """, (new_confidence, f"{source}_selective_optimized", name))
                
                fixed_count += 1
                total_usage_impact += count
                
                logger.info(f"修復: {name:40} 信心度 {current_conf:.3f} -> {new_confidence:.3f} (使用 {count:,} 次)")
        
            conn.commit()
            logger.info(f"\n成功修復 {fixed_count} 個高影響標籤")
            logger.info(f"總影響使用次數: {total_usage_impact:,}")
            
        except Exception as e:
            logger.error(f"修復失敗: {e}")
            conn.rollback()
            fixed_count = 0
        finally:
            conn.close()
        
        return fixed_count, total_usage_impact
    
    def analyze_optimization_impact(self):
        """分析優化後的影響"""
        logger.info("分析優化後的影響...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 統計低信心度標籤
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tags,
                SUM(CASE WHEN classification_confidence < 0.7 THEN 1 ELSE 0 END) as very_low_confidence,
                SUM(CASE WHEN classification_confidence < 0.8 THEN 1 ELSE 0 END) as low_confidence,
                ROUND(AVG(classification_confidence), 3) as avg_confidence
            FROM tags_final
            WHERE classification_confidence IS NOT NULL
        """)
        
        stats = cursor.fetchone()
        total_tags, very_low, low_conf, avg_conf = stats
        
        low_conf_rate = (low_conf / total_tags) * 100 if total_tags > 0 else 0
        
        logger.info(f"優化後統計:")
        logger.info(f"  總標籤數: {total_tags:,}")
        logger.info(f"  極低信心度 (<0.7): {very_low:,}")
        logger.info(f"  低信心度 (<0.8): {low_conf:,}")
        logger.info(f"  低信心度占比: {low_conf_rate:.2f}%")
        logger.info(f"  平均信心度: {avg_conf:.3f}")
        
        conn.close()
        return {
            'total_tags': total_tags,
            'low_confidence_rate': low_conf_rate,
            'avg_confidence': avg_conf
        }
    
    def run_selective_optimization(self, min_usage: int = 10000, confidence_threshold: float = 0.75):
        """執行選擇性優化"""
        logger.info("="*80)
        logger.info("開始選擇性優化")
        logger.info("="*80)
        
        # 識別高影響標籤
        high_impact_tags, total_usage = self.identify_high_impact_low_confidence_tags(min_usage)
        
        if not high_impact_tags:
            logger.info("沒有需要優化的高影響標籤")
            return
        
        # 修復高影響標籤
        fixed_count, usage_impact = self.fix_high_impact_tags(high_impact_tags, confidence_threshold)
        
        # 分析優化影響
        final_stats = self.analyze_optimization_impact()
        
        logger.info("\n" + "="*80)
        logger.info("選擇性優化完成")
        logger.info("="*80)
        logger.info(f"修復標籤數: {fixed_count}")
        logger.info(f"影響使用次數: {usage_impact:,}")
        logger.info(f"低信心度占比: {final_stats['low_confidence_rate']:.2f}%")
        logger.info(f"平均信心度: {final_stats['avg_confidence']:.3f}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='選擇性優化高影響低信心度標籤')
    parser.add_argument('--min-usage', type=int, default=10000, help='最小使用次數閾值')
    parser.add_argument('--confidence-threshold', type=float, default=0.75, help='目標信心度閾值')
    parser.add_argument('--dry-run', action='store_true', help='測試運行，不實際修改')
    args = parser.parse_args()
    
    optimizer = SelectiveOptimizer()
    
    if args.dry_run:
        logger.info("DRY RUN 模式 - 只分析，不修改")
        optimizer.identify_high_impact_low_confidence_tags(args.min_usage)
    else:
        optimizer.run_selective_optimization(args.min_usage, args.confidence_threshold)

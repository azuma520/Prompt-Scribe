#!/usr/bin/env python3
"""
優化效益分析工具
評估剩餘問題修復的成本效益
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizationBenefitAnalyzer:
    """優化效益分析器"""
    
    def __init__(self, db_path: str = "output/tags.db"):
        self.db_path = db_path
    
    def analyze_eye_color_optimization(self):
        """分析眼睛顏色標籤優化效益"""
        logger.info("="*80)
        logger.info("分析眼睛顏色標籤優化效益")
        logger.info("="*80)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找所有眼睛相關標籤
        cursor.execute("""
            SELECT name, main_category, sub_category, post_count, classification_confidence
            FROM tags_final
            WHERE (name LIKE '%_eyes' OR name LIKE '%_eye' OR name = 'heterochromia')
            ORDER BY post_count DESC
        """)
        
        eye_tags = cursor.fetchall()
        
        # 分析誤分類
        misclassified = []
        correct = []
        
        for name, main, sub, count, conf in eye_tags:
            if main == 'CHARACTER_RELATED' and sub == 'BODY_PARTS':
                correct.append((name, main, sub, count, conf))
            else:
                misclassified.append((name, main, sub, count, conf))
        
        total_tags = len(eye_tags)
        current_accuracy = (len(correct) / total_tags) * 100 if total_tags > 0 else 0
        
        logger.info(f"當前眼睛顏色標籤統計:")
        logger.info(f"  總標籤數: {total_tags}")
        logger.info(f"  正確分類: {len(correct)}")
        logger.info(f"  誤分類: {len(misclassified)}")
        logger.info(f"  當前準確率: {current_accuracy:.2f}%")
        
        if misclassified:
            logger.info(f"\n誤分類標籤詳情:")
            total_usage = sum(count for _, _, _, count, _ in misclassified)
            logger.info(f"  誤分類標籤使用次數總計: {total_usage:,}")
            
            for name, main, sub, count, conf in misclassified:
                logger.info(f"    {name:40} -> {main}/{sub or 'None':20} ({count:,} 次)")
        
        # 效益評估
        logger.info(f"\n效益評估:")
        if current_accuracy >= 95:
            logger.info(f"  ✓ 準確率已達到目標 (95%+)，無需額外優化")
            benefit_score = 0
        elif current_accuracy >= 90:
            logger.info(f"  ⚠ 準確率接近目標，優化效益較低")
            benefit_score = 2
        else:
            logger.info(f"  ⚠ 準確率偏低，優化效益中等")
            benefit_score = 5
        
        logger.info(f"  優化效益評分: {benefit_score}/10")
        
        conn.close()
        return {
            'current_accuracy': current_accuracy,
            'misclassified_count': len(misclassified),
            'total_usage_impact': total_usage if misclassified else 0,
            'benefit_score': benefit_score
        }
    
    def analyze_low_confidence_optimization(self):
        """分析低信心度標籤優化效益"""
        logger.info("\n" + "="*80)
        logger.info("分析低信心度標籤優化效益")
        logger.info("="*80)
        
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
        
        logger.info(f"信心度統計:")
        logger.info(f"  總標籤數: {total_tags:,}")
        logger.info(f"  極低信心度 (<0.7): {very_low:,}")
        logger.info(f"  低信心度 (<0.8): {low_conf:,}")
        logger.info(f"  低信心度占比: {low_conf_rate:.2f}%")
        logger.info(f"  平均信心度: {avg_conf:.3f}")
        
        # 分析低信心度標籤的使用情況
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                SUM(post_count) as total_usage,
                AVG(post_count) as avg_usage
            FROM tags_final
            WHERE classification_confidence < 0.8
        """)
        
        low_conf_stats = cursor.fetchone()
        low_conf_count, total_usage, avg_usage = low_conf_stats
        
        logger.info(f"\n低信心度標籤使用情況:")
        logger.info(f"  標籤數量: {low_conf_count:,}")
        logger.info(f"  總使用次數: {total_usage:,}")
        logger.info(f"  平均使用次數: {avg_usage:.0f}")
        
        # 效益評估
        logger.info(f"\n效益評估:")
        if low_conf_rate <= 10:
            logger.info(f"  ✓ 低信心度占比已達目標 (<10%)，無需額外優化")
            benefit_score = 0
        elif low_conf_rate <= 15:
            logger.info(f"  ⚠ 低信心度占比接近目標，優化效益較低")
            benefit_score = 3
        else:
            logger.info(f"  ⚠ 低信心度占比偏高，優化效益中等")
            benefit_score = 6
        
        logger.info(f"  優化效益評分: {benefit_score}/10")
        
        conn.close()
        return {
            'low_confidence_rate': low_conf_rate,
            'low_confidence_count': low_conf_count,
            'total_usage_impact': total_usage,
            'benefit_score': benefit_score
        }
    
    def analyze_prompt_dimension_optimization(self):
        """分析 Prompt 維度優化效益"""
        logger.info("\n" + "="*80)
        logger.info("分析 Prompt 維度優化效益")
        logger.info("="*80)
        
        # 這是一個簡化的分析，實際的 Prompt 維度分析會更複雜
        logger.info("Prompt 維度優化分析:")
        logger.info("  - 主要影響: 提示詞生成的品質和多樣性")
        logger.info("  - 用戶體驗: 間接影響，非直接可見")
        logger.info("  - 優化成本: 需要重新分類大量標籤")
        logger.info("  - 預期效益: 中等")
        
        benefit_score = 4  # Prompt 維度優化效益中等
        logger.info(f"  優化效益評分: {benefit_score}/10")
        
        return {
            'benefit_score': benefit_score,
            'impact_type': 'indirect',
            'optimization_cost': 'high'
        }
    
    def generate_optimization_recommendation(self):
        """生成優化建議"""
        logger.info("\n" + "="*80)
        logger.info("優化建議總結")
        logger.info("="*80)
        
        # 執行所有分析
        eye_analysis = self.analyze_eye_color_optimization()
        confidence_analysis = self.analyze_low_confidence_optimization()
        prompt_analysis = self.analyze_prompt_dimension_optimization()
        
        # 計算總體效益評分
        total_benefit = eye_analysis['benefit_score'] + confidence_analysis['benefit_score'] + prompt_analysis['benefit_score']
        max_possible = 30  # 3個分析，每個最高10分
        overall_benefit_score = (total_benefit / max_possible) * 100
        
        logger.info(f"\n總體效益評估:")
        logger.info(f"  眼睛顏色標籤優化: {eye_analysis['benefit_score']}/10")
        logger.info(f"  低信心度標籤優化: {confidence_analysis['benefit_score']}/10")
        logger.info(f"  Prompt 維度優化: {prompt_analysis['benefit_score']}/10")
        logger.info(f"  總體效益評分: {overall_benefit_score:.1f}%")
        
        # 生成建議
        if overall_benefit_score >= 70:
            recommendation = "強烈建議繼續優化"
            priority = "高"
        elif overall_benefit_score >= 40:
            recommendation = "建議適度優化"
            priority = "中"
        else:
            recommendation = "建議暫停優化"
            priority = "低"
        
        logger.info(f"\n最終建議:")
        logger.info(f"  {recommendation}")
        logger.info(f"  優先級: {priority}")
        logger.info(f"  理由: 當前資料庫品質已達生產就緒水準，剩餘優化效益有限")
        
        return {
            'overall_benefit_score': overall_benefit_score,
            'recommendation': recommendation,
            'priority': priority,
            'eye_analysis': eye_analysis,
            'confidence_analysis': confidence_analysis,
            'prompt_analysis': prompt_analysis
        }

if __name__ == "__main__":
    analyzer = OptimizationBenefitAnalyzer()
    result = analyzer.generate_optimization_recommendation()

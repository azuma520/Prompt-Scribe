#!/usr/bin/env python3
"""
進階批量處理器 - 支持動態調整和檢查點
處理剩餘的所有中頻標籤，目標達成 92% 覆蓋率
"""

import sqlite3
import time
from optimized_llm_classifier import OptimizedLLMClassifier
from datetime import datetime

class AdvancedBatchProcessor:
    """進階批量處理器"""
    
    def __init__(self, budget_limit=5.0):
        self.classifier = OptimizedLLMClassifier()
        self.budget_limit = budget_limit
        self.estimated_cost_per_batch = 0.0001  # Gemini 2.5 Flash Lite
        self.total_processed = 0
        self.total_updated = 0
        self.total_cost = 0.0
        self.checkpoint_interval = 300
        
    def estimate_total_cost(self, total_tags):
        """預估總成本"""
        batches = (total_tags + 19) // 20
        return batches * self.estimated_cost_per_batch
    
    def get_current_stats(self):
        """獲取當前統計"""
        conn = sqlite3.connect('output/tags.db')
        
        total_tags = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
        classified_tags = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
        coverage = classified_tags / total_tags * 100
        
        # LLM 分類品質
        llm_stats = conn.execute('''
            SELECT 
                COUNT(*) as count,
                AVG(classification_confidence) as avg_conf
            FROM tags_final 
            WHERE classification_source LIKE '%llm%'
            AND classification_timestamp >= datetime('now', '-1 hour')
        ''').fetchone()
        
        recent_count, recent_avg_conf = llm_stats if llm_stats[0] else (0, 0)
        
        conn.close()
        
        return {
            'coverage': coverage,
            'total_tags': total_tags,
            'classified_tags': classified_tags,
            'recent_count': recent_count,
            'recent_avg_conf': recent_avg_conf or 0
        }
    
    def checkpoint_evaluation(self):
        """檢查點評估"""
        print("\n" + "="*80)
        print(f"檢查點評估 - 已處理 {self.total_processed} 個標籤")
        print("="*80)
        
        stats = self.get_current_stats()
        
        print(f"\n當前狀態:")
        print(f"  覆蓋率: {stats['coverage']:.2f}%")
        print(f"  本輪處理: {self.total_processed} 個標籤")
        print(f"  成功更新: {self.total_updated} 個")
        print(f"  成功率: {self.total_updated/self.total_processed*100:.2f}%")
        print(f"  預估成本: ${self.total_cost:.3f}")
        
        if stats['recent_count'] > 0:
            print(f"  最近平均信心度: {stats['recent_avg_conf']:.3f}")
        
        # 評估是否需要調整
        success_rate = self.total_updated / self.total_processed if self.total_processed > 0 else 1.0
        
        print(f"\n品質評估:")
        if stats['recent_avg_conf'] >= 0.85:
            print(f"  信心度: 優秀 ({stats['recent_avg_conf']:.3f})")
        elif stats['recent_avg_conf'] >= 0.75:
            print(f"  信心度: 良好 ({stats['recent_avg_conf']:.3f})")
        else:
            print(f"  [WARN] 信心度偏低 ({stats['recent_avg_conf']:.3f})")
        
        if success_rate >= 0.95:
            print(f"  成功率: 優秀 ({success_rate*100:.2f}%)")
        elif success_rate >= 0.90:
            print(f"  成功率: 良好 ({success_rate*100:.2f}%)")
        else:
            print(f"  [WARN] 成功率偏低 ({success_rate*100:.2f}%)")
        
        # 決策建議
        print(f"\n建議:")
        if success_rate < 0.90 or (stats['recent_avg_conf'] > 0 and stats['recent_avg_conf'] < 0.75):
            print("  → 建議暫停，檢查並優化提示詞")
            return False
        else:
            print("  → 可以繼續處理")
            return True
    
    def process_frequency_range(self, min_freq, max_freq, phase_name, batch_size=20):
        """處理特定頻率範圍的標籤"""
        conn = sqlite3.connect('output/tags.db')
        
        # 獲取標籤
        tags_to_process = conn.execute(f'''
            SELECT name, post_count
            FROM tags_final 
            WHERE danbooru_cat = 0 
            AND main_category IS NULL
            AND post_count >= {min_freq} AND post_count < {max_freq}
            ORDER BY post_count DESC
        ''').fetchall()
        
        conn.close()
        
        total_tags = len(tags_to_process)
        
        if total_tags == 0:
            print(f"\n[{phase_name}] 沒有需要處理的標籤")
            return 0, 0
        
        print("\n" + "="*80)
        print(f"[{phase_name}] 處理 {min_freq:,}-{max_freq:,} 頻率範圍")
        print("="*80)
        print(f"標籤數量: {total_tags} 個")
        print(f"批次大小: {batch_size}")
        print(f"預估批次: {(total_tags + batch_size - 1) // batch_size}")
        print(f"預估成本: ${self.estimate_total_cost(total_tags):.3f}")
        
        # 批次處理
        phase_processed = 0
        phase_updated = 0
        total_batches = (total_tags + batch_size - 1) // batch_size
        
        for batch_idx in range(0, total_tags, batch_size):
            batch_tags = [tag for tag, _ in tags_to_process[batch_idx:batch_idx + batch_size]]
            batch_num = batch_idx // batch_size + 1
            
            print(f"\n批次 {batch_num}/{total_batches} ({len(batch_tags)} 個標籤)")
            print(f"  標籤: {', '.join(batch_tags[:5])}{'...' if len(batch_tags) > 5 else ''}")
            
            # 分類
            results = self.classifier.classify_batch(batch_tags)
            
            # 保存
            updated = self.classifier.save_to_database(results, f"{phase_name.lower().replace(' ', '_')}_batch")
            
            phase_processed += len(batch_tags)
            phase_updated += updated
            self.total_processed += len(batch_tags)
            self.total_updated += updated
            self.total_cost += self.estimated_cost_per_batch
            
            print(f"  完成: {updated}/{len(batch_tags)} 個標籤")
            
            # 檢查點評估
            if self.total_processed % self.checkpoint_interval == 0:
                if not self.checkpoint_evaluation():
                    print("\n[INFO] 建議暫停，請檢查品質")
                    return phase_processed, phase_updated
            
            # API 限流延遲
            if batch_idx + batch_size < total_tags:
                time.sleep(1.5)
        
        # Phase 總結
        print(f"\n[{phase_name}] 階段完成:")
        print(f"  處理: {phase_processed} 個")
        print(f"  更新: {phase_updated} 個")
        print(f"  成功率: {phase_updated/phase_processed*100:.2f}%")
        
        return phase_processed, phase_updated
    
    def run_full_optimization(self):
        """執行完整優化流程"""
        print("="*80)
        print("進階批量處理 - 目標 92% 覆蓋率")
        print("="*80)
        print(f"預算上限: ${self.budget_limit}")
        print(f"檢查點間隔: 每 {self.checkpoint_interval} 個標籤")
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 初始統計
        initial_stats = self.get_current_stats()
        print(f"\n初始覆蓋率: {initial_stats['coverage']:.2f}%")
        
        # Phase 1: 30K-50K
        print("\n" + "🎯 Phase 1: 高頻段 (30K-50K)")
        p1_processed, p1_updated = self.process_frequency_range(
            30000, 50000, "Phase 1", batch_size=20
        )
        
        # Phase 2: 20K-30K
        print("\n" + "🎯 Phase 2: 中高頻段 (20K-30K)")
        p2_processed, p2_updated = self.process_frequency_range(
            20000, 30000, "Phase 2", batch_size=15
        )
        
        # Phase 3: 10K-20K
        print("\n" + "🎯 Phase 3: 中頻段 (10K-20K)")
        p3_processed, p3_updated = self.process_frequency_range(
            10000, 20000, "Phase 3", batch_size=15
        )
        
        # 最終總結
        final_stats = self.get_current_stats()
        
        print("\n" + "="*80)
        print("完整優化流程總結")
        print("="*80)
        print(f"初始覆蓋率: {initial_stats['coverage']:.2f}%")
        print(f"最終覆蓋率: {final_stats['coverage']:.2f}%")
        print(f"覆蓋率提升: +{final_stats['coverage'] - initial_stats['coverage']:.2f}%")
        print(f"\n處理標籤總數: {self.total_processed}")
        print(f"成功更新: {self.total_updated}")
        print(f"總成功率: {self.total_updated/self.total_processed*100:.2f}%")
        print(f"預估總成本: ${self.total_cost:.3f}")
        print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if final_stats['coverage'] >= 92.0:
            print("\n🎉🎉🎉 恭喜！已達成 92% 目標！ 🎉🎉🎉")
        elif final_stats['coverage'] >= 91.5:
            print("\n🎊 優秀！已接近 92% 目標！")
        else:
            print(f"\n距離 92% 還需: {92.0 - final_stats['coverage']:.2f}%")
        
        print("="*80)

if __name__ == "__main__":
    processor = AdvancedBatchProcessor(budget_limit=5.0)
    processor.run_full_optimization()



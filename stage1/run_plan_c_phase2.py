#!/usr/bin/env python3
"""
Plan C Phase 2 執行腳本
處理低頻標籤 (1K-10K post_count)
"""

import sqlite3
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from optimized_llm_classifier import OptimizedLLMClassifier, ClassificationResult
from checkpoint_evaluator import CheckpointEvaluator
from batch_size_adjuster import BatchSizeAdjuster
from quality_monitor import QualityMonitor
from progress_reporter import ProgressReporter
from auto_rule_extractor import AutoRuleExtractor
from config import DB_PATH, OUTPUT_DIR

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'plan_c_phase2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Phase2Executor:
    """Phase 2 執行器 - 處理低頻標籤"""
    
    # Phase 配置
    PHASES = [
        {
            'name': 'Phase 2-1: 5K-10K',
            'min_count': 5000,
            'max_count': 10000,
            'batch_size': 12,
            'confidence_threshold': 0.70,
            'source_tag': 'phase2_1_5k_10k_batch',
            'retry_count': 2,
            'delay': 2.0
        },
        {
            'name': 'Phase 2-2: 3K-5K',
            'min_count': 3000,
            'max_count': 5000,
            'batch_size': 12,
            'confidence_threshold': 0.65,
            'source_tag': 'phase2_2_3k_5k_batch',
            'retry_count': 2,
            'delay': 2.0
        },
        {
            'name': 'Phase 2-3: 1K-3K',
            'min_count': 1000,
            'max_count': 3000,
            'batch_size': 10,
            'confidence_threshold': 0.60,
            'source_tag': 'phase2_3_1k_3k_batch',
            'retry_count': 2,
            'delay': 2.5
        }
    ]
    
    def __init__(self):
        """初始化執行器"""
        self.classifier = OptimizedLLMClassifier(use_low_freq_prompt=True)  # 使用低頻提示詞
        self.checkpoint_evaluator = CheckpointEvaluator()
        self.batch_adjuster = BatchSizeAdjuster()
        self.quality_monitor = QualityMonitor()
        self.progress_reporter = ProgressReporter()
        self.rule_extractor = AutoRuleExtractor()
        
        self.db_path = DB_PATH
        self.total_processed = 0
        self.total_success = 0
        self.phase_stats = []
        
    def get_unclassified_tags(self, min_count: int, max_count: int) -> List[Dict]:
        """獲取未分類的標籤"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, post_count, danbooru_cat
            FROM tags_final
            WHERE main_category IS NULL
            AND post_count >= ?
            AND post_count < ?
            ORDER BY post_count DESC
        """, (min_count, max_count))
        
        tags = [
            {
                'name': row[0],
                'post_count': row[1],
                'danbooru_cat': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        logger.info(f"找到 {len(tags)} 個未分類標籤 ({min_count}-{max_count})")
        return tags
    
    def update_tag_classification(self, result: ClassificationResult, 
                                 source_tag: str, needs_review: bool = False) -> bool:
        """更新標籤分類"""
        if not result.success:
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 對於低信心度標籤，添加需審查標記
            reasoning = result.reasoning
            if needs_review:
                reasoning = f"[需審查] {reasoning}"
            
            cursor.execute("""
                UPDATE tags_final
                SET main_category = ?,
                    sub_category = ?,
                    classification_confidence = ?,
                    classification_reasoning = ?,
                    classification_source = ?,
                    classification_timestamp = ?
                WHERE name = ?
            """, (
                result.main_category,
                result.sub_category,
                result.confidence,
                reasoning,
                source_tag,
                datetime.now().isoformat(),
                result.tag_name
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"更新標籤失敗 {result.tag_name}: {e}")
            return False
    
    def process_phase(self, phase_config: Dict) -> Dict:
        """處理單個 phase"""
        logger.info("="*80)
        logger.info(f"開始 {phase_config['name']}")
        logger.info("="*80)
        
        # 獲取待處理標籤
        tags = self.get_unclassified_tags(
            phase_config['min_count'],
            phase_config['max_count']
        )
        
        if not tags:
            logger.info(f"{phase_config['name']}: 沒有待處理標籤")
            return {
                'phase': phase_config['name'],
                'processed': 0,
                'success': 0,
                'failed': 0,
                'success_rate': 0.0,
                'avg_confidence': 0.0
            }
        
        # 初始化統計
        phase_start_time = time.time()
        processed = 0
        success = 0
        failed = 0
        low_confidence_count = 0
        confidences = []
        
        # 動態批次大小
        current_batch_size = phase_config['batch_size']
        
        # 分批處理
        for i in range(0, len(tags), current_batch_size):
            batch = tags[i:i + current_batch_size]
            batch_names = [tag['name'] for tag in batch]
            
            logger.info(f"\n處理批次 {i//current_batch_size + 1}: {len(batch)} 個標籤")
            
            # 使用分類器處理
            results = self.classifier.classify_batch(
                batch_names,
                max_retries=phase_config['retry_count']
            )
            
            # 更新數據庫
            batch_success = 0
            batch_confidences = []
            
            for result in results:
                processed += 1
                self.total_processed += 1
                
                # 檢查信心度閾值
                if result.success and result.confidence >= phase_config['confidence_threshold']:
                    # 標記低信心度標籤
                    needs_review = result.confidence < 0.70
                    if needs_review:
                        low_confidence_count += 1
                    
                    if self.update_tag_classification(result, phase_config['source_tag'], needs_review):
                        success += 1
                        batch_success += 1
                        self.total_success += 1
                        confidences.append(result.confidence)
                        batch_confidences.append(result.confidence)
                        
                        if needs_review:
                            logger.warning(f"標籤 {result.tag_name} 信心度較低: {result.confidence:.2f} [已標記需審查]")
                    else:
                        failed += 1
                else:
                    failed += 1
                    if result.success:
                        logger.warning(f"標籤 {result.tag_name} 信心度不足: {result.confidence:.2f}")
            
            # 批次統計
            logger.info(f"批次成功: {batch_success}/{len(batch)} ({batch_success/len(batch)*100:.1f}%)")
            if batch_confidences:
                logger.info(f"批次平均信心度: {sum(batch_confidences)/len(batch_confidences):.3f}")
            
            # 品質監控
            self.quality_monitor.record_batch(results, phase_config['name'])
            
            # 檢查點評估（每 300 個標籤）
            if processed % 300 == 0:
                checkpoint_result = self.checkpoint_evaluator.evaluate(
                    processed=processed,
                    success=success,
                    confidences=confidences,
                    phase_name=phase_config['name']
                )
                
                logger.info("\n" + "="*60)
                logger.info("檢查點評估")
                logger.info("="*60)
                logger.info(f"成功率: {checkpoint_result['success_rate']:.1%} - {checkpoint_result['success_rating']}")
                logger.info(f"平均信心度: {checkpoint_result['avg_confidence']:.3f} - {checkpoint_result['confidence_rating']}")
                logger.info(f"覆蓋率進度: {checkpoint_result['coverage_progress']}")
                logger.info(f"低信心度標籤: {low_confidence_count} ({low_confidence_count/processed*100:.1f}%)")
                logger.info("="*60 + "\n")
                
                # 根據評估結果調整批次大小
                if checkpoint_result['success_rating'] == '🛑 警告':
                    logger.warning("成功率過低，降低批次大小")
                    current_batch_size = max(6, current_batch_size - 2)
            
            # 每 500 個標籤提取規則
            if processed % 500 == 0:
                logger.info("提取規則模式...")
                try:
                    rules = self.rule_extractor.extract_all_rules()
                    total_rules = sum(len(r) for r in rules.values())
                    logger.info(f"提取到 {total_rules} 個規則模式")
                except Exception as e:
                    logger.error(f"規則提取失敗: {e}")
            
            # 延遲
            time.sleep(phase_config['delay'])
        
        # Phase 統計
        phase_duration = time.time() - phase_start_time
        success_rate = success / processed if processed > 0 else 0.0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        phase_stats = {
            'phase': phase_config['name'],
            'processed': processed,
            'success': success,
            'failed': failed,
            'low_confidence_count': low_confidence_count,
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'duration': phase_duration
        }
        
        self.phase_stats.append(phase_stats)
        
        logger.info("\n" + "="*80)
        logger.info(f"{phase_config['name']} 完成")
        logger.info("="*80)
        logger.info(f"處理: {processed} 個")
        logger.info(f"成功: {success} 個 ({success_rate*100:.1f}%)")
        logger.info(f"失敗: {failed} 個")
        logger.info(f"低信心度: {low_confidence_count} 個 ({low_confidence_count/processed*100:.1f}%)")
        logger.info(f"平均信心度: {avg_confidence:.3f}")
        logger.info(f"耗時: {phase_duration/60:.1f} 分鐘")
        logger.info("="*80 + "\n")
        
        return phase_stats
    
    def run(self, phase_range: Optional[List[int]] = None):
        """執行 Phase 2 的所有階段"""
        logger.info("\n" + "🚀"*40)
        logger.info("開始執行 Plan C Phase 2: 低頻標籤處理")
        logger.info("🚀"*40 + "\n")
        
        start_time = time.time()
        
        # 確定要執行的 phase
        phases_to_run = self.PHASES
        if phase_range:
            phases_to_run = [self.PHASES[i] for i in phase_range if i < len(self.PHASES)]
        
        # 執行各個 phase
        for phase_config in phases_to_run:
            self.process_phase(phase_config)
            
            # 生成進度報告
            self.progress_reporter.generate_phase2_report(
                self.phase_stats,
                self.total_processed,
                self.total_success
            )
            
            # 檢查是否達到目標
            overall_stats = self.progress_reporter.get_overall_stats()
            if overall_stats['coverage'] >= 96.0:
                logger.info("\n" + "🎉"*40)
                logger.info("已達成 96% 覆蓋率目標！")
                logger.info("🎉"*40 + "\n")
                break
        
        # 總結
        total_duration = time.time() - start_time
        overall_success_rate = self.total_success / self.total_processed if self.total_processed > 0 else 0.0
        
        # 獲取最終統計
        final_stats = self.progress_reporter.get_overall_stats()
        
        logger.info("\n" + "🎉"*40)
        logger.info("Phase 2 全部完成！")
        logger.info("🎉"*40)
        logger.info(f"\n總處理: {self.total_processed} 個標籤")
        logger.info(f"總成功: {self.total_success} 個")
        logger.info(f"總成功率: {overall_success_rate*100:.1f}%")
        logger.info(f"總耗時: {total_duration/3600:.2f} 小時")
        logger.info(f"\n最終覆蓋率: {final_stats['coverage']:.2f}%")
        logger.info(f"已分類標籤: {final_stats['classified_tags']:,}")
        logger.info(f"未分類標籤: {final_stats['unclassified_tags']:,}")
        logger.info("\n" + "="*80 + "\n")
        
        # 生成最終報告
        logger.info("生成最終報告...")
        self.quality_monitor.generate_quality_report()
        self.rule_extractor.generate_report()
        self.rule_extractor.generate_python_code()
        
        # 如果達到 96%，生成達成報告
        if final_stats['coverage'] >= 96.0:
            self.progress_reporter.generate_milestone_report(96)
        
        return {
            'total_processed': self.total_processed,
            'total_success': self.total_success,
            'success_rate': overall_success_rate,
            'duration': total_duration,
            'phases': self.phase_stats,
            'final_coverage': final_stats['coverage']
        }


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plan C Phase 2 執行器')
    parser.add_argument('--phases', type=int, nargs='+',
                      help='指定要執行的 phase (0-2)，例如: --phases 0 1')
    parser.add_argument('--dry-run', action='store_true',
                      help='測試運行，不實際更新數據庫')
    
    args = parser.parse_args()
    
    executor = Phase2Executor()
    
    try:
        result = executor.run(phase_range=args.phases)
        
        if result['final_coverage'] >= 96.0:
            logger.info("✅ Plan C 目標達成！覆蓋率 >= 96%")
        else:
            logger.info(f"⚠️ 目標未完全達成，當前覆蓋率: {result['final_coverage']:.2f}%")
        
        return 0
    except Exception as e:
        logger.error(f"❌ Phase 2 執行失敗: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())


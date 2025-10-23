#!/usr/bin/env python3
"""
Plan C Phase 1 執行腳本
處理中頻標籤 (10K-100K post_count)
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
from config import DB_PATH, OUTPUT_DIR

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'plan_c_phase1.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Phase1Executor:
    """Phase 1 執行器 - 處理中頻標籤"""
    
    # Phase 配置
    PHASES = [
        {
            'name': 'Phase 1-1: 50K-100K',
            'min_count': 50000,
            'max_count': 100000,
            'batch_size': 20,
            'confidence_threshold': 0.85,
            'source_tag': 'phase1_1_50k_100k_batch',
            'retry_count': 3,
            'delay': 1.5
        },
        {
            'name': 'Phase 1-2: 30K-50K',
            'min_count': 30000,
            'max_count': 50000,
            'batch_size': 20,
            'confidence_threshold': 0.80,
            'source_tag': 'phase1_2_30k_50k_batch',
            'retry_count': 3,
            'delay': 1.5
        },
        {
            'name': 'Phase 1-3: 20K-30K',
            'min_count': 20000,
            'max_count': 30000,
            'batch_size': 15,
            'confidence_threshold': 0.75,
            'source_tag': 'phase1_3_20k_30k_batch',
            'retry_count': 3,
            'delay': 1.5
        },
        {
            'name': 'Phase 1-4: 10K-20K',
            'min_count': 10000,
            'max_count': 20000,
            'batch_size': 15,
            'confidence_threshold': 0.70,
            'source_tag': 'phase1_4_10k_20k_batch',
            'retry_count': 2,
            'delay': 2.0
        }
    ]
    
    def __init__(self):
        """初始化執行器"""
        self.classifier = OptimizedLLMClassifier()
        self.checkpoint_evaluator = CheckpointEvaluator()
        self.batch_adjuster = BatchSizeAdjuster()
        self.quality_monitor = QualityMonitor()
        self.progress_reporter = ProgressReporter()
        
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
                                 source_tag: str) -> bool:
        """更新標籤分類"""
        if not result.success:
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                result.reasoning,
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
                    if self.update_tag_classification(result, phase_config['source_tag']):
                        success += 1
                        batch_success += 1
                        self.total_success += 1
                        confidences.append(result.confidence)
                        batch_confidences.append(result.confidence)
                    else:
                        failed += 1
                else:
                    failed += 1
                    logger.warning(f"標籤 {result.tag_name} 信心度不足: {result.confidence:.2f}")
            
            # 批次統計
            logger.info(f"批次成功: {batch_success}/{len(batch)} ({batch_success/len(batch)*100:.1f}%)")
            if batch_confidences:
                logger.info(f"批次平均信心度: {sum(batch_confidences)/len(batch_confidences):.3f}")
            
            # 品質監控
            self.quality_monitor.record_batch(results, phase_config['name'])
            
            # 檢查點評估（每 300 個標籤或每 20 批）
            if processed % 300 == 0 or (i // current_batch_size + 1) % 20 == 0:
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
                logger.info("="*60 + "\n")
                
                # 根據評估結果調整批次大小
                if checkpoint_result['success_rating'] == '🛑 警告':
                    logger.warning("成功率過低，降低批次大小")
                    current_batch_size = max(8, current_batch_size - 2)
                elif checkpoint_result['confidence_rating'] == '🛑 警告':
                    logger.warning("信心度過低，調整批次大小")
                    current_batch_size = max(8, current_batch_size - 2)
            
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
        logger.info(f"平均信心度: {avg_confidence:.3f}")
        logger.info(f"耗時: {phase_duration/60:.1f} 分鐘")
        logger.info("="*80 + "\n")
        
        return phase_stats
    
    def run(self, phase_range: Optional[List[int]] = None):
        """執行 Phase 1 的所有階段"""
        logger.info("\n" + "🚀"*40)
        logger.info("開始執行 Plan C Phase 1: 中頻標籤處理")
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
            self.progress_reporter.generate_phase1_report(
                self.phase_stats,
                self.total_processed,
                self.total_success
            )
        
        # 總結
        total_duration = time.time() - start_time
        overall_success_rate = self.total_success / self.total_processed if self.total_processed > 0 else 0.0
        
        logger.info("\n" + "🎉"*40)
        logger.info("Phase 1 全部完成！")
        logger.info("🎉"*40)
        logger.info(f"\n總處理: {self.total_processed} 個標籤")
        logger.info(f"總成功: {self.total_success} 個")
        logger.info(f"總成功率: {overall_success_rate*100:.1f}%")
        logger.info(f"總耗時: {total_duration/3600:.2f} 小時")
        logger.info("\n" + "="*80 + "\n")
        
        # 生成最終報告
        self.progress_reporter.generate_phase1_final_report(
            self.phase_stats,
            self.total_processed,
            self.total_success,
            total_duration
        )
        
        return {
            'total_processed': self.total_processed,
            'total_success': self.total_success,
            'success_rate': overall_success_rate,
            'duration': total_duration,
            'phases': self.phase_stats
        }


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plan C Phase 1 執行器')
    parser.add_argument('--phases', type=int, nargs='+',
                      help='指定要執行的 phase (0-3)，例如: --phases 0 1')
    parser.add_argument('--dry-run', action='store_true',
                      help='測試運行，不實際更新數據庫')
    
    args = parser.parse_args()
    
    executor = Phase1Executor()
    
    try:
        result = executor.run(phase_range=args.phases)
        logger.info("✅ Phase 1 執行成功")
        return 0
    except Exception as e:
        logger.error(f"❌ Phase 1 執行失敗: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())


#!/usr/bin/env python3
"""
快速健康檢查腳本
用於部署後的即時驗證
"""

import sqlite3
import time
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseHealthChecker:
    """資料庫健康檢查器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 嘗試多個可能的路徑
            possible_paths = [
                "output/tags.db",
                "/var/lib/prompt-scribe/tags.db",
                "./tags.db"
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    db_path = path
                    break
        
        if not db_path or not Path(db_path).exists():
            raise FileNotFoundError(f"找不到資料庫文件: {db_path}")
        
        self.db_path = db_path
    
    def check_connection(self):
        """檢查資料庫連接"""
        try:
            start_time = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 基本查詢測試
            cursor.execute("SELECT COUNT(*) FROM tags_final")
            total_tags = cursor.fetchone()[0]
            
            conn.close()
            response_time = time.time() - start_time
            
            logger.info(f"✓ 資料庫連接正常")
            logger.info(f"  - 總標籤數: {total_tags:,}")
            logger.info(f"  - 響應時間: {response_time:.3f}s")
            
            return True, response_time, total_tags
            
        except Exception as e:
            logger.error(f"✗ 資料庫連接失敗: {e}")
            return False, 0, 0
    
    def check_performance(self):
        """檢查查詢性能"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 性能測試查詢
            test_queries = [
                ("高頻標籤查詢", "SELECT * FROM tags_final WHERE post_count > 1000000 LIMIT 10"),
                ("分類統計查詢", "SELECT main_category, COUNT(*) FROM tags_final GROUP BY main_category"),
                ("信心度查詢", "SELECT AVG(classification_confidence) FROM tags_final WHERE classification_confidence IS NOT NULL"),
                ("複雜查詢", "SELECT name, main_category, sub_category, post_count FROM tags_final WHERE main_category = 'CHARACTER_RELATED' AND sub_category = 'HAIR' LIMIT 20")
            ]
            
            total_time = 0
            passed_tests = 0
            
            for test_name, query in test_queries:
                start_time = time.time()
                cursor.execute(query)
                results = cursor.fetchall()
                query_time = time.time() - start_time
                total_time += query_time
                
                if query_time < 0.1:  # 100ms 閾值
                    logger.info(f"✓ {test_name}: {query_time:.3f}s ({len(results)} 結果)")
                    passed_tests += 1
                else:
                    logger.warning(f"⚠ {test_name}: {query_time:.3f}s (較慢)")
            
            conn.close()
            
            avg_time = total_time / len(test_queries)
            performance_score = (passed_tests / len(test_queries)) * 100
            
            logger.info(f"性能測試完成: {passed_tests}/{len(test_queries)} 通過")
            logger.info(f"平均查詢時間: {avg_time:.3f}s")
            
            return performance_score >= 75, avg_time, passed_tests
            
        except Exception as e:
            logger.error(f"✗ 性能測試失敗: {e}")
            return False, 0, 0
    
    def check_data_integrity(self):
        """檢查數據完整性"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 完整性檢查
            checks = [
                ("NULL 字符串檢查", "SELECT COUNT(*) FROM tags_final WHERE sub_category = 'null'"),
                ("空值檢查", "SELECT COUNT(*) FROM tags_final WHERE main_category IS NULL"),
                ("信心度檢查", "SELECT COUNT(*) FROM tags_final WHERE classification_confidence IS NULL"),
                ("負信心度檢查", "SELECT COUNT(*) FROM tags_final WHERE classification_confidence < 0"),
                ("超信心度檢查", "SELECT COUNT(*) FROM tags_final WHERE classification_confidence > 1.0")
            ]
            
            issues_found = 0
            
            for check_name, query in checks:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.warning(f"⚠ {check_name}: 發現 {count} 個問題")
                    issues_found += count
                else:
                    logger.info(f"✓ {check_name}: 正常")
            
            conn.close()
            
            integrity_score = 100 - (issues_found / 1000 * 100)  # 簡單評分
            integrity_score = max(0, integrity_score)
            
            logger.info(f"數據完整性: {integrity_score:.1f}%")
            
            return integrity_score >= 90, issues_found
            
        except Exception as e:
            logger.error(f"✗ 完整性檢查失敗: {e}")
            return False, 0
    
    def run_full_check(self):
        """執行完整健康檢查"""
        logger.info("="*60)
        logger.info("開始資料庫健康檢查")
        logger.info("="*60)
        
        # 連接檢查
        conn_ok, response_time, total_tags = self.check_connection()
        if not conn_ok:
            return False, "資料庫連接失敗"
        
        # 性能檢查
        perf_ok, avg_time, passed_tests = self.check_performance()
        if not perf_ok:
            logger.warning("性能測試未完全通過，但可繼續")
        
        # 完整性檢查
        integrity_ok, issues = self.check_data_integrity()
        if not integrity_ok:
            logger.warning("數據完整性問題，需要檢查")
        
        # 總體評估
        logger.info("\n" + "="*60)
        logger.info("健康檢查總結")
        logger.info("="*60)
        
        overall_status = "健康" if conn_ok and integrity_ok else "需要關注"
        logger.info(f"總體狀態: {overall_status}")
        logger.info(f"資料庫路徑: {self.db_path}")
        logger.info(f"總標籤數: {total_tags:,}")
        logger.info(f"平均響應時間: {avg_time:.3f}s")
        logger.info(f"性能測試通過率: {passed_tests}/4")
        logger.info(f"數據問題數量: {issues}")
        
        # 返回狀態
        if conn_ok and integrity_ok and avg_time < 0.1:
            return True, "資料庫健康，可以部署"
        elif conn_ok and integrity_ok:
            return True, "資料庫基本健康，性能可接受"
        else:
            return False, "資料庫存在問題，需要修復"

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='資料庫健康檢查工具')
    parser.add_argument('--db-path', help='資料庫文件路徑')
    parser.add_argument('--exit-code', action='store_true', help='根據檢查結果設置退出碼')
    args = parser.parse_args()
    
    try:
        checker = DatabaseHealthChecker(args.db_path)
        is_healthy, message = checker.run_full_check()
        
        if args.exit_code:
            sys.exit(0 if is_healthy else 1)
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        if args.exit_code:
            sys.exit(1)

if __name__ == "__main__":
    main()

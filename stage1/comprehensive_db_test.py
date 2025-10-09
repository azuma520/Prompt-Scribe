"""
全面資料庫分析與測試腳本
使用 SQL 語法深度分析 tags.db
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

class DatabaseAnalyzer:
    """資料庫分析器"""
    
    def __init__(self, db_path: str = 'output/tags.db'):
        self.db_path = db_path
        self.conn = None
        self.results = {}
        
    def connect(self):
        """連接資料庫"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print(f"[OK] 成功連接資料庫: {self.db_path}")
            return True
        except Exception as e:
            print(f"[ERROR] 資料庫連接失敗: {e}")
            return False
    
    def close(self):
        """關閉連接"""
        if self.conn:
            self.conn.close()
            print("\n[OK] 資料庫連接已關閉")
    
    def execute_query(self, name: str, query: str, description: str = ""):
        """執行 SQL 查詢並儲存結果"""
        print(f"\n{'='*80}")
        print(f"測試：{name}")
        if description:
            print(f"說明：{description}")
        print(f"{'='*80}")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            self.results[name] = {
                'query': query,
                'results': results,
                'count': len(results),
                'success': True
            }
            
            # 顯示結果
            if results:
                # 顯示欄位名稱
                if hasattr(results[0], 'keys'):
                    columns = results[0].keys()
                    print(f"\n欄位: {', '.join(columns)}")
                
                # 顯示數據
                print(f"\n結果 ({len(results)} 筆):")
                print("-" * 80)
                for row in results:
                    if isinstance(row, sqlite3.Row):
                        print(" | ".join(str(row[col]) for col in row.keys()))
                    else:
                        print(row)
                print("-" * 80)
            else:
                print("\n[WARNING] 查詢結果為空")
            
            return results
            
        except Exception as e:
            print(f"\n[ERROR] 查詢失敗: {e}")
            self.results[name] = {
                'query': query,
                'error': str(e),
                'success': False
            }
            return None
    
    def run_all_tests(self):
        """執行所有測試"""
        print("\n" + "="*80)
        print("開始全面資料庫分析與測試")
        print(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. 基本資料庫資訊
        self.test_database_info()
        
        # 2. 資料表結構
        self.test_table_schema()
        
        # 3. 基本統計
        self.test_basic_statistics()
        
        # 4. 資料完整性
        self.test_data_integrity()
        
        # 5. 分類分析
        self.test_classification_analysis()
        
        # 6. 頻率層級分析
        self.test_frequency_tiers()
        
        # 7. Danbooru 分類分析
        self.test_danbooru_categories()
        
        # 8. 副分類分析
        self.test_sub_categories()
        
        # 9. 未分類標籤分析
        self.test_unclassified_tags()
        
        # 10. 高頻標籤分析
        self.test_high_frequency_tags()
        
        # 11. 資料品質驗證
        self.test_data_quality()
        
        # 12. 分類來源分析
        self.test_classification_sources()
        
        # 13. 索引效能測試
        self.test_index_performance()
        
        # 14. 邊界值測試
        self.test_edge_cases()
        
        # 生成摘要報告
        self.generate_summary()
    
    def test_database_info(self):
        """測試 1：基本資料庫資訊"""
        # 檢查資料表列表
        self.execute_query(
            "1.1 資料表列表",
            """
            SELECT name, type 
            FROM sqlite_master 
            WHERE type IN ('table', 'index')
            ORDER BY type, name;
            """,
            "列出所有資料表和索引"
        )
        
        # 資料庫大小
        query = f"SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();"
        result = self.execute_query(
            "1.2 資料庫大小",
            query,
            "計算資料庫檔案大小"
        )
    
    def test_table_schema(self):
        """測試 2：資料表結構"""
        # tags_raw 結構
        self.execute_query(
            "2.1 tags_raw 表結構",
            "PRAGMA table_info(tags_raw);",
            "檢查 tags_raw 表的欄位定義"
        )
        
        # tags_final 結構
        self.execute_query(
            "2.2 tags_final 表結構",
            "PRAGMA table_info(tags_final);",
            "檢查 tags_final 表的欄位定義"
        )
        
        # 索引資訊
        self.execute_query(
            "2.3 tags_final 索引",
            "PRAGMA index_list(tags_final);",
            "檢查 tags_final 表的索引"
        )
    
    def test_basic_statistics(self):
        """測試 3：基本統計"""
        # 總記錄數
        self.execute_query(
            "3.1 總標籤數",
            """
            SELECT 
                COUNT(*) as total_tags,
                COUNT(DISTINCT name) as unique_tags
            FROM tags_final;
            """,
            "計算總標籤數和唯一標籤數"
        )
        
        # post_count 統計
        self.execute_query(
            "3.2 使用次數統計",
            """
            SELECT 
                MIN(post_count) as min_usage,
                MAX(post_count) as max_usage,
                AVG(post_count) as avg_usage,
                SUM(post_count) as total_usage
            FROM tags_final;
            """,
            "分析標籤使用次數的統計特徵"
        )
        
        # danbooru_cat 分布
        self.execute_query(
            "3.3 Danbooru 分類分布",
            """
            SELECT 
                danbooru_cat,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final), 2) as percentage
            FROM tags_final
            GROUP BY danbooru_cat
            ORDER BY danbooru_cat;
            """,
            "統計各 Danbooru 分類的標籤數量"
        )
    
    def test_data_integrity(self):
        """測試 4：資料完整性"""
        # 檢查 NULL 值
        self.execute_query(
            "4.1 NULL 值檢查",
            """
            SELECT 
                'name' as field,
                COUNT(*) as null_count
            FROM tags_final
            WHERE name IS NULL
            UNION ALL
            SELECT 
                'danbooru_cat',
                COUNT(*)
            FROM tags_final
            WHERE danbooru_cat IS NULL
            UNION ALL
            SELECT 
                'post_count',
                COUNT(*)
            FROM tags_final
            WHERE post_count IS NULL;
            """,
            "檢查必要欄位是否有 NULL 值"
        )
        
        # 檢查重複標籤
        self.execute_query(
            "4.2 重複標籤檢查",
            """
            SELECT 
                name,
                COUNT(*) as duplicate_count
            FROM tags_final
            GROUP BY name
            HAVING COUNT(*) > 1;
            """,
            "檢查是否有重複的標籤名稱"
        )
        
        # 檢查異常值
        self.execute_query(
            "4.3 異常值檢查",
            """
            SELECT 
                'negative_post_count' as issue,
                COUNT(*) as count
            FROM tags_final
            WHERE post_count < 0
            UNION ALL
            SELECT 
                'invalid_danbooru_cat',
                COUNT(*)
            FROM tags_final
            WHERE danbooru_cat NOT IN (0, 1, 3, 4, 5)
            UNION ALL
            SELECT 
                'empty_name',
                COUNT(*)
            FROM tags_final
            WHERE name = '' OR LENGTH(TRIM(name)) = 0;
            """,
            "檢查資料異常值"
        )
    
    def test_classification_analysis(self):
        """測試 5：分類分析"""
        # 主分類分布
        self.execute_query(
            "5.1 主分類分布",
            """
            SELECT 
                main_category,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final), 2) as percentage,
                SUM(post_count) as total_usage
            FROM tags_final
            GROUP BY main_category
            ORDER BY count DESC;
            """,
            "統計各主分類的標籤數量和使用次數"
        )
        
        # 分類覆蓋率
        self.execute_query(
            "5.2 分類覆蓋率",
            """
            SELECT 
                '已分類' as status,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final), 2) as percentage
            FROM tags_final
            WHERE main_category IS NOT NULL
            UNION ALL
            SELECT 
                '未分類',
                COUNT(*),
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final), 2)
            FROM tags_final
            WHERE main_category IS NULL;
            """,
            "計算整體分類覆蓋率"
        )
        
        # 各 Danbooru 分類的覆蓋率
        self.execute_query(
            "5.3 各類別覆蓋率",
            """
            SELECT 
                danbooru_cat,
                COUNT(*) as total,
                SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified,
                ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage_rate
            FROM tags_final
            GROUP BY danbooru_cat
            ORDER BY danbooru_cat;
            """,
            "分析各 Danbooru 分類的覆蓋情況"
        )
    
    def test_frequency_tiers(self):
        """測試 6：頻率層級分析"""
        self.execute_query(
            "6.1 頻率層級分布",
            """
            SELECT 
                CASE 
                    WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
                    WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
                    WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
                    WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
                    WHEN post_count >= 100 THEN '低頻 (100-1k)'
                    ELSE '極低頻 (<100)'
                END as frequency_tier,
                COUNT(*) as tag_count,
                SUM(post_count) as total_usage,
                ROUND(AVG(post_count), 0) as avg_usage,
                SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified_count,
                ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage_rate
            FROM tags_final
            GROUP BY 
                CASE 
                    WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
                    WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
                    WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
                    WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
                    WHEN post_count >= 100 THEN '低頻 (100-1k)'
                    ELSE '極低頻 (<100)'
                END
            ORDER BY MIN(post_count) DESC;
            """,
            "按使用頻率層級統計標籤分布和覆蓋率"
        )
    
    def test_danbooru_categories(self):
        """測試 7：Danbooru 分類詳細分析"""
        # Danbooru 分類對應的主分類
        self.execute_query(
            "7.1 Danbooru 分類映射",
            """
            SELECT 
                danbooru_cat,
                main_category,
                COUNT(*) as count
            FROM tags_final
            WHERE main_category IS NOT NULL
            GROUP BY danbooru_cat, main_category
            ORDER BY danbooru_cat, count DESC;
            """,
            "查看 Danbooru 分類對應到哪些主分類"
        )
        
        # 各 Danbooru 分類的 TOP 10
        for cat in [0, 1, 3, 4, 5]:
            cat_name = {
                0: '一般標籤',
                1: '藝術家',
                3: '版權作品',
                4: '角色',
                5: '元數據'
            }.get(cat, f'分類{cat}')
            
            self.execute_query(
                f"7.{cat+2} Danbooru Cat={cat} ({cat_name}) TOP 10",
                f"""
                SELECT 
                    name,
                    main_category,
                    sub_category,
                    post_count
                FROM tags_final
                WHERE danbooru_cat = {cat}
                ORDER BY post_count DESC
                LIMIT 10;
                """,
                f"查看 {cat_name} 類別的最常用標籤"
            )
    
    def test_sub_categories(self):
        """測試 8：副分類分析"""
        # 副分類分布
        self.execute_query(
            "8.1 副分類整體分布",
            """
            SELECT 
                main_category,
                sub_category,
                COUNT(*) as count,
                SUM(post_count) as total_usage
            FROM tags_final
            WHERE sub_category IS NOT NULL
            GROUP BY main_category, sub_category
            ORDER BY main_category, count DESC;
            """,
            "統計各副分類的標籤數量"
        )
        
        # CHARACTER_RELATED 副分類詳細
        self.execute_query(
            "8.2 CHARACTER_RELATED 副分類",
            """
            SELECT 
                sub_category,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (
                    SELECT COUNT(*) 
                    FROM tags_final 
                    WHERE main_category = 'CHARACTER_RELATED'
                ), 2) as percentage_in_category,
                MIN(post_count) as min_usage,
                MAX(post_count) as max_usage,
                ROUND(AVG(post_count), 0) as avg_usage
            FROM tags_final
            WHERE main_category = 'CHARACTER_RELATED'
            GROUP BY sub_category
            ORDER BY count DESC;
            """,
            "分析 CHARACTER_RELATED 的副分類分布"
        )
    
    def test_unclassified_tags(self):
        """測試 9：未分類標籤分析"""
        # 未分類標籤總體統計
        self.execute_query(
            "9.1 未分類標籤統計",
            """
            SELECT 
                danbooru_cat,
                COUNT(*) as count,
                SUM(post_count) as total_usage,
                ROUND(AVG(post_count), 0) as avg_usage
            FROM tags_final
            WHERE main_category IS NULL
            GROUP BY danbooru_cat
            ORDER BY count DESC;
            """,
            "按 Danbooru 分類統計未分類標籤"
        )
        
        # 未分類高頻標籤
        self.execute_query(
            "9.2 未分類高頻標籤 TOP 30",
            """
            SELECT 
                name,
                danbooru_cat,
                post_count
            FROM tags_final
            WHERE main_category IS NULL
            ORDER BY post_count DESC
            LIMIT 30;
            """,
            "列出最需要處理的未分類高頻標籤"
        )
        
        # 未分類標籤頻率分布
        self.execute_query(
            "9.3 未分類標籤頻率層級",
            """
            SELECT 
                CASE 
                    WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
                    WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
                    WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
                    WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
                    ELSE '低頻 (<1k)'
                END as frequency_tier,
                COUNT(*) as count,
                SUM(post_count) as total_usage
            FROM tags_final
            WHERE main_category IS NULL
            GROUP BY 
                CASE 
                    WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
                    WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
                    WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
                    WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
                    ELSE '低頻 (<1k)'
                END
            ORDER BY MIN(post_count) DESC;
            """,
            "分析未分類標籤的頻率分布"
        )
    
    def test_high_frequency_tags(self):
        """測試 10：高頻標籤分析"""
        # TOP 50 高頻標籤
        self.execute_query(
            "10.1 TOP 50 高頻標籤",
            """
            SELECT 
                name,
                main_category,
                sub_category,
                danbooru_cat,
                post_count
            FROM tags_final
            ORDER BY post_count DESC
            LIMIT 50;
            """,
            "列出使用次數最多的 50 個標籤"
        )
        
        # 高頻標籤覆蓋率
        self.execute_query(
            "10.2 TOP 100 標籤覆蓋率",
            """
            SELECT 
                SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified,
                COUNT(*) as total,
                ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage_rate
            FROM (
                SELECT main_category
                FROM tags_final
                ORDER BY post_count DESC
                LIMIT 100
            );
            """,
            "計算 TOP 100 高頻標籤的覆蓋率"
        )
    
    def test_data_quality(self):
        """測試 11：資料品質驗證"""
        # 檢查標籤名稱長度
        self.execute_query(
            "11.1 標籤名稱長度分析",
            """
            SELECT 
                MIN(LENGTH(name)) as min_length,
                MAX(LENGTH(name)) as max_length,
                ROUND(AVG(LENGTH(name)), 2) as avg_length,
                COUNT(CASE WHEN LENGTH(name) > 50 THEN 1 END) as long_names,
                COUNT(CASE WHEN LENGTH(name) < 3 THEN 1 END) as short_names
            FROM tags_final;
            """,
            "分析標籤名稱長度特徵"
        )
        
        # 檢查特殊字元
        self.execute_query(
            "11.2 特殊字元標籤",
            """
            SELECT 
                name,
                LENGTH(name) as length,
                post_count
            FROM tags_final
            WHERE name LIKE '%:%' 
               OR name LIKE '%(%' 
               OR name LIKE '%)%'
               OR name LIKE '%+%'
            ORDER BY post_count DESC
            LIMIT 20;
            """,
            "列出包含特殊字元的標籤"
        )
        
        # source_count 統計
        self.execute_query(
            "11.3 資料來源統計",
            """
            SELECT 
                source_count,
                COUNT(*) as tag_count
            FROM tags_final
            GROUP BY source_count
            ORDER BY source_count;
            """,
            "統計標籤來自多少個資料源"
        )
    
    def test_classification_sources(self):
        """測試 12：分類來源分析"""
        # 規則分類 vs Danbooru 分類
        self.execute_query(
            "12.1 分類來源統計",
            """
            SELECT 
                CASE 
                    WHEN danbooru_cat IN (1, 3, 4, 5) AND main_category IS NOT NULL THEN 'Danbooru 直接分類'
                    WHEN danbooru_cat = 0 AND main_category IS NOT NULL THEN '規則分類器'
                    ELSE '未分類'
                END as classification_source,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tags_final), 2) as percentage
            FROM tags_final
            GROUP BY 
                CASE 
                    WHEN danbooru_cat IN (1, 3, 4, 5) AND main_category IS NOT NULL THEN 'Danbooru 直接分類'
                    WHEN danbooru_cat = 0 AND main_category IS NOT NULL THEN '規則分類器'
                    ELSE '未分類'
                END;
            """,
            "統計標籤的分類來源"
        )
        
        # 各主分類的來源
        self.execute_query(
            "12.2 各主分類的資料來源",
            """
            SELECT 
                main_category,
                SUM(CASE WHEN danbooru_cat IN (1, 3, 4, 5) THEN 1 ELSE 0 END) as from_danbooru,
                SUM(CASE WHEN danbooru_cat = 0 THEN 1 ELSE 0 END) as from_rules
            FROM tags_final
            WHERE main_category IS NOT NULL
            GROUP BY main_category
            ORDER BY (from_danbooru + from_rules) DESC;
            """,
            "分析各主分類來自 Danbooru 或規則"
        )
    
    def test_index_performance(self):
        """測試 13：索引效能測試"""
        # 使用索引的查詢
        self.execute_query(
            "13.1 按名稱查詢 (使用索引)",
            """
            EXPLAIN QUERY PLAN
            SELECT * FROM tags_final WHERE name = '1girl';
            """,
            "測試名稱索引的使用情況"
        )
        
        self.execute_query(
            "13.2 按主分類查詢 (使用索引)",
            """
            EXPLAIN QUERY PLAN
            SELECT * FROM tags_final WHERE main_category = 'CHARACTER_RELATED';
            """,
            "測試主分類索引的使用情況"
        )
        
        self.execute_query(
            "13.3 按使用次數排序 (使用索引)",
            """
            EXPLAIN QUERY PLAN
            SELECT * FROM tags_final ORDER BY post_count DESC LIMIT 100;
            """,
            "測試 post_count 索引的使用情況"
        )
    
    def test_edge_cases(self):
        """測試 14：邊界值測試"""
        # 極端值
        self.execute_query(
            "14.1 極端使用次數",
            """
            SELECT 
                type,
                name,
                post_count
            FROM (
                SELECT 
                    '最少使用' as type,
                    name,
                    post_count
                FROM tags_final
                WHERE post_count > 0
                ORDER BY post_count ASC
                LIMIT 5
            )
            UNION ALL
            SELECT 
                type,
                name,
                post_count
            FROM (
                SELECT 
                    '最多使用' as type,
                    name,
                    post_count
                FROM tags_final
                ORDER BY post_count DESC
                LIMIT 5
            )
            ORDER BY post_count ASC;
            """,
            "查看使用次數的極端值"
        )
        
        # 最長和最短的標籤名稱
        self.execute_query(
            "14.2 極端標籤長度",
            """
            SELECT 
                type,
                name,
                length
            FROM (
                SELECT 
                    '最長標籤' as type,
                    name,
                    LENGTH(name) as length
                FROM tags_final
                ORDER BY LENGTH(name) DESC
                LIMIT 5
            )
            UNION ALL
            SELECT 
                type,
                name,
                length
            FROM (
                SELECT 
                    '最短標籤' as type,
                    name,
                    LENGTH(name) as length
                FROM tags_final
                WHERE LENGTH(name) > 0
                ORDER BY LENGTH(name) ASC
                LIMIT 5
            )
            ORDER BY length DESC;
            """,
            "查看標籤名稱長度的極端值"
        )
    
    def generate_summary(self):
        """生成測試摘要"""
        print("\n" + "="*80)
        print("測試摘要報告")
        print("="*80)
        
        # 統計成功/失敗的測試
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        print(f"\n總測試數：{total_tests}")
        print(f"[OK] 成功：{successful_tests}")
        print(f"[ERROR] 失敗：{failed_tests}")
        
        if failed_tests > 0:
            print("\n失敗的測試：")
            for name, result in self.results.items():
                if not result.get('success', False):
                    print(f"  - {name}: {result.get('error', '未知錯誤')}")
        
        # 關鍵指標摘要
        print("\n" + "-"*80)
        print("關鍵指標摘要")
        print("-"*80)
        
        # 從測試結果中提取關鍵指標
        try:
            # 總標籤數
            if "3.1 總標籤數" in self.results and self.results["3.1 總標籤數"]['success']:
                result = self.results["3.1 總標籤數"]['results'][0]
                print(f"總標籤數：{result[0]:,}")
            
            # 覆蓋率
            if "5.2 分類覆蓋率" in self.results and self.results["5.2 分類覆蓋率"]['success']:
                results = self.results["5.2 分類覆蓋率"]['results']
                for row in results:
                    print(f"{row[0]}：{row[1]:,} ({row[2]}%)")
            
            # 分類來源
            if "12.1 分類來源統計" in self.results and self.results["12.1 分類來源統計"]['success']:
                results = self.results["12.1 分類來源統計"]['results']
                print("\n分類來源：")
                for row in results:
                    print(f"  {row[0]}：{row[1]:,} ({row[2]}%)")
        
        except Exception as e:
            print(f"[WARNING] 無法生成摘要：{e}")
        
        print("\n" + "="*80)
        print(f"[OK] 測試完成！時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)


def main():
    """主程式"""
    # 檢查資料庫檔案
    db_path = Path('output/tags.db')
    if not db_path.exists():
        print(f"[ERROR] 找不到資料庫檔案: {db_path}")
        print("請先執行 run_pipeline.py 生成資料庫")
        sys.exit(1)
    
    # 創建分析器並執行測試
    analyzer = DatabaseAnalyzer(str(db_path))
    
    if analyzer.connect():
        try:
            analyzer.run_all_tests()
        except KeyboardInterrupt:
            print("\n\n[WARNING] 測試被用戶中斷")
        except Exception as e:
            print(f"\n\n[ERROR] 測試過程發生錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            analyzer.close()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()


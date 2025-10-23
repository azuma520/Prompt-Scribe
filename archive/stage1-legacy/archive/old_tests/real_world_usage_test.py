"""
實際使用場景 SQL 測試腳本

目的：
1. 模擬真實使用場景
2. 測試分類可用性和錯誤率
3. 識別需要 LLM 處理的高價值標籤
4. 生成精進方案
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict
from collections import defaultdict


class RealWorldUsageTest:
    """實際使用場景測試器"""
    
    def __init__(self, db_path: str = 'output/tags.db'):
        self.db_path = db_path
        self.conn = None
        self.test_results = {}
        self.issues_found = []
        self.llm_candidates = []
        
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
    
    def execute_test(self, name: str, query: str, description: str = "") -> List:
        """執行測試查詢"""
        print(f"\n{'='*80}")
        print(f"場景測試：{name}")
        if description:
            print(f"說明：{description}")
        print(f"{'='*80}")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            self.test_results[name] = {
                'query': query,
                'results': results,
                'count': len(results),
                'success': True
            }
            
            print(f"\n結果數量: {len(results)}")
            return results
            
        except Exception as e:
            print(f"\n[ERROR] 查詢失敗: {e}")
            self.test_results[name] = {
                'query': query,
                'error': str(e),
                'success': False
            }
            return []
    
    def run_all_tests(self):
        """執行所有實際使用場景測試"""
        print("\n" + "="*80)
        print("實際使用場景測試開始")
        print(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 場景 1: 內容創作者搜索標籤
        self.test_content_creator_scenarios()
        
        # 場景 2: 內容過濾和分類
        self.test_content_filtering_scenarios()
        
        # 場景 3: 標籤推薦系統
        self.test_tag_recommendation_scenarios()
        
        # 場景 4: 數據質量檢查
        self.test_data_quality_scenarios()
        
        # 場景 5: 分類錯誤檢測
        self.test_classification_errors()
        
        # 場景 6: 未分類高價值標籤識別
        self.identify_llm_candidates()
        
        # 生成總結報告
        self.generate_summary_report()
    
    def test_content_creator_scenarios(self):
        """場景 1: 內容創作者使用場景"""
        print("\n" + "#"*80)
        print("# 場景 1: 內容創作者使用場景")
        print("#"*80)
        
        # 1.1 搜索「女性角色穿著校服」相關標籤
        results = self.execute_test(
            "1.1 搜索特定主題標籤",
            """
            SELECT name, main_category, sub_category, post_count
            FROM tags_final
            WHERE (main_category = 'CHARACTER_RELATED' AND sub_category = 'CLOTHING')
               OR (main_category = 'CHARACTER_RELATED' AND sub_category = 'CHARACTER_COUNT')
            ORDER BY post_count DESC
            LIMIT 20;
            """,
            "創作者想找「女性角色 + 服裝」相關的常用標籤"
        )
        self._display_results(results, ['name', 'main_category', 'sub_category', 'post_count'])
        
        # 1.2 找出所有表情相關標籤
        results = self.execute_test(
            "1.2 搜索表情標籤",
            """
            SELECT name, sub_category, post_count
            FROM tags_final
            WHERE main_category = 'ACTION_POSE' AND sub_category = 'EXPRESSION'
            ORDER BY post_count DESC
            LIMIT 30;
            """,
            "創作者想找常用的表情標籤"
        )
        self._display_results(results, ['name', 'sub_category', 'post_count'])
        
        # 1.3 檢查「微笑的女孩」組合標籤覆蓋率
        results = self.execute_test(
            "1.3 組合標籤覆蓋率測試",
            """
            SELECT 
                '1girl' as tag_type,
                COUNT(*) FILTER (WHERE name = '1girl' AND main_category IS NOT NULL) as classified,
                COUNT(*) FILTER (WHERE name = '1girl') as total
            FROM tags_final
            UNION ALL
            SELECT 
                'smile',
                COUNT(*) FILTER (WHERE name = 'smile' AND main_category IS NOT NULL),
                COUNT(*) FILTER (WHERE name = 'smile')
            FROM tags_final
            UNION ALL
            SELECT 
                'school_uniform',
                COUNT(*) FILTER (WHERE name = 'school_uniform' AND main_category IS NOT NULL),
                COUNT(*) FILTER (WHERE name = 'school_uniform')
            FROM tags_final;
            """,
            "檢查常用組合標籤是否都已分類"
        )
        self._display_results(results, ['tag_type', 'classified', 'total'])
    
    def test_content_filtering_scenarios(self):
        """場景 2: 內容過濾場景"""
        print("\n" + "#"*80)
        print("# 場景 2: 內容過濾和分類場景")
        print("#"*80)
        
        # 2.1 過濾成人內容
        results = self.execute_test(
            "2.1 成人內容識別能力",
            """
            SELECT 
                main_category,
                sub_category,
                COUNT(*) as tag_count,
                SUM(post_count) as total_usage
            FROM tags_final
            WHERE main_category = 'ADULT_CONTENT'
            GROUP BY main_category, sub_category
            ORDER BY tag_count DESC;
            """,
            "測試成人內容過濾的覆蓋情況"
        )
        self._display_results(results, ['main_category', 'sub_category', 'tag_count', 'total_usage'])
        
        # 2.2 安全級別標籤覆蓋
        results = self.execute_test(
            "2.2 未分類的潛在成人標籤",
            """
            SELECT name, post_count
            FROM tags_final
            WHERE danbooru_cat = 0 
              AND main_category IS NULL
              AND (
                  name LIKE '%nude%' OR 
                  name LIKE '%naked%' OR
                  name LIKE '%sex%' OR
                  name LIKE '%nsfw%' OR
                  name LIKE '%explicit%'
              )
            ORDER BY post_count DESC
            LIMIT 30;
            """,
            "找出可能被遺漏的成人內容標籤"
        )
        if results:
            self._display_results(results, ['name', 'post_count'])
            for row in results:
                self.issues_found.append({
                    'type': 'missing_adult_content',
                    'tag': row['name'],
                    'usage': row['post_count']
                })
        else:
            print("[OK] 未發現遺漏的成人內容標籤")
        
        # 2.3 按主分類統計使用量
        results = self.execute_test(
            "2.3 各分類的實際使用量分布",
            """
            SELECT 
                COALESCE(main_category, 'UNCLASSIFIED') as category,
                COUNT(*) as tag_count,
                SUM(post_count) as total_usage,
                ROUND(SUM(post_count) * 100.0 / (SELECT SUM(post_count) FROM tags_final), 2) as usage_percentage
            FROM tags_final
            GROUP BY main_category
            ORDER BY total_usage DESC;
            """,
            "了解各分類在實際應用中的使用比例"
        )
        self._display_results(results, ['category', 'tag_count', 'total_usage', 'usage_percentage'])
    
    def test_tag_recommendation_scenarios(self):
        """場景 3: 標籤推薦系統場景"""
        print("\n" + "#"*80)
        print("# 場景 3: 標籤推薦系統場景")
        print("#"*80)
        
        # 3.1 根據主分類推薦相關標籤
        results = self.execute_test(
            "3.1 CHARACTER_RELATED 推薦標籤池",
            """
            SELECT 
                sub_category,
                COUNT(*) as available_tags,
                SUM(post_count) as total_usage,
                GROUP_CONCAT(name, ', ') as sample_tags
            FROM (
                SELECT sub_category, name, post_count
                FROM tags_final
                WHERE main_category = 'CHARACTER_RELATED' 
                  AND sub_category IS NOT NULL
                GROUP BY sub_category, name
                ORDER BY post_count DESC
            )
            GROUP BY sub_category
            ORDER BY total_usage DESC;
            """,
            "推薦系統可用的 CHARACTER_RELATED 標籤"
        )
        # 結果太長，只顯示統計
        if results:
            print(f"\n可用副分類: {len(results)} 個")
            for row in results:
                print(f"  {row['sub_category']}: {row['available_tags']} 個標籤")
        
        # 3.2 高頻但未分類的「孤兒」標籤
        results = self.execute_test(
            "3.2 高頻未分類標籤（推薦系統盲區）",
            """
            SELECT 
                name, 
                post_count,
                CASE 
                    WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
                    WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
                    WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
                    ELSE '中頻 (1k-10k)'
                END as frequency_tier
            FROM tags_final
            WHERE danbooru_cat = 0 
              AND main_category IS NULL
              AND post_count >= 1000
            ORDER BY post_count DESC
            LIMIT 50;
            """,
            "這些高頻標籤無法被推薦系統使用，影響用戶體驗"
        )
        self._display_results(results, ['name', 'post_count', 'frequency_tier'])
        
        # 統計影響
        if results:
            total_missing_usage = sum(row['post_count'] for row in results)
            print(f"\n[WARN] 推薦系統盲區影響: {total_missing_usage:,} 次使用")
            print(f"[WARN] 這佔總使用量的 {total_missing_usage / 1188647968 * 100:.2f}%")
    
    def test_data_quality_scenarios(self):
        """場景 4: 數據質量檢查"""
        print("\n" + "#"*80)
        print("# 場景 4: 數據質量檢查")
        print("#"*80)
        
        # 4.1 副分類完整性檢查
        results = self.execute_test(
            "4.1 副分類覆蓋率",
            """
            SELECT 
                main_category,
                COUNT(*) as total_tags,
                SUM(CASE WHEN sub_category IS NOT NULL THEN 1 ELSE 0 END) as with_subcat,
                ROUND(SUM(CASE WHEN sub_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as subcat_coverage
            FROM tags_final
            WHERE main_category IS NOT NULL 
              AND main_category NOT IN ('ARTIST', 'CHARACTER', 'COPYRIGHT', 'TECHNICAL', 'QUALITY')
            GROUP BY main_category
            ORDER BY subcat_coverage ASC;
            """,
            "檢查哪些主分類的副分類覆蓋不足"
        )
        self._display_results(results, ['main_category', 'total_tags', 'with_subcat', 'subcat_coverage'])
        
        # 記錄問題
        if results:
            for row in results:
                if row['subcat_coverage'] < 50:
                    self.issues_found.append({
                        'type': 'low_subcategory_coverage',
                        'category': row['main_category'],
                        'coverage': row['subcat_coverage']
                    })
        
        # 4.2 可能的分類衝突
        results = self.execute_test(
            "4.2 可疑的分類組合",
            """
            SELECT name, main_category, sub_category, post_count
            FROM tags_final
            WHERE 
                -- BODY_PARTS 標籤被分到 CLOTHING
                (main_category = 'CHARACTER_RELATED' AND sub_category = 'CLOTHING' 
                 AND (name LIKE '%navel%' OR name LIKE '%collarbone%'))
                OR
                -- 表情標籤被分到 POSE
                (main_category = 'ACTION_POSE' AND sub_category = 'POSE'
                 AND (name LIKE '%smile%' OR name LIKE '%blush%' OR name LIKE '%:%'))
                OR
                -- BACKGROUND 標籤可能被誤分為 BODY_PARTS
                (main_category = 'CHARACTER_RELATED' AND sub_category = 'BODY_PARTS'
                 AND name LIKE '%background%')
            ORDER BY post_count DESC
            LIMIT 20;
            """,
            "檢測可能的分類錯誤"
        )
        if results:
            self._display_results(results, ['name', 'main_category', 'sub_category', 'post_count'])
            for row in results:
                self.issues_found.append({
                    'type': 'possible_misclassification',
                    'tag': row['name'],
                    'current_category': f"{row['main_category']}/{row['sub_category']}",
                    'usage': row['post_count']
                })
        else:
            print("[OK] 未發現明顯的分類衝突")
        
        # 4.3 統計各頻率層級的覆蓋情況
        results = self.execute_test(
            "4.3 頻率層級覆蓋率（使用場景影響分析）",
            """
            SELECT 
                CASE 
                    WHEN post_count >= 1000000 THEN '超高頻 (>1M)'
                    WHEN post_count >= 100000 THEN '高頻 (100k-1M)'
                    WHEN post_count >= 10000 THEN '中高頻 (10k-100k)'
                    WHEN post_count >= 1000 THEN '中頻 (1k-10k)'
                    ELSE '低頻 (<1k)'
                END as frequency_tier,
                COUNT(*) as tag_count,
                SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified,
                ROUND(SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as coverage_rate,
                SUM(post_count) as total_usage,
                SUM(CASE WHEN main_category IS NULL THEN post_count ELSE 0 END) as missing_usage
            FROM tags_final
            WHERE danbooru_cat = 0
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
            "不同頻率層級對實際使用的影響"
        )
        self._display_results(results, ['frequency_tier', 'tag_count', 'classified', 'coverage_rate', 'total_usage', 'missing_usage'])
    
    def test_classification_errors(self):
        """場景 5: 分類錯誤檢測"""
        print("\n" + "#"*80)
        print("# 場景 5: 潛在分類錯誤檢測")
        print("#"*80)
        
        # 5.1 檢查常見的誤分類模式
        test_cases = [
            ("simple_background", "ENVIRONMENT", "可能被誤分為 CHARACTER_RELATED"),
            ("white_background", "ENVIRONMENT", "可能被誤分為 CHARACTER_RELATED"),
            ("thighhighs", "CHARACTER_RELATED", "應為 CLOTHING 副分類"),
            ("pantyhose", "CHARACTER_RELATED", "應為 CLOTHING 副分類"),
        ]
        
        print("\n測試常見標籤的分類正確性:")
        print("-" * 80)
        
        for tag, expected_main, note in test_cases:
            result = self.conn.execute(
                "SELECT name, main_category, sub_category FROM tags_final WHERE name = ?",
                (tag,)
            ).fetchone()
            
            if result:
                status = "[OK]" if result['main_category'] == expected_main else "[WARN]"
                print(f"{status} {result['name']:20} -> {result['main_category'] or 'NULL':20} / {result['sub_category'] or 'NULL':15} ({note})")
                
                if result['main_category'] != expected_main:
                    self.issues_found.append({
                        'type': 'misclassification',
                        'tag': tag,
                        'expected': expected_main,
                        'actual': result['main_category'],
                        'note': note
                    })
            else:
                print(f"[ERROR] {tag:20} -> 未找到")
    
    def identify_llm_candidates(self):
        """場景 6: 識別需要 LLM 處理的高價值標籤"""
        print("\n" + "#"*80)
        print("# 場景 6: LLM 處理優先級分析")
        print("#"*80)
        
        # 6.1 超高頻未分類標籤（必須處理）
        results = self.execute_test(
            "6.1 超高頻未分類標籤 (post_count > 1M)",
            """
            SELECT 
                name, 
                post_count,
                danbooru_cat,
                ROUND(post_count * 100.0 / (SELECT SUM(post_count) FROM tags_final), 4) as usage_percentage
            FROM tags_final
            WHERE danbooru_cat = 0 
              AND main_category IS NULL
              AND post_count >= 1000000
            ORDER BY post_count DESC;
            """,
            "這些標籤使用量極高，必須優先處理"
        )
        
        if results:
            self._display_results(results, ['name', 'post_count', 'usage_percentage'])
            for row in results:
                self.llm_candidates.append({
                    'tag': row['name'],
                    'usage': row['post_count'],
                    'priority': 'CRITICAL',
                    'reason': '超高頻標籤，影響大量用戶'
                })
        
        # 6.2 高頻未分類標籤（應該處理）
        results = self.execute_test(
            "6.2 高頻未分類標籤 (100k < post_count < 1M)",
            """
            SELECT 
                name, 
                post_count
            FROM tags_final
            WHERE danbooru_cat = 0 
              AND main_category IS NULL
              AND post_count >= 100000 AND post_count < 1000000
            ORDER BY post_count DESC
            LIMIT 50;
            """,
            "這些標籤使用量很高，建議處理"
        )
        
        if results:
            print(f"\n找到 {len(results)} 個高頻未分類標籤")
            print("前 20 個:")
            for i, row in enumerate(results[:20], 1):
                print(f"  {i:2}. {row['name']:30} {row['post_count']:>12,} 次")
                self.llm_candidates.append({
                    'tag': row['name'],
                    'usage': row['post_count'],
                    'priority': 'HIGH',
                    'reason': '高頻標籤'
                })
        
        # 6.3 中高頻未分類標籤（可選處理）
        results = self.execute_test(
            "6.3 中高頻未分類標籤統計 (10k < post_count < 100k)",
            """
            SELECT 
                COUNT(*) as tag_count,
                SUM(post_count) as total_usage,
                ROUND(AVG(post_count), 0) as avg_usage
            FROM tags_final
            WHERE danbooru_cat = 0 
              AND main_category IS NULL
              AND post_count >= 10000 AND post_count < 100000;
            """,
            "這些標籤可根據預算選擇性處理"
        )
        self._display_results(results, ['tag_count', 'total_usage', 'avg_usage'])
        
        # 6.4 LLM 處理成本估算
        print("\n" + "="*80)
        print("LLM 處理成本估算")
        print("="*80)
        
        priority_stats = {
            'CRITICAL': len([c for c in self.llm_candidates if c['priority'] == 'CRITICAL']),
            'HIGH': len([c for c in self.llm_candidates if c['priority'] == 'HIGH'])
        }
        
        print(f"\nCRITICAL 優先級: {priority_stats['CRITICAL']} 個標籤")
        print(f"HIGH 優先級: {priority_stats['HIGH']} 個標籤")
        print(f"總計: {sum(priority_stats.values())} 個標籤")
        
        # 成本估算 (GPT-4o-mini: $0.15/1M input, $0.60/1M output)
        # 假設每個標籤 30 tokens input, 20 tokens output
        total_tags = sum(priority_stats.values())
        estimated_cost = (total_tags * 30 / 1_000_000 * 0.15) + (total_tags * 20 / 1_000_000 * 0.60)
        
        print(f"\n預估 LLM 成本:")
        print(f"  - CRITICAL 標籤: ${priority_stats['CRITICAL'] * 0.00005:.2f}")
        print(f"  - HIGH 標籤: ${priority_stats['HIGH'] * 0.00005:.2f}")
        print(f"  - 總計: ${estimated_cost:.2f}")
    
    def generate_summary_report(self):
        """生成總結報告"""
        print("\n" + "="*80)
        print("實際使用場景測試總結")
        print("="*80)
        
        # 統計測試結果
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r.get('success', False))
        
        print(f"\n總測試場景數：{total_tests}")
        print(f"[OK] 成功：{successful_tests}")
        print(f"[ERROR] 失敗：{total_tests - successful_tests}")
        
        # 發現的問題
        print(f"\n發現的問題數：{len(self.issues_found)}")
        if self.issues_found:
            issue_types = defaultdict(int)
            for issue in self.issues_found:
                issue_types[issue['type']] += 1
            
            print("\n問題分類:")
            for issue_type, count in issue_types.items():
                print(f"  - {issue_type}: {count} 個")
        
        # LLM 候選標籤
        print(f"\n識別出 {len(self.llm_candidates)} 個需要 LLM 處理的標籤")
        
        priority_groups = defaultdict(list)
        for candidate in self.llm_candidates:
            priority_groups[candidate['priority']].append(candidate)
        
        for priority in ['CRITICAL', 'HIGH']:
            if priority in priority_groups:
                tags = priority_groups[priority]
                total_usage = sum(t['usage'] for t in tags)
                print(f"\n{priority} 優先級: {len(tags)} 個標籤")
                print(f"  合計使用次數: {total_usage:,}")
                print(f"  佔總使用量: {total_usage / 1188647968 * 100:.2f}%")
        
        print("\n" + "="*80)
        print(f"[OK] 測試完成！時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def _display_results(self, results: List, columns: List[str], limit: int = 20):
        """顯示查詢結果"""
        if not results:
            print("無結果")
            return
        
        # 顯示表頭
        header = " | ".join(f"{col:20}" for col in columns)
        print(f"\n{header}")
        print("-" * len(header))
        
        # 顯示數據
        for i, row in enumerate(results[:limit]):
            values = []
            for col in columns:
                val = row[col]
                if isinstance(val, int) and val > 1000:
                    values.append(f"{val:>20,}")
                elif isinstance(val, float):
                    values.append(f"{val:>20.2f}")
                else:
                    values.append(f"{str(val):20}")
            print(" | ".join(values))
        
        if len(results) > limit:
            print(f"\n... 還有 {len(results) - limit} 筆結果未顯示")
    
    def save_llm_candidates_to_file(self, filename: str = 'output/llm_candidates.txt'):
        """將 LLM 候選標籤保存到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("LLM 處理候選標籤列表\n")
            f.write("="*80 + "\n")
            f.write(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"總標籤數：{len(self.llm_candidates)}\n")
            f.write("="*80 + "\n\n")
            
            # 按優先級分組
            for priority in ['CRITICAL', 'HIGH']:
                candidates = [c for c in self.llm_candidates if c['priority'] == priority]
                if candidates:
                    f.write(f"\n{priority} 優先級 ({len(candidates)} 個標籤)\n")
                    f.write("-"*80 + "\n")
                    for i, candidate in enumerate(candidates, 1):
                        f.write(f"{i:3}. {candidate['tag']:30} {candidate['usage']:>12,} 次 - {candidate['reason']}\n")
        
        print(f"\n[OK] LLM 候選標籤已保存到: {filename}")


def main():
    """主程式"""
    # 檢查資料庫檔案
    db_path = Path('output/tags.db')
    if not db_path.exists():
        print(f"[ERROR] 找不到資料庫檔案: {db_path}")
        print("請先執行 run_pipeline.py 生成資料庫")
        sys.exit(1)
    
    # 創建測試器並執行測試
    tester = RealWorldUsageTest(str(db_path))
    
    if tester.connect():
        try:
            tester.run_all_tests()
            tester.save_llm_candidates_to_file()
        except KeyboardInterrupt:
            print("\n\n[WARNING] 測試被用戶中斷")
        except Exception as e:
            print(f"\n\n[ERROR] 測試過程發生錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            tester.close()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()


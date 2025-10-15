"""
最終整合測試 - P1 & P2 優化驗證
完整測試所有新功能和優化效果
"""
import asyncio
import httpx
import time
import json
from typing import Dict, List
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class FinalIntegrationTest:
    """最終整合測試類"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    async def run_all_tests(self):
        """執行所有測試"""
        logger.info("🚀 開始最終整合測試 - P1 & P2 優化驗證")
        
        # 基本功能測試
        await self.test_health_check()
        await self.test_cache_system()
        
        # P1 優化測試
        await self.test_advanced_keyword_matching()
        await self.test_ngram_complex_scenarios()
        await self.test_relevance_scoring()
        await self.test_usage_logging()
        
        # P2 優化測試
        await self.test_smart_combinations()
        await self.test_redis_cache_if_available()
        
        # 使用場景測試
        await self.test_realistic_scenarios()
        await self.test_performance_benchmarks()
        
        # 生成報告
        await self.generate_final_report()
    
    def record_test(self, test_name: str, passed: bool, details: Dict = None):
        """記錄測試結果"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}")
        else:
            logger.error(f"❌ {test_name}")
        
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'details': details or {}
        })
    
    async def test_health_check(self):
        """測試健康檢查"""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            passed = response.status_code == 200
            self.record_test("健康檢查", passed, {'status_code': response.status_code})
        except Exception as e:
            self.record_test("健康檢查", False, {'error': str(e)})
    
    async def test_cache_system(self):
        """測試快取系統"""
        try:
            # 測試快取統計
            response = await self.client.get(f"{BASE_URL}/cache/stats")
            stats_passed = response.status_code == 200
            
            # 測試快取健康檢查
            response = await self.client.get(f"{BASE_URL}/cache/health")
            health_passed = response.status_code == 200
            
            passed = stats_passed and health_passed
            self.record_test("快取系統", passed, {
                'stats_available': stats_passed,
                'health_check': health_passed
            })
        except Exception as e:
            self.record_test("快取系統", False, {'error': str(e)})
    
    async def test_advanced_keyword_matching(self):
        """測試 P1 進階關鍵字匹配"""
        test_cases = [
            {
                'description': 'cute girl sitting in classroom',
                'expected_improvements': ['1girl', 'cute', 'sitting', 'classroom']
            },
            {
                'description': 'lonely girl in cyberpunk city at night',
                'expected_improvements': ['1girl', 'lonely', 'cyberpunk', 'city', 'night']
            }
        ]
        
        passed_cases = 0
        
        for case in test_cases:
            try:
                response = await self.client.post(
                    f"{BASE_URL}/api/llm/recommend-tags",
                    json={'description': case['description']}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    recommended_tags = [tag['tag'] for tag in data.get('recommended_tags', [])]
                    
                    # 檢查是否包含預期的改善
                    matches = sum(1 for expected in case['expected_improvements'] 
                                if any(expected.lower() in tag.lower() for tag in recommended_tags))
                    
                    if matches >= len(case['expected_improvements']) * 0.6:  # 60% 匹配率
                        passed_cases += 1
                
            except Exception as e:
                logger.error(f"關鍵字匹配測試錯誤: {e}")
        
        passed = passed_cases >= len(test_cases) * 0.8  # 80% 通過率
        self.record_test("P1 進階關鍵字匹配", passed, {
            'passed_cases': passed_cases,
            'total_cases': len(test_cases),
            'pass_rate': passed_cases / len(test_cases)
        })
    
    async def test_ngram_complex_scenarios(self):
        """測試 N-gram 複合詞處理"""
        complex_scenarios = [
            'school uniform girl',  # 應該優先匹配 school_uniform
            'cyberpunk city night',  # 應該處理複合概念
            'magical girl transformation'  # 複雜的複合詞
        ]
        
        passed_scenarios = 0
        
        for scenario in complex_scenarios:
            try:
                response = await self.client.post(
                    f"{BASE_URL}/api/llm/recommend-tags",
                    json={'description': scenario}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 檢查是否有合理的推薦
                    if len(data.get('recommended_tags', [])) >= 3:
                        passed_scenarios += 1
                
            except Exception:
                continue
        
        passed = passed_scenarios >= len(complex_scenarios) * 0.7
        self.record_test("N-gram 複合詞處理", passed, {
            'passed_scenarios': passed_scenarios,
            'total_scenarios': len(complex_scenarios)
        })
    
    async def test_relevance_scoring(self):
        """測試相關性評分系統"""
        try:
            # 測試相同查詢的一致性
            test_query = 'cute girl with long hair'
            
            results = []
            for _ in range(3):
                response = await self.client.post(
                    f"{BASE_URL}/api/llm/recommend-tags",
                    json={'description': test_query}
                )
                if response.status_code == 200:
                    data = response.json()
                    top_tags = [tag['tag'] for tag in data.get('recommended_tags', [])[:5]]
                    results.append(top_tags)
            
            # 檢查前 3 個標籤的一致性
            if results:
                consistency = len(set(results[0][:3]).intersection(set(results[1][:3])))
                passed = consistency >= 2  # 至少 2 個標籤一致
            else:
                passed = False
            
            self.record_test("相關性評分一致性", passed, {
                'consistency_count': consistency if results else 0,
                'test_runs': len(results)
            })
            
        except Exception as e:
            self.record_test("相關性評分一致性", False, {'error': str(e)})
    
    async def test_usage_logging(self):
        """測試使用數據記錄"""
        try:
            # 發起幾個請求
            for i in range(3):
                await self.client.post(
                    f"{BASE_URL}/api/llm/recommend-tags",
                    json={'description': f'test query {i}'}
                )
            
            # 檢查快取統計是否有更新
            response = await self.client.get(f"{BASE_URL}/cache/stats")
            if response.status_code == 200:
                stats = response.json()
                # 檢查是否有請求記錄
                passed = 'total_requests' in str(stats) or 'hits' in str(stats)
            else:
                passed = False
            
            self.record_test("使用數據記錄", passed, {'stats_available': response.status_code == 200})
            
        except Exception as e:
            self.record_test("使用數據記錄", False, {'error': str(e)})
    
    async def test_smart_combinations(self):
        """測試 P2 智能標籤組合"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/llm/suggest-combinations",
                json={'tags': ['1girl', 'long_hair']}
            )
            
            if response.status_code == 200:
                data = response.json()
                has_combinations = len(data.get('combinations', [])) > 0
                has_prompts = len(data.get('complete_prompts', [])) > 0
                has_analysis = 'balance_analysis' in data
                
                passed = has_combinations and has_prompts and has_analysis
            else:
                passed = False
            
            self.record_test("P2 智能標籤組合", passed, {
                'status_code': response.status_code,
                'has_combinations': has_combinations if response.status_code == 200 else False,
                'has_prompts': has_prompts if response.status_code == 200 else False
            })
            
        except Exception as e:
            self.record_test("P2 智能標籤組合", False, {'error': str(e)})
    
    async def test_redis_cache_if_available(self):
        """測試 Redis 快取（如果可用）"""
        try:
            response = await self.client.get(f"{BASE_URL}/cache/health")
            if response.status_code == 200:
                health = response.json()
                redis_available = 'redis' in str(health).lower() or 'l2_status' in str(health)
                
                self.record_test("Redis 快取可用性", True, {
                    'redis_detected': redis_available,
                    'health_status': health
                })
            else:
                self.record_test("Redis 快取可用性", False, {'health_check_failed': True})
                
        except Exception as e:
            self.record_test("Redis 快取可用性", False, {'error': str(e)})
    
    async def test_realistic_scenarios(self):
        """測試實際使用場景"""
        realistic_scenarios = [
            {
                'name': '初學者簡單查詢',
                'description': 'cute girl',
                'min_tags': 5,
                'should_include': ['1girl']
            },
            {
                'name': '進階場景描述',
                'description': 'lonely girl sitting in empty classroom at sunset',
                'min_tags': 8,
                'should_include': ['1girl', 'sitting']
            },
            {
                'name': '複雜藝術風格',
                'description': 'cyberpunk girl with neon lights in futuristic city',
                'min_tags': 6,
                'should_include': ['1girl', 'cyberpunk']
            }
        ]
        
        passed_scenarios = 0
        
        for scenario in realistic_scenarios:
            try:
                response = await self.client.post(
                    f"{BASE_URL}/api/llm/recommend-tags",
                    json={'description': scenario['description']}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tags = [tag['tag'] for tag in data.get('recommended_tags', [])]
                    
                    # 檢查條件
                    has_min_tags = len(tags) >= scenario['min_tags']
                    includes_required = all(
                        any(req.lower() in tag.lower() for tag in tags)
                        for req in scenario['should_include']
                    )
                    
                    if has_min_tags and includes_required:
                        passed_scenarios += 1
                
            except Exception:
                continue
        
        passed = passed_scenarios >= len(realistic_scenarios) * 0.8
        self.record_test("實際使用場景", passed, {
            'passed_scenarios': passed_scenarios,
            'total_scenarios': len(realistic_scenarios),
            'pass_rate': passed_scenarios / len(realistic_scenarios)
        })
    
    async def test_performance_benchmarks(self):
        """測試效能基準"""
        try:
            # 測試響應時間
            start_time = time.time()
            response = await self.client.post(
                f"{BASE_URL}/api/llm/recommend-tags",
                json={'description': 'performance test query'}
            )
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            # 效能要求
            fast_response = response_time_ms < 2000  # < 2 秒
            successful_response = response.status_code == 200
            
            passed = fast_response and successful_response
            
            self.record_test("效能基準測試", passed, {
                'response_time_ms': round(response_time_ms, 2),
                'status_code': response.status_code,
                'meets_sla': fast_response
            })
            
        except Exception as e:
            self.record_test("效能基準測試", False, {'error': str(e)})
    
    async def generate_final_report(self):
        """生成最終測試報告"""
        pass_rate = self.passed_tests / self.total_tests if self.total_tests > 0 else 0
        
        report = {
            'test_summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.total_tests - self.passed_tests,
                'pass_rate': round(pass_rate * 100, 1),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'p1_optimizations': {
                'keyword_matching': None,
                'ngram_processing': None,
                'relevance_scoring': None,
                'usage_logging': None
            },
            'p2_optimizations': {
                'smart_combinations': None,
                'redis_cache': None
            },
            'overall_assessment': 'PASS' if pass_rate >= 0.8 else 'FAIL',
            'detailed_results': self.test_results
        }
        
        # 分類測試結果
        for result in self.test_results:
            name = result['test_name']
            if 'P1' in name or '關鍵字' in name or 'N-gram' in name or '相關性' in name or '記錄' in name:
                if '關鍵字' in name:
                    report['p1_optimizations']['keyword_matching'] = result['passed']
                elif 'N-gram' in name:
                    report['p1_optimizations']['ngram_processing'] = result['passed']
                elif '相關性' in name:
                    report['p1_optimizations']['relevance_scoring'] = result['passed']
                elif '記錄' in name:
                    report['p1_optimizations']['usage_logging'] = result['passed']
            elif 'P2' in name or '組合' in name or 'Redis' in name:
                if '組合' in name:
                    report['p2_optimizations']['smart_combinations'] = result['passed']
                elif 'Redis' in name:
                    report['p2_optimizations']['redis_cache'] = result['passed']
        
        # 保存報告
        with open('FINAL_TEST_REPORT.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 顯示結果
        logger.info("=" * 60)
        logger.info("🎯 最終測試報告")
        logger.info("=" * 60)
        logger.info(f"總測試數: {self.total_tests}")
        logger.info(f"通過測試: {self.passed_tests}")
        logger.info(f"失敗測試: {self.total_tests - self.passed_tests}")
        logger.info(f"通過率: {pass_rate * 100:.1f}%")
        logger.info(f"整體評估: {report['overall_assessment']}")
        
        if pass_rate >= 0.9:
            logger.info("🎉 優秀！所有優化效果顯著")
        elif pass_rate >= 0.8:
            logger.info("✅ 良好！大部分優化成功")
        else:
            logger.info("⚠️ 需要改善，部分功能未達預期")
        
        logger.info("=" * 60)
        
        return report
    
    async def close(self):
        """關閉客戶端"""
        await self.client.aclose()


async def main():
    """主程式"""
    tester = FinalIntegrationTest()
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        logger.info("測試被中斷")
    except Exception as e:
        logger.error(f"測試執行錯誤: {e}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())

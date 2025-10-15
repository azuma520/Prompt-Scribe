"""
負載測試和併發效能測試
測試 API 在高負載下的表現
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestBasicLoadPerformance:
    """基礎負載效能測試"""
    
    def test_health_endpoint_load(self):
        """測試健康檢查端點的負載"""
        num_requests = 100
        times = []
        
        start_time = time.time()
        
        for _ in range(num_requests):
            req_start = time.time()
            response = client.get("/health")
            req_time = time.time() - req_start
            times.append(req_time)
            
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        
        # 統計分析
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        p99_time = sorted(times)[int(len(times) * 0.99)]
        
        print(f"\n=== 健康檢查端點負載測試 ===")
        print(f"請求數: {num_requests}")
        print(f"總時間: {total_time:.2f}s")
        print(f"吞吐量: {num_requests/total_time:.1f} req/s")
        print(f"平均時間: {avg_time*1000:.2f}ms")
        print(f"中位數: {median_time*1000:.2f}ms")
        print(f"P95: {p95_time*1000:.2f}ms")
        print(f"P99: {p99_time*1000:.2f}ms")
        
        # 效能要求
        assert avg_time < 0.1  # 平均 < 100ms
        assert p95_time < 0.2  # P95 < 200ms


class TestConcurrentRequests:
    """併發請求測試"""
    
    def _make_request(self, endpoint: str):
        """發送單個請求並測量時間"""
        start = time.time()
        try:
            response = client.get(endpoint)
            elapsed = time.time() - start
            return {
                'success': response.status_code == 200,
                'time': elapsed,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'time': time.time() - start,
                'error': str(e)
            }
    
    def test_concurrent_health_checks(self):
        """測試併發健康檢查"""
        num_concurrent = 20
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            start_time = time.time()
            
            # 提交併發請求
            futures = [
                executor.submit(self._make_request, "/health")
                for _ in range(num_concurrent)
            ]
            
            # 收集結果
            results = []
            for future in as_completed(futures):
                results.append(future.result())
            
            total_time = time.time() - start_time
        
        # 分析結果
        success_count = sum(1 for r in results if r['success'])
        times = [r['time'] for r in results if r['success']]
        
        print(f"\n=== 併發健康檢查測試 ===")
        print(f"併發數: {num_concurrent}")
        print(f"成功請求: {success_count}/{num_concurrent}")
        print(f"總時間: {total_time:.2f}s")
        print(f"平均響應時間: {statistics.mean(times)*1000:.2f}ms")
        print(f"最大響應時間: {max(times)*1000:.2f}ms")
        
        # 所有請求都應該成功
        assert success_count == num_concurrent
        
        # 平均響應時間應該合理
        assert statistics.mean(times) < 1.0
    
    def test_concurrent_tag_queries(self):
        """測試併發標籤查詢"""
        tag_names = ["1girl", "solo", "long_hair", "smile", "school_uniform"]
        num_concurrent = 10
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            start_time = time.time()
            
            # 提交併發請求
            futures = []
            for tag in tag_names:
                for _ in range(num_concurrent // len(tag_names) + 1):
                    futures.append(
                        executor.submit(self._make_request, f"/api/v1/tags/{tag}")
                    )
            
            # 收集結果
            results = []
            for future in as_completed(futures[:num_concurrent]):
                results.append(future.result())
            
            total_time = time.time() - start_time
        
        success_count = sum(1 for r in results if r['success'])
        times = [r['time'] for r in results if r['success']]
        
        print(f"\n=== 併發標籤查詢測試 ===")
        print(f"併發數: {num_concurrent}")
        print(f"成功率: {success_count/len(results)*100:.1f}%")
        print(f"總時間: {total_time:.2f}s")
        if times:
            print(f"平均響應時間: {statistics.mean(times)*1000:.2f}ms")
            print(f"P95 響應時間: {sorted(times)[int(len(times)*0.95)]*1000:.2f}ms")


class TestSearchLoadPerformance:
    """搜尋端點負載測試"""
    
    def test_search_load(self):
        """測試搜尋端點的負載"""
        search_terms = ["girl", "city", "night", "happy", "school"]
        num_requests = 50
        
        times = []
        start_time = time.time()
        
        for i in range(num_requests):
            term = search_terms[i % len(search_terms)]
            req_start = time.time()
            
            response = client.post(
                "/api/v1/search",
                json={"query": term, "limit": 10}
            )
            
            req_time = time.time() - req_start
            times.append(req_time)
            
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        
        print(f"\n=== 搜尋端點負載測試 ===")
        print(f"請求數: {num_requests}")
        print(f"總時間: {total_time:.2f}s")
        print(f"吞吐量: {num_requests/total_time:.1f} req/s")
        print(f"平均時間: {statistics.mean(times)*1000:.2f}ms")
        print(f"P95: {sorted(times)[int(len(times)*0.95)]*1000:.2f}ms")


class TestLLMEndpointLoad:
    """LLM 端點負載測試"""
    
    def test_recommend_tags_load(self):
        """測試標籤推薦端點的負載"""
        descriptions = [
            "a cute girl",
            "cyberpunk city",
            "happy smile",
            "school uniform",
            "night scene"
        ]
        num_requests = 25
        
        times = []
        start_time = time.time()
        
        for i in range(num_requests):
            desc = descriptions[i % len(descriptions)]
            req_start = time.time()
            
            response = client.post(
                "/api/llm/recommend-tags",
                json={"description": desc, "max_tags": 8}
            )
            
            req_time = time.time() - req_start
            times.append(req_time)
            
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        
        print(f"\n=== 標籤推薦負載測試 ===")
        print(f"請求數: {num_requests}")
        print(f"總時間: {total_time:.2f}s")
        print(f"吞吐量: {num_requests/total_time:.1f} req/s")
        print(f"平均時間: {statistics.mean(times)*1000:.2f}ms")
        print(f"P95: {sorted(times)[int(len(times)*0.95)]*1000:.2f}ms")
        
        # LLM 端點效能要求
        assert statistics.mean(times) < 0.5  # 平均 < 500ms
        assert sorted(times)[int(len(times)*0.95)] < 1.0  # P95 < 1s
    
    def test_validation_load(self):
        """測試驗證端點的負載"""
        tag_sets = [
            ["1girl", "solo"],
            ["2girls", "yuri"],
            ["1boy", "male_focus"],
            ["cat", "animal"],
            ["city", "night"]
        ]
        num_requests = 30
        
        times = []
        start_time = time.time()
        
        for i in range(num_requests):
            tags = tag_sets[i % len(tag_sets)]
            req_start = time.time()
            
            response = client.post(
                "/api/llm/validate-prompt",
                json={"tags": tags}
            )
            
            req_time = time.time() - req_start
            times.append(req_time)
            
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        
        print(f"\n=== 驗證端點負載測試 ===")
        print(f"請求數: {num_requests}")
        print(f"總時間: {total_time:.2f}s")
        print(f"平均時間: {statistics.mean(times)*1000:.2f}ms")


class TestCacheUnderLoad:
    """測試快取在高負載下的表現"""
    
    def test_cache_effectiveness_under_load(self):
        """測試快取在高負載下的效果"""
        tag_name = "1girl"
        num_requests = 100
        
        times = []
        start_time = time.time()
        
        for _ in range(num_requests):
            req_start = time.time()
            response = client.get(f"/api/v1/tags/{tag_name}")
            req_time = time.time() - req_start
            times.append(req_time)
            
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        
        # 前 10% 的請求（無快取或建立快取）
        first_10_percent = times[:10]
        # 後 90% 的請求（應該有快取）
        last_90_percent = times[10:]
        
        avg_first = statistics.mean(first_10_percent)
        avg_last = statistics.mean(last_90_percent)
        
        print(f"\n=== 快取負載測試 ===")
        print(f"請求數: {num_requests}")
        print(f"總時間: {total_time:.2f}s")
        print(f"吞吐量: {num_requests/total_time:.1f} req/s")
        print(f"前 10% 平均時間: {avg_first*1000:.2f}ms")
        print(f"後 90% 平均時間: {avg_last*1000:.2f}ms")
        print(f"快取效能提升: {avg_first/avg_last:.1f}x")
        
        # 快取應該帶來效能提升
        if avg_first > 0.01:  # 只在第一批足夠慢時檢查
            assert avg_last < avg_first


class TestStressTest:
    """壓力測試"""
    
    def test_sustained_load(self):
        """測試持續負載"""
        duration_seconds = 10
        num_workers = 5
        
        def worker():
            """工作線程"""
            results = []
            end_time = time.time() + duration_seconds
            
            while time.time() < end_time:
                start = time.time()
                response = client.get("/health")
                elapsed = time.time() - start
                
                results.append({
                    'success': response.status_code == 200,
                    'time': elapsed
                })
            
            return results
        
        # 執行持續負載測試
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker) for _ in range(num_workers)]
            all_results = []
            
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        total_time = time.time() - start_time
        
        # 分析結果
        total_requests = len(all_results)
        success_count = sum(1 for r in all_results if r['success'])
        success_rate = success_count / total_requests * 100
        
        times = [r['time'] for r in all_results if r['success']]
        
        print(f"\n=== 持續負載測試 ===")
        print(f"測試時長: {total_time:.1f}s")
        print(f"總請求數: {total_requests}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"吞吐量: {total_requests/total_time:.1f} req/s")
        print(f"平均響應時間: {statistics.mean(times)*1000:.2f}ms")
        print(f"P95 響應時間: {sorted(times)[int(len(times)*0.95)]*1000:.2f}ms")
        print(f"P99 響應時間: {sorted(times)[int(len(times)*0.99)]*1000:.2f}ms")
        
        # 成功率應該很高
        assert success_rate > 95
        
        # 平均響應時間應該合理
        assert statistics.mean(times) < 0.5


class TestMemoryAndResourceUsage:
    """記憶體和資源使用測試"""
    
    @pytest.mark.skip(reason="需要 psutil 套件")
    def test_memory_usage(self):
        """測試記憶體使用情況"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 記錄初始記憶體
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 執行大量請求
        num_requests = 1000
        for _ in range(num_requests):
            client.get("/health")
        
        # 記錄最終記憶體
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\n=== 記憶體使用測試 ===")
        print(f"請求數: {num_requests}")
        print(f"初始記憶體: {initial_memory:.1f} MB")
        print(f"最終記憶體: {final_memory:.1f} MB")
        print(f"記憶體增長: {memory_increase:.1f} MB")
        
        # 記憶體增長應該在合理範圍內
        assert memory_increase < 100  # 不應該增長超過 100MB


if __name__ == "__main__":
    # 運行負載測試時顯示詳細輸出
    pytest.main([__file__, "-v", "-s", "--tb=short"])


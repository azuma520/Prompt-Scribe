#!/usr/bin/env python3
"""
⚡ Performance Test Suite for Prompt-Scribe Supabase Database

Specialized performance testing focusing on query speed, throughput, and scalability.
"""

import os
import time
import statistics
import threading
import queue
import random
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Missing supabase dependency. Install with: pip install supabase")
    sys.exit(1)

@dataclass
class PerformanceResult:
    """Performance test result"""
    test_name: str
    total_operations: int
    duration_seconds: float
    operations_per_second: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    success_rate: float
    errors: int

class PerformanceTestSuite:
    """Performance testing suite"""
    
    def __init__(self):
        # Load environment variables
        env_path = project_root / "specs" / "001-sqlite-ags-db" / ".env"
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except ImportError:
                pass
        
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing Supabase credentials")
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        self.results: List[PerformanceResult] = []
        
        # Pre-load some sample data for testing
        self.sample_names = []
        self.sample_ids = []
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample data for performance testing"""
        try:
            # Get sample names
            response = self.client.table('tags_final').select('name').limit(100).execute()
            self.sample_names = [item['name'] for item in response.data]
            
            # Get sample IDs
            response = self.client.table('tags_final').select('id').limit(100).execute()
            self.sample_ids = [item['id'] for item in response.data]
            
            print(f"📊 Loaded {len(self.sample_names)} sample names and {len(self.sample_ids)} sample IDs")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load sample data: {e}")

    def measure_query_performance(self, test_name: str, query_func, iterations: int = 100) -> PerformanceResult:
        """Measure performance of a query function"""
        print(f"⚡ Running {test_name} ({iterations} iterations)...")
        
        response_times = []
        errors = 0
        start_time = time.time()
        
        for i in range(iterations):
            query_start = time.time()
            try:
                result = query_func()
                query_time = (time.time() - query_start) * 1000  # Convert to ms
                response_times.append(query_time)
            except Exception as e:
                errors += 1
                if errors <= 3:  # Only print first few errors
                    print(f"   Error in iteration {i+1}: {str(e)[:50]}...")
        
        total_duration = time.time() - start_time
        successful_operations = len(response_times)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_time
        else:
            avg_time = min_time = max_time = p95_time = 0
        
        ops_per_second = successful_operations / total_duration if total_duration > 0 else 0
        success_rate = successful_operations / iterations * 100
        
        result = PerformanceResult(
            test_name=test_name,
            total_operations=iterations,
            duration_seconds=total_duration,
            operations_per_second=ops_per_second,
            avg_response_time_ms=avg_time,
            min_response_time_ms=min_time,
            max_response_time_ms=max_time,
            p95_response_time_ms=p95_time,
            success_rate=success_rate,
            errors=errors
        )
        
        self.results.append(result)
        self._print_result(result)
        return result

    def _print_result(self, result: PerformanceResult):
        """Print performance result"""
        print(f"   ✅ {result.test_name}:")
        print(f"      Operations/sec: {result.operations_per_second:.1f}")
        print(f"      Avg response: {result.avg_response_time_ms:.1f}ms")
        print(f"      P95 response: {result.p95_response_time_ms:.1f}ms")
        print(f"      Success rate: {result.success_rate:.1f}%")
        if result.errors > 0:
            print(f"      Errors: {result.errors}")
        print()

    # =============================================================================
    # Performance Test Cases
    # =============================================================================

    def test_primary_key_queries(self) -> PerformanceResult:
        """Test primary key query performance"""
        def query():
            if not self.sample_ids:
                return None
            random_id = random.choice(self.sample_ids)
            return self.client.table('tags_final').select('*').eq('id', random_id).execute()
        
        return self.measure_query_performance("Primary Key Queries", query, 200)

    def test_name_exact_match(self) -> PerformanceResult:
        """Test exact name match performance"""
        def query():
            if not self.sample_names:
                return None
            random_name = random.choice(self.sample_names)
            return self.client.table('tags_final').select('*').eq('name', random_name).execute()
        
        return self.measure_query_performance("Name Exact Match", query, 150)

    def test_name_prefix_search(self) -> PerformanceResult:
        """Test name prefix search performance"""
        def query():
            if not self.sample_names:
                return None
            random_name = random.choice(self.sample_names)
            prefix = random_name[:3] if len(random_name) >= 3 else random_name
            return self.client.table('tags_final').select('*').like('name', f'{prefix}%').limit(20).execute()
        
        return self.measure_query_performance("Name Prefix Search", query, 100)

    def test_category_queries(self) -> PerformanceResult:
        """Test category-based query performance"""
        categories = ['character', 'action_pose', 'theme_concept', 'adult_content']
        
        def query():
            category = random.choice(categories)
            return self.client.table('tags_final').select('*').eq('main_category', category).limit(50).execute()
        
        return self.measure_query_performance("Category Queries", query, 100)

    def test_range_queries(self) -> PerformanceResult:
        """Test range query performance"""
        def query():
            min_count = random.randint(1, 1000)
            max_count = min_count + random.randint(1000, 5000)
            return self.client.table('tags_final').select('*').gte('post_count', min_count).lte('post_count', max_count).limit(30).execute()
        
        return self.measure_query_performance("Range Queries", query, 80)

    def test_complex_queries(self) -> PerformanceResult:
        """Test complex multi-condition queries"""
        categories = ['character', 'action_pose', 'theme_concept']
        
        def query():
            category = random.choice(categories)
            min_count = random.randint(10, 100)
            min_confidence = random.uniform(0.5, 0.9)
            return self.client.table('tags_final').select('*').eq('main_category', category).gte('post_count', min_count).gte('confidence', min_confidence).limit(20).execute()
        
        return self.measure_query_performance("Complex Queries", query, 60)

    def test_sorting_queries(self) -> PerformanceResult:
        """Test sorting performance"""
        sort_fields = ['post_count', 'confidence', 'name']
        
        def query():
            field = random.choice(sort_fields)
            desc = random.choice([True, False])
            return self.client.table('tags_final').select('*').order(field, desc=desc).limit(25).execute()
        
        return self.measure_query_performance("Sorting Queries", query, 50)

    def test_aggregation_queries(self) -> PerformanceResult:
        """Test aggregation performance"""
        def query():
            # Note: This might not work with all Supabase plans
            try:
                return self.client.table('tags_final').select('main_category', count='exact').execute()
            except:
                # Fallback to simple count
                return self.client.table('tags_final').select('id', count='exact').limit(1).execute()
        
        return self.measure_query_performance("Aggregation Queries", query, 30)

    # =============================================================================
    # Concurrent Performance Tests
    # =============================================================================

    def test_concurrent_reads(self, num_threads: int = 10, queries_per_thread: int = 20) -> PerformanceResult:
        """Test concurrent read performance"""
        print(f"⚡ Running Concurrent Reads ({num_threads} threads, {queries_per_thread} queries each)...")
        
        results_queue = queue.Queue()
        errors = 0
        start_time = time.time()
        
        def worker():
            thread_times = []
            thread_errors = 0
            for _ in range(queries_per_thread):
                query_start = time.time()
                try:
                    if self.sample_names:
                        name = random.choice(self.sample_names)
                        response = self.client.table('tags_final').select('*').eq('name', name).execute()
                    else:
                        response = self.client.table('tags_final').select('*').limit(10).execute()
                    
                    query_time = (time.time() - query_start) * 1000
                    thread_times.append(query_time)
                except Exception as e:
                    thread_errors += 1
            
            results_queue.put((thread_times, thread_errors))
        
        # Start threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        all_times = []
        while not results_queue.empty():
            thread_times, thread_errors = results_queue.get()
            all_times.extend(thread_times)
            errors += thread_errors
        
        total_duration = time.time() - start_time
        total_operations = num_threads * queries_per_thread
        successful_operations = len(all_times)
        
        if all_times:
            avg_time = statistics.mean(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            p95_time = statistics.quantiles(all_times, n=20)[18] if len(all_times) >= 20 else max_time
        else:
            avg_time = min_time = max_time = p95_time = 0
        
        ops_per_second = successful_operations / total_duration if total_duration > 0 else 0
        success_rate = successful_operations / total_operations * 100
        
        result = PerformanceResult(
            test_name="Concurrent Reads",
            total_operations=total_operations,
            duration_seconds=total_duration,
            operations_per_second=ops_per_second,
            avg_response_time_ms=avg_time,
            min_response_time_ms=min_time,
            max_response_time_ms=max_time,
            p95_response_time_ms=p95_time,
            success_rate=success_rate,
            errors=errors
        )
        
        self.results.append(result)
        self._print_result(result)
        return result

    # =============================================================================
    # Test Runner and Reporting
    # =============================================================================

    def run_performance_suite(self):
        """Run complete performance test suite"""
        print("⚡ Starting Performance Test Suite")
        print("=" * 60)
        
        suite_start = time.time()
        
        # Run individual performance tests
        self.test_primary_key_queries()
        self.test_name_exact_match()
        self.test_name_prefix_search()
        self.test_category_queries()
        self.test_range_queries()
        self.test_complex_queries()
        self.test_sorting_queries()
        self.test_aggregation_queries()
        
        # Run concurrent tests
        self.test_concurrent_reads(num_threads=5, queries_per_thread=10)
        self.test_concurrent_reads(num_threads=10, queries_per_thread=10)
        
        suite_duration = time.time() - suite_start
        
        # Generate performance report
        self.generate_performance_report(suite_duration)

    def generate_performance_report(self, suite_duration: float):
        """Generate comprehensive performance report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST REPORT")
        print("=" * 60)
        
        if not self.results:
            print("❌ No results to report")
            return
        
        # Overall statistics
        total_operations = sum(r.total_operations for r in self.results)
        avg_ops_per_second = statistics.mean([r.operations_per_second for r in self.results])
        avg_response_time = statistics.mean([r.avg_response_time_ms for r in self.results])
        overall_success_rate = statistics.mean([r.success_rate for r in self.results])
        
        print(f"📈 Overall Performance:")
        print(f"   Total Operations: {total_operations:,}")
        print(f"   Suite Duration: {suite_duration:.1f}s")
        print(f"   Average Ops/sec: {avg_ops_per_second:.1f}")
        print(f"   Average Response Time: {avg_response_time:.1f}ms")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        print(f"\n🏆 Best Performers:")
        # Sort by operations per second
        sorted_by_ops = sorted(self.results, key=lambda x: x.operations_per_second, reverse=True)
        for i, result in enumerate(sorted_by_ops[:3]):
            print(f"   {i+1}. {result.test_name}: {result.operations_per_second:.1f} ops/sec")
        
        print(f"\n⚡ Fastest Response Times:")
        # Sort by average response time
        sorted_by_time = sorted(self.results, key=lambda x: x.avg_response_time_ms)
        for i, result in enumerate(sorted_by_time[:3]):
            print(f"   {i+1}. {result.test_name}: {result.avg_response_time_ms:.1f}ms avg")
        
        print(f"\n⚠️  Performance Concerns:")
        concerns = []
        for result in self.results:
            if result.avg_response_time_ms > 500:
                concerns.append(f"{result.test_name}: Slow response ({result.avg_response_time_ms:.1f}ms)")
            if result.success_rate < 95:
                concerns.append(f"{result.test_name}: Low success rate ({result.success_rate:.1f}%)")
            if result.operations_per_second < 10:
                concerns.append(f"{result.test_name}: Low throughput ({result.operations_per_second:.1f} ops/sec)")
        
        if concerns:
            for concern in concerns:
                print(f"   ⚠️  {concern}")
        else:
            print("   🎉 No performance concerns detected!")
        
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            print(f"   {result.test_name}:")
            print(f"      Ops/sec: {result.operations_per_second:.1f} | "
                  f"Avg: {result.avg_response_time_ms:.1f}ms | "
                  f"P95: {result.p95_response_time_ms:.1f}ms | "
                  f"Success: {result.success_rate:.1f}%")
        
        print("\n" + "=" * 60)
        print("🏁 Performance Test Suite Complete")
        print("=" * 60)

def main():
    """Main performance test runner"""
    try:
        test_suite = PerformanceTestSuite()
        test_suite.run_performance_suite()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Performance test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

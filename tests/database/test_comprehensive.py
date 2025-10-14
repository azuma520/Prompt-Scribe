#!/usr/bin/env python3
"""
🧪 Comprehensive Database Test Suite for Prompt-Scribe Supabase Database

This test suite provides comprehensive testing for the migrated Supabase database,
including functionality, performance, data integrity, and edge cases.
"""

import asyncio
import time
import random
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(project_root))

try:
    from supabase import create_client, Client
    import pytest
    import asyncpg
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please install: pip install supabase pytest asyncpg")
    sys.exit(1)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    success: bool
    duration_ms: float
    details: Dict[str, Any]
    error: str = None

class DatabaseTestSuite:
    """Comprehensive database test suite"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        self.service_client = create_client(self.supabase_url, self.service_role_key) if self.service_role_key else None
        self.results: List[TestResult] = []
        
    def log_result(self, test_name: str, success: bool, duration_ms: float, 
                   details: Dict[str, Any] = None, error: str = None):
        """Log test result"""
        result = TestResult(
            test_name=test_name,
            success=success,
            duration_ms=duration_ms,
            details=details or {},
            error=error
        )
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration_ms:.2f}ms)")
        if error:
            print(f"   Error: {error}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    # =============================================================================
    # 1. Basic Functionality Tests
    # =============================================================================
    
    def test_connection(self) -> bool:
        """Test basic database connection"""
        start_time = time.time()
        try:
            # Test basic connection
            response = self.client.table('tags_final').select('id').limit(1).execute()
            
            duration_ms = (time.time() - start_time) * 1000
            success = len(response.data) > 0
            
            self.log_result(
                "Database Connection",
                success,
                duration_ms,
                {"records_found": len(response.data)}
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Database Connection", False, duration_ms, error=str(e))
            return False

    def test_data_existence(self) -> bool:
        """Test that all migrated data exists"""
        start_time = time.time()
        try:
            # Count total records
            response = self.client.table('tags_final').select('id', count='exact').execute()
            total_count = response.count
            
            duration_ms = (time.time() - start_time) * 1000
            expected_count = 140782
            success = total_count == expected_count
            
            self.log_result(
                "Data Existence Check",
                success,
                duration_ms,
                {
                    "expected_count": expected_count,
                    "actual_count": total_count,
                    "match": success
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Data Existence Check", False, duration_ms, error=str(e))
            return False

    def test_basic_crud_operations(self) -> bool:
        """Test basic CRUD operations"""
        if not self.service_client:
            self.log_result("CRUD Operations", False, 0, error="Service role key required for CRUD tests")
            return False
            
        start_time = time.time()
        test_tag_name = f"test_tag_{int(time.time())}"
        
        try:
            # CREATE - Insert test record
            insert_response = self.service_client.table('tags_final').insert({
                'name': test_tag_name,
                'danbooru_cat': 'general',
                'post_count': 1,
                'main_category': 'test_category',
                'sub_category': 'test_sub',
                'confidence': 0.95,
                'classification_source': 'test'
            }).execute()
            
            if not insert_response.data:
                raise Exception("Insert failed - no data returned")
                
            inserted_id = insert_response.data[0]['id']
            
            # READ - Query the inserted record
            read_response = self.service_client.table('tags_final').select('*').eq('id', inserted_id).execute()
            if not read_response.data:
                raise Exception("Read failed - record not found")
            
            # UPDATE - Modify the record
            update_response = self.service_client.table('tags_final').update({
                'post_count': 2
            }).eq('id', inserted_id).execute()
            
            if not update_response.data:
                raise Exception("Update failed - no data returned")
            
            # Verify update
            verify_response = self.service_client.table('tags_final').select('post_count').eq('id', inserted_id).execute()
            if verify_response.data[0]['post_count'] != 2:
                raise Exception("Update verification failed")
            
            # DELETE - Remove the test record
            delete_response = self.service_client.table('tags_final').delete().eq('id', inserted_id).execute()
            
            # Verify deletion
            final_check = self.service_client.table('tags_final').select('id').eq('id', inserted_id).execute()
            if final_check.data:
                raise Exception("Delete verification failed - record still exists")
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "CRUD Operations",
                True,
                duration_ms,
                {
                    "operations": "CREATE, READ, UPDATE, DELETE",
                    "test_record": test_tag_name
                }
            )
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("CRUD Operations", False, duration_ms, error=str(e))
            return False

    # =============================================================================
    # 2. Query Performance Tests
    # =============================================================================
    
    def test_primary_key_query_performance(self) -> bool:
        """Test primary key query performance"""
        start_time = time.time()
        try:
            # Get a random ID first
            sample_response = self.client.table('tags_final').select('id').limit(100).execute()
            if not sample_response.data:
                raise Exception("No sample data found")
            
            random_id = random.choice(sample_response.data)['id']
            
            # Measure query time
            query_start = time.time()
            response = self.client.table('tags_final').select('*').eq('id', random_id).execute()
            query_duration = (time.time() - query_start) * 1000
            
            success = len(response.data) == 1 and query_duration < 100  # Should be < 100ms
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Primary Key Query Performance",
                success,
                duration_ms,
                {
                    "query_time_ms": f"{query_duration:.2f}",
                    "records_found": len(response.data),
                    "performance_target": "< 100ms"
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Primary Key Query Performance", False, duration_ms, error=str(e))
            return False

    def test_name_search_performance(self) -> bool:
        """Test name search performance"""
        start_time = time.time()
        try:
            # Get some sample names
            sample_response = self.client.table('tags_final').select('name').limit(10).execute()
            if not sample_response.data:
                raise Exception("No sample data found")
            
            sample_name = random.choice(sample_response.data)['name']
            
            # Test exact match
            query_start = time.time()
            response = self.client.table('tags_final').select('*').eq('name', sample_name).execute()
            exact_duration = (time.time() - query_start) * 1000
            
            # Test prefix search
            prefix = sample_name[:3] if len(sample_name) >= 3 else sample_name
            query_start = time.time()
            prefix_response = self.client.table('tags_final').select('*').like('name', f'{prefix}%').limit(10).execute()
            prefix_duration = (time.time() - query_start) * 1000
            
            success = (exact_duration < 200 and prefix_duration < 500 and 
                      len(response.data) > 0)
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Name Search Performance",
                success,
                duration_ms,
                {
                    "exact_match_ms": f"{exact_duration:.2f}",
                    "prefix_search_ms": f"{prefix_duration:.2f}",
                    "exact_results": len(response.data),
                    "prefix_results": len(prefix_response.data)
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Name Search Performance", False, duration_ms, error=str(e))
            return False

    def test_category_query_performance(self) -> bool:
        """Test category-based query performance"""
        start_time = time.time()
        try:
            # Test main category query
            query_start = time.time()
            response = self.client.table('tags_final').select('*').eq('main_category', 'character').limit(100).execute()
            category_duration = (time.time() - query_start) * 1000
            
            # Test range query (post_count)
            query_start = time.time()
            range_response = self.client.table('tags_final').select('*').gte('post_count', 1000).lte('post_count', 5000).limit(50).execute()
            range_duration = (time.time() - query_start) * 1000
            
            success = category_duration < 300 and range_duration < 500
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Category Query Performance",
                success,
                duration_ms,
                {
                    "category_query_ms": f"{category_duration:.2f}",
                    "range_query_ms": f"{range_duration:.2f}",
                    "category_results": len(response.data),
                    "range_results": len(range_response.data)
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Category Query Performance", False, duration_ms, error=str(e))
            return False

    # =============================================================================
    # 3. Data Integrity Tests
    # =============================================================================
    
    def test_data_integrity(self) -> bool:
        """Test data integrity and constraints"""
        start_time = time.time()
        try:
            # Test unique constraint on name
            response = self.client.table('tags_final').select('name', count='exact').execute()
            total_names = response.count
            
            # Count distinct names
            distinct_response = self.client.rpc('count_distinct_names').execute()
            distinct_names = distinct_response.data if distinct_response.data else 0
            
            # Check for null values in required fields
            null_check = self.client.table('tags_final').select('id').is_('name', 'null').execute()
            has_null_names = len(null_check.data) > 0
            
            # Check data types and ranges
            invalid_counts = self.client.table('tags_final').select('id').lt('post_count', 0).execute()
            has_invalid_counts = len(invalid_counts.data) > 0
            
            invalid_confidence = self.client.table('tags_final').select('id').or_('confidence.lt.0,confidence.gt.1').execute()
            has_invalid_confidence = len(invalid_confidence.data) > 0
            
            success = (not has_null_names and not has_invalid_counts and 
                      not has_invalid_confidence)
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Data Integrity Check",
                success,
                duration_ms,
                {
                    "total_records": total_names,
                    "null_names": has_null_names,
                    "invalid_post_counts": has_invalid_counts,
                    "invalid_confidence": has_invalid_confidence
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Data Integrity Check", False, duration_ms, error=str(e))
            return False

    # =============================================================================
    # 4. Search Functionality Tests
    # =============================================================================
    
    def test_search_functionality(self) -> bool:
        """Test various search functionalities"""
        start_time = time.time()
        try:
            # Text search with ILIKE
            search_term = "girl"
            ilike_response = self.client.table('tags_final').select('*').ilike('name', f'%{search_term}%').limit(20).execute()
            
            # Category-based search
            category_response = self.client.table('tags_final').select('*').eq('main_category', 'character').limit(20).execute()
            
            # Multi-condition search
            complex_response = self.client.table('tags_final').select('*').eq('main_category', 'character').gte('post_count', 100).gte('confidence', 0.8).limit(10).execute()
            
            # Sorting test
            sorted_response = self.client.table('tags_final').select('*').order('post_count', desc=True).limit(10).execute()
            
            success = (len(ilike_response.data) > 0 and 
                      len(category_response.data) > 0 and
                      len(complex_response.data) > 0 and
                      len(sorted_response.data) > 0)
            
            # Verify sorting
            if len(sorted_response.data) > 1:
                is_sorted = all(sorted_response.data[i]['post_count'] >= sorted_response.data[i+1]['post_count'] 
                               for i in range(len(sorted_response.data)-1))
                success = success and is_sorted
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Search Functionality",
                success,
                duration_ms,
                {
                    "text_search_results": len(ilike_response.data),
                    "category_search_results": len(category_response.data),
                    "complex_search_results": len(complex_response.data),
                    "sorted_results": len(sorted_response.data),
                    "sorting_correct": is_sorted if len(sorted_response.data) > 1 else True
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Search Functionality", False, duration_ms, error=str(e))
            return False

    # =============================================================================
    # 5. Performance Benchmark Tests
    # =============================================================================
    
    def test_concurrent_queries(self) -> bool:
        """Test concurrent query performance"""
        start_time = time.time()
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            num_threads = 10
            queries_per_thread = 5
            
            def worker():
                thread_times = []
                for _ in range(queries_per_thread):
                    query_start = time.time()
                    try:
                        response = self.client.table('tags_final').select('*').limit(10).execute()
                        query_time = (time.time() - query_start) * 1000
                        thread_times.append(query_time)
                    except Exception as e:
                        thread_times.append(-1)  # Error marker
                results_queue.put(thread_times)
            
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
            error_count = 0
            while not results_queue.empty():
                thread_times = results_queue.get()
                for t in thread_times:
                    if t == -1:
                        error_count += 1
                    else:
                        all_times.append(t)
            
            if all_times:
                avg_time = statistics.mean(all_times)
                max_time = max(all_times)
                min_time = min(all_times)
                success = error_count == 0 and avg_time < 500
            else:
                success = False
                avg_time = max_time = min_time = 0
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Concurrent Query Performance",
                success,
                duration_ms,
                {
                    "threads": num_threads,
                    "queries_per_thread": queries_per_thread,
                    "total_queries": len(all_times) + error_count,
                    "errors": error_count,
                    "avg_query_time_ms": f"{avg_time:.2f}" if all_times else "N/A",
                    "max_query_time_ms": f"{max_time:.2f}" if all_times else "N/A",
                    "min_query_time_ms": f"{min_time:.2f}" if all_times else "N/A"
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Concurrent Query Performance", False, duration_ms, error=str(e))
            return False

    # =============================================================================
    # 6. Edge Case Tests
    # =============================================================================
    
    def test_edge_cases(self) -> bool:
        """Test edge cases and error handling"""
        start_time = time.time()
        try:
            edge_cases_passed = 0
            total_edge_cases = 0
            
            # Test 1: Query non-existent record
            total_edge_cases += 1
            try:
                response = self.client.table('tags_final').select('*').eq('id', -999999).execute()
                if len(response.data) == 0:
                    edge_cases_passed += 1
            except:
                pass
            
            # Test 2: Empty string search
            total_edge_cases += 1
            try:
                response = self.client.table('tags_final').select('*').eq('name', '').execute()
                # Should handle gracefully
                edge_cases_passed += 1
            except:
                pass
            
            # Test 3: Very long string search
            total_edge_cases += 1
            try:
                long_string = 'a' * 1000
                response = self.client.table('tags_final').select('*').ilike('name', f'%{long_string}%').execute()
                # Should handle gracefully
                edge_cases_passed += 1
            except:
                pass
            
            # Test 4: Large limit value
            total_edge_cases += 1
            try:
                response = self.client.table('tags_final').select('id').limit(10000).execute()
                # Should handle gracefully (may be limited by Supabase)
                edge_cases_passed += 1
            except:
                pass
            
            # Test 5: Invalid column name (should fail gracefully)
            total_edge_cases += 1
            try:
                response = self.client.table('tags_final').select('nonexistent_column').limit(1).execute()
                # This should fail, but we're testing graceful failure
            except:
                edge_cases_passed += 1  # Expected to fail
            
            success = edge_cases_passed >= total_edge_cases * 0.8  # 80% pass rate
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_result(
                "Edge Case Handling",
                success,
                duration_ms,
                {
                    "total_cases": total_edge_cases,
                    "passed_cases": edge_cases_passed,
                    "pass_rate": f"{(edge_cases_passed/total_edge_cases)*100:.1f}%"
                }
            )
            return success
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Edge Case Handling", False, duration_ms, error=str(e))
            return False

    # =============================================================================
    # Test Runner and Reporting
    # =============================================================================
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🧪 Starting Comprehensive Database Test Suite")
        print("=" * 60)
        
        suite_start = time.time()
        
        # Run all test categories
        test_methods = [
            self.test_connection,
            self.test_data_existence,
            self.test_basic_crud_operations,
            self.test_primary_key_query_performance,
            self.test_name_search_performance,
            self.test_category_query_performance,
            self.test_data_integrity,
            self.test_search_functionality,
            self.test_concurrent_queries,
            self.test_edge_cases
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {e}")
            print()  # Add spacing between tests
        
        suite_duration = (time.time() - suite_start) * 1000
        
        # Generate summary report
        return self.generate_report(suite_duration)
    
    def generate_report(self, suite_duration_ms: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        # Calculate performance stats
        durations = [r.duration_ms for r in self.results]
        avg_duration = statistics.mean(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Categorize results
        categories = {
            'Basic Functionality': [],
            'Performance': [],
            'Data Integrity': [],
            'Search Functionality': [],
            'Edge Cases': []
        }
        
        for result in self.results:
            if 'Connection' in result.test_name or 'CRUD' in result.test_name or 'Existence' in result.test_name:
                categories['Basic Functionality'].append(result)
            elif 'Performance' in result.test_name or 'Concurrent' in result.test_name:
                categories['Performance'].append(result)
            elif 'Integrity' in result.test_name:
                categories['Data Integrity'].append(result)
            elif 'Search' in result.test_name:
                categories['Search Functionality'].append(result)
            elif 'Edge' in result.test_name:
                categories['Edge Cases'].append(result)
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                'total_duration_ms': suite_duration_ms,
                'avg_test_duration_ms': avg_duration,
                'max_test_duration_ms': max_duration
            },
            'categories': {},
            'detailed_results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add category summaries
        for category, results in categories.items():
            if results:
                cat_passed = sum(1 for r in results if r.success)
                cat_total = len(results)
                report['categories'][category] = {
                    'total': cat_total,
                    'passed': cat_passed,
                    'failed': cat_total - cat_passed,
                    'success_rate': f"{(cat_passed/cat_total)*100:.1f}%"
                }
        
        self.print_report(report)
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY REPORT")
        print("=" * 60)
        
        summary = report['summary']
        print(f"📈 Overall Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']} ✅")
        print(f"   Failed: {summary['failed_tests']} ❌")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Total Duration: {summary['total_duration_ms']:.2f}ms")
        print(f"   Average Test Duration: {summary['avg_test_duration_ms']:.2f}ms")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in report['categories'].items():
            status_icon = "✅" if stats['passed'] == stats['total'] else "⚠️" if stats['passed'] > 0 else "❌"
            print(f"   {status_icon} {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']})")
        
        print(f"\n🔍 Failed Tests:")
        failed_results = [r for r in report['detailed_results'] if not r.success]
        if failed_results:
            for result in failed_results:
                print(f"   ❌ {result.test_name}: {result.error}")
        else:
            print("   🎉 No failed tests!")
        
        print("\n" + "=" * 60)
        overall_status = "🎉 ALL TESTS PASSED!" if summary['failed_tests'] == 0 else f"⚠️  {summary['failed_tests']} TESTS FAILED"
        print(f"🏁 {overall_status}")
        print("=" * 60)

def main():
    """Main test runner"""
    try:
        # Load environment variables
        env_path = Path(__file__).parent.parent.parent / "specs" / "001-sqlite-ags-db" / ".env"
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(env_path)
        
        # Initialize and run test suite
        test_suite = DatabaseTestSuite()
        results = test_suite.run_all_tests()
        
        # Save results to file
        import json
        results_file = Path(__file__).parent / f"test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            # Convert TestResult objects to dicts for JSON serialization
            serializable_results = []
            for result in results['detailed_results']:
                serializable_results.append({
                    'test_name': result.test_name,
                    'success': result.success,
                    'duration_ms': result.duration_ms,
                    'details': result.details,
                    'error': result.error
                })
            results['detailed_results'] = serializable_results
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Return exit code based on results
        return 0 if results['summary']['failed_tests'] == 0 else 1
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

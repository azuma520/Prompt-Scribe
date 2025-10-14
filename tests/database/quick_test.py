#!/usr/bin/env python3
"""
🚀 Quick Database Test for Prompt-Scribe Supabase Database

A simplified test script for quick validation of database functionality.
Perfect for daily checks and CI/CD integration.
"""

import os
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from supabase import create_client, Client
except ImportError:
    print("Missing supabase dependency. Install with: pip install supabase")
    sys.exit(1)

class QuickDatabaseTest:
    """Quick database test runner"""
    
    def __init__(self):
        # Load environment variables
        env_path = project_root / "specs" / "001-sqlite-ags-db" / ".env"
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except ImportError:
                print("python-dotenv not installed. Using system environment variables.")
        
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not all([self.supabase_url, self.supabase_key]):
            print("Missing Supabase credentials in environment variables")
            print("Required: SUPABASE_URL, SUPABASE_ANON_KEY")
            sys.exit(1)
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        self.tests_passed = 0
        self.tests_failed = 0

    def run_test(self, test_name: str, test_func):
        """Run a single test and track results"""
        print(f"Testing {test_name}...", end=" ")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = (time.time() - start_time) * 1000
            
            if result:
                print(f"PASS ({duration:.1f}ms)")
                self.tests_passed += 1
            else:
                print(f"FAIL ({duration:.1f}ms)")
                self.tests_failed += 1
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"ERROR ({duration:.1f}ms): {str(e)[:50]}...")
            self.tests_failed += 1

    def test_connection(self) -> bool:
        """Test basic database connection"""
        response = self.client.table('tags_final').select('id').limit(1).execute()
        return len(response.data) > 0

    def test_record_count(self) -> bool:
        """Test total record count"""
        response = self.client.table('tags_final').select('id', count='exact').execute()
        expected_count = 140782
        actual_count = response.count
        
        if actual_count != expected_count:
            print(f"\n   Expected: {expected_count}, Got: {actual_count}")
            return False
        return True

    def test_basic_query(self) -> bool:
        """Test basic query functionality"""
        # Test name query
        response = self.client.table('tags_final').select('*').eq('name', '1girl').execute()
        if not response.data:
            return False
        
        # Test category query
        response = self.client.table('tags_final').select('*').eq('main_category', 'CHARACTER').limit(10).execute()
        return len(response.data) > 0

    def test_search_performance(self) -> bool:
        """Test search performance"""
        start_time = time.time()
        response = self.client.table('tags_final').select('*').ilike('name', '%girl%').limit(20).execute()
        duration = (time.time() - start_time) * 1000
        
        # Should complete in under 500ms and return results
        return duration < 500 and len(response.data) > 0

    def test_sorting_and_pagination(self) -> bool:
        """Test sorting and pagination"""
        # Test sorting by post_count
        response = self.client.table('tags_final').select('name', 'post_count').order('post_count', desc=True).limit(5).execute()
        
        if len(response.data) < 2:
            return False
        
        # Verify sorting
        for i in range(len(response.data) - 1):
            if response.data[i]['post_count'] < response.data[i + 1]['post_count']:
                return False
        
        return True

    def test_data_integrity(self) -> bool:
        """Test basic data integrity"""
        # Check for null names
        response = self.client.table('tags_final').select('id').is_('name', 'null').limit(1).execute()
        if response.data:
            return False
        
        # Check for negative post_counts
        response = self.client.table('tags_final').select('id').lt('post_count', 0).limit(1).execute()
        if response.data:
            return False
        
        return True

    def test_category_distribution(self) -> bool:
        """Test category distribution"""
        categories = ['CHARACTER', 'ACTION_POSE', 'THEME_CONCEPT', 'ADULT_CONTENT', 'ARTIST']
        
        for category in categories:
            response = self.client.table('tags_final').select('id', count='exact').eq('main_category', category).execute()
            if response.count == 0:
                print(f"\n   No records found for category: {category}")
                return False
        
        return True

    def run_all_tests(self):
        """Run all quick tests"""
        print("Starting Quick Database Test Suite")
        print("=" * 50)
        
        # Define test suite
        tests = [
            ("Database Connection", self.test_connection),
            ("Record Count", self.test_record_count),
            ("Basic Queries", self.test_basic_query),
            ("Search Performance", self.test_search_performance),
            ("Sorting & Pagination", self.test_sorting_and_pagination),
            ("Data Integrity", self.test_data_integrity),
            ("Category Distribution", self.test_category_distribution),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        print("\n" + "=" * 50)
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\nAll tests passed! Database is healthy.")
            return True
        else:
            print(f"\n{self.tests_failed} test(s) failed. Please check the database.")
            return False

def main():
    """Main test runner"""
    try:
        test_runner = QuickDatabaseTest()
        success = test_runner.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"\nCritical error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

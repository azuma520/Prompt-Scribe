#!/usr/bin/env python3
"""
🎯 Database Test Runner for Prompt-Scribe

Unified test runner that orchestrates all database tests including
comprehensive functionality, performance, and integrity tests.
"""

import os
import sys
import time
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import test modules
try:
    from tests.database.quick_test import QuickDatabaseTest
    from tests.database.performance_test import PerformanceTestSuite
    from tests.database.test_comprehensive import DatabaseTestSuite
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all test modules are available")
    sys.exit(1)

class DatabaseTestRunner:
    """Main test runner orchestrating all database tests"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'quick_test': None,
            'comprehensive_test': None,
            'performance_test': None,
            'summary': {}
        }
        
    def run_quick_test(self) -> bool:
        """Run quick database test"""
        print("🚀 Running Quick Database Test...")
        print("-" * 50)
        
        try:
            quick_test = QuickDatabaseTest()
            success = quick_test.run_all_tests()
            
            self.results['quick_test'] = {
                'success': success,
                'tests_passed': quick_test.tests_passed,
                'tests_failed': quick_test.tests_failed,
                'total_tests': quick_test.tests_passed + quick_test.tests_failed
            }
            
            return success
            
        except Exception as e:
            print(f"❌ Quick test failed: {e}")
            self.results['quick_test'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run comprehensive database test"""
        print("\n🧪 Running Comprehensive Database Test...")
        print("-" * 50)
        
        try:
            comprehensive_test = DatabaseTestSuite()
            results = comprehensive_test.run_all_tests()
            
            self.results['comprehensive_test'] = {
                'success': results['summary']['failed_tests'] == 0,
                'summary': results['summary'],
                'categories': results['categories']
            }
            
            return results['summary']['failed_tests'] == 0
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {e}")
            self.results['comprehensive_test'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def run_performance_test(self) -> bool:
        """Run performance test"""
        print("\n⚡ Running Performance Test...")
        print("-" * 50)
        
        try:
            performance_test = PerformanceTestSuite()
            performance_test.run_performance_suite()
            
            # Calculate performance summary
            if performance_test.results:
                avg_ops_per_sec = sum(r.operations_per_second for r in performance_test.results) / len(performance_test.results)
                avg_response_time = sum(r.avg_response_time_ms for r in performance_test.results) / len(performance_test.results)
                avg_success_rate = sum(r.success_rate for r in performance_test.results) / len(performance_test.results)
                
                # Performance is considered successful if avg response < 200ms and success rate > 95%
                performance_success = avg_response_time < 200 and avg_success_rate > 95
                
                self.results['performance_test'] = {
                    'success': performance_success,
                    'avg_ops_per_second': avg_ops_per_sec,
                    'avg_response_time_ms': avg_response_time,
                    'avg_success_rate': avg_success_rate,
                    'total_tests': len(performance_test.results)
                }
                
                return performance_success
            else:
                self.results['performance_test'] = {
                    'success': False,
                    'error': 'No performance results generated'
                }
                return False
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.results['performance_test'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 70)
        print("📊 FINAL DATABASE TEST REPORT")
        print("=" * 70)
        
        # Calculate overall success
        test_results = []
        if self.results['quick_test']:
            test_results.append(self.results['quick_test']['success'])
        if self.results['comprehensive_test']:
            test_results.append(self.results['comprehensive_test']['success'])
        if self.results['performance_test']:
            test_results.append(self.results['performance_test']['success'])
        
        overall_success = all(test_results) if test_results else False
        
        self.results['summary'] = {
            'overall_success': overall_success,
            'tests_run': len(test_results),
            'tests_passed': sum(test_results),
            'tests_failed': len(test_results) - sum(test_results)
        }
        
        # Print summary
        status_icon = "🎉" if overall_success else "⚠️"
        print(f"{status_icon} Overall Status: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
        print(f"📈 Test Suites: {self.results['summary']['tests_passed']}/{self.results['summary']['tests_run']} passed")
        
        # Quick test results
        if self.results['quick_test']:
            qt = self.results['quick_test']
            status = "✅ PASS" if qt['success'] else "❌ FAIL"
            print(f"\n🚀 Quick Test: {status}")
            if 'total_tests' in qt:
                print(f"   Individual Tests: {qt['tests_passed']}/{qt['total_tests']} passed")
        
        # Comprehensive test results
        if self.results['comprehensive_test']:
            ct = self.results['comprehensive_test']
            status = "✅ PASS" if ct['success'] else "❌ FAIL"
            print(f"\n🧪 Comprehensive Test: {status}")
            if 'summary' in ct:
                summary = ct['summary']
                print(f"   Individual Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
                print(f"   Success Rate: {summary['success_rate']}")
        
        # Performance test results
        if self.results['performance_test']:
            pt = self.results['performance_test']
            status = "✅ PASS" if pt['success'] else "❌ FAIL"
            print(f"\n⚡ Performance Test: {status}")
            if 'avg_response_time_ms' in pt:
                print(f"   Avg Response Time: {pt['avg_response_time_ms']:.1f}ms")
                print(f"   Avg Success Rate: {pt['avg_success_rate']:.1f}%")
                print(f"   Avg Ops/Second: {pt['avg_ops_per_second']:.1f}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if overall_success:
            print("   🎉 Database is performing excellently!")
            print("   ✅ All systems are ready for production use")
            print("   📈 Consider implementing monitoring for ongoing health checks")
        else:
            print("   ⚠️  Some tests failed - review the detailed results above")
            print("   🔧 Address any performance or functionality issues")
            print("   🔄 Re-run tests after making improvements")
        
        print("\n" + "=" * 70)
        print(f"🏁 Database Testing Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        return overall_success
    
    def save_results(self, output_file: str = None):
        """Save test results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"database_test_results_{timestamp}.json"
        
        output_path = Path(__file__).parent / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Test results saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return None

def main():
    """Main test runner with command line interface"""
    parser = argparse.ArgumentParser(description='Database Test Runner for Prompt-Scribe')
    parser.add_argument('--quick-only', action='store_true', help='Run only quick tests')
    parser.add_argument('--comprehensive-only', action='store_true', help='Run only comprehensive tests')
    parser.add_argument('--performance-only', action='store_true', help='Run only performance tests')
    parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Load environment variables
    env_path = project_root / "specs" / "001-sqlite-ags-db" / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            print("⚠️  python-dotenv not installed. Using system environment variables.")
    
    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or system environment variables.")
        return 1
    
    print("🎯 Database Test Runner Starting...")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Supabase URL: {os.getenv('SUPABASE_URL')}")
    
    runner = DatabaseTestRunner()
    overall_success = True
    
    try:
        # Determine which tests to run
        if args.quick_only:
            overall_success = runner.run_quick_test()
        elif args.comprehensive_only:
            overall_success = runner.run_comprehensive_test()
        elif args.performance_only:
            overall_success = runner.run_performance_test()
        else:
            # Run all tests by default
            quick_success = runner.run_quick_test()
            comprehensive_success = runner.run_comprehensive_test()
            performance_success = runner.run_performance_test()
            
            overall_success = quick_success and comprehensive_success and performance_success
        
        # Generate final report
        final_success = runner.generate_final_report()
        
        # Save results
        runner.save_results(args.output)
        
        return 0 if final_success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test runner interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Critical error in test runner: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

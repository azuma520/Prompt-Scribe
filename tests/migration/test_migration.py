#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T014: Test Complete Migration Flow
End-to-end test of migration process
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "migration"))

from migrate_to_supabase import MigrationOrchestrator


def test_small_batch_migration():
    """Test migration with small batch (50 records)"""
    print("=" * 60)
    print("[TEST] Small Batch Migration Test")
    print("=" * 60)
    print("Testing with 50 records to verify:")
    print("- SQLite reading")
    print("- Data transformation")
    print("- Batch uploading to Supabase")
    print("- Error handling")
    print()
    
    # Create orchestrator
    orchestrator = MigrationOrchestrator(
        env_path="specs/001-sqlite-ags-db/.env",
        dry_run=False
    )
    
    # Run migration with limit
    success = orchestrator.migrate(limit=50)
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] T014 PASSED: Small batch migration test successful!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review uploaded data in Supabase Dashboard")
        print("2. If test successful, run full migration:")
        print("   python src/migration/migrate_to_supabase.py")
        print()
        return True
    else:
        print("\n" + "=" * 60)
        print("[FAIL] T014 FAILED: Migration test failed")
        print("=" * 60)
        return False


def test_dry_run():
    """Test dry run mode"""
    print("\n" + "=" * 60)
    print("[TEST] Dry Run Test")
    print("=" * 60)
    
    orchestrator = MigrationOrchestrator(
        env_path="specs/001-sqlite-ags-db/.env",
        dry_run=True
    )
    
    success = orchestrator.migrate(limit=100)
    
    if success:
        print("[OK] Dry run completed successfully")
        return True
    else:
        print("[FAIL] Dry run failed")
        return False


if __name__ == "__main__":
    # Run tests
    print("=" * 60)
    print("[INFO] T014: Testing Complete Migration Flow")
    print("=" * 60)
    print()
    
    # Test 1: Dry run
    print("[Test 1] Dry run test...")
    test1_passed = test_dry_run()
    
    # Test 2: Small batch migration
    print("\n" + "=" * 60)
    print("[Test 2] Small batch migration (50 records)...")
    test2_passed = test_small_batch_migration()
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] Test Results")
    print("=" * 60)
    print(f"Test 1 (Dry run): {'PASS' if test1_passed else 'FAIL'}")
    print(f"Test 2 (Small batch): {'PASS' if test2_passed else 'FAIL'}")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("\n[SUCCESS] T014 completed: All migration tests passed!")
        sys.exit(0)
    else:
        print("\n[FAIL] Some tests failed")
        sys.exit(1)


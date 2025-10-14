#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T004: Validate local SQLite database
Check SQLite file integrity and data quality
"""

import sqlite3
import os


def validate_sqlite_database(db_path: str = "./stage1/output/tags.db"):
    """Validate SQLite database integrity"""
    
    print("=" * 60)
    print("[INFO] Validating SQLite Database")
    print("=" * 60)
    
    # Check file exists
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    print(f"[OK] Database file exists: {db_path}")
    print(f"[OK] File size: {file_size:.2f} MB")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check total record count
        cursor.execute("SELECT COUNT(*) FROM tags_final")
        total_count = cursor.fetchone()[0]
        print(f"[OK] Total records: {total_count:,}")
        
        # Check classified tags
        cursor.execute("SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL")
        classified_count = cursor.fetchone()[0]
        coverage_rate = (classified_count / total_count * 100) if total_count > 0 else 0
        print(f"[OK] Classified tags: {classified_count:,}")
        print(f"[OK] Classification coverage: {coverage_rate:.2f}%")
        
        # Check category distribution
        cursor.execute("""
            SELECT main_category, COUNT(*) as count 
            FROM tags_final 
            WHERE main_category IS NOT NULL 
            GROUP BY main_category 
            ORDER BY count DESC 
            LIMIT 5
        """)
        print("\n[INFO] TOP 5 Categories:")
        for category, count in cursor.fetchall():
            percentage = (count / classified_count * 100) if classified_count > 0 else 0
            print(f"   {category}: {count:,} ({percentage:.1f}%)")
        
        # Check TOP tags
        cursor.execute("""
            SELECT name, post_count, main_category 
            FROM tags_final 
            ORDER BY post_count DESC 
            LIMIT 5
        """)
        print("\n[INFO] TOP 5 Popular Tags:")
        for name, post_count, category in cursor.fetchall():
            print(f"   {name}: {post_count:,} uses [{category or 'Unclassified'}]")
        
        conn.close()
        
        # Acceptance criteria check
        print("\n" + "=" * 60)
        print("[INFO] Acceptance Criteria Check")
        print("=" * 60)
        
        checks = [
            ("Total record count", total_count == 140782, f"Expected: 140,782, Actual: {total_count:,}"),
            ("Coverage rate", coverage_rate >= 96.0, f"Expected: >= 96%, Actual: {coverage_rate:.2f}%"),
            ("Database readable", True, "Successfully connected and queried"),
        ]
        
        all_passed = True
        for check_name, passed, details in checks:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status}: {check_name}")
            print(f"   {details}")
            if not passed:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("[SUCCESS] T004 completed: SQLite database validation passed")
        else:
            print("[FAIL] T004 failed: Some validations did not pass")
        print("=" * 60)
        
        return all_passed
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


if __name__ == "__main__":
    validate_sqlite_database()

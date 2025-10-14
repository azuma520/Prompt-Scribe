#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T012: Data Validator Module
4-level validation system for migration integrity
"""

import os
import random
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlite_reader import SQLiteReader


class DataValidator:
    """4-level data validation system"""
    
    def __init__(self, env_path: str = "specs/001-sqlite-ags-db/.env"):
        """Initialize validator
        
        Args:
            env_path: Path to .env file
        """
        load_dotenv(env_path)
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.sqlite_path = os.getenv("SOURCE_DB_PATH", "./stage1/output/tags.db")
        
        # Create Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def level1_record_count_validation(self) -> Tuple[bool, str]:
        """Level 1: Validate total record count
        
        Returns:
            (passed, message)
        """
        print("\n[Level 1] Record Count Validation")
        print("-" * 60)
        
        try:
            # Get SQLite count
            with SQLiteReader(self.sqlite_path) as reader:
                sqlite_count = reader.get_total_count()
            
            # Get Supabase count
            response = self.supabase.table("tags_final").select("*", count="exact").execute()
            supabase_count = response.count
            
            print(f"SQLite count: {sqlite_count:,}")
            print(f"Supabase count: {supabase_count:,}")
            
            if sqlite_count == supabase_count:
                print("[PASS] Record counts match!")
                return True, f"Both databases have {sqlite_count:,} records"
            else:
                diff = abs(sqlite_count - supabase_count)
                print(f"[FAIL] Count mismatch: difference of {diff:,} records")
                return False, f"Difference: {diff:,} records"
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    def level2_sample_validation(self, sample_size: int = 100) -> Tuple[bool, str]:
        """Level 2: Validate sample data field-by-field
        
        Args:
            sample_size: Number of records to sample
            
        Returns:
            (passed, message)
        """
        print(f"\n[Level 2] Sample Validation ({sample_size} records)")
        print("-" * 60)
        
        try:
            # Get all tag names from SQLite
            with SQLiteReader(self.sqlite_path) as reader:
                all_tags = reader.read_batch(0, 1000)  # Get first 1000
            
            # Random sample
            sample_tags = random.sample(all_tags, min(sample_size, len(all_tags)))
            
            mismatches = []
            
            for tag in sample_tags:
                # Get from Supabase
                response = self.supabase.table("tags_final")\
                    .select("*")\
                    .eq("name", tag['name'])\
                    .execute()
                
                if not response.data:
                    mismatches.append(f"{tag['name']}: Not found in Supabase")
                    continue
                
                supabase_tag = response.data[0]
                
                # Compare fields
                fields_to_check = ['danbooru_cat', 'post_count', 'main_category', 'sub_category']
                for field in fields_to_check:
                    if tag.get(field) != supabase_tag.get(field):
                        mismatches.append(f"{tag['name']}.{field}: {tag.get(field)} != {supabase_tag.get(field)}")
            
            print(f"Checked: {len(sample_tags)} records")
            print(f"Mismatches: {len(mismatches)}")
            
            if mismatches:
                print("[FAIL] Found mismatches:")
                for mismatch in mismatches[:5]:  # Show first 5
                    print(f"  - {mismatch}")
                return False, f"{len(mismatches)} mismatches found"
            else:
                print("[PASS] All sampled records match!")
                return True, f"All {len(sample_tags)} samples validated"
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    def level3_statistics_validation(self) -> Tuple[bool, str]:
        """Level 3: Validate statistical distribution
        
        Returns:
            (passed, message)
        """
        print("\n[Level 3] Statistics Validation")
        print("-" * 60)
        
        try:
            # Get SQLite statistics
            with SQLiteReader(self.sqlite_path) as reader:
                cursor = reader.conn.cursor()
                cursor.execute("""
                    SELECT main_category, COUNT(*) as count
                    FROM tags_final
                    WHERE main_category IS NOT NULL
                    GROUP BY main_category
                    ORDER BY count DESC
                """)
                sqlite_dist = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get Supabase statistics using RPC
            response = self.supabase.rpc("get_category_statistics").execute()
            supabase_dist = {row['category']: row['tag_count'] for row in response.data}
            
            print("Category distribution comparison:")
            mismatches = []
            
            for category in sqlite_dist:
                sqlite_count = sqlite_dist.get(category, 0)
                supabase_count = supabase_dist.get(category, 0)
                diff = abs(sqlite_count - supabase_count)
                diff_pct = (diff / sqlite_count * 100) if sqlite_count > 0 else 0
                
                print(f"  {category}: SQLite={sqlite_count:,}, Supabase={supabase_count:,}, Diff={diff}")
                
                if diff_pct > 1.0:  # Allow 1% tolerance
                    mismatches.append(category)
            
            if mismatches:
                print(f"[FAIL] Distribution mismatch in: {mismatches}")
                return False, f"Mismatch in {len(mismatches)} categories"
            else:
                print("[PASS] Distribution matches!")
                return True, "All categories match"
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    def level4_constraints_validation(self) -> Tuple[bool, str]:
        """Level 4: Validate database constraints
        
        Returns:
            (passed, message)
        """
        print("\n[Level 4] Constraints Validation")
        print("-" * 60)
        
        try:
            # Use the RPC function we created
            response = self.supabase.rpc("check_data_integrity").execute()
            
            all_passed = True
            for check in response.data:
                status = "[PASS]" if check['result'] == 'PASS' else f"[{check['result']}]"
                print(f"{status} {check['check_name']}: {check['details']}")
                
                if check['result'] == 'FAIL':
                    all_passed = False
            
            if all_passed:
                print("[PASS] All constraints validated!")
                return True, "All checks passed"
            else:
                print("[FAIL] Some constraints failed")
                return False, "Constraint validation failed"
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    def validate_all(self) -> bool:
        """Run all 4 levels of validation
        
        Returns:
            True if all levels pass
        """
        print("=" * 60)
        print("[INFO] Running 4-Level Validation")
        print("=" * 60)
        
        results = []
        
        # Level 1: Record count
        passed, msg = self.level1_record_count_validation()
        results.append(("Level 1: Record Count", passed, msg))
        
        # Level 2: Sample data (only if Level 1 passes)
        if passed:
            passed, msg = self.level2_sample_validation(sample_size=100)
            results.append(("Level 2: Sample Data", passed, msg))
        
        # Level 3: Statistics (only if previous levels pass)
        if all(r[1] for r in results):
            passed, msg = self.level3_statistics_validation()
            results.append(("Level 3: Statistics", passed, msg))
        
        # Level 4: Constraints (only if previous levels pass)
        if all(r[1] for r in results):
            passed, msg = self.level4_constraints_validation()
            results.append(("Level 4: Constraints", passed, msg))
        
        # Summary
        print("\n" + "=" * 60)
        print("[INFO] Validation Summary")
        print("=" * 60)
        
        all_passed = True
        for level_name, passed, msg in results:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {level_name}: {msg}")
            if not passed:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("[SUCCESS] All validation levels passed!")
        else:
            print("[FAIL] Some validation levels failed")
        print("=" * 60)
        
        return all_passed


if __name__ == "__main__":
    validator = DataValidator()
    validator.validate_all()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T013: Complete Migration Flow
Integrate all modules for full migration process
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlite_reader import SQLiteReader
from batch_uploader import BatchUploader
from migration_logger import MigrationLogger
from validator import DataValidator


class MigrationOrchestrator:
    """Orchestrates the complete migration process"""
    
    def __init__(self, env_path: str = "specs/001-sqlite-ags-db/.env", dry_run: bool = False):
        """Initialize migration orchestrator
        
        Args:
            env_path: Path to .env file
            dry_run: If True, only simulate migration without uploading
        """
        load_dotenv(env_path)
        
        self.dry_run = dry_run
        self.sqlite_path = os.getenv("SOURCE_DB_PATH", "./stage1/output/tags.db")
        self.batch_size = int(os.getenv("BATCH_SIZE", "500"))
        
        # Initialize components
        self.reader = SQLiteReader(self.sqlite_path)
        self.uploader = BatchUploader(env_path)
        self.logger = MigrationLogger(env_path)
        self.validator = DataValidator(env_path)
    
    def migrate(self, limit: Optional[int] = None) -> bool:
        """Execute complete migration
        
        Args:
            limit: Limit number of records (for testing)
            
        Returns:
            True if migration successful
        """
        print("=" * 60)
        print("[INFO] Starting Complete Migration Process")
        print("=" * 60)
        print(f"Source: {self.sqlite_path}")
        print(f"Batch size: {self.batch_size}")
        print(f"Dry run: {self.dry_run}")
        if limit:
            print(f"Limit: {limit} records (test mode)")
        print()
        
        start_time = time.time()
        
        try:
            # Step 1: Connect to SQLite
            print("[Step 1] Connecting to SQLite...")
            if not self.reader.connect():
                print("[FAIL] Could not connect to SQLite")
                return False
            
            total_count = self.reader.get_total_count()
            print(f"[OK] Connected - {total_count:,} records found")
            
            # Step 2: Read data in batches
            print("\n[Step 2] Reading data from SQLite...")
            batches = []
            offset = 0
            records_to_process = limit if limit else total_count
            
            while offset < records_to_process:
                batch_limit = min(self.batch_size, records_to_process - offset)
                batch = self.reader.read_batch(offset, batch_limit)
                
                if not batch:
                    break
                
                batches.append(batch)
                offset += len(batch)
                
                if (len(batches) % 10 == 0):
                    print(f"[PROGRESS] Read {len(batches)} batches ({offset:,} records)")
            
            print(f"[OK] Read {len(batches)} batches ({offset:,} records total)")
            
            # Step 3: Upload batches to Supabase
            if self.dry_run:
                print("\n[Step 3] DRY RUN - Skipping upload")
            else:
                print("\n[Step 3] Uploading to Supabase...")
                result = self.uploader.upload_all(batches)
                
                print(f"[OK] Upload complete:")
                print(f"  Success: {result['success_count']}/{len(batches)} batches")
                print(f"  Failed: {result['failed_count']} batches")
                print(f"  Total uploaded: {result['total_uploaded']:,} records")
                
                if result['failed_count'] > 0:
                    print(f"[WARN] {result['failed_count']} batches failed")
                    print("Failed batches:", [b['batch_id'] for b in result['failed_batches'][:5]])
            
            # Step 4: Validate migration
            print("\n[Step 4] Validating migration...")
            if self.dry_run or limit:
                print("[SKIP] Validation skipped in test mode")
            else:
                validation_passed = self.validator.validate_all()
                
                if not validation_passed:
                    print("[FAIL] Validation failed")
                    return False
            
            # Step 5: Summary
            duration = time.time() - start_time
            print("\n" + "=" * 60)
            print("[SUCCESS] Migration Complete!")
            print("=" * 60)
            print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f"Records processed: {offset:,}")
            if not self.dry_run and not limit:
                print(f"Records validated: {offset:,}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            return False
        
        finally:
            self.reader.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Migrate SQLite to Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without uploading")
    parser.add_argument("--limit", type=int, help="Limit number of records (for testing)")
    parser.add_argument("--env", default="specs/001-sqlite-ags-db/.env", help="Path to .env file")
    
    args = parser.parse_args()
    
    orchestrator = MigrationOrchestrator(env_path=args.env, dry_run=args.dry_run)
    success = orchestrator.migrate(limit=args.limit)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T010: Batch Uploader Module
Upload batches to Supabase with retry and checkpoint support
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential


class BatchUploader:
    """Batch uploader for Supabase migration"""
    
    def __init__(self, env_path: str = "specs/001-sqlite-ags-db/.env"):
        """Initialize batch uploader
        
        Args:
            env_path: Path to .env file
        """
        load_dotenv(env_path)
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.batch_size = int(os.getenv("BATCH_SIZE", "500"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        # Create Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Checkpoint file
        self.checkpoint_file = Path("migration_checkpoint.json")
        self.checkpoint_data = self._load_checkpoint()
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load checkpoint data"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {"uploaded_batches": [], "last_offset": 0, "total_uploaded": 0}
    
    def _save_checkpoint(self):
        """Save checkpoint data"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint_data, f, indent=2)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def upload_batch(self, batch: List[Dict[str, Any]], batch_id: str) -> bool:
        """Upload a batch of records to Supabase
        
        Args:
            batch: List of records to upload
            batch_id: Unique batch identifier
            
        Returns:
            True if successful
        """
        if batch_id in self.checkpoint_data["uploaded_batches"]:
            print(f"[SKIP] Batch {batch_id} already uploaded")
            return True
        
        start_time = time.time()
        
        try:
            # Upsert batch using Supabase client (handles duplicates)
            response = self.supabase.table("tags_final").upsert(batch, on_conflict="name").execute()
            
            duration = time.time() - start_time
            
            # Log to migration_log
            self.supabase.table("migration_log").insert({
                "migration_batch": batch_id,
                "operation": "batch_upload",
                "records_affected": len(batch),
                "status": "success",
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration
            }).execute()
            
            # Update checkpoint
            self.checkpoint_data["uploaded_batches"].append(batch_id)
            self.checkpoint_data["total_uploaded"] += len(batch)
            self._save_checkpoint()
            
            print(f"[OK] Uploaded batch {batch_id}: {len(batch)} records in {duration:.2f}s")
            return True
            
        except Exception as e:
            # Log error
            self.supabase.table("migration_log").insert({
                "migration_batch": batch_id,
                "operation": "batch_upload",
                "records_affected": 0,
                "status": "failed",
                "error_message": str(e),
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": time.time() - start_time
            }).execute()
            
            print(f"[ERROR] Failed to upload batch {batch_id}: {e}")
            raise
    
    def upload_all(self, batches: List[List[Dict[str, Any]]], start_batch: int = 0) -> Dict[str, Any]:
        """Upload all batches
        
        Args:
            batches: List of batches to upload
            start_batch: Starting batch index
            
        Returns:
            Upload statistics
        """
        print("=" * 60)
        print("[INFO] Starting Batch Upload")
        print("=" * 60)
        print(f"Total batches: {len(batches)}")
        print(f"Starting from: batch {start_batch}")
        print(f"Already uploaded: {self.checkpoint_data['total_uploaded']} records")
        print()
        
        success_count = 0
        failed_batches = []
        
        for i, batch in enumerate(batches[start_batch:], start=start_batch):
            batch_id = f"batch_{i:04d}"
            
            try:
                if self.upload_batch(batch, batch_id):
                    success_count += 1
                    
                    # Progress update every 10 batches
                    if (i + 1) % 10 == 0:
                        progress = (i + 1) / len(batches) * 100
                        print(f"[PROGRESS] {i + 1}/{len(batches)} batches ({progress:.1f}%)")
                        
            except Exception as e:
                failed_batches.append({"batch_id": batch_id, "error": str(e)})
                print(f"[WARN] Batch {batch_id} failed after retries, continuing...")
        
        print("\n" + "=" * 60)
        print("[INFO] Batch Upload Complete")
        print("=" * 60)
        print(f"Successful: {success_count}/{len(batches)}")
        print(f"Failed: {len(failed_batches)}")
        print(f"Total uploaded: {self.checkpoint_data['total_uploaded']} records")
        
        return {
            "success_count": success_count,
            "failed_count": len(failed_batches),
            "failed_batches": failed_batches,
            "total_uploaded": self.checkpoint_data["total_uploaded"]
        }
    
    def reset_checkpoint(self):
        """Reset checkpoint (for testing)"""
        self.checkpoint_data = {"uploaded_batches": [], "last_offset": 0, "total_uploaded": 0}
        self._save_checkpoint()
        print("[INFO] Checkpoint reset")


def test_batch_uploader():
    """Test batch uploader with small batch"""
    print("=" * 60)
    print("[INFO] Testing Batch Uploader")
    print("=" * 60)
    
    from sqlite_reader import SQLiteReader
    
    # Read a small test batch
    with SQLiteReader() as reader:
        test_batch = reader.read_batch(0, 10)  # Just 10 records for testing
    
    print(f"[INFO] Read {len(test_batch)} test records")
    
    # Upload test batch
    uploader = BatchUploader()
    result = uploader.upload_batch(test_batch, "test_batch_001")
    
    if result:
        print("\n[SUCCESS] T010 test completed: Batch uploader working!")
    else:
        print("\n[FAIL] T010 test failed")


if __name__ == "__main__":
    test_batch_uploader()


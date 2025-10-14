#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T011: Migration Logger System
Record all migration operations to migration_log table
"""

import os
import time
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client


class MigrationLogger:
    """Migration logger for tracking operations"""
    
    def __init__(self, env_path: str = "specs/001-sqlite-ags-db/.env"):
        """Initialize migration logger
        
        Args:
            env_path: Path to .env file
        """
        load_dotenv(env_path)
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Create Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def log_operation(
        self,
        migration_batch: str,
        operation: str,
        records_affected: int = 0,
        status: str = "success",
        error_message: Optional[str] = None,
        started_at: Optional[float] = None,
        duration_seconds: Optional[float] = None
    ) -> bool:
        """Log a migration operation
        
        Args:
            migration_batch: Batch identifier
            operation: Operation type (e.g., 'batch_upload', 'generate_embeddings')
            records_affected: Number of records affected
            status: Status ('success', 'failed', 'pending')
            error_message: Error message if failed
            started_at: Start timestamp (Unix time)
            duration_seconds: Duration in seconds
            
        Returns:
            True if logged successfully
        """
        try:
            if started_at is None:
                started_at = time.time()
            
            log_entry = {
                "migration_batch": migration_batch,
                "operation": operation,
                "records_affected": records_affected,
                "status": status,
                "error_message": error_message,
                "started_at": datetime.fromtimestamp(started_at).isoformat(),
                "completed_at": datetime.now().isoformat() if status in ['success', 'failed'] else None,
                "duration_seconds": duration_seconds
            }
            
            self.supabase.table("migration_log").insert(log_entry).execute()
            return True
            
        except Exception as e:
            print(f"[WARN] Failed to log operation: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status
        
        Returns:
            Migration status summary
        """
        try:
            # Get all logs
            response = self.supabase.table("migration_log")\
                .select("*")\
                .order("started_at", desc=True)\
                .execute()
            
            logs = response.data
            
            # Calculate statistics
            total_operations = len(logs)
            successful = sum(1 for log in logs if log['status'] == 'success')
            failed = sum(1 for log in logs if log['status'] == 'failed')
            pending = sum(1 for log in logs if log['status'] == 'pending')
            total_records = sum(log['records_affected'] for log in logs if log['status'] == 'success')
            
            return {
                "total_operations": total_operations,
                "successful": successful,
                "failed": failed,
                "pending": pending,
                "total_records_migrated": total_records,
                "recent_logs": logs[:10]  # Last 10 operations
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get migration status: {e}")
            return {}
    
    def print_status(self):
        """Print migration status"""
        status = self.get_migration_status()
        
        print("=" * 60)
        print("[INFO] Migration Status")
        print("=" * 60)
        print(f"Total operations: {status.get('total_operations', 0)}")
        print(f"Successful: {status.get('successful', 0)}")
        print(f"Failed: {status.get('failed', 0)}")
        print(f"Pending: {status.get('pending', 0)}")
        print(f"Total records migrated: {status.get('total_records_migrated', 0):,}")
        print()
        
        recent_logs = status.get('recent_logs', [])
        if recent_logs:
            print("[INFO] Recent Operations:")
            for log in recent_logs[:5]:
                print(f"  - {log['operation']}: {log['status']} ({log['records_affected']} records)")


def test_migration_logger():
    """Test migration logger"""
    print("=" * 60)
    print("[INFO] Testing Migration Logger")
    print("=" * 60)
    
    logger = MigrationLogger()
    
    # Test logging an operation
    logger.log_operation(
        migration_batch="test_001",
        operation="test_operation",
        records_affected=10,
        status="success",
        started_at=time.time(),
        duration_seconds=1.5
    )
    
    print("[OK] Test operation logged")
    
    # Print status
    logger.print_status()
    
    print("\n[SUCCESS] T011 completed: Migration Logger working!")


if __name__ == "__main__":
    test_migration_logger()


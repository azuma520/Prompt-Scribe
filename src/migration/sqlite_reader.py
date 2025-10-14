#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T009: SQLite Data Reader Module
Read and transform data from SQLite database
"""

import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid


class SQLiteReader:
    """SQLite database reader for tags.db"""
    
    def __init__(self, db_path: str = "./stage1/output/tags.db"):
        """Initialize SQLite reader
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> bool:
        """Connect to SQLite database
        
        Returns:
            True if connection successful
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to database: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_total_count(self) -> int:
        """Get total number of tags
        
        Returns:
            Total record count
        """
        if not self.conn:
            return 0
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tags_final")
        return cursor.fetchone()[0]
    
    def read_batch(self, offset: int, limit: int = 500) -> List[Dict[str, Any]]:
        """Read a batch of tags from database
        
        Args:
            offset: Starting offset
            limit: Number of records to read
            
        Returns:
            List of tag records as dictionaries
        """
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                name,
                danbooru_cat,
                post_count,
                main_category,
                sub_category,
                classification_confidence,
                classification_source
            FROM tags_final
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        records = []
        for row in cursor.fetchall():
            # Transform to Supabase format (remove id - let Supabase auto-generate)
            record = {
                'name': row['name'],
                'danbooru_cat': row['danbooru_cat'],
                'post_count': row['post_count'],
                'main_category': row['main_category'],
                'sub_category': row['sub_category'],
                'confidence': row['classification_confidence'],  # Map to Supabase field name
                'classification_source': row['classification_source'],
            }
            records.append(record)
        
        return records
    
    def read_all(self, batch_size: int = 500) -> List[List[Dict[str, Any]]]:
        """Read all tags in batches
        
        Args:
            batch_size: Size of each batch
            
        Yields:
            Batches of tag records
        """
        if not self.conn:
            return
        
        total_count = self.get_total_count()
        offset = 0
        
        while offset < total_count:
            batch = self.read_batch(offset, batch_size)
            if not batch:
                break
            
            yield batch
            offset += batch_size
    
    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a single tag by name
        
        Args:
            name: Tag name
            
        Returns:
            Tag record or None if not found
        """
        if not self.conn:
            return None
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                name,
                danbooru_cat,
                post_count,
                main_category,
                sub_category,
                classification_confidence,
                classification_source
            FROM tags_final
            WHERE name = ?
        """, (name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': str(uuid.uuid4()),
            'name': row['name'],
            'danbooru_cat': row['danbooru_cat'],
            'post_count': row['post_count'],
            'main_category': row['main_category'],
            'sub_category': row['sub_category'],
            'confidence': row['classification_confidence'],
            'classification_source': row['classification_source'],
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def test_sqlite_reader():
    """Test SQLite reader"""
    print("=" * 60)
    print("[INFO] Testing SQLite Reader")
    print("=" * 60)
    
    with SQLiteReader() as reader:
        # Test connection
        total = reader.get_total_count()
        print(f"[OK] Total records: {total:,}")
        
        # Test read single record
        tag = reader.get_tag_by_name("1girl")
        if tag:
            print(f"[OK] Read single tag: {tag['name']}")
            print(f"     Category: {tag['main_category']}")
            print(f"     Post count: {tag['post_count']:,}")
        
        # Test read batch
        batch = reader.read_batch(0, 10)
        print(f"[OK] Read batch: {len(batch)} records")
        
        for i, tag in enumerate(batch[:3], 1):
            print(f"     {i}. {tag['name']} ({tag['main_category']})")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] T009 completed: SQLite Reader Module")
    print("=" * 60)


if __name__ == "__main__":
    test_sqlite_reader()


#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('output/tags.db')

# 檢查 medium_freq_llm_batch 處理的標籤數
result = conn.execute('''
    SELECT COUNT(*), SUM(post_count)
    FROM tags_final 
    WHERE classification_source = "medium_freq_llm_batch"
''').fetchone()

count, usage = result
print(f"medium_freq_llm_batch 處理進度:")
print(f"  已處理標籤: {count} 個")
print(f"  影響使用次數: {usage:,} 次")

# 整體進度
total = conn.execute('SELECT COUNT(*) FROM tags_final').fetchone()[0]
classified = conn.execute('SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL').fetchone()[0]
coverage = classified / total * 100

print(f"\n整體覆蓋率: {coverage:.2f}%")

conn.close()


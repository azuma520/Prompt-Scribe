#!/usr/bin/env python3
"""
測試 Supabase 連接和 Session 創建
"""

import sys
import os
sys.path.append('src/api')

# 設置環境變數
os.environ['SUPABASE_URL'] = 'https://fumuvmbhmmzkenizksyq.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1bXV2bWJobW16a2VuaXprc3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAzMTg2OTAsImV4cCI6MjA3NTg5NDY5MH0.zQn4miaoW1wpwVYFHWhZLaapfOcfOrsKOGjkMqDS7lo'

try:
    from services.inspire_db_wrapper import InspireDBWrapper
    import uuid
    
    print("Testing Supabase connection and Session creation...")
    
    # 創建資料庫封裝層
    db = InspireDBWrapper()
    print("InspireDBWrapper created successfully")
    
    # 生成測試 Session ID
    test_session_id = str(uuid.uuid4())
    print(f"Test Session ID: {test_session_id}")
    
    # 測試創建 Session
    print("Creating Session...")
    create_result = db.create_session(test_session_id, user_access_level="all-ages")
    print(f"Create result: {create_result}")
    
    # 測試查詢 Session
    print("Querying Session...")
    get_result = db.get_session(test_session_id)
    print(f"Query result: {get_result}")
    
    if get_result:
        print("Session creation and query successful!")
    else:
        print("Session query failed")
        
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()

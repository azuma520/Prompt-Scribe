#!/usr/bin/env python3
"""
簡化的後端服務器啟動腳本
解決導入路徑問題
"""
import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 設置環境變數
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_ANON_KEY'] = 'test-key'
os.environ['OPENAI_API_KEY'] = 'test-key'

# 導入並啟動應用
if __name__ == "__main__":
    import uvicorn
    from api.main import app
    
    print("🚀 啟動 Prompt-Scribe 後端服務器...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


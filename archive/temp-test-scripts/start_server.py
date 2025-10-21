"""
啟動 Prompt-Scribe API 伺服器
"""

import sys
import os
import uvicorn

# 確保在正確的目錄
os.chdir(os.path.join(os.path.dirname(__file__), 'src', 'api'))

print("=" * 60)
print("🚀 啟動 Prompt-Scribe API 伺服器")
print("=" * 60)
print(f"📍 工作目錄: {os.getcwd()}")
print(f"🐍 Python 版本: {sys.version}")
print()

# 檢查必要文件
if not os.path.exists('main.py'):
    print("❌ 錯誤: main.py 不存在")
    sys.exit(1)

if not os.path.exists('config.py'):
    print("❌ 錯誤: config.py 不存在")
    sys.exit(1)

print("✅ 必要文件檢查通過")
print()

# 測試導入
try:
    print("🔍 測試模組導入...")
    from config import settings
    print("✅ config 導入成功")
    
    from fastapi import FastAPI
    print("✅ FastAPI 導入成功")
    
    from routers.v1 import tags
    print("✅ 路由導入成功")
    
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

print()
print("🎯 啟動伺服器...")
print("📡 地址: http://127.0.0.1:8000")
print("📚 文檔: http://127.0.0.1:8000/docs")
print("🔧 健康檢查: http://127.0.0.1:8000/health")
print()
print("按 Ctrl+C 停止伺服器")
print("=" * 60)

# 啟動伺服器
uvicorn.run(
    "main:app",
    host="127.0.0.1",
    port=8000,
    reload=True,
    log_level="info"
)

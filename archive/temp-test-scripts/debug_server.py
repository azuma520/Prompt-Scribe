"""
調試伺服器啟動問題
"""

import sys
import os

# 添加路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

print("🔍 調試伺服器啟動問題...")
print(f"Python 路徑: {sys.executable}")
print(f"工作目錄: {os.getcwd()}")
print(f"Python 路徑列表: {sys.path[:3]}...")
print()

try:
    print("1. 測試導入 config...")
    from config import settings
    print("✅ config 導入成功")
    print(f"   - API 前綴: {settings.api_prefix}")
    print(f"   - 日誌級別: {settings.log_level}")
except Exception as e:
    print(f"❌ config 導入失敗: {e}")

try:
    print("\n2. 測試導入 FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI 導入成功")
except Exception as e:
    print(f"❌ FastAPI 導入失敗: {e}")

try:
    print("\n3. 測試導入路由...")
    from routers.v1 import tags, search, statistics
    print("✅ 路由導入成功")
except Exception as e:
    print(f"❌ 路由導入失敗: {e}")

try:
    print("\n4. 測試創建 FastAPI 應用...")
    app = FastAPI(title="Prompt-Scribe API", version="1.0.0")
    print("✅ FastAPI 應用創建成功")
except Exception as e:
    print(f"❌ FastAPI 應用創建失敗: {e}")

print("\n🔍 檢查文件結構...")
api_dir = os.path.join(os.path.dirname(__file__), 'src', 'api')
if os.path.exists(api_dir):
    print(f"✅ API 目錄存在: {api_dir}")
    files = os.listdir(api_dir)
    print(f"   文件列表: {files[:5]}...")
else:
    print(f"❌ API 目錄不存在: {api_dir}")

print("\n🎯 診斷完成")

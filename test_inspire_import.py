"""
快速測試 Inspire Agent 組件導入

檢查所有組件是否能正常導入和初始化。
"""

import sys
import os

# 確保能找到 src/api 模組
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

def test_imports():
    """測試所有導入"""
    print("=" * 60)
    print("  Inspire Agent 組件導入測試")
    print("=" * 60)
    print()
    
    # Test 1: System Prompt
    print("Test 1: 導入 System Prompt...")
    try:
        from prompts import get_system_prompt, INSPIRE_AGENT_SYSTEM_PROMPT
        prompt = get_system_prompt("full")
        print("[OK] System Prompt imported successfully")
        print(f"   Prompt 長度: {len(prompt)} 字元")
        print()
    except Exception as e:
        print(f"[FAIL] System Prompt import failed: {e}")
        return False
    
    # Test 2: Models
    print("Test 2: 導入 API 模型...")
    try:
        from models.inspire_models import (
            InspireStartRequest,
            InspireStartResponse,
            InspireSession,
        )
        print("[OK] API 模型導入成功")
        print(f"   - InspireStartRequest")
        print(f"   - InspireStartResponse")
        print(f"   - InspireSession")
        print()
    except Exception as e:
        print(f"[FAIL] API 模型導入失敗: {e}")
        return False
    
    # Test 3: Tools
    print("Test 3: 導入工具...")
    try:
        from tools.inspire_tools import (
            understand_intent,
            search_examples,
            generate_ideas,
            validate_quality,
            finalize_prompt,
            INSPIRE_TOOLS,
        )
        print("[OK] 工具導入成功")
        print(f"   總計: {len(INSPIRE_TOOLS)} 個工具")
        for tool in INSPIRE_TOOLS:
            print(f"   - {tool.name if hasattr(tool, 'name') else tool}")
        print()
    except Exception as e:
        print(f"[FAIL] 工具導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Session Manager
    print("Test 4: 導入 Session Manager...")
    try:
        from services.inspire_session_manager import get_session_manager
        manager = get_session_manager()
        info = manager.get_session_storage_info()
        print("[OK] Session Manager 導入成功")
        print(f"   環境: {info['environment']}")
        print(f"   存儲類型: {info['storage_type']}")
        print(f"   Redis 可用: {info['redis_available']}")
        print()
    except Exception as e:
        print(f"[FAIL] Session Manager 導入失敗: {e}")
        return False
    
    # Test 5: Router
    print("Test 5: 導入 API Router...")
    try:
        from routers.inspire_agent import router
        print("[OK] API Router 導入成功")
        print(f"   Prefix: {router.prefix}")
        print(f"   Routes: {len(router.routes)}")
        print()
    except Exception as e:
        print(f"[FAIL] API Router 導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Main App
    print("Test 6: 導入主應用...")
    try:
        from main import app
        print("[OK] 主應用導入成功")
        print(f"   總路由數: {len(app.routes)}")
        print()
    except Exception as e:
        print(f"[FAIL] 主應用導入失敗: {e}")
        return False
    
    print("=" * 60)
    print("  [OK] 所有組件導入成功!")
    print("=" * 60)
    print()
    
    return True


if __name__ == "__main__":
    success = test_imports()
    
    if success:
        print("[OK] 測試通過！可以繼續啟動伺服器")
        sys.exit(0)
    else:
        print("[FAIL] 測試失敗！請修復問題後再試")
        sys.exit(1)


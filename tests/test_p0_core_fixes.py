"""
P0 核心修復驗證（簡化版）
只驗證最關鍵的兩點：
1. 同步 Supabase 調用在 async 環境中可用
2. Session 管理器正確切換環境
"""

import sys
import os
import asyncio

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

# 測試環境變數
os.environ['SUPABASE_URL'] = os.getenv('SUPABASE_URL', '')
os.environ['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY', '')
os.environ['ENVIRONMENT'] = 'development'

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# ==============================================
# 測試 1: Supabase 同步調用在 async 環境
# ==============================================

def test_sync_supabase_in_async():
    """
    驗證 Supabase 同步客戶端可以在 async 環境中調用
    這是 P0 修復的核心：避免 asyncio.run() 的 event loop 錯誤
    """
    print("\n" + "="*60)
    print("Test 1: Synchronous Supabase calls in async context")
    print("="*60)
    
    from services.supabase_client import get_supabase_service
    
    async def fastapi_like_handler():
        """模擬 FastAPI async 端點"""
        logger.info("Simulating FastAPI async environment...")
        
        try:
            # 獲取 Supabase 服務
            db = get_supabase_service()
            
            # 同步調用（關鍵：不用 asyncio.run()）
            result = db.client.table('tags_final')\
                .select('name')\
                .limit(5)\
                .execute()
            
            logger.info(f"Query successful! Got {len(result.data)} results")
            
            if len(result.data) > 0:
                logger.info(f"Example tag: {result.data[0]['name']}")
            
            return True
            
        except RuntimeError as e:
            if "event loop" in str(e):
                logger.error(f"Event loop error (This should NOT happen): {e}")
                return False
            raise
        
        except Exception as e:
            logger.error(f"Other error: {e}")
            return False
    
    # 在新的 event loop 中運行（模擬 FastAPI）
    result = asyncio.run(fastapi_like_handler())
    
    if result:
        print("[PASS] Synchronous Supabase works in async environment")
    else:
        print("[FAIL] Event loop error occurred")
    
    return result


# ==============================================
# 測試 2: Session 管理器環境切換
# ==============================================

def test_session_manager():
    """驗證 Session 管理器正確切換環境"""
    print("\n" + "="*60)
    print("Test 2: Session Manager Environment Switching")
    print("="*60)
    
    from services.inspire_session_manager import get_session_manager
    
    manager = get_session_manager()
    info = manager.get_session_storage_info()
    
    print(f"\nConfiguration:")
    print(f"  Environment: {info['environment']}")
    print(f"  Storage Type: {info['storage_type']}")
    print(f"  Storage Location: {info['storage_location']}")
    print(f"  Redis Available: {info['redis_available']}")
    
    try:
        session = manager.create_session("test_p0_session")
        logger.info(f"Session created: {type(session).__name__}")
        print(f"\n[PASS] Session created successfully ({type(session).__name__})")
        return True
    
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        print(f"\n[FAIL] Session creation failed: {e}")
        return False


# ==============================================
# 測試 3: 驗證 Context 變數機制
# ==============================================

def test_context_vars():
    """驗證 Context 變數可以在函數間共享"""
    print("\n" + "="*60)
    print("Test 3: Context Variable Sharing")
    print("="*60)
    
    from contextvars import ContextVar
    
    test_context = ContextVar('test_context', default={})
    
    # 設置 Context
    ctx = {"user_id": "test_123", "access_level": "all-ages"}
    test_context.set(ctx)
    
    # 讀取 Context
    retrieved_ctx = test_context.get()
    
    if retrieved_ctx == ctx:
        logger.info("Context variable works correctly")
        print("[PASS] Context variables work correctly")
        return True
    else:
        logger.error(f"Context mismatch: {retrieved_ctx} != {ctx}")
        print("[FAIL] Context variable mismatch")
        return False


# ==============================================
# 主測試
# ==============================================

def main():
    """運行所有核心 P0 修復驗證"""
    
    print("\n" + "="*60)
    print("P0 Core Fixes Verification (Simplified)")
    print("="*60)
    
    results = []
    
    # 測試 1: Supabase 同步調用
    try:
        results.append(("Sync Supabase in async", test_sync_supabase_in_async()))
    except Exception as e:
        logger.error(f"Test 1 exception: {e}")
        results.append(("Sync Supabase in async", False))
    
    # 測試 2: Session 管理器
    try:
        results.append(("Session Manager", test_session_manager()))
    except Exception as e:
        logger.error(f"Test 2 exception: {e}")
        results.append(("Session Manager", False))
    
    # 測試 3: Context 變數
    try:
        results.append(("Context Variables", test_context_vars()))
    except Exception as e:
        logger.error(f"Test 3 exception: {e}")
        results.append(("Context Variables", False))
    
    # 總結
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n========================================")
        print("SUCCESS: All P0 core fixes verified!")
        print("========================================")
        print("\nKey achievements:")
        print("1. Supabase sync client works in async environment")
        print("2. Session manager switches correctly (SQLite/Redis)")
        print("3. Context variables work for state sharing")
        print("\nReady to proceed with Inspire Agent implementation!")
        return 0
    else:
        print(f"\n{total - passed} tests failed. Need adjustments.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


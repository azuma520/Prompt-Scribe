"""
P0 修復驗證測試
驗證：
1. 工具在 FastAPI async 環境中正常運行（無 event loop 錯誤）
2. Session 管理器正確切換 SQLite/Redis
"""

import sys
import os
import asyncio

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

# 測試環境變數
os.environ['SUPABASE_URL'] = os.getenv('SUPABASE_URL', '')
os.environ['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY', '')
os.environ['ENVIRONMENT'] = 'development'  # 測試環境

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# ==============================================
# 測試 1: 工具在 async 環境中運行
# ==============================================

def test_tools_in_async_context():
    """
    測試工具在 async 環境中運行（模擬 FastAPI）
    關鍵：不應出現 "event loop already running" 錯誤
    """
    print("\n" + "="*60)
    print("測試 1: 工具在 async 環境中運行")
    print("="*60)
    
    from tools.inspire_tools import search_examples
    
    async def fastapi_like_handler():
        """模擬 FastAPI async 端點"""
        logger.info("模擬 FastAPI async 環境...")
        
        # 調用工具（同步函數，但在 async context 中）
        try:
            result = search_examples(
                search_keywords=["moonlight", "night"],
                search_purpose="find_mood_tags",
                min_popularity=5000,
                max_results=5
            )
            
            logger.info(f"成功！找到 {result['found']} 個結果")
            
            if result['found'] > 0:
                logger.info(f"範例標籤: {result['examples'][0]['tag']}")
            
            return True
            
        except RuntimeError as e:
            if "event loop" in str(e):
                logger.error(f"Event loop error: {e}")
                return False
            raise
        
        except Exception as e:
            logger.error(f"其他錯誤: {e}")
            return False
    
    # 在新的 event loop 中運行（模擬 FastAPI）
    result = asyncio.run(fastapi_like_handler())
    
    if result:
        print("[PASS] Tools work correctly in async environment")
    else:
        print("[FAIL] Event loop error occurred")
    
    return result


# ==============================================
# 測試 2: Session 管理器環境切換
# ==============================================

def test_session_manager():
    """
    測試 Session 管理器的環境切換
    """
    print("\n" + "="*60)
    print("測試 2: Session 管理器環境切換")
    print("="*60)
    
    from services.inspire_session_manager import get_session_manager
    
    manager = get_session_manager()
    
    # 獲取配置資訊
    info = manager.get_session_storage_info()
    
    print(f"\n當前配置:")
    print(f"  環境: {info['environment']}")
    print(f"  存儲類型: {info['storage_type']}")
    print(f"  存儲位置: {info['storage_location']}")
    print(f"  Redis 可用: {info['redis_available']}")
    
    # 創建 session
    try:
        session = manager.create_session("test_session_123")
        logger.info(f"Session created successfully: {type(session).__name__}")
        print(f"\n[PASS] Session created successfully ({type(session).__name__})")
        return True
    
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        print(f"\n[FAIL] Session creation failed: {e}")
        return False


# ==============================================
# 測試 3: 完整工具調用（無 Context 錯誤）
# ==============================================

def test_full_tool_pipeline():
    """
    測試完整工具調用流程
    驗證 Context 變數在工具間共享
    """
    print("\n" + "="*60)
    print("測試 3: 完整工具調用流程")
    print("="*60)
    
    from tools.inspire_tools import (
        understand_intent,
        generate_ideas,
        session_context
    )
    
    # 設置初始 Context
    ctx = {"user_access_level": "all-ages"}
    session_context.set(ctx)
    
    try:
        # 調用工具 1
        result1 = understand_intent(
            core_mood="dreamy",
            visual_elements=["moonlight", "girl", "night_sky"],
            style_preference="anime",
            clarity_level="mostly_clear",
            confidence=0.85,
            next_action="generate_directly"
        )
        
        logger.info(f"understand_intent 成功: {result1['status']}")
        
        # 檢查 Context 更新
        ctx = session_context.get()
        if "extracted_intent" not in ctx:
            raise ValueError("Context 未更新")
        
        logger.info(f"Context 已更新: {ctx.keys()}")
        
        # 調用工具 2（應該能讀取 Context）
        result2 = generate_ideas(
            ideas=[
                {
                    "title": "月下獨舞",
                    "concept": "優雅的少女在月光下獨舞",
                    "vibe": "dreamy, elegant",
                    "main_tags": [
                        "1girl", "solo", "moonlight", "night_sky", "dancing",
                        "elegant", "dreamy", "white_dress", "stars", "graceful",
                        "ethereal", "soft_glow"
                    ],
                    "quick_preview": "1girl, moonlight, dancing, dreamy",
                    "uniqueness": "強調孤獨的詩意美"
                }
            ],
            generation_basis="Based on user intent",
            diversity_achieved="moderate"
        )
        
        logger.info(f"generate_ideas success: {result2['status']}")
        
        print("\n[PASS] Full tool pipeline works correctly")
        return True
    
    except Exception as e:
        logger.error(f"Tool invocation failed: {e}")
        print(f"\n[FAIL] Test failed: {e}")
        return False


# ==============================================
# 主測試
# ==============================================

def main():
    """運行所有 P0 修復驗證測試"""
    
    print("\n" + "="*60)
    print("P0 Critical Fixes Verification Tests")
    print("="*60)
    
    results = []
    
    # 測試 1
    try:
        results.append(("工具在 async 環境", test_tools_in_async_context()))
    except Exception as e:
        logger.error(f"測試 1 異常: {e}")
        results.append(("工具在 async 環境", False))
    
    # 測試 2
    try:
        results.append(("Session 管理器", test_session_manager()))
    except Exception as e:
        logger.error(f"測試 2 異常: {e}")
        results.append(("Session 管理器", False))
    
    # 測試 3
    try:
        results.append(("完整工具流程", test_full_tool_pipeline()))
    except Exception as e:
        logger.error(f"測試 3 異常: {e}")
        results.append(("完整工具流程", False))
    
    # 總結
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\nAll P0 fixes verified! Ready to continue development.")
        return 0
    else:
        print(f"\n{total - passed} tests failed. Need further adjustments.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


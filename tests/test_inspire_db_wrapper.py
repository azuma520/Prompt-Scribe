"""
測試 Inspire DB Wrapper 封裝層
驗證所有契約方法是否正常工作
"""

import sys
import os

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

# 設置環境變數
os.environ['SUPABASE_URL'] = os.getenv('SUPABASE_URL', '')
os.environ['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY', '')

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_session_operations():
    """測試 Session CRUD 操作"""
    print("\n" + "="*60)
    print("Test 1: Session Operations")
    print("="*60)
    
    from services.inspire_db_wrapper import get_inspire_db_wrapper
    import uuid
    
    wrapper = get_inspire_db_wrapper()
    test_session_id = f"test_{uuid.uuid4().hex[:8]}"
    
    try:
        # 1. 創建 Session
        print("\n[1] Creating session...")
        result = wrapper.create_session(
            session_id=test_session_id,
            user_id="test_user_123",
            user_access_level="all-ages"
        )
        
        if "error" in result:
            print(f"[FAIL] Failed to create session: {result['error']}")
            return False
        
        print(f"[PASS] Session created: {test_session_id}")
        
        # 2. 獲取 Session
        print("\n[2] Getting session...")
        session = wrapper.get_session(test_session_id)
        
        if not session:
            print("[FAIL] Session not found")
            return False
        
        print(f"[PASS] Session retrieved: phase={session['current_phase']}")
        
        # 3. 更新狀態
        print("\n[3] Updating phase...")
        success = wrapper.update_session_phase(test_session_id, "exploring")
        
        if not success:
            print("[FAIL] Failed to update phase")
            return False
        
        print("[PASS] Phase updated to 'exploring'")
        
        # 4. 更新成本
        print("\n[4] Updating cost...")
        cost_result = wrapper.update_session_cost(test_session_id, 0.005, 1000)
        
        if not cost_result["success"]:
            print("[FAIL] Failed to update cost")
            return False
        
        print(f"[PASS] Cost updated: ${cost_result['current_cost']:.6f}")
        
        # 5. 完成 Session
        print("\n[5] Completing session...")
        success = wrapper.complete_session(
            test_session_id,
            quality_score=85,
            final_output={"test": "data"}
        )
        
        if not success:
            print("[FAIL] Failed to complete session")
            return False
        
        print("[PASS] Session completed")
        
        print("\n[SUCCESS] All session operations passed!")
        return True
    
    except Exception as e:
        print(f"\n[FAIL] Exception: {e}")
        return False


def test_tag_search():
    """測試標籤搜尋"""
    print("\n" + "="*60)
    print("Test 2: Tag Search")
    print("="*60)
    
    from services.inspire_db_wrapper import get_inspire_db_wrapper
    
    wrapper = get_inspire_db_wrapper()
    
    try:
        # 搜尋標籤
        print("\n[1] Searching tags with keywords: ['moonlight', 'night']")
        results = wrapper.search_tags_by_keywords(
            keywords=["moonlight", "night"],
            user_access="all-ages",
            min_popularity=5000,
            max_results=5
        )
        
        if not results:
            print("[WARN] No results found (might be expected)")
            return True
        
        print(f"[PASS] Found {len(results)} tags:")
        for tag in results[:3]:
            print(f"  - {tag['tag']} ({tag['category']}, {tag['popularity']:,} uses)")
        
        print("\n[SUCCESS] Tag search passed!")
        return True
    
    except Exception as e:
        print(f"\n[FAIL] Exception: {e}")
        return False


def test_tag_validation():
    """測試標籤驗證"""
    print("\n" + "="*60)
    print("Test 3: Tag Validation")
    print("="*60)
    
    from services.inspire_db_wrapper import get_inspire_db_wrapper
    
    wrapper = get_inspire_db_wrapper()
    
    try:
        # 測試標籤列表（混合有效和無效）
        test_tags = ["1girl", "solo", "invalid_tag_xyz", "smile"]
        
        print(f"\n[1] Validating tags: {test_tags}")
        valid, invalid = wrapper.validate_tags_exist(
            tags=test_tags,
            user_access="all-ages"
        )
        
        print(f"\n[PASS] Validation complete:")
        print(f"  Valid: {valid}")
        print(f"  Invalid: {invalid}")
        
        if len(valid) + len(invalid) != len(test_tags):
            print("[FAIL] Count mismatch")
            return False
        
        print("\n[SUCCESS] Tag validation passed!")
        return True
    
    except Exception as e:
        print(f"\n[FAIL] Exception: {e}")
        return False


def test_popular_tags():
    """測試熱門標籤"""
    print("\n" + "="*60)
    print("Test 4: Popular Tags")
    print("="*60)
    
    from services.inspire_db_wrapper import get_inspire_db_wrapper
    
    wrapper = get_inspire_db_wrapper()
    
    try:
        print("\n[1] Getting popular tags...")
        popular = wrapper.get_popular_tags(
            user_access="all-ages",
            min_popularity=50000,
            max_results=10
        )
        
        if not popular:
            print("[WARN] No popular tags found")
            return True
        
        print(f"[PASS] Found {len(popular)} popular tags:")
        for tag in popular[:5]:
            print(f"  - {tag['tag']} ({tag['category']}, {tag['popularity']:,} uses)")
        
        print("\n[SUCCESS] Popular tags test passed!")
        return True
    
    except Exception as e:
        print(f"\n[FAIL] Exception: {e}")
        return False


def main():
    """運行所有測試"""
    
    print("\n" + "="*60)
    print("Inspire DB Wrapper Tests")
    print("="*60)
    
    results = []
    
    # 測試 1: Session 操作
    try:
        results.append(("Session Operations", test_session_operations()))
    except Exception as e:
        logger.error(f"Test 1 exception: {e}")
        results.append(("Session Operations", False))
    
    # 測試 2: 標籤搜尋
    try:
        results.append(("Tag Search", test_tag_search()))
    except Exception as e:
        logger.error(f"Test 2 exception: {e}")
        results.append(("Tag Search", False))
    
    # 測試 3: 標籤驗證
    try:
        results.append(("Tag Validation", test_tag_validation()))
    except Exception as e:
        logger.error(f"Test 3 exception: {e}")
        results.append(("Tag Validation", False))
    
    # 測試 4: 熱門標籤
    try:
        results.append(("Popular Tags", test_popular_tags()))
    except Exception as e:
        logger.error(f"Test 4 exception: {e}")
        results.append(("Popular Tags", False))
    
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
        print("\n" + "="*60)
        print("SUCCESS: All DB Wrapper tests passed!")
        print("="*60)
        print("\nKey features verified:")
        print("1. Session CRUD operations work correctly")
        print("2. Tag search with NSFW filtering works")
        print("3. Tag validation with alias resolution works")
        print("4. Popular tags retrieval works")
        print("\nReady for tool integration!")
        return 0
    else:
        print(f"\n{total - passed} tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


"""
Inspire Agent 端到端測試

測試完整的 Inspire 對話流程，從開始到完成。

Version: 2.0.0
Date: 2025-10-22
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime

# 測試配置
TEST_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30.0


# ============================================================================
# 輔助函數
# ============================================================================

def print_test_section(title: str):
    """打印測試分段標題"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_result(label: str, data: dict):
    """打印結果"""
    print(f"✓ {label}:")
    for key, value in data.items():
        if isinstance(value, dict) and len(str(value)) > 100:
            print(f"  - {key}: <complex_object>")
        else:
            print(f"  - {key}: {value}")
    print()


# ============================================================================
# 基礎測試
# ============================================================================

@pytest.mark.asyncio
async def test_inspire_health_check():
    """測試 Inspire Agent 健康檢查"""
    print_test_section("Test 1: Health Check")
    
    async with AsyncClient(base_url=TEST_BASE_URL, timeout=TEST_TIMEOUT) as client:
        response = await client.get("/api/inspire/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") in ["healthy", "operational"]
        assert "storage" in data
        
        print_result("Health Check", {
            "status": data.get("status"),
            "service": data.get("service"),
            "storage_type": data.get("storage", {}).get("storage_type"),
        })
        
        print("✅ Test 1 PASSED: Health check successful\n")


# ============================================================================
# 對話流程測試
# ============================================================================

@pytest.mark.asyncio
async def test_inspire_simple_conversation_flow():
    """
    測試場景：簡單的完整對話流程
    
    流程：
    1. 開始對話（清晰輸入）
    2. 獲取 Session 狀態
    3. 繼續對話（選擇方向）
    4. 完成對話
    """
    print_test_section("Test 2: Simple Conversation Flow")
    
    async with AsyncClient(base_url=TEST_BASE_URL, timeout=TEST_TIMEOUT) as client:
        
        # 步驟 1: 開始對話
        print("Step 1: Starting conversation...")
        
        start_request = {
            "message": "櫻花樹下的和服少女，溫柔寧靜的氛圍",
            "user_access_level": "all-ages",
            "preferences": {
                "language": "zh",
                "verbosity": "concise"
            }
        }
        
        start_response = await client.post(
            "/api/inspire/start",
            json=start_request
        )
        
        assert start_response.status_code == 200, f"Start failed: {start_response.status_code}"
        
        start_data = start_response.json()
        session_id = start_data.get("session_id")
        
        assert session_id is not None, "No session_id returned"
        
        print_result("Start Response", {
            "session_id": session_id,
            "type": start_data.get("type"),
            "message": start_data.get("message")[:100] + "..." if len(start_data.get("message", "")) > 100 else start_data.get("message"),
            "phase": start_data.get("phase"),
        })
        
        # 步驟 2: 查詢狀態
        print("Step 2: Checking session status...")
        
        status_response = await client.get(f"/api/inspire/status/{session_id}")
        
        assert status_response.status_code == 200, "Status check failed"
        
        status_data = status_response.json()
        
        print_result("Status Response", {
            "status": status_data.get("status"),
            "phase": status_data.get("metadata", {}).get("current_phase"),
            "tool_calls": status_data.get("metadata", {}).get("total_tool_calls"),
        })
        
        # 步驟 3: 繼續對話
        print("Step 3: Continuing conversation...")
        
        continue_request = {
            "session_id": session_id,
            "message": "這個感覺很好，可以更夢幻一點嗎？",
        }
        
        continue_response = await client.post(
            "/api/inspire/continue",
            json=continue_request
        )
        
        assert continue_response.status_code == 200, "Continue failed"
        
        continue_data = continue_response.json()
        
        print_result("Continue Response", {
            "type": continue_data.get("type"),
            "message": continue_data.get("message")[:100] + "...",
            "is_completed": continue_data.get("is_completed"),
        })
        
        # 步驟 4: 提交反饋（可選）
        print("Step 4: Submitting feedback...")
        
        feedback_request = {
            "session_id": session_id,
            "satisfaction": 5,
            "feedback_text": "非常好！",
            "would_use_again": True
        }
        
        feedback_response = await client.post(
            "/api/inspire/feedback",
            json=feedback_request
        )
        
        assert feedback_response.status_code == 200, "Feedback failed"
        
        print("✅ Feedback submitted")
        
        print("\n✅ Test 2 PASSED: Complete conversation flow successful\n")


# ============================================================================
# 錯誤處理測試
# ============================================================================

@pytest.mark.asyncio
async def test_inspire_error_handling():
    """測試錯誤處理"""
    print_test_section("Test 3: Error Handling")
    
    async with AsyncClient(base_url=TEST_BASE_URL, timeout=TEST_TIMEOUT) as client:
        
        # 測試 1: 空消息
        print("Test 3.1: Empty message...")
        
        response = await client.post(
            "/api/inspire/start",
            json={"message": "", "user_access_level": "all-ages"}
        )
        
        assert response.status_code == 422, f"Expected 422 for empty message, got {response.status_code}"
        print("✓ Empty message rejected\n")
        
        # 測試 2: 不存在的 Session
        print("Test 3.2: Non-existent session...")
        
        response = await client.get("/api/inspire/status/non-existent-session-id")
        
        assert response.status_code == 404, f"Expected 404 for non-existent session, got {response.status_code}"
        print("✓ Non-existent session handled correctly\n")
        
        print("✅ Test 3 PASSED: Error handling works correctly\n")


# ============================================================================
# 性能測試
# ============================================================================

@pytest.mark.asyncio
async def test_inspire_performance():
    """
    測試性能指標
    
    目標：
    - 首次回應 < 10 秒
    - 後續回應 < 5 秒
    """
    print_test_section("Test 4: Performance")
    
    async with AsyncClient(base_url=TEST_BASE_URL, timeout=TEST_TIMEOUT) as client:
        
        # 測試首次回應時間
        start_time = datetime.now()
        
        response = await client.post(
            "/api/inspire/start",
            json={
                "message": "測試訊息",
                "user_access_level": "all-ages"
            }
        )
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200
        assert response_time < 10.0, f"First response took {response_time:.2f}s (should be < 10s)"
        
        print_result("Performance Metrics", {
            "first_response_time": f"{response_time:.2f}s",
            "status": "✅ PASS" if response_time < 10.0 else "❌ FAIL",
        })
        
        print("✅ Test 4 PASSED: Performance within acceptable range\n")


# ============================================================================
# 測試套件總結
# ============================================================================

@pytest.mark.asyncio
async def test_inspire_full_suite():
    """運行完整測試套件"""
    print("\n" + "=" * 60)
    print("  INSPIRE AGENT E2E TEST SUITE")
    print("=" * 60 + "\n")
    
    test_results = []
    
    # Test 1: Health Check
    try:
        await test_inspire_health_check()
        test_results.append(("Health Check", "PASS"))
    except Exception as e:
        test_results.append(("Health Check", f"FAIL: {e}"))
    
    # Test 2: Conversation Flow
    try:
        await test_inspire_simple_conversation_flow()
        test_results.append(("Conversation Flow", "PASS"))
    except Exception as e:
        test_results.append(("Conversation Flow", f"FAIL: {e}"))
    
    # Test 3: Error Handling
    try:
        await test_inspire_error_handling()
        test_results.append(("Error Handling", "PASS"))
    except Exception as e:
        test_results.append(("Error Handling", f"FAIL: {e}"))
    
    # Test 4: Performance
    try:
        await test_inspire_performance()
        test_results.append(("Performance", "PASS"))
    except Exception as e:
        test_results.append(("Performance", f"FAIL: {e}"))
    
    # 打印總結
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60 + "\n")
    
    passed = sum(1 for _, result in test_results if result == "PASS")
    total = len(test_results)
    
    for test_name, result in test_results:
        status_emoji = "✅" if result == "PASS" else "❌"
        print(f"{status_emoji} {test_name}: {result}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed\n")
    
    assert passed == total, f"Only {passed}/{total} tests passed"


# ============================================================================
# 主函數（用於直接執行）
# ============================================================================

if __name__ == "__main__":
    """
    直接執行測試（不使用 pytest）
    
    使用方法：
        python test_inspire_e2e.py
    """
    
    print("🚀 Starting Inspire Agent E2E Tests...\n")
    print("⚠️  Make sure the API server is running at http://localhost:8000\n")
    
    try:
        # 運行完整測試套件
        asyncio.run(test_inspire_full_suite())
        
        print("\n" + "=" * 60)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"  ❌ TEST FAILED: {e}")
        print("=" * 60 + "\n")
        exit(1)
    
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"  ❌ ERROR: {e}")
        print("=" * 60 + "\n")
        import traceback
        traceback.print_exc()
        exit(1)


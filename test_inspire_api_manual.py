"""
Inspire Agent API 手動測試腳本

這個腳本會測試 Inspire Agent 的 API 端點。
運行前請確保伺服器已啟動（python src/api/main.py）。
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔線"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def test_health():
    """測試健康檢查"""
    print_section("Test 1: Health Check")
    
    try:
        # 主健康檢查
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"[OK] Main health: {r.status_code}")
        print(f"     Response: {r.json()}")
        print()
        
        # Inspire 健康檢查
        r = requests.get(f"{BASE_URL}/api/inspire/health", timeout=5)
        print(f"[OK] Inspire health: {r.status_code}")
        data = r.json()
        print(f"     Service: {data.get('service')}")
        print(f"     Version: {data.get('version')}")
        print(f"     Storage: {data.get('storage', {}).get('storage_type')}")
        print()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to server")
        print("       Please start the server first:")
        print("       cd src/api && python main.py")
        return False
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False


def test_start_conversation():
    """測試開始對話"""
    print_section("Test 2: Start Conversation")
    
    try:
        payload = {
            "message": "櫻花樹下的和服少女，溫柔寧靜的氛圍",
            "user_access_level": "all-ages",
            "preferences": {
                "language": "zh",
                "verbosity": "concise"
            }
        }
        
        print(f"Request payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print()
        
        r = requests.post(
            f"{BASE_URL}/api/inspire/start",
            json=payload,
            timeout=60  # 增加到 60 秒（gpt-5-mini 需要 15-20秒）
        )
        
        print(f"[OK] Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"     Session ID: {data.get('session_id')}")
            print(f"     Type: {data.get('type')}")
            print(f"     Phase: {data.get('phase')}")
            print(f"     Message: {data.get('message')[:100]}...")
            print()
            
            return data.get('session_id')
        else:
            print(f"[FAIL] Response:")
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
            return None
            
    except Exception as e:
        print(f"[FAIL] Start conversation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_status(session_id):
    """測試狀態查詢"""
    print_section("Test 3: Query Status")
    
    try:
        r = requests.get(
            f"{BASE_URL}/api/inspire/status/{session_id}",
            timeout=10
        )
        
        print(f"[OK] Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"     Session ID: {data.get('session_id')}")
            print(f"     Status: {data.get('status')}")
            print(f"     Phase: {data.get('metadata', {}).get('current_phase')}")
            print(f"     Tool calls: {data.get('metadata', {}).get('total_tool_calls')}")
            print(f"     Cost: ${data.get('metadata', {}).get('total_cost', 0):.6f}")
            print()
            return True
        else:
            print(f"[FAIL] Response:")
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
            return False
            
    except Exception as e:
        print(f"[FAIL] Status query failed: {e}")
        return False


def test_continue_conversation(session_id):
    """測試繼續對話"""
    print_section("Test 4: Continue Conversation")
    
    try:
        payload = {
            "session_id": session_id,
            "message": "這個感覺很好，可以更夢幻一點嗎？"
        }
        
        print(f"Request payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print()
        
        r = requests.post(
            f"{BASE_URL}/api/inspire/continue",
            json=payload,
            timeout=30
        )
        
        print(f"[OK] Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"     Type: {data.get('type')}")
            print(f"     Phase: {data.get('phase')}")
            print(f"     Message: {data.get('message')[:100]}...")
            print(f"     Is completed: {data.get('is_completed')}")
            print()
            return True
        else:
            print(f"[FAIL] Response:")
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
            return False
            
    except Exception as e:
        print(f"[FAIL] Continue conversation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Inspire Agent API Manual Test")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("  1. Environment variables set (OPENAI_API_KEY, etc.)")
    print("  2. Server running (python src/api/main.py)")
    print()
    print("Starting tests...")
    print()
    
    # Test 1: Health Check
    if not test_health():
        print("\n[ERROR] Health check failed. Cannot proceed.")
        print("Please make sure the server is running.")
        exit(1)
    
    # Test 2: Start Conversation
    session_id = test_start_conversation()
    
    if not session_id:
        print("\n[ERROR] Could not start conversation.")
        exit(1)
    
    # Wait a bit
    time.sleep(2)
    
    # Test 3: Query Status
    test_status(session_id)
    
    # Test 4: Continue Conversation
    test_continue_conversation(session_id)
    
    # Summary
    print_section("Test Summary")
    print("[OK] All tests completed!")
    print()
    print(f"Session ID: {session_id}")
    print(f"You can check the session status at:")
    print(f"http://localhost:8000/api/inspire/status/{session_id}")
    print()
    print("Next: Open http://localhost:8000/docs to explore all endpoints")
    print()


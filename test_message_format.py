#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_message_format():
    """測試 message 格式修復"""
    print("測試 message 格式修復")
    print("=" * 50)
    
    try:
        # 測試 API 響應
        print("1. 測試 API 響應...")
        start_time = time.time()
        
        test_data = {"message": "測試 message 格式", "user_access_level": "all-ages"}
        
        response = requests.post(
            "http://localhost:3000/api/inspire/start",
            json=test_data,
            timeout=60
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"API 響應時間: {response_time:.2f} 秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] API 調用成功")
            
            # 檢查 message 格式
            message = result.get('message', '')
            print(f"Message 類型: {type(message)}")
            print(f"Message 內容: {message}")
            
            # 檢查是否包含 ResponseOutputText 字符串表示
            if "ResponseOutputText" in str(message):
                print("[FAIL] Message 仍然包含 ResponseOutputText 字符串表示")
                return False
            else:
                print("[OK] Message 是純文本格式")
            
            # 檢查 directions
            directions = result.get('data', {}).get('directions', [])
            print(f"Directions 數量: {len(directions)}")
            
            if len(directions) > 0:
                print("[OK] Directions 數據正常")
                return True
            else:
                print("[WARN] Directions 數據為空")
                return False
        else:
            print(f"[FAIL] API 調用失敗: {response.status_code}")
            print(f"錯誤響應: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 測試異常: {e}")
        return False

if __name__ == "__main__":
    success = test_message_format()
    if success:
        print("\n[SUCCESS] Message 格式修復成功")
        print("現在前端應該能正確顯示對話內容")
    else:
        print("\n[FAIL] Message 格式修復失敗")
        print("需要進一步檢查後端邏輯")
    
    print("\n測試完成！")






#!/usr/bin/env python3
"""
測試 GPT-5 模型並獲取詳細錯誤信息
"""
import sys
import os

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from openai import OpenAI

client = OpenAI()

print("=" * 60)
print("🔍 測試 GPT-5 系列模型 - 詳細錯誤分析")
print("=" * 60)

models_to_test = ["gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o", "gpt-4o-mini"]

for model in models_to_test:
    print(f"\n測試模型: {model}")
    print("-" * 60)
    
    try:
        # 準備參數
        params = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Say 'test'"}
            ]
        }
        
        # GPT-5 系列使用不同的參數
        if model.startswith("gpt-5"):
            params["max_completion_tokens"] = 50  # 增加 tokens 以獲得回應
            params["reasoning_effort"] = "low"
            params["verbosity"] = "low"
        else:
            params["max_tokens"] = 50
        
        response = client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        print(f"  ✅ 成功: {content}")
        
    except Exception as e:
        print(f"  ❌ 失敗:")
        print(f"    錯誤類型: {type(e).__name__}")
        print(f"    錯誤訊息: {str(e)}")
        
        # 如果有 response 屬性，顯示詳細信息
        if hasattr(e, 'response') and e.response is not None:
            print(f"    HTTP 狀態碼: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"    詳細錯誤: {error_data}")
            except:
                pass

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)

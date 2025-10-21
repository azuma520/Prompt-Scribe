#!/usr/bin/env python3
"""
測試 GPT-5 Mini 標籤生成功能
"""
import sys
import os
import json

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from openai import OpenAI

client = OpenAI()

print("=" * 60)
print("🏷️ GPT-5 Mini 標籤生成測試")
print("=" * 60)

system_prompt = """You are an expert AI image generation tag recommendation assistant.

Return ONLY a valid JSON object in this EXACT format:
{
    "tags": ["tag1", "tag2", "tag3"],
    "confidence": 0.85,
    "reasoning": "Brief explanation"
}

Return ONLY the JSON, no other text."""

test_description = "一個長髮藍眼的動漫女孩"

print(f"\n測試描述: {test_description}")
print("-" * 60)

models_to_test = ["gpt-5-mini", "gpt-5-nano", "gpt-4o-mini"]

for model in models_to_test:
    print(f"\n🤖 測試模型: {model}")
    
    try:
        # 準備參數
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Recommend tags for: {test_description}"}
            ]
        }
        
        # GPT-5 系列使用特殊參數
        if model.startswith("gpt-5"):
            params["max_completion_tokens"] = 500
            params["reasoning_effort"] = "low"
            params["verbosity"] = "low"
            print(f"  參數: max_completion_tokens=500, reasoning_effort=low, verbosity=low")
        else:
            params["max_tokens"] = 500
            params["temperature"] = 0.7
            print(f"  參數: max_tokens=500, temperature=0.7")
        
        print(f"  調用 API...")
        response = client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        usage = response.usage
        
        print(f"  ✅ 成功!")
        print(f"  📝 回應長度: {len(content)} 字符")
        print(f"  📊 Token 使用:")
        print(f"    - Prompt: {usage.prompt_tokens}")
        print(f"    - Completion: {usage.completion_tokens}")
        print(f"    - Total: {usage.total_tokens}")
        
        if content:
            print(f"  📦 回應內容:")
            print(f"    {content[:200]}...")
            
            # 嘗試解析 JSON
            try:
                data = json.loads(content)
                print(f"  ✅ JSON 解析成功:")
                print(f"    - Tags: {data.get('tags', [])}")
                print(f"    - Confidence: {data.get('confidence', 0)}")
            except json.JSONDecodeError:
                print(f"  ⚠️ JSON 解析失敗（可能需要調整 prompt）")
        else:
            print(f"  ⚠️ 回應為空")
        
    except Exception as e:
        print(f"  ❌ 失敗: {e}")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)

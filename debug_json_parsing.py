#!/usr/bin/env python3
"""
調查 GPT-5 Mini JSON 解析失敗問題
"""
import sys
import os
import asyncio
import json

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

from services.gpt5_nano_client import GPT5NanoClient
from openai import OpenAI

async def test_failing_case():
    """測試失敗的案例"""
    print("="*60)
    print("🔍 調查 JSON 解析失敗問題")
    print("="*60)
    
    # 失敗的測試案例
    description = "穿著校服的女孩"
    
    print(f"\n測試描述: {description}")
    print("-"*60)
    
    # 測試 1: 使用 GPT5NanoClient
    print("\n📋 測試 1: 使用 GPT5NanoClient")
    
    client = GPT5NanoClient()
    
    if not client.is_available():
        print("❌ 客戶端不可用")
        return
    
    print(f"  模型: {client.model}")
    print(f"  GPT-5: {client.is_gpt5}")
    
    try:
        result = await client.generate_tags(description)
        if result:
            print(f"  ✅ 成功")
            print(f"  Tags: {result.get('tags', [])}")
            print(f"  Confidence: {result.get('confidence', 0)}")
        else:
            print(f"  ❌ 返回 None")
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    # 測試 2: 直接調用 OpenAI API，獲取原始回應
    print(f"\n📋 測試 2: 直接調用 OpenAI API（獲取原始回應）")
    
    openai_client = OpenAI()
    
    system_prompt = """You are an expert AI image generation tag recommendation assistant.

Return ONLY a valid JSON object in this EXACT format:
{
    "tags": ["tag1", "tag2", "tag3"],
    "confidence": 0.85,
    "reasoning": "Brief explanation"
}

Return ONLY the JSON, no other text."""
    
    params = {
        "model": client.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Recommend tags for: {description}"}
        ]
    }
    
    # GPT-5 參數
    if client.is_gpt5:
        params["max_completion_tokens"] = 500
        params["reasoning_effort"] = "low"
        params["verbosity"] = "low"
        print(f"  參數: max_completion_tokens=500, reasoning_effort=low, verbosity=low")
    else:
        params["max_tokens"] = 500
        params["temperature"] = 0.7
        print(f"  參數: max_tokens=500, temperature=0.7")
    
    try:
        print(f"\n  調用 API...")
        response = openai_client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        usage = response.usage
        
        print(f"\n  ✅ API 調用成功")
        print(f"\n  📦 原始回應:")
        print(f"  {'─'*58}")
        print(content)
        print(f"  {'─'*58}")
        
        print(f"\n  📊 Token 使用:")
        print(f"    - Prompt: {usage.prompt_tokens}")
        print(f"    - Completion: {usage.completion_tokens}")
        print(f"    - Total: {usage.total_tokens}")
        
        # 檢查回應長度
        print(f"\n  📏 回應分析:")
        print(f"    - 長度: {len(content)} 字符")
        print(f"    - 是否為空: {'是' if not content else '否'}")
        print(f"    - 開頭 100 字符: {repr(content[:100])}")
        print(f"    - 結尾 100 字符: {repr(content[-100:])}")
        
        # 嘗試解析 JSON
        print(f"\n  🔍 JSON 解析測試:")
        
        try:
            data = json.loads(content)
            print(f"    ✅ JSON 解析成功")
            print(f"    - Tags: {data.get('tags', [])}")
            print(f"    - Confidence: {data.get('confidence', 0)}")
            print(f"    - Reasoning: {data.get('reasoning', '')[:50]}...")
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON 解析失敗")
            print(f"    - 錯誤: {e}")
            print(f"    - 位置: line {e.lineno}, column {e.colno}")
            
            # 嘗試清理並重新解析
            print(f"\n  🔧 嘗試清理回應:")
            
            # 方法 1: 去除 markdown 代碼塊
            cleaned = content.strip()
            if cleaned.startswith("```"):
                print(f"    - 檢測到 markdown 代碼塊")
                lines = cleaned.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = '\n'.join(lines)
            
            # 方法 2: 提取 JSON 部分
            if '{' in cleaned and '}' in cleaned:
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                cleaned = cleaned[start:end]
                print(f"    - 提取 JSON 部分: {len(cleaned)} 字符")
            
            # 再次嘗試解析
            try:
                data = json.loads(cleaned)
                print(f"    ✅ 清理後解析成功！")
                print(f"    - Tags: {data.get('tags', [])}")
                print(f"    - Confidence: {data.get('confidence', 0)}")
            except:
                print(f"    ❌ 清理後仍然失敗")
                print(f"    - 清理後內容: {repr(cleaned[:200])}")
        
    except Exception as e:
        print(f"  ❌ API 調用失敗: {e}")
        import traceback
        traceback.print_exc()

    # 測試 3: 多次重複測試
    print(f"\n{'='*60}")
    print(f"📋 測試 3: 重複測試（檢查穩定性）")
    print(f"{'='*60}")
    
    print(f"\n對同一描述進行 5 次測試，檢查是否隨機失敗...")
    
    success_count = 0
    failure_count = 0
    
    for i in range(5):
        print(f"\n  第 {i+1} 次測試...")
        try:
            result = await client.generate_tags(description)
            if result:
                print(f"    ✅ 成功 - Tags: {len(result.get('tags', []))}個")
                success_count += 1
            else:
                print(f"    ❌ 失敗 - 返回 None")
                failure_count += 1
        except Exception as e:
            print(f"    ❌ 錯誤: {str(e)[:100]}")
            failure_count += 1
    
    print(f"\n  結果:")
    print(f"    ✅ 成功: {success_count}/5")
    print(f"    ❌ 失敗: {failure_count}/5")
    print(f"    穩定性: {success_count/5*100:.0f}%")
    
    if failure_count > 0:
        print(f"\n  ⚠️ 發現不穩定性！")
        print(f"    可能原因:")
        print(f"    1. GPT-5 回應格式不一致")
        print(f"    2. verbosity='low' 可能導致回應過於簡略")
        print(f"    3. prompt 需要更明確的格式要求")
    else:
        print(f"\n  ✅ 穩定性良好！")

    # 測試 4: 測試不同的 verbosity 設置
    print(f"\n{'='*60}")
    print(f"📋 測試 4: 測試不同的 verbosity 設置")
    print(f"{'='*60}")
    
    for verbosity in ["low", "medium"]:
        print(f"\n  測試 verbosity='{verbosity}':")
        
        try:
            params = {
                "model": client.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Recommend tags for: {description}"}
                ],
                "max_completion_tokens": 500,
                "reasoning_effort": "low",
                "verbosity": verbosity
            }
            
            response = openai_client.chat.completions.create(**params)
            content = response.choices[0].message.content
            
            print(f"    回應長度: {len(content)} 字符")
            
            try:
                data = json.loads(content)
                print(f"    ✅ JSON 解析成功")
                print(f"    Tags: {len(data.get('tags', []))}個")
            except:
                print(f"    ❌ JSON 解析失敗")
                print(f"    前 200 字符: {repr(content[:200])}")
                
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")

    print(f"\n{'='*60}")
    print("調查完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_failing_case())

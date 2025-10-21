#!/usr/bin/env python3
"""
測試 Responses API 基本功能
"""
import sys
import os

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from openai import OpenAI

# 從環境變數獲取 API Key
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ OPENAI_API_KEY 未設置")
    sys.exit(1)

client = OpenAI(api_key=api_key)

print("="*60)
print("🧪 Responses API 基本功能測試")
print("="*60)

# 檢查 Responses API 可用性
print("\n📋 步驟 1: 檢查 API 可用性")
print("-"*60)

has_responses = hasattr(client, 'responses')
print(f"  Responses API: {'✅ 可用' if has_responses else '❌ 不可用'}")

if not has_responses:
    print("\n❌ Responses API 不可用")
    print("SDK 版本可能不夠新")
    sys.exit(1)

# 測試簡單調用
print("\n📋 步驟 2: 測試簡單調用")
print("-"*60)

try:
    response = client.responses.create(
        model="gpt-5-mini",
        input="Say 'Hello, Responses API!'"
    )
    
    print(f"  ✅ 調用成功")
    print(f"  回應: {response.output_text}")
    print(f"  Response ID: {response.id}")
    
except Exception as e:
    print(f"  ❌ 調用失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 測試帶參數的調用
print("\n📋 步驟 3: 測試帶參數調用")
print("-"*60)

try:
    response = client.responses.create(
        model="gpt-5-mini",
        input="List 3 colors",
        reasoning={"effort": "low"},
        text={"verbosity": "medium"}
    )
    
    print(f"  ✅ 調用成功")
    print(f"  回應: {response.output_text}")
    
except Exception as e:
    print(f"  ❌ 調用失敗: {e}")
    sys.exit(1)

# 測試 Structured Output
print("\n📋 步驟 4: 測試 Structured Output")
print("-"*60)

try:
    response = client.responses.create(
        model="gpt-5-mini",
        input="Recommend tags for: cute anime girl",
        reasoning={"effort": "low"},
        text={
            "verbosity": "medium",
            "format": {
                "type": "json_schema",
                "name": "tag_recommendation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "confidence": {
                            "type": "number"
                        }
                    },
                    "required": ["tags", "confidence"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    print(f"  ✅ 調用成功")
    print(f"  回應長度: {len(response.output_text)} 字符")
    print(f"  回應內容: {response.output_text[:200]}...")
    
    # 嘗試解析 JSON
    import json
    try:
        data = json.loads(response.output_text)
        print(f"  ✅ JSON 解析成功")
        print(f"    Tags: {data.get('tags', [])})")
        print(f"    Confidence: {data.get('confidence', 0)}")
    except:
        print(f"  ⚠️ JSON 解析失敗（可能需要調整）")
    
except Exception as e:
    print(f"  ❌ 調用失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 穩定性測試
print("\n📋 步驟 5: 穩定性測試（5次重複調用）")
print("-"*60)

success_count = 0
failures = []

for i in range(5):
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=f"Test {i+1}: Say 'success'",
            reasoning={"effort": "low"},
            text={"verbosity": "medium"}
        )
        
        if response.output_text and len(response.output_text) > 0:
            success_count += 1
            print(f"  [{i+1}/5] ✅ 成功")
        else:
            failures.append(i+1)
            print(f"  [{i+1}/5] ❌ 空回應")
            
    except Exception as e:
        failures.append(i+1)
        print(f"  [{i+1}/5] ❌ 錯誤: {e}")

stability = success_count / 5 * 100
print(f"\n  穩定性: {stability:.0f}% ({success_count}/5)")

if stability >= 95:
    print(f"  ✅ 穩定性優秀！")
elif stability >= 80:
    print(f"  ⚠️ 穩定性良好，可接受")
else:
    print(f"  ❌ 穩定性不足")
    sys.exit(1)

print("\n" + "="*60)
print("🎉 所有基本測試通過！")
print("="*60)
print("\n✅ Responses API 準備就緒")
print("✅ 可以開始實施遷移")

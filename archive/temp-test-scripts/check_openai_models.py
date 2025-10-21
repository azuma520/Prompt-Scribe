#!/usr/bin/env python3
"""
檢查 OpenAI API Key 可以訪問的模型
"""
import os
import sys
import requests
import json
from datetime import datetime

# 設置編碼
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def check_openai_models():
    """檢查可用的 OpenAI 模型"""
    
    # 從環境變數獲取 API Key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY 環境變數")
        print("請設置環境變數：")
        print("  Windows: $env:OPENAI_API_KEY = 'your_api_key_here'")
        print("  Linux/Mac: export OPENAI_API_KEY='your_api_key_here'")
        return
    
    print("🔍 檢查 OpenAI API 可用模型...")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print("=" * 60)
    
    # 檢查模型列表
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get('data', [])
            
            print(f"✅ 成功獲取模型列表，共 {len(models)} 個模型")
            print()
            
            # 分類顯示模型
            gpt_models = []
            other_models = []
            
            for model in models:
                model_id = model.get('id', '')
                if 'gpt' in model_id.lower():
                    gpt_models.append(model)
                else:
                    other_models.append(model)
            
            # 顯示 GPT 模型
            print("🤖 GPT 模型:")
            for model in sorted(gpt_models, key=lambda x: x['id']):
                model_id = model['id']
                created = model.get('created', 0)
                created_date = datetime.fromtimestamp(created).strftime('%Y-%m-%d') if created else 'Unknown'
                print(f"  - {model_id} (創建於: {created_date})")
            
            print()
            
            # 顯示其他模型
            print("🔧 其他模型:")
            for model in sorted(other_models, key=lambda x: x['id']):
                model_id = model['id']
                created = model.get('created', 0)
                created_date = datetime.fromtimestamp(created).strftime('%Y-%m-%d') if created else 'Unknown'
                print(f"  - {model_id} (創建於: {created_date})")
            
            print()
            
            # 檢查特定模型
            target_models = ['gpt-5-nano', 'gpt-5-mini', 'gpt-5', 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo']
            print("🎯 檢查目標模型:")
            for target in target_models:
                found = any(model['id'] == target for model in models)
                status = "✅ 可用" if found else "❌ 不可用"
                print(f"  - {target}: {status}")
            
        else:
            print(f"❌ 獲取模型列表失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 檢查模型時發生錯誤: {e}")

def test_simple_completion():
    """測試簡單的完成請求"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY")
        return
    
    print("\n🧪 測試簡單的完成請求...")
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 使用 gpt-4o-mini 進行測試
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'user', 'content': 'Hello, please respond with just "Hello World"'}
            ],
            'max_tokens': 10,
            'temperature': 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ 測試成功: {content}")
            
            # 顯示使用統計
            usage = result.get('usage', {})
            print(f"📊 使用統計:")
            print(f"  - Prompt tokens: {usage.get('prompt_tokens', 0)}")
            print(f"  - Completion tokens: {usage.get('completion_tokens', 0)}")
            print(f"  - Total tokens: {usage.get('total_tokens', 0)}")
            
        else:
            print(f"❌ 測試失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {e}")

if __name__ == "__main__":
    print("🔍 OpenAI API 模型檢查工具")
    print("=" * 60)
    
    check_openai_models()
    test_simple_completion()
    
    print("\n" + "=" * 60)
    print("檢查完成！")

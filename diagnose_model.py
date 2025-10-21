#!/usr/bin/env python3
"""
診斷 OpenAI 模型配置
檢查實際使用的模型和可用的模型
"""
import sys
import os
import json

# 修復編碼
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 添加 src/api 到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'api'))

def check_current_config():
    """檢查當前配置"""
    print("=" * 60)
    print("🔍 檢查當前 OpenAI 配置")
    print("=" * 60)
    
    try:
        from config import settings
        
        print("\n📋 配置設定:")
        print(f"  - OPENAI_API_KEY: {'✅ 已設置' if settings.openai_api_key else '❌ 未設置'}")
        if settings.openai_api_key:
            print(f"    前8碼: {settings.openai_api_key[:8]}...")
            print(f"    後4碼: ...{settings.openai_api_key[-4:]}")
        
        print(f"  - 配置的模型: {settings.openai_model}")
        print(f"  - 最大 Tokens: {settings.openai_max_tokens}")
        print(f"  - Temperature: {settings.openai_temperature}")
        print(f"  - Timeout: {settings.openai_timeout}秒")
        print(f"  - 功能啟用: {'✅ 是' if settings.enable_openai_integration else '❌ 否'}")
        
        return settings.openai_api_key
        
    except Exception as e:
        print(f"❌ 讀取配置失敗: {e}")
        return None

def check_gpt5_client():
    """檢查 GPT5 客戶端實際使用的模型"""
    print("\n" + "=" * 60)
    print("🤖 檢查 GPT5 Nano 客戶端")
    print("=" * 60)
    
    try:
        from services.gpt5_nano_client import GPT5NanoClient
        
        print("\n初始化客戶端...")
        client = GPT5NanoClient()
        
        print(f"\n📊 客戶端配置:")
        print(f"  - 實際使用的模型: {client.model}")
        print(f"  - 最大 Tokens: {client.max_tokens}")
        print(f"  - Temperature: {client.temperature}")
        print(f"  - Timeout: {client.timeout}秒")
        print(f"  - API Key: {'✅ 已設置' if client.api_key else '❌ 未設置'}")
        print(f"  - OpenAI 客戶端: {'✅ 已初始化' if client.client else '❌ 未初始化'}")
        print(f"  - 功能啟用: {'✅ 是' if client.enabled else '❌ 否'}")
        print(f"  - 可用性: {'✅ 可用' if client.is_available() else '❌ 不可用'}")
        print(f"  - GPT-5 系列: {'✅ 是' if client.is_gpt5 else '❌ 否'}")
        
        return client
        
    except Exception as e:
        print(f"❌ 初始化客戶端失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_available_models(api_key):
    """檢查可用的模型"""
    print("\n" + "=" * 60)
    print("🌐 檢查 OpenAI 可用模型")
    print("=" * 60)
    
    if not api_key:
        print("❌ 沒有 API Key，無法檢查可用模型")
        return
    
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        print("\n正在查詢 OpenAI API...")
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            models_data = response.json()
            all_models = [model['id'] for model in models_data.get('data', [])]
            
            # 過濾 GPT 模型
            gpt_models = [m for m in all_models if 'gpt' in m.lower()]
            
            print(f"\n✅ 找到 {len(gpt_models)} 個 GPT 模型:")
            
            # 分類顯示
            categories = {
                'GPT-5': [m for m in gpt_models if 'gpt-5' in m.lower()],
                'GPT-4': [m for m in gpt_models if 'gpt-4' in m.lower()],
                'GPT-3.5': [m for m in gpt_models if 'gpt-3.5' in m.lower()],
                'GPT-3': [m for m in gpt_models if m.startswith('gpt-3') and 'gpt-3.5' not in m.lower()]
            }
            
            for category, models in categories.items():
                if models:
                    print(f"\n  {category}:")
                    for model in sorted(models):
                        print(f"    - {model}")
            
            # 檢查特定模型
            print("\n🎯 檢查目標模型可用性:")
            target_models = [
                'gpt-5-nano',
                'gpt-5-mini', 
                'gpt-5',
                'gpt-4o',
                'gpt-4o-mini',
                'gpt-4-turbo',
                'gpt-3.5-turbo'
            ]
            
            for target in target_models:
                available = target in all_models
                status = "✅ 可用" if available else "❌ 不可用"
                print(f"  - {target}: {status}")
            
        else:
            print(f"❌ API 請求失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 檢查模型時發生錯誤: {e}")
        import traceback
        traceback.print_exc()

def test_simple_call(api_key, model_name):
    """測試簡單的 API 調用"""
    print("\n" + "=" * 60)
    print(f"🧪 測試 {model_name} 模型")
    print("=" * 60)
    
    if not api_key:
        print("❌ 沒有 API Key，無法測試")
        return
    
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant. Respond with ONLY valid JSON.'
                },
                {
                    'role': 'user',
                    'content': 'Return this JSON: {"test": "success", "model": "' + model_name + '"}'
                }
            ],
            'max_tokens': 50
        }
        
        # 只有非 GPT-5 模型才設置 temperature
        if not model_name.startswith('gpt-5'):
            data['temperature'] = 0.1
        
        print(f"\n正在調用 {model_name}...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            usage = result.get('usage', {})
            
            print(f"✅ 測試成功!")
            print(f"\n📝 回應內容:")
            print(f"  {content}")
            
            print(f"\n📊 使用統計:")
            print(f"  - Prompt tokens: {usage.get('prompt_tokens', 0)}")
            print(f"  - Completion tokens: {usage.get('completion_tokens', 0)}")
            print(f"  - Total tokens: {usage.get('total_tokens', 0)}")
            
            # 嘗試解析 JSON
            try:
                json_data = json.loads(content)
                print(f"\n✅ JSON 解析成功:")
                print(f"  {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"\n⚠️ 回應不是有效的 JSON")
            
        else:
            print(f"❌ 測試失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🔍 OpenAI 模型診斷工具")
    print("=" * 60)
    
    # 1. 檢查配置
    api_key = check_current_config()
    
    # 2. 檢查客戶端
    client = check_gpt5_client()
    
    # 3. 檢查可用模型
    if api_key:
        check_available_models(api_key)
        
        # 4. 測試當前配置的模型
        if client and client.model:
            test_simple_call(api_key, client.model)
    
    print("\n" + "=" * 60)
    print("診斷完成！")
    print("=" * 60)
    
    # 建議
    print("\n💡 建議:")
    if not api_key:
        print("  1. 請設置 OPENAI_API_KEY 環境變數")
        print("     Windows: $env:OPENAI_API_KEY = 'your_key_here'")
    elif client and not client.is_available():
        print("  1. 客戶端不可用，請檢查 API Key 和網路連線")
    elif client and client.model.startswith('gpt-5'):
        print("  1. 如果 GPT-5 系列不可用，建議修改配置使用 gpt-4o-mini")
        print("     設置環境變數: $env:OPENAI_MODEL = 'gpt-4o-mini'")
    else:
        print("  1. 配置看起來正常！")

if __name__ == "__main__":
    main()

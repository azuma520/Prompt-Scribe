"""
Check configuration details
"""

import sys
import os

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

print("檢查配置詳情...")
print("=" * 50)

try:
    from config import settings
    
    print("OpenAI 配置:")
    print(f"  - API Key: {'已設置' if settings.openai_api_key else '未設置'}")
    print(f"  - 模型: {settings.openai_model}")
    print(f"  - 最大 Tokens: {settings.openai_max_tokens}")
    print(f"  - 溫度: {settings.openai_temperature}")
    print(f"  - 超時: {settings.openai_timeout}秒")
    print(f"  - 功能啟用: {settings.enable_openai_integration}")
    
    print("\n環境變數:")
    print(f"  - OPENAI_API_KEY: {'已設置' if os.getenv('OPENAI_API_KEY') else '未設置'}")
    print(f"  - ENABLE_OPENAI_INTEGRATION: {os.getenv('ENABLE_OPENAI_INTEGRATION', '未設置')}")
    
    print("\nSupabase 配置:")
    print(f"  - URL: {'已設置' if settings.supabase_url else '未設置'}")
    print(f"  - Key: {'已設置' if settings.supabase_anon_key else '未設置'}")
    
except Exception as e:
    print(f"配置檢查失敗: {e}")

print("\n檢查完成")

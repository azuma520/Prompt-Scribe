"""
LLM 增強配置 - Qwen3 Next 80B A3B Thinking
基於 OpenRouter API
"""

import os
from pathlib import Path

# 嘗試載入 .env 檔案
def load_env(env_path: str = ".env") -> None:
    """載入環境變數檔案"""
    if os.path.exists(env_path):
        try:
            # 嘗試多種編碼
            for encoding in ['utf-8-sig', 'utf-8', 'cp950', 'gbk']:
                try:
                    with open(env_path, "r", encoding=encoding) as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip().lstrip("\ufeff")
                                v = v.strip()
                                os.environ[k] = v
                    break  # 成功讀取，跳出循環
                except (UnicodeDecodeError, UnicodeError):
                    continue  # 嘗試下一個編碼
        except Exception as e:
            print(f"警告：無法載入 .env 檔案: {e}")

# 載入環境變數
load_env()
load_env(os.path.join("..", ".env"))

# API 配置
# 支援多種 API Key 名稱
OPENROUTER_API_KEY = (
    os.environ.get("OPENROUTER_API_KEY") or 
    os.environ.get("DEEPSEEK_API_KEY") or 
    ""
)
QWEN_MODEL = (
    os.environ.get("QWEN_MODEL") or 
    os.environ.get("DEEPSEEK_MODEL") or 
    "qwen/qwen3-next-80b-a3b-thinking"
)

# OpenRouter 排名標頭（可選）
OPENROUTER_REFERER = os.environ.get("OPENROUTER_REFERER", "https://github.com/prompt-scribe")
OPENROUTER_TITLE = os.environ.get("OPENROUTER_TITLE", "Prompt-Scribe Tag Classifier")

# OpenRouter API 配置
LLM_CONFIG = {
    "api_key": OPENROUTER_API_KEY,
    "base_url": "https://openrouter.ai/api/v1",
    "model": QWEN_MODEL,
    "temperature": float(os.environ.get("TEMPERATURE", "0.1")),
    "max_tokens": 4000,
    "timeout": 60,
    "batch_size": int(os.environ.get("BATCH_SIZE", "20")),
    "max_retries": int(os.environ.get("MAX_RETRIES", "3")),
    "retry_delay": 2,
    "extra_headers": {
        "HTTP-Referer": OPENROUTER_REFERER,
        "X-Title": OPENROUTER_TITLE,
    }
}

# 測試標籤（用於驗證）
TEST_TAGS = [
    "thighhighs",
    "navel", 
    "jewelry",
    "cleavage",
    "nipples",
    "dated",
    "username",
    "zzz",
    "colored_tips",
    "off_shoulder"
]

def validate_config():
    """驗證配置是否完整"""
    if not OPENROUTER_API_KEY:
        print("[ERROR] 未設定 OPENROUTER_API_KEY")
        print("\n請設定環境變數：")
        print("  1. 在 stage1 目錄建立 .env 檔案")
        print("  2. 加入以下內容：")
        print("     OPENROUTER_API_KEY=your_api_key_here")
        print("     QWEN_MODEL=qwen/qwen3-next-80b-a3b-thinking")
        return False
    
    print("[OK] API Key 已設定")
    print(f"[OK] 使用模型: {QWEN_MODEL}")
    print(f"[OK] Batch Size: {LLM_CONFIG['batch_size']}")
    print(f"[OK] Temperature: {LLM_CONFIG['temperature']}")
    return True

if __name__ == "__main__":
    print("="*80)
    print("LLM 配置驗證")
    print("="*80)
    validate_config()


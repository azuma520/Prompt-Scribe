"""
OpenAI 模型選擇器
根據 API Key 權限動態選擇可用的模型
"""
import os
import logging
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class ModelSelector:
    """OpenAI 模型選擇器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.available_models: List[str] = []
        self.preferred_models = [
            "gpt-5-nano",
            "gpt-5-mini", 
            "gpt-5",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        self.selected_model: Optional[str] = None
        
    def check_available_models(self) -> List[str]:
        """檢查可用的模型"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                models_data = response.json()
                all_models = [model['id'] for model in models_data.get('data', [])]
                
                # 過濾出我們需要的模型
                self.available_models = [
                    model for model in all_models 
                    if any(pref in model for pref in ['gpt-5', 'gpt-4', 'gpt-3.5'])
                ]
                
                logger.info(f"✅ 發現 {len(self.available_models)} 個可用模型")
                return self.available_models
            else:
                logger.error(f"❌ 獲取模型列表失敗: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 檢查模型時發生錯誤: {e}")
            return []
    
    def select_best_model(self) -> str:
        """選擇最佳可用模型"""
        if not self.available_models:
            self.check_available_models()
        
        # 按優先級選擇模型，並測試每個模型
        for preferred in self.preferred_models:
            if preferred in self.available_models:
                logger.info(f"🔍 測試模型: {preferred}")
                if self.test_model(preferred):
                    self.selected_model = preferred
                    logger.info(f"✅ 選擇模型: {preferred}")
                    return preferred
                else:
                    logger.warning(f"⚠️ 模型 {preferred} 測試失敗，嘗試下一個")
        
        # 如果沒有找到任何可用模型，返回預設值
        logger.warning("⚠️ 未找到任何可用模型，使用預設值 gpt-4o-mini")
        return "gpt-4o-mini"
    
    def test_model(self, model: str) -> bool:
        """測試模型是否可用"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': 'Say "test"'}
                ],
                'max_tokens': 10
            }
            
            # GPT-5 系列不支持 temperature
            if not model.startswith('gpt-5'):
                data['temperature'] = 0.1
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # 檢查回應是否為空
                if not content or len(content.strip()) == 0:
                    logger.warning(f"⚠️ 模型 {model} 返回空內容")
                    return False
                
                logger.info(f"✅ 模型 {model} 測試成功，回應: {content[:50]}")
                return True
            else:
                logger.warning(f"⚠️ 模型 {model} 測試失敗: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 測試模型 {model} 時發生錯誤: {e}")
            return False
    
    def get_model_config(self) -> Dict[str, Any]:
        """獲取模型配置"""
        model = self.select_best_model()
        
        # 根據模型類型調整配置
        config = {
            "model": model,
            "max_tokens": 500,
            "temperature": 0.7,
            "timeout": 30
        }
        
        # GPT-5 系列的特殊配置
        if "gpt-5" in model:
            config.update({
                "max_tokens": 500,
                "temperature": 0.7,
                "timeout": 30
            })
        # GPT-4 系列配置
        elif "gpt-4" in model:
            config.update({
                "max_tokens": 500,
                "temperature": 0.7,
                "timeout": 30
            })
        # GPT-3.5 系列配置
        elif "gpt-3.5" in model:
            config.update({
                "max_tokens": 500,
                "temperature": 0.7,
                "timeout": 30
            })
        
        return config

def get_optimal_model(api_key: str) -> Dict[str, Any]:
    """獲取最佳模型配置"""
    selector = ModelSelector(api_key)
    return selector.get_model_config()

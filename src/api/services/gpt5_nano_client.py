"""
GPT-5 Nano 客戶端服務
用於與 OpenAI GPT-5 Nano 模型進行交互
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

from config import settings
from .gpt5_output_schema import get_gpt5_validator, GPT5TagOutputSchema
from .model_selector import get_optimal_model

logger = logging.getLogger(__name__)


class GPT5NanoClient:
    """OpenAI LLM 客戶端類別
    
    支援的 GPT-5 系列模型（2025 最新）：
    - gpt-5: 複雜推理、廣闊的世界知識、代碼繁重或多步驟代理任務（最強大）
    - gpt-5-mini: 成本優化的推理和聊天；平衡速度、成本和能力（推薦）
    - gpt-5-nano: 高通量任務，特別是簡單的指令遵循或分類（最經濟）
    
    支援的 GPT-4 系列模型：
    - gpt-4o: 多模態旗艦模型
    - gpt-4o-mini: 快速經濟的模型（默認）
    
    注意：GPT-5 系列不支持 temperature、top_p、logprobs 參數
    """
    
    def __init__(self):
        """初始化 OpenAI 客戶端"""
        # 從配置對象讀取
        self.api_key = settings.openai_api_key
        self.enabled = settings.enable_openai_integration
        
        # 使用配置的模型（不進行動態選擇以避免延遲）
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        self.timeout = settings.openai_timeout
        
        # 檢查是否為 GPT-5 系列
        self.is_gpt5 = self.model.startswith("gpt-5")
        
        # 記錄配置狀態
        logger.info("=" * 60)
        logger.info("🤖 GPT-5 Nano 客戶端初始化")
        logger.info(f"  - API Key 已設置: {'✅ 是' if self.api_key else '❌ 否'}")
        logger.info(f"  - 模型: {self.model}")
        logger.info(f"  - 最大 Tokens: {self.max_tokens}")
        logger.info(f"  - 超時時間: {self.timeout}秒")
        logger.info(f"  - 功能啟用: {'✅ 是' if self.enabled else '❌ 否'}")
        logger.info(f"  - OpenAI 庫: {'✅ 已安裝' if openai else '❌ 未安裝'}")
        
        # 記錄使用的模型類型
        if self.enabled:
            model_type = "GPT-5 系列" if self.is_gpt5 else "GPT-4 系列"
            logger.info(f"  - 模型類型: {model_type}")
            if self.is_gpt5:
                logger.info(f"  - 注意: GPT-5 不支持 temperature 參數")
        logger.info("=" * 60)
        
        # 初始化 OpenAI 客戶端
        if self.api_key and openai:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI 客戶端初始化成功")
                
                # 檢測 Responses API 可用性
                self.has_responses_api = hasattr(self.client, 'responses')
                self.prefer_responses_api = True  # 優先使用 Responses API
                
                logger.info(f"  - Responses API: {'✅ 可用' if self.has_responses_api else '❌ 不可用'}")
                
                if self.has_responses_api and self.is_gpt5:
                    logger.info(f"  - 將使用: Responses API (推薦)")
                elif self.is_gpt5:
                    logger.warning(f"  - 將使用: Chat Completions API (Responses API 不可用)")
                else:
                    logger.info(f"  - 將使用: Chat Completions API (GPT-4 系列)")
                    
            except Exception as e:
                self.client = None
                self.has_responses_api = False
                logger.error(f"❌ OpenAI 客戶端初始化失敗: {e}")
        else:
            self.client = None
            self.has_responses_api = False
            if not self.api_key:
                logger.warning("⚠️ OpenAI API key 未設置 (請在環境變數中設置 OPENAI_API_KEY)")
            if not openai:
                logger.warning("⚠️ OpenAI library 未安裝 (執行: pip install openai)")
    
    def is_available(self) -> bool:
        """檢查 GPT-5 Nano 是否可用"""
        return (
            self.enabled and 
            self.client is not None and 
            self.api_key is not None
        )
    
    async def generate_tags(
        self, 
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        生成標籤推薦
        
        Args:
            description: 用戶描述
            context: 額外上下文資訊
            
        Returns:
            標籤推薦結果或 None
        """
        logger.info("=" * 60)
        logger.info("🎯 開始 GPT-5 Nano 標籤生成")
        logger.info(f"  - 描述: {description[:100]}{'...' if len(description) > 100 else ''}")
        
        # 檢查可用性
        if not self.is_available():
            logger.warning("❌ GPT-5 Nano 不可用，使用降級方案")
            logger.warning(f"  - Enabled: {self.enabled}")
            logger.warning(f"  - Client: {self.client is not None}")
            logger.warning(f"  - API Key: {self.api_key is not None}")
            
            # 返回降級方案
            fallback_result = GPT5TagOutputSchema.create_fallback_response(description)
            logger.info("🔄 使用降級方案回應")
            return fallback_result
        
        # 選擇最佳 API
        if self.has_responses_api and self.is_gpt5 and self.prefer_responses_api:
            logger.info("📡 使用 Responses API (推薦)")
            return await self._generate_with_responses_api(description, context)
        else:
            logger.info("📡 使用 Chat Completions API")
            return await self._generate_with_chat_completions(description, context)
    
    async def _generate_with_chat_completions(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """使用 Chat Completions API 生成標籤（備用方案）"""
        try:
            # 構建系統提示詞
            system_prompt = self._build_system_prompt(context)
            logger.info(f"  - System prompt 長度: {len(system_prompt)} 字符")
            
            # 構建用戶提示詞
            user_prompt = self._build_user_prompt(description, context)
            logger.info(f"  - User prompt 長度: {len(user_prompt)} 字符")
            
            # 調用 OpenAI API
            logger.info(f"📡 調用 OpenAI API")
            logger.info(f"  - 模型: {self.model}")
            logger.info(f"  - Max tokens: {self.max_tokens}")
            logger.info(f"  - Timeout: {self.timeout}秒")
            
            # 準備 API 參數
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "timeout": self.timeout
            }
            
            # GPT-5 系列使用特殊參數
            if self.is_gpt5:
                api_params["max_completion_tokens"] = self.max_tokens  # GPT-5 使用 max_completion_tokens
                api_params["reasoning_effort"] = "low"  # 標籤推薦不需要複雜推理
                api_params["verbosity"] = "medium"  # 改為 medium 以提高穩定性
                logger.info(f"  - Max completion tokens: {self.max_tokens} (GPT-5)")
                logger.info(f"  - Reasoning effort: low (GPT-5)")
                logger.info(f"  - Verbosity: medium (GPT-5，提高穩定性)")
                logger.info(f"  - Temperature: N/A (GPT-5 不支持)")
            else:
                api_params["max_tokens"] = self.max_tokens  # GPT-4 使用 max_tokens
                api_params["temperature"] = self.temperature
                logger.info(f"  - Max tokens: {self.max_tokens}")
                logger.info(f"  - Temperature: {self.temperature}")
            
            # 調用 API
            logger.info("⏳ 等待 API 回應...")
            response = self.client.chat.completions.create(**api_params)
            logger.info("✅ API 回應成功")
            
            # 解析回應
            content = response.choices[0].message.content
            logger.info(f"📦 回應內容:")
            logger.info(f"  - 長度: {len(content)} 字符")
            logger.info(f"  - 前 500 字符: {content[:500]}")
            
            # 解析 JSON 回應
            result = self._parse_response(content)
            
            if result:
                logger.info("✅ JSON 解析成功")
                logger.info(f"  - Tags: {result.get('tags', [])[:5]}")
                logger.info(f"  - Confidence: {result.get('confidence', 0)}")
            else:
                logger.error("❌ JSON 解析失敗")
            
            # 記錄使用量
            self._log_usage(response)
            
            logger.info("=" * 60)
            return result
            
        except openai.APIError as e:
            logger.error("=" * 60)
            logger.error(f"❌ OpenAI API 錯誤: {e}")
            logger.error(f"  - 狀態碼: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
            logger.error(f"  - 錯誤訊息: {str(e)}")
            logger.error("=" * 60)
            return None
        except openai.APIConnectionError as e:
            logger.error("=" * 60)
            logger.error(f"❌ OpenAI 連接錯誤: {e}")
            logger.error("  - 可能原因:")
            logger.error("    1. 網路連接問題")
            logger.error("    2. API 金鑰無效")
            logger.error("    3. OpenAI 服務暫時不可用")
            logger.error("=" * 60)
            return None
        except openai.RateLimitError as e:
            logger.error("=" * 60)
            logger.error(f"❌ OpenAI 速率限制: {e}")
            logger.error("  - 建議: 稍後再試或升級 API 方案")
            logger.error("=" * 60)
            return None
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ GPT-5 Nano 未預期的錯誤: {e}", exc_info=True)
            logger.error("=" * 60)
            return None
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """構建系統提示詞（結構化輸出版本）"""
        base_prompt = """You are an expert AI image generation tag recommendation assistant for Danbooru-style tagging system.

Your task:
1. Analyze the user's description carefully
2. Recommend 5-10 relevant English tags that best match the description
3. Tags should follow Danbooru conventions (e.g., "1girl", "long_hair", "blue_eyes", "school_uniform")
4. Prioritize commonly used and effective tags
5. Include character, appearance, clothing, and scene tags as appropriate

Tag Categories:
- Character count: 1girl, 2girls, solo, multiple_girls
- Physical features: long_hair, short_hair, blue_eyes, blonde_hair
- Clothing: school_uniform, dress, shirt, skirt
- Actions: sitting, standing, smiling, looking_at_viewer
- Scene: outdoors, indoors, city, forest, night, sunset
- Art style: anime_style, realistic, masterpiece, high_quality

CRITICAL: You MUST return a valid JSON object in this EXACT format:
{
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "confidence": 0.85,
    "reasoning": "Brief explanation of why these tags were chosen",
    "categories": ["CHARACTER", "APPEARANCE", "SCENE"]
}

VALIDATION RULES (strictly enforced):
- "tags": Array of 1-15 strings, English only, use underscores for multi-word tags
- "confidence": Number between 0.6 and 0.95
- "reasoning": Non-empty string explaining your choices (max 500 chars)
- "categories": Optional array from: CHARACTER, APPEARANCE, CLOTHING, ACTION, SCENE, STYLE, OBJECT, COMPOSITION, EFFECT
- Return ONLY the JSON object, no other text
- All field names must be exactly as shown above

Examples of valid tags:
- "1girl", "solo", "long_hair", "blue_eyes", "school_uniform"
- "smiling", "looking_at_viewer", "outdoors", "sunset"
- "anime_style", "masterpiece", "high_quality" """
        
        if context:
            context_info = f"\n\nAdditional context: {json.dumps(context, ensure_ascii=False)}"
            base_prompt += context_info
        
        return base_prompt
    
    def _build_user_prompt(self, description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """構建用戶提示詞"""
        prompt = f"User Description: \"{description}\"\n\nPlease analyze this description and recommend the most appropriate Danbooru-style tags for AI image generation."
        
        if context and context.get("existing_tags"):
            prompt += f"\n\nExisting tags to consider: {', '.join(context['existing_tags'])}"
        
        if context and context.get("user_preferences"):
            prompt += f"\n\nUser preferences: {context['user_preferences']}"
        
        if context and context.get("style_hint"):
            prompt += f"\n\nStyle hint: {context['style_hint']}"
        
        return prompt
    
    def _parse_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析 GPT-5 Nano 回應（使用結構化驗證，強化錯誤處理）"""
        try:
            # 檢查空回應
            if not content or len(content.strip()) == 0:
                logger.error(f"❌ 收到空回應")
                return None
            
            # 清理回應內容（移除可能的 markdown 代碼塊）
            cleaned_content = content.strip()
            if cleaned_content.startswith("```"):
                lines = cleaned_content.split('\n')
                # 移除開頭的 ```json 或 ```
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # 移除結尾的 ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned_content = '\n'.join(lines).strip()
            
            # 提取 JSON 部分（如果有額外文字）
            if '{' in cleaned_content and '}' in cleaned_content:
                start = cleaned_content.find('{')
                end = cleaned_content.rfind('}') + 1
                json_part = cleaned_content[start:end]
            else:
                json_part = cleaned_content
            
            # 使用結構化驗證系統
            validator = get_gpt5_validator()
            result = validator.validate(json_part)
            
            # 檢查驗證結果
            if result is None:
                logger.error("❌ Validator returned None")
                return None
            
            # 添加額外的元資料
            result["generated_at"] = datetime.now().isoformat()
            result["source"] = self.model
            result["validation_method"] = "json_schema_v1"
            
            # 記錄驗證統計
            stats = validator.get_stats()
            logger.info(f"📊 驗證統計: 成功率 {stats['success_rate']}% ({stats['successful']}/{stats['total_validations']})")
            
            logger.info(f"✅ 返回完整結果，包含 keys: {list(result.keys())}")
            return result
            
        except ValueError as e:
            logger.error(f"❌ GPT-5 回應驗證失敗: {e}")
            logger.error(f"Raw response: {content[:200] if content else '(empty)'}...")
            return None
        except Exception as e:
            logger.error(f"❌ 未預期的解析錯誤: {e}", exc_info=True)
            logger.error(f"Raw response: {content[:200] if content else '(empty)'}...")
            return None
    
    def _log_usage(self, response) -> Dict[str, Any]:
        """
        記錄 API 使用量並計算成本
        
        GPT-5 Nano 定價 (2025 最新):
        - Input: $0.00002 / 1K tokens
        - Output: $0.00008 / 1K tokens
        
        Returns:
            使用量統計字典
        """
        usage_stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "model": self.model
        }
        
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                usage_stats["prompt_tokens"] = usage.prompt_tokens
                usage_stats["completion_tokens"] = usage.completion_tokens
                usage_stats["total_tokens"] = usage.total_tokens
                
                # 根據模型計算實際成本
                if self.model == "gpt-5-nano":
                    # GPT-5 Nano 定價
                    input_cost = (usage.prompt_tokens / 1000) * 0.00002
                    output_cost = (usage.completion_tokens / 1000) * 0.00008
                elif self.model == "gpt-5-mini":
                    # GPT-5 Mini 定價（預估）
                    input_cost = (usage.prompt_tokens / 1000) * 0.00005
                    output_cost = (usage.completion_tokens / 1000) * 0.0002
                elif self.model.startswith("gpt-4"):
                    # GPT-4 系列定價（預估）
                    input_cost = (usage.prompt_tokens / 1000) * 0.00015
                    output_cost = (usage.completion_tokens / 1000) * 0.0006
                else:
                    # 默認使用 GPT-5 Nano 價格
                    input_cost = (usage.prompt_tokens / 1000) * 0.00002
                    output_cost = (usage.completion_tokens / 1000) * 0.00008
                
                total_cost = input_cost + output_cost
                usage_stats["estimated_cost_usd"] = total_cost
                usage_stats["input_cost_usd"] = input_cost
                usage_stats["output_cost_usd"] = output_cost
                
                logger.info("💰 API 使用量統計:")
                logger.info(f"  - Prompt tokens: {usage.prompt_tokens}")
                logger.info(f"  - Completion tokens: {usage.completion_tokens}")
                logger.info(f"  - Total tokens: {usage.total_tokens}")
                logger.info(f"  - Input cost: ${input_cost:.6f}")
                logger.info(f"  - Output cost: ${output_cost:.6f}")
                logger.info(f"  - Total cost: ${total_cost:.6f} USD")
                
                # 計算每月成本預估
                monthly_estimate_1k = total_cost * 1000
                monthly_estimate_10k = total_cost * 10000
                logger.info(f"  - 月度成本預估:")
                logger.info(f"    • 1,000 次調用: ${monthly_estimate_1k:.2f}")
                logger.info(f"    • 10,000 次調用: ${monthly_estimate_10k:.2f}")
                
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
        
        return usage_stats
    
    async def _generate_with_responses_api(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """使用 Responses API 生成標籤（優先方案）"""
        try:
            # 構建 instructions (系統提示詞)
            instructions = self._build_system_prompt(context)
            logger.info(f"  - Instructions 長度: {len(instructions)} 字符")
            
            # 構建 input (用戶輸入)
            user_input = self._build_user_prompt(description, context)
            logger.info(f"  - Input 長度: {len(user_input)} 字符")
            
            # 調用 Responses API
            logger.info(f"📡 調用 Responses API")
            logger.info(f"  - 模型: {self.model}")
            logger.info(f"  - Reasoning effort: low")
            logger.info(f"  - Text verbosity: medium")
            logger.info(f"  - Max output tokens: {self.max_tokens}")
            
            logger.info("⏳ 等待 API 回應...")
            
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=user_input,
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
                                    "items": {"type": "string"},
                                    "minItems": 1,
                                    "maxItems": 15
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0
                                },
                                "reasoning": {
                                    "type": "string",
                                    "maxLength": 500
                                },
                                "categories": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "CHARACTER", "APPEARANCE", "CLOTHING", "ACTION", 
                                            "SCENE", "STYLE", "OBJECT", "COMPOSITION", "EFFECT"
                                        ]
                                    }
                                }
                            },
                            "required": ["tags", "confidence", "reasoning", "categories"],
                            "additionalProperties": False
                        }
                    }
                },
                max_output_tokens=self.max_tokens
            )
            
            logger.info("✅ API 回應成功")
            
            # 獲取回應文字
            output_text = response.output_text
            logger.info(f"📦 回應內容:")
            logger.info(f"  - 長度: {len(output_text)} 字符")
            logger.info(f"  - 前 200 字符: {output_text[:200]}")
            
            # 解析回應（Responses API 已經保證 JSON 格式）
            result = self._parse_response(output_text)
            
            if result:
                logger.info("✅ JSON 解析成功")
                logger.info(f"  - Tags: {result.get('tags', [])[:5]}")
                logger.info(f"  - Confidence: {result.get('confidence', 0)}")
            else:
                logger.error("❌ JSON 解析失敗")
            
            # 記錄使用量
            self._log_responses_api_usage(response)
            
            logger.info("=" * 60)
            return result
            
        except openai.APIError as e:
            logger.error("=" * 60)
            logger.error(f"❌ Responses API 錯誤: {e}")
            logger.error(f"  - 狀態碼: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
            logger.error("=" * 60)
            return None
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ Responses API 未預期錯誤: {e}", exc_info=True)
            logger.error("=" * 60)
            return None
    
    def _log_responses_api_usage(self, response) -> Dict[str, Any]:
        """記錄 Responses API 使用量"""
        usage_stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "model": self.model,
            "api_type": "responses"
        }
        
        try:
            # Responses API 的 usage 可能在不同位置
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                
                # 嘗試獲取 token 數據
                prompt_tokens = getattr(usage, 'input_tokens', 0) or getattr(usage, 'prompt_tokens', 0)
                completion_tokens = getattr(usage, 'output_tokens', 0) or getattr(usage, 'completion_tokens', 0)
                total_tokens = getattr(usage, 'total_tokens', 0) or (prompt_tokens + completion_tokens)
                
                usage_stats["prompt_tokens"] = prompt_tokens
                usage_stats["completion_tokens"] = completion_tokens
                usage_stats["total_tokens"] = total_tokens
                
                # 計算成本
                if self.model == "gpt-5-mini":
                    input_cost = (prompt_tokens / 1000) * 0.00005
                    output_cost = (completion_tokens / 1000) * 0.0002
                else:
                    input_cost = (prompt_tokens / 1000) * 0.00002
                    output_cost = (completion_tokens / 1000) * 0.00008
                
                total_cost = input_cost + output_cost
                usage_stats["estimated_cost_usd"] = total_cost
                
                logger.info("💰 Responses API 使用量:")
                logger.info(f"  - Input tokens: {prompt_tokens}")
                logger.info(f"  - Output tokens: {completion_tokens}")
                logger.info(f"  - Total tokens: {total_tokens}")
                logger.info(f"  - 成本: ${total_cost:.6f}")
                
        except Exception as e:
            logger.error(f"記錄 Responses API 使用量失敗: {e}")
        
        return usage_stats
    
    async def test_connection(self) -> Dict[str, Any]:
        """測試 GPT-5 Nano 連接"""
        test_result = {
            "available": False,
            "error": None,
            "config": {},
            "test_response": None,
            "validation_stats": None
        }
        
        try:
            # 檢查配置
            test_result["config"] = {
                "api_key_set": bool(self.api_key),
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "timeout": self.timeout,
                "enabled": self.enabled
            }
            
            # 獲取驗證統計
            validator = get_gpt5_validator()
            test_result["validation_stats"] = validator.get_stats()
            
            if not self.is_available():
                test_result["error"] = "GPT-5 Nano not available"
                return test_result
            
            # 測試 API 調用
            test_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一個測試助手。請回應 'Hello, OpenAI!'"},
                    {"role": "user", "content": "請回應測試訊息"}
                ],
                "max_completion_tokens": 50,
                "timeout": 10
            }
            
            # 只有非 GPT-5 模型才添加 temperature
            if not self.is_gpt5:
                test_params["temperature"] = 0.1
            
            test_response = self.client.chat.completions.create(**test_params)
            
            test_result["available"] = True
            test_result["test_response"] = test_response.choices[0].message.content
            
        except Exception as e:
            test_result["error"] = str(e)
            logger.error(f"GPT-5 Nano connection test failed: {e}")
        
        return test_result
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """獲取驗證統計信息"""
        validator = get_gpt5_validator()
        return validator.get_stats()
    
    def reset_validation_stats(self) -> None:
        """重置驗證統計"""
        validator = get_gpt5_validator()
        validator.reset_stats()


# 全域實例
_gpt5_nano_client = None


def get_gpt5_nano_client() -> GPT5NanoClient:
    """獲取 GPT-5 Nano 客戶端實例"""
    global _gpt5_nano_client
    if _gpt5_nano_client is None:
        _gpt5_nano_client = GPT5NanoClient()
    return _gpt5_nano_client

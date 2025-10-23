"""
Prompt-Scribe API Configuration
專案: PLAN-2025-005
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    """API 配置設定"""
    
    # 應用基本設定
    app_name: str = "Prompt-Scribe API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Supabase 設定
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: Optional[str] = None
    
    # API 設定
    api_prefix: str = "/api"
    cors_origins: Optional[list[str]] = None
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if v is None:
            return ["*"]
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return ["*"]
        return v
    max_results_limit: int = 100
    default_results_limit: int = 20
    
    # 快取設定
    cache_ttl_seconds: int = 3600  # 1 小時
    cache_max_size: int = 1000
    
    # LLM 設定
    llm_default_max_tags: int = 10
    llm_min_popularity: int = 100
    llm_exclude_adult_default: bool = True
    
    # 效能設定
    request_timeout_seconds: int = 30
    db_connection_pool_size: int = 10
    
    # 日誌設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_emoji: bool = False  # 是否在日誌中輸出 emoji（預設關閉以避免編碼問題）
    
    # Redis 設定
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True
    redis_key_prefix: str = "prompt_scribe:"
    redis_default_ttl: int = 3600
    
    # 快取策略設定
    cache_strategy: str = "hybrid"  # memory, redis, hybrid
    hybrid_l1_ttl: int = 300
    hybrid_l2_ttl: int = 3600

    # OpenAI / GPT-5 設定
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-5-mini"  # gpt-5-nano, gpt-5-mini, gpt-5, gpt-4o, gpt-4o-mini
    openai_max_tokens: int = 500
    openai_temperature: float = 0.7
    openai_timeout: int = 30
    enable_openai_integration: bool = True  # 預設啟用，可透過環境變數覆蓋

    # 代理設定（公司網路可選）
    http_proxy: Optional[str] = None  # e.g. http://proxy.company.com:8080
    https_proxy: Optional[str] = None  # e.g. http://proxy.company.com:8080
    all_proxy: Optional[str] = None  # 兼容 socks/http 統一入口
    
    # Pydantic v2 設定：讀取 .env，忽略多餘變數，大小寫不敏感
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


# 全域配置實例
settings = Settings()


def get_settings() -> Settings:
    """獲取配置實例"""
    return settings


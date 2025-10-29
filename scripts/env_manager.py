#!/usr/bin/env python3
"""
環境變數管理工具
提供標準化的環境變數載入和驗證功能
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

class EnvironmentManager:
    """環境變數管理器"""
    
    REQUIRED_VARS = [
        'OPENAI_API_KEY',
        'SUPABASE_URL', 
        'SUPABASE_SERVICE_KEY'
    ]
    
    OPTIONAL_VARS = {
        'OPENAI_MODEL': 'gpt-5-mini',
        'ENABLE_OPENAI_INTEGRATION': 'true',
        'DEBUG': 'false',
        'LOG_LEVEL': 'INFO'
    }
    
    def __init__(self, env_file: str = '.env'):
        """初始化環境變數管理器"""
        self.env_file = env_file
        self.loaded = False
        
    def load_environment(self) -> bool:
        """載入環境變數"""
        try:
            # 載入 .env 檔案
            if os.path.exists(self.env_file):
                load_dotenv(self.env_file)
                print(f"SUCCESS: Loaded environment from {self.env_file}")
            else:
                print(f"WARNING: {self.env_file} not found, using system environment")
            
            # 設定預設值
            for var, default_value in self.OPTIONAL_VARS.items():
                if not os.environ.get(var):
                    os.environ[var] = default_value
            
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to load environment: {e}")
            return False
    
    def validate_environment(self) -> bool:
        """驗證必要的環境變數"""
        if not self.loaded:
            print("ERROR: Environment not loaded. Call load_environment() first.")
            return False
        
        missing_vars = []
        for var in self.REQUIRED_VARS:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            print("Please ensure .env file contains all required variables")
            return False
        
        print("SUCCESS: All required environment variables are set")
        return True
    
    def get_config(self) -> Dict[str, str]:
        """獲取所有環境變數配置"""
        if not self.loaded:
            self.load_environment()
        
        config = {}
        for var in self.REQUIRED_VARS + list(self.OPTIONAL_VARS.keys()):
            config[var] = os.environ.get(var, '')
        
        return config
    
    def print_status(self):
        """打印環境變數狀態"""
        print("=" * 60)
        print("Environment Variables Status")
        print("=" * 60)
        
        config = self.get_config()
        
        for var in self.REQUIRED_VARS:
            value = config.get(var, '')
            if value:
                # 隱藏敏感資訊
                if 'KEY' in var or 'SECRET' in var:
                    display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                else:
                    display_value = value
                print(f"SUCCESS: {var}: {display_value}")
            else:
                print(f"ERROR: {var}: Not Set")
        
        print("\nOptional Variables:")
        for var, default in self.OPTIONAL_VARS.items():
            value = config.get(var, default)
            print(f"  {var}: {value}")
        
        print("=" * 60)

def get_environment_manager() -> EnvironmentManager:
    """獲取環境變數管理器實例"""
    return EnvironmentManager()

def ensure_environment_loaded() -> bool:
    """確保環境變數已載入並驗證"""
    manager = get_environment_manager()
    
    if not manager.load_environment():
        return False
    
    if not manager.validate_environment():
        return False
    
    return True

if __name__ == "__main__":
    # 測試環境變數管理
    manager = get_environment_manager()
    manager.print_status()
    
    if manager.load_environment():
        print("\nEnvironment loaded successfully!")
        if manager.validate_environment():
            print("All required variables are set!")
        else:
            print("Some required variables are missing.")
    else:
        print("Failed to load environment.")

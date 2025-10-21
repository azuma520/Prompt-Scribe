# GPT-5 Mini 環境變數設置指南

## 📋 概述

本指南協助您設置 GPT-5 Mini 所需的環境變數，適用於本地開發和 Zeabur 部署。

---

## 🔑 必要的環境變數

### 1. OpenAI API Key

```bash
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

**如何獲取**：
1. 訪問 https://platform.openai.com/api-keys
2. 登入您的 OpenAI 帳戶
3. 點擊 "Create new secret key"
4. 複製生成的 API Key

⚠️ **重要**：請勿將 API Key 提交到 Git！

### 2. Supabase 配置（已有）

```bash
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 3. OpenAI 模型配置（可選）

```bash
# 預設使用 gpt-5-mini，可以覆蓋
OPENAI_MODEL=gpt-5-mini

# 功能開關
ENABLE_OPENAI_INTEGRATION=true
```

---

## 💻 本地開發設置

### 方法 1: 使用 PowerShell 腳本（推薦）

創建並運行設置腳本：

#### 步驟 1: 編輯 `setup_env_local.ps1`

```powershell
# setup_env_local.ps1
# GPT-5 Mini 本地環境設置腳本

Write-Host "🔧 設置 Prompt-Scribe GPT-5 Mini 環境變數" -ForegroundColor Cyan
Write-Host "=" * 60

# ============================================
# 請在這裡填入您的實際 API Keys
# ============================================

# OpenAI API Key（必填）
$env:OPENAI_API_KEY = "sk-proj-your-actual-key-here"

# Supabase 配置（必填）
$env:SUPABASE_URL = "https://fumuvmbhmmzkenizksyq.supabase.co"
$env:SUPABASE_ANON_KEY = "your-supabase-anon-key-here"

# OpenAI 模型設置（可選，已有預設值）
$env:OPENAI_MODEL = "gpt-5-mini"
$env:ENABLE_OPENAI_INTEGRATION = "true"

# 其他設置
$env:DEBUG = "false"
$env:LOG_LEVEL = "INFO"

# ============================================
# 驗證設置
# ============================================

Write-Host ""
Write-Host "✅ 環境變數已設置:" -ForegroundColor Green
Write-Host "  OPENAI_API_KEY: $(if($env:OPENAI_API_KEY -and $env:OPENAI_API_KEY -ne 'sk-proj-your-actual-key-here') {'已設置 (' + $env:OPENAI_API_KEY.Substring(0,8) + '...)'} else {'❌ 未設置或使用預設值'})" -ForegroundColor $(if($env:OPENAI_API_KEY -and $env:OPENAI_API_KEY -ne 'sk-proj-your-actual-key-here') {'Green'} else {'Red'})
Write-Host "  OPENAI_MODEL: $env:OPENAI_MODEL"
Write-Host "  ENABLE_OPENAI_INTEGRATION: $env:ENABLE_OPENAI_INTEGRATION"
Write-Host "  SUPABASE_URL: $env:SUPABASE_URL"

Write-Host ""
if ($env:OPENAI_API_KEY -eq "sk-proj-your-actual-key-here") {
    Write-Host "⚠️  警告: 請編輯此文件並填入實際的 OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "   1. 用文本編輯器打開 setup_env_local.ps1" -ForegroundColor Yellow
    Write-Host "   2. 將 'sk-proj-your-actual-key-here' 替換為您的實際 API Key" -ForegroundColor Yellow
    Write-Host "   3. 保存並重新運行此腳本" -ForegroundColor Yellow
} else {
    Write-Host "🚀 環境變數設置完成！您可以:" -ForegroundColor Green
    Write-Host "   1. 運行: python run_server.py" -ForegroundColor Cyan
    Write-Host "   2. 或運行: python diagnose_model.py" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" * 60


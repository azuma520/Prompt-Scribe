# GPT-5 Nano 測試伺服器啟動腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 啟動 Prompt-Scribe 測試伺服器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切換到 API 目錄
Set-Location "D:\Prompt-Scribe\src\api"

Write-Host "📍 工作目錄: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# 檢查 Python
Write-Host "🔍 檢查 Python 環境..." -ForegroundColor Yellow
python --version
Write-Host ""

# 檢查環境變數
Write-Host "🔍 檢查環境變數..." -ForegroundColor Yellow
if ($env:OPENAI_API_KEY) {
    Write-Host "✅ OPENAI_API_KEY: 已設置" -ForegroundColor Green
} else {
    Write-Host "⚠️  OPENAI_API_KEY: 未設置" -ForegroundColor Red
}

if ($env:SUPABASE_URL) {
    Write-Host "✅ SUPABASE_URL: 已設置" -ForegroundColor Green
} else {
    Write-Host "⚠️  SUPABASE_URL: 未設置" -ForegroundColor Red
}

if ($env:SUPABASE_KEY) {
    Write-Host "✅ SUPABASE_KEY: 已設置" -ForegroundColor Green
} else {
    Write-Host "⚠️  SUPABASE_KEY: 未設置" -ForegroundColor Red
}
Write-Host ""

# 啟動伺服器
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 啟動 FastAPI 伺服器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 伺服器地址: http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API 文檔: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "🔧 健康檢查: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止伺服器" -ForegroundColor Yellow
Write-Host ""

# 啟動 uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info

# 啟動伺服器並保留環境變數
# 這個腳本會在當前 PowerShell session 中啟動伺服器，保留所有環境變數

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Inspire Server with ENV" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 顯示環境變數狀態
Write-Host "Environment variables:" -ForegroundColor Yellow

if ($env:OPENAI_API_KEY) {
    $masked = $env:OPENAI_API_KEY.Substring(0, 10) + "..."
    Write-Host "  OPENAI_API_KEY: $masked" -ForegroundColor Green
} else {
    Write-Host "  OPENAI_API_KEY: [NOT SET]" -ForegroundColor Red
}

if ($env:SUPABASE_URL) {
    Write-Host "  SUPABASE_URL: $env:SUPABASE_URL" -ForegroundColor Green
} else {
    Write-Host "  SUPABASE_URL: [NOT SET]" -ForegroundColor Red
}

if ($env:SUPABASE_ANON_KEY) {
    $masked = $env:SUPABASE_ANON_KEY.Substring(0, 10) + "..."
    Write-Host "  SUPABASE_ANON_KEY: $masked" -ForegroundColor Green
} else {
    Write-Host "  SUPABASE_ANON_KEY: [NOT SET]" -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host "Server will run at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# 切換到 API 目錄並啟動
Set-Location src/api
python main.py


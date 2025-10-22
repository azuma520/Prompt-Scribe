# Inspire Agent 伺服器啟動腳本
# 自動切換到正確目錄並啟動伺服器

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Inspire Agent Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查環境變數
Write-Host "Checking environment variables..." -ForegroundColor Yellow

$has_openai = -not [string]::IsNullOrEmpty($env:OPENAI_API_KEY)
$has_supabase_url = -not [string]::IsNullOrEmpty($env:SUPABASE_URL)
$has_supabase_key = -not [string]::IsNullOrEmpty($env:SUPABASE_ANON_KEY)

if ($has_openai) {
    $masked_key = $env:OPENAI_API_KEY.Substring(0, 10) + "..."
    Write-Host "[OK] OPENAI_API_KEY: $masked_key" -ForegroundColor Green
} else {
    Write-Host "[WARN] OPENAI_API_KEY not set" -ForegroundColor Yellow
}

if ($has_supabase_url) {
    Write-Host "[OK] SUPABASE_URL: $env:SUPABASE_URL" -ForegroundColor Green
} else {
    Write-Host "[WARN] SUPABASE_URL not set" -ForegroundColor Yellow
}

if ($has_supabase_key) {
    $masked_key = $env:SUPABASE_ANON_KEY.Substring(0, 10) + "..."
    Write-Host "[OK] SUPABASE_ANON_KEY: $masked_key" -ForegroundColor Green
} else {
    Write-Host "[WARN] SUPABASE_ANON_KEY not set" -ForegroundColor Yellow
}

Write-Host ""

# 切換到 API 目錄
Write-Host "Changing to API directory..." -ForegroundColor Yellow
Set-Location -Path "src/api"
Write-Host "[OK] Current directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# 啟動伺服器
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "Server will start at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Inspire Health: http://localhost:8000/api/inspire/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 啟動伺服器（前台，這樣可以看到日誌）
python main.py


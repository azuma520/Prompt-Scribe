# 啟動後端服務器的 PowerShell 腳本
Write-Host "🚀 正在啟動 Prompt-Scribe 後端服務器..." -ForegroundColor Green

# 設置環境變數
$env:SUPABASE_URL = "http://localhost:54321"
$env:SUPABASE_ANON_KEY = "test-key"
$env:OPENAI_API_KEY = "test-key"

# 切換到 src 目錄
Set-Location "src"

# 檢查 main.py 是否存在
if (Test-Path "api/main.py") {
    Write-Host "✅ 找到 main.py，正在啟動服務器..." -ForegroundColor Green
    
    # 啟動服務器
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    Write-Host "❌ 在 src 目錄中找不到 api/main.py" -ForegroundColor Red
    Write-Host "當前目錄: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "目錄內容:" -ForegroundColor Yellow
    Get-ChildItem | Format-Table Name, Mode
}


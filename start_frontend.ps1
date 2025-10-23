# 啟動前端服務器的 PowerShell 腳本
Write-Host "🚀 正在啟動 Inspire Agent 前端服務器..." -ForegroundColor Green

# 切換到前端目錄
Set-Location "prompt-scribe-web"

# 檢查 package.json 是否存在
if (Test-Path "package.json") {
    Write-Host "✅ 找到 package.json，正在啟動開發服務器..." -ForegroundColor Green
    
    # 啟動開發服務器
    npm run dev
} else {
    Write-Host "❌ 在 prompt-scribe-web 目錄中找不到 package.json" -ForegroundColor Red
    Write-Host "當前目錄: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "目錄內容:" -ForegroundColor Yellow
    Get-ChildItem | Format-Table Name, Mode
}

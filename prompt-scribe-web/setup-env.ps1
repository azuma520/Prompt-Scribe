# Prompt-Scribe Web 環境設置腳本
# 用於快速設置開發環境

Write-Host "🚀 Prompt-Scribe Web 環境設置" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 檢查是否在正確的目錄
if (-not (Test-Path "package.json")) {
    Write-Host "❌ 錯誤：請在 prompt-scribe-web 目錄下執行此腳本" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 目錄正確" -ForegroundColor Green

# 創建 .env.local 文件
Write-Host ""
Write-Host "📝 創建 .env.local 文件..." -ForegroundColor Yellow

$envContent = @"
# Prompt-Scribe Web Frontend 環境變數

# API 基礎 URL (Zeabur 生產環境)
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.zeabur.app

# API 超時設置（毫秒）
NEXT_PUBLIC_API_TIMEOUT=30000

# 環境
NEXT_PUBLIC_ENV=development
"@

$envContent | Out-File -FilePath ".env.local" -Encoding utf8 -Force

if (Test-Path ".env.local") {
    Write-Host "✅ .env.local 創建成功！" -ForegroundColor Green
} else {
    Write-Host "❌ .env.local 創建失敗" -ForegroundColor Red
    exit 1
}

# 顯示環境變數內容
Write-Host ""
Write-Host "📋 環境變數內容：" -ForegroundColor Cyan
Get-Content ".env.local" | ForEach-Object {
    if ($_ -and -not $_.StartsWith("#")) {
        Write-Host "   $_" -ForegroundColor Gray
    }
}

# 測試 API 連接
Write-Host ""
Write-Host "🔍 測試 API 連接..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "https://prompt-scribe-api.zeabur.app/health" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API 連接成功！" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  API 連接失敗，請檢查網路連接" -ForegroundColor Yellow
    Write-Host "   錯誤訊息: $($_.Exception.Message)" -ForegroundColor Red
}

# 安裝依賴（如果需要）
Write-Host ""
Write-Host "📦 檢查依賴..." -ForegroundColor Yellow

if (Test-Path "node_modules") {
    Write-Host "✅ 依賴已安裝" -ForegroundColor Green
} else {
    Write-Host "⏳ 正在安裝依賴..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ 依賴安裝完成" -ForegroundColor Green
}

# 完成
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "🎉 設置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "1. 啟動開發伺服器：npm run dev" -ForegroundColor White
Write-Host "2. 訪問應用：http://localhost:3000" -ForegroundColor White
Write-Host "3. 測試標籤搜尋：http://localhost:3000/tags" -ForegroundColor White
Write-Host ""


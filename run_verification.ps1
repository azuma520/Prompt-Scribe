# GPT-5 修復驗證腳本
# 快速運行驗證測試

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GPT-5 Nano Schema 修復驗證" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 檢查虛擬環境
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "🔧 啟動虛擬環境..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ 找不到虛擬環境，使用系統 Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 選擇要執行的操作:" -ForegroundColor Green
Write-Host "  1. 快速驗證 (verify_gpt5_fixes.py)" -ForegroundColor White
Write-Host "  2. 完整測試 (pytest)" -ForegroundColor White
Write-Host "  3. 兩者都執行" -ForegroundColor White
Write-Host ""

$choice = Read-Host "請輸入選項 (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 執行快速驗證..." -ForegroundColor Cyan
        python verify_gpt5_fixes.py
    }
    "2" {
        Write-Host ""
        Write-Host "🧪 執行 pytest 測試..." -ForegroundColor Cyan
        pytest tests/test_gpt5_schema_consistency.py -v --tb=short
    }
    "3" {
        Write-Host ""
        Write-Host "🚀 執行快速驗證..." -ForegroundColor Cyan
        python verify_gpt5_fixes.py
        
        Write-Host ""
        Write-Host "🧪 執行 pytest 測試..." -ForegroundColor Cyan
        pytest tests/test_gpt5_schema_consistency.py -v --tb=short
    }
    default {
        Write-Host "❌ 無效的選項" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  驗證完成！" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 詢問是否要查看改進文檔
Write-Host "📚 是否要查看改進文檔？(y/n)" -ForegroundColor Green
$viewDoc = Read-Host

if ($viewDoc -eq "y" -or $viewDoc -eq "Y") {
    if (Test-Path ".\GPT5_CLIENT_IMPROVEMENTS.md") {
        notepad .\GPT5_CLIENT_IMPROVEMENTS.md
    } else {
        Write-Host "❌ 找不到 GPT5_CLIENT_IMPROVEMENTS.md" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ 完成！" -ForegroundColor Green







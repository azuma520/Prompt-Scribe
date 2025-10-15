# API 測試執行腳本（Windows PowerShell）
# 使用方式: .\run_tests.ps1 [test_type]
# test_type: all, quick, cache, batch, load, coverage

param(
    [string]$TestType = "all"
)

Write-Host "========================================" -ForegroundColor Blue
Write-Host "   Prompt-Scribe API 測試執行器" -ForegroundColor Blue
Write-Host "========================================`n" -ForegroundColor Blue

# 檢查測試依賴
function Check-Dependencies {
    Write-Host "檢查測試依賴..." -ForegroundColor Yellow
    
    try {
        python -c "import pytest" 2>$null
        Write-Host "✅ 測試依賴已安裝`n" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ pytest 未安裝，正在安裝..." -ForegroundColor Red
        pip install -r tests/requirements-test.txt
    }
}

# 快速測試（不需資料庫）
function Run-QuickTests {
    Write-Host "執行快速測試（不需資料庫）..." -ForegroundColor Blue
    pytest tests/test_cache.py -v -s --tb=short
}

# 快取測試
function Run-CacheTests {
    Write-Host "執行快取功能測試..." -ForegroundColor Blue
    pytest tests/test_cache.py -v -s --tb=short
}

# 批量查詢測試
function Run-BatchTests {
    Write-Host "執行批量查詢測試（需要 Supabase 連接）..." -ForegroundColor Blue
    pytest tests/test_batch_queries.py -v -s --tb=short
}

# 負載測試
function Run-LoadTests {
    Write-Host "執行負載和併發測試..." -ForegroundColor Blue
    pytest tests/test_load_performance.py -v -s --tb=short
}

# 所有測試
function Run-AllTests {
    Write-Host "執行所有測試..." -ForegroundColor Blue
    pytest tests/ -v --tb=short
}

# 覆蓋率測試
function Run-CoverageTests {
    Write-Host "執行測試並生成覆蓋率報告..." -ForegroundColor Blue
    pytest tests/ --cov=. --cov-report=html --cov-report=term
    Write-Host "`n✅ 覆蓋率報告已生成至 htmlcov/index.html" -ForegroundColor Green
}

# 並行測試
function Run-ParallelTests {
    Write-Host "執行並行測試（4 個工作程序）..." -ForegroundColor Blue
    pytest tests/ -v -n 4 --tb=short
}

# 主程式
Check-Dependencies

switch ($TestType.ToLower()) {
    "quick" {
        Run-QuickTests
    }
    "cache" {
        Run-CacheTests
    }
    "batch" {
        Run-BatchTests
    }
    "load" {
        Run-LoadTests
    }
    "coverage" {
        Run-CoverageTests
    }
    "parallel" {
        Run-ParallelTests
    }
    "all" {
        Run-AllTests
    }
    default {
        Write-Host "使用方式: .\run_tests.ps1 [test_type]"
        Write-Host "test_type 選項:"
        Write-Host "  quick    - 快速測試（不需資料庫）"
        Write-Host "  cache    - 快取功能測試"
        Write-Host "  batch    - 批量查詢測試"
        Write-Host "  load     - 負載測試"
        Write-Host "  coverage - 生成覆蓋率報告"
        Write-Host "  parallel - 並行測試"
        Write-Host "  all      - 所有測試（預設）"
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   測試執行完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green


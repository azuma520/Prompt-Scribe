#!/bin/bash
# API 測試執行腳本
# 使用方式: ./run_tests.sh [test_type]
# test_type: all, quick, cache, batch, load, coverage

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Prompt-Scribe API 測試執行器${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 檢查測試依賴
check_dependencies() {
    echo -e "${YELLOW}檢查測試依賴...${NC}"
    if ! python -c "import pytest" 2>/dev/null; then
        echo "❌ pytest 未安裝，正在安裝..."
        pip install -r tests/requirements-test.txt
    else
        echo -e "${GREEN}✅ 測試依賴已安裝${NC}\n"
    fi
}

# 快速測試（不需資料庫）
run_quick_tests() {
    echo -e "${BLUE}執行快速測試（不需資料庫）...${NC}"
    pytest tests/test_cache.py -v -s --tb=short
}

# 快取測試
run_cache_tests() {
    echo -e "${BLUE}執行快取功能測試...${NC}"
    pytest tests/test_cache.py -v -s --tb=short
}

# 批量查詢測試
run_batch_tests() {
    echo -e "${BLUE}執行批量查詢測試（需要 Supabase 連接）...${NC}"
    pytest tests/test_batch_queries.py -v -s --tb=short
}

# 負載測試
run_load_tests() {
    echo -e "${BLUE}執行負載和併發測試...${NC}"
    pytest tests/test_load_performance.py -v -s --tb=short
}

# 所有測試
run_all_tests() {
    echo -e "${BLUE}執行所有測試...${NC}"
    pytest tests/ -v --tb=short
}

# 覆蓋率測試
run_coverage_tests() {
    echo -e "${BLUE}執行測試並生成覆蓋率報告...${NC}"
    pytest tests/ --cov=. --cov-report=html --cov-report=term
    echo -e "\n${GREEN}✅ 覆蓋率報告已生成至 htmlcov/index.html${NC}"
}

# 並行測試
run_parallel_tests() {
    echo -e "${BLUE}執行並行測試（4 個工作程序）...${NC}"
    pytest tests/ -v -n 4 --tb=short
}

# 主程式
main() {
    check_dependencies
    
    case "${1:-all}" in
        quick)
            run_quick_tests
            ;;
        cache)
            run_cache_tests
            ;;
        batch)
            run_batch_tests
            ;;
        load)
            run_load_tests
            ;;
        coverage)
            run_coverage_tests
            ;;
        parallel)
            run_parallel_tests
            ;;
        all)
            run_all_tests
            ;;
        *)
            echo "使用方式: $0 [test_type]"
            echo "test_type 選項:"
            echo "  quick    - 快速測試（不需資料庫）"
            echo "  cache    - 快取功能測試"
            echo "  batch    - 批量查詢測試"
            echo "  load     - 負載測試"
            echo "  coverage - 生成覆蓋率報告"
            echo "  parallel - 並行測試"
            echo "  all      - 所有測試（預設）"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}   測試執行完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
}

main "$@"


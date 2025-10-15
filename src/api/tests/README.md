# API 測試說明

## 測試結構

```
tests/
├── test_basic_api.py        # 基礎 API 端點測試
├── test_llm_endpoints.py    # LLM 專用端點測試
└── README.md                # 本檔案
```

## 執行測試

### 前置條件

1. 安裝測試依賴:
```bash
pip install pytest pytest-asyncio pytest-cov httpx-test
```

2. 配置環境變數:
```bash
cp .env.example .env
# 編輯 .env 並填入 Supabase 憑證
```

### 運行所有測試

```bash
# 從 src/api 目錄執行
pytest tests/ -v
```

### 運行特定測試

```bash
# 只測試基礎 API
pytest tests/test_basic_api.py -v

# 只測試 LLM 端點
pytest tests/test_llm_endpoints.py -v

# 測試特定類別
pytest tests/test_basic_api.py::TestHealthEndpoint -v
```

### 查看覆蓋率

```bash
pytest tests/ --cov=. --cov-report=html
# 生成 HTML 報告在 htmlcov/ 目錄
```

## 測試類型

### 1. 單元測試
- 測試單一功能或模組
- 不需要外部依賴
- 快速執行

### 2. 整合測試 (需要 Supabase)
- 測試 API 端點完整流程
- 需要實際資料庫連接
- 使用 `@pytest.mark.skip` 標記

### 3. 效能測試
- 測試 API 回應時間
- 測試併發處理能力
- TODO: 待實作

## 注意事項

### 跳過的測試

大部分涉及資料庫的測試都被標記為 skip，因為需要：
- 有效的 Supabase 連接
- 已遷移的資料

要運行這些測試，請：
1. 配置正確的 `.env`
2. 移除 `@pytest.mark.skip` 裝飾器
3. 確保資料庫有測試資料

### 測試資料

建議使用測試專用的 Supabase 專案，避免影響生產資料。

## CI/CD 整合

TODO: 設置 GitHub Actions 自動測試

## 待完成項目

- [ ] 完善效能測試
- [ ] 添加負載測試
- [ ] 設置 CI/CD 管道
- [ ] 增加測試覆蓋率至 > 80%
- [ ] 添加 mock 資料，減少對實際資料庫的依賴


# ✅ Inspire Agent P0 實作檢查清單（已更新）

**工具 I/O 契約部分已完成** - 2025-01-27

---

### 4. 工具 I/O 契約（Day 2-4）✅ 已完成 (2025-01-27)

- [x] **understand_intent**
  - [x] 輸出只包含 6 個鍵（嚴格）
  - [x] `clarity_level` 枚舉驗證
  - [x] `confidence` 範圍 0-1
  - [x] 單元測試：5 個案例
  
- [x] **generate_ideas**
  - [x] 輸出 `ideas` 為陣列，2-3 個元素
  - [x] 每個 idea 包含 6 個鍵（嚴格）
  - [x] `main_tags` 至少 10 個
  - [x] 單元測試：3 個案例
  
- [x] **validate_quality**
  - [x] 輸出嚴格符合契約（8 個頂層鍵）
  - [x] `score` 範圍 0-100
  - [x] `quick_fixes` 包含 remove/add/replace
  - [x] 單元測試：3 個案例（含邊界情況）
  
- [x] **finalize_prompt**
  - [x] 輸出嚴格符合契約
  - [x] `positive_prompt` 長度 <500 字
  - [x] `negative_prompt` 包含固定前綴
  - [x] 單元測試：3 個案例

**驗收標準：**
- ✅ 所有合約測試通過（`tests/test_inspire_contracts.py`）
- ✅ 未知鍵被忽略或返回錯誤（使用 `extra="forbid"`）
- ✅ 缺失必要鍵返回錯誤（Pydantic 自動驗證）

**實施文件：**
- 驗證器模組: `src/api/utils/tool_contract_validator.py`
- 測試文件: `tests/test_inspire_contracts.py`
- 完整報告: `docs/TOOL_CONTRACT_IMPLEMENTATION.md`


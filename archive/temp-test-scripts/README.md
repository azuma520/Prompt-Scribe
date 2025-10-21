# 臨時測試腳本歸檔

## 📋 目錄說明

本目錄保存開發過程中產生的臨時測試和調試腳本。

---

## 📁 文件清單

### 測試腳本

| 文件 | 用途 | 狀態 |
|------|------|------|
| `test_api.py` | API 端點測試 | 已完成 |
| `test_simple_server.py` | 簡單伺服器測試 | 已完成 |
| `test_schema_validation_simple.py` | Schema 驗證測試 | 已完成 |
| `check_config.py` | 配置檢查工具 | 已完成 |
| `check_openai_models.py` | OpenAI 模型檢查 | 已完成 |

### 調試腳本

| 文件 | 用途 | 狀態 |
|------|------|------|
| `debug_server.py` | 伺服器調試 | 已完成 |
| `simple_debug.py` | 簡單調試 | 已完成 |
| `start_server.py` | 伺服器啟動（舊版） | 已替換 |
| `start_server_simple.py` | 簡單啟動腳本 | 已替換 |

### 環境設置腳本

| 文件 | 用途 | 狀態 |
|------|------|------|
| `set_env_and_run.ps1` | 環境設置並運行 | 已替換 |
| `start_test_server.ps1` | 測試伺服器啟動 | 已替換 |
| `env_template.txt` | 環境變數模板 | 已替換 |

### 其他

| 文件 | 用途 | 狀態 |
|------|------|------|
| `local_test.py` | 本地測試 | 已完成 |

---

## 🔄 替代文件

這些歸檔的文件已被更好的版本替代：

| 舊文件 | 新文件 | 改進 |
|--------|--------|------|
| `start_server.py` | `run_server.py` | 更穩定，正確的工作目錄 |
| `set_env_and_run.ps1` | `setup_env_local.ps1.template` | 更安全，模板化 |
| `env_template.txt` | `setup_env_local.ps1.template` | PowerShell 自動化 |
| `check_config.py` | `diagnose_model.py` | 更完整的診斷 |

---

## 📚 當前使用的工具

### 核心工具（根目錄）

| 工具 | 用途 |
|------|------|
| `run_server.py` | 啟動 API 伺服器 |
| `diagnose_model.py` | 診斷 OpenAI 配置 |
| `setup_env_local.ps1.template` | 環境設置模板 |

### 專業測試（tests/ 目錄）

| 工具 | 用途 |
|------|------|
| `tests/test_gpt5_nano_integration.py` | GPT-5 集成測試 |
| `tests/test_gpt5_nano_live.py` | GPT-5 實時測試 |
| `tests/test_gpt5_schema_validation.py` | Schema 驗證測試 |

---

**歸檔日期**: 2025-10-21  
**原因**: 開發完成，功能已整合到主系統

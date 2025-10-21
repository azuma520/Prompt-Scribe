# 🔒 API Key 安全最佳實踐

## ⚠️ 重要安全提醒

**永遠不要將 API Keys 提交到 Git 倉庫！**

---

## 🛡️ 當前安全措施

### 1. ✅ .gitignore 保護

以下文件已被 `.gitignore` 保護，**不會**被提交到 Git：

```
setup_env_local.ps1     # ✅ 已忽略
.env                     # ✅ 已忽略
.env.*                   # ✅ 已忽略
*_env_local.ps1         # ✅ 已忽略
set_env_*.ps1           # ✅ 已忽略
test_with_env.ps1       # ✅ 已忽略
```

### 2. ✅ 模板文件系統

- **模板文件**: `setup_env_local.ps1.template` （安全，可提交）
- **實際配置**: `setup_env_local.ps1` （包含 Keys，已忽略）

---

## 📋 安全檢查清單

### 提交代碼前必須檢查

在運行 `git add` 或 `git commit` 之前：

```powershell
# 1. 檢查 Git 狀態
git status

# 2. 確認沒有這些文件
# ❌ setup_env_local.ps1
# ❌ .env
# ❌ 任何包含 API Key 的文件

# 3. 驗證 gitignore 是否生效
git check-ignore -v setup_env_local.ps1

# 4. 應該看到：
# .gitignore:58:*_env_local.ps1	setup_env_local.ps1
```

### 提交安全的文件

✅ **可以安全提交**：
```
setup_env_local.ps1.template   # 模板，不含真實 Keys
env_template.txt               # 模板
SETUP_GPT5_ENV.md             # 文檔
```

❌ **絕對不要提交**：
```
setup_env_local.ps1           # 包含真實 Keys
.env                          # 包含真實 Keys
任何包含 "sk-proj-" 的文件    # OpenAI API Key
任何包含 "eyJ" 的文件         # Supabase JWT Token
```

---

## 🚨 如果不小心提交了 API Key

### 立即行動

1. **撤銷提交**（如果還沒 push）
   ```powershell
   git reset HEAD~1
   ```

2. **如果已經 push 到遠端**
   ```powershell
   # ⚠️ 危險操作，謹慎使用
   # 立即聯繫團隊成員
   ```

3. **立即撤銷 API Key**
   - OpenAI: https://platform.openai.com/api-keys
   - Supabase: https://supabase.com/dashboard/project/settings/api

4. **生成新的 API Key**

5. **更新 Zeabur 環境變數**

---

## 🔐 推薦的安全實踐

### 開發環境

#### 方法 1: 使用環境變數（推薦）

```powershell
# 每次開發前設置（僅在當前 session 有效）
$env:OPENAI_API_KEY = "your-key"
$env:SUPABASE_ANON_KEY = "your-key"

# 然後運行
python run_server.py
```

**優點**：
- ✅ 不會儲存在文件中
- ✅ 關閉終端後自動清除
- ✅ 零洩漏風險

#### 方法 2: 使用受保護的配置文件

```powershell
# 1. 複製模板
copy setup_env_local.ps1.template setup_env_local.ps1

# 2. 編輯 setup_env_local.ps1（已被 gitignore）

# 3. 運行
powershell -ExecutionPolicy Bypass -File setup_env_local.ps1
```

**優點**：
- ✅ 方便快速啟動
- ✅ .gitignore 保護
- ⚠️ 文件仍在本地硬碟

### 生產環境（Zeabur）

#### 最佳實踐

1. **僅在 Zeabur Dashboard 設置環境變數**
   - 不要寫在配置文件中
   - 不要寫在代碼中

2. **使用 Zeabur 的加密環境變數**
   - Zeabur 會自動加密儲存
   - 運行時才解密

3. **定期輪換 API Key**
   - 每 3-6 個月更換一次
   - 或在懷疑洩漏時立即更換

---

## 🔍 檢測敏感信息

### 檢查文件中是否有敏感信息

```powershell
# 搜索可能的 API Key
git grep -i "sk-proj-" .
git grep -i "sk-svcacct-" .
git grep -i "eyJhbGciOi" .  # JWT token

# 應該返回空結果
```

### 檢查 Git 歷史

```powershell
# 檢查是否曾經提交過敏感信息
git log --all --full-history -- "*env*.ps1"
git log --all --full-history -- "*.env*"
```

---

## 📊 當前狀況評估

### ✅ 已保護

- `.gitignore` 已更新
- `setup_env_local.ps1` 已被忽略
- 提供了安全的模板文件

### ⚠️ 需要注意

- `setup_env_local.ps1` **仍在您的本地硬碟**
  - 包含真實的 API Keys
  - 已被 Git 忽略
  - 但仍存在於文件系統中

### 🔒 建議的額外措施

1. **本地文件加密**（可選）
   ```powershell
   # Windows 檔案加密
   cipher /e setup_env_local.ps1
   ```

2. **使用密碼管理器**（推薦）
   - 將 API Keys 儲存在 1Password、LastPass 等
   - 需要時手動設置環境變數

3. **使用 .env 文件**（替代方案）
   ```bash
   # 創建 src/api/.env （已被 gitignore）
   OPENAI_API_KEY=your-key
   SUPABASE_ANON_KEY=your-key
   ```

---

## 🎯 推薦的工作流程

### 開發時

```powershell
# 選項 A: 手動設置（最安全）
$env:OPENAI_API_KEY = "從密碼管理器複製"
python run_server.py

# 選項 B: 使用受保護的腳本（方便）
powershell -ExecutionPolicy Bypass -File setup_env_local.ps1
python run_server.py
```

### 部署時

```
僅在 Zeabur Dashboard 設置環境變數
不要將生產環境的 Keys 用於開發
```

---

## 📝 安全檢查清單

提交前必須確認：

- [ ] `git status` 沒有顯示任何包含 Keys 的文件
- [ ] `.gitignore` 包含所有環境設置文件
- [ ] `setup_env_local.ps1` 被成功忽略
- [ ] 只提交模板文件（.template）
- [ ] 沒有硬編碼的 API Keys
- [ ] README 中沒有真實的 Keys

---

## 🆘 緊急應對

### 如果 API Key 已洩漏

1. **立即撤銷**
   ```
   OpenAI: https://platform.openai.com/api-keys
   → 找到該 Key → 點擊 "Revoke"
   ```

2. **生成新 Key**

3. **檢查使用記錄**
   ```
   OpenAI: https://platform.openai.com/usage
   檢查是否有異常使用
   ```

4. **更新所有環境**
   - 本地開發環境
   - Zeabur 環境變數
   - 團隊成員（如有）

---

## ✅ 現在是安全的嗎？

### 當前狀態

✅ **Git 倉庫**: 安全
- `setup_env_local.ps1` 已被 gitignore
- 不會被提交

⚠️ **本地硬碟**: Keys 仍在文件中
- 建議使用臨時環境變數
- 或加密文件

✅ **Zeabur**: 安全
- 環境變數加密儲存
- 不會洩漏

---

## 💡 最佳實踐總結

1. **✅ 使用 .gitignore 保護敏感文件**
2. **✅ 使用模板文件系統**
3. **✅ 定期檢查 `git status`**
4. **✅ 使用環境變數而非硬編碼**
5. **✅ 定期輪換 API Keys**
6. **✅ 使用密碼管理器**
7. **✅ 本地和生產使用不同的 Keys**

---

**您的安全意識很好！** 👍

現在 `setup_env_local.ps1` 已被保護，不會被提交到 Git。

**準備好繼續測試了嗎？** 🚀

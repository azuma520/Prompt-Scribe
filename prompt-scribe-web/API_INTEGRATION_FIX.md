# 🔧 API 整合修復指南

**日期**: 2025-10-20  
**狀態**: 🚧 需要修復

---

## 🚨 當前問題

### 發現的問題
1. **環境變數未設置** - `.env.local` 文件不存在
2. **資料欄位不匹配** - 使用 `category` 但 API 返回 `main_category` 和 `sub_category`
3. **API 回應格式** - 需要從 `data` 欄位取得標籤陣列

---

## ✅ 已修復

### 1. 類型定義更新
```typescript
// types/api.ts
export interface Tag {
  id: string;
  name: string;
  danbooru_cat: number;
  post_count: number;
  main_category: string | null;
  sub_category: string | null;
  confidence: number | null;
  classification_source: string | null;
  category?: string; // 計算屬性
}

export interface TagsResponse {
  data: Tag[];
  total: number;
  limit: number;
  offset: number;
}
```

### 2. API 客戶端修復
```typescript
// lib/api/tags.ts
function processTag(tag: Tag): Tag {
  return {
    ...tag,
    category: tag.sub_category || tag.main_category || 'OTHER'
  }
}

export async function getTags(limit: number = 200): Promise<Tag[]> {
  const result: TagsResponse = await response.json()
  return result.data.map(processTag) // 修復：從 data 欄位取得
}
```

### 3. 組件更新
- ✅ 更新所有使用 `tag.category` 的地方
- ✅ 改為使用 `tag.sub_category || tag.main_category`
- ✅ 分類篩選邏輯更新

---

## 🔧 需要手動操作

### Step 1: 創建環境變數文件

```bash
# 在 prompt-scribe-web 目錄下創建 .env.local
cd prompt-scribe-web

# Windows PowerShell
New-Item -Path ".env.local" -ItemType File -Force

# 寫入內容
@"
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.zeabur.app
NEXT_PUBLIC_API_TIMEOUT=30000
"@ | Out-File -FilePath ".env.local" -Encoding utf8
```

或者手動創建文件並複製以下內容：

```.env
NEXT_PUBLIC_API_URL=https://prompt-scribe-api.zeabur.app
NEXT_PUBLIC_API_TIMEOUT=30000
```

### Step 2: 重啟開發伺服器

```bash
# 停止當前伺服器（Ctrl+C）
# 然後重新啟動
npm run dev
```

### Step 3: 測試 API 連接

訪問以下 URL 測試：
```
http://localhost:3002/tags
```

應該能看到從 API 載入的實際標籤資料。

---

## 🧪 驗證 API 連接

### 方法 1: 使用 PowerShell 測試

```powershell
# 測試健康檢查
Invoke-WebRequest -Uri "https://prompt-scribe-api.zeabur.app/health"

# 測試標籤 API（前 5 個）
$response = Invoke-WebRequest -Uri "https://prompt-scribe-api.zeabur.app/api/v1/tags?limit=5"
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 方法 2: 使用瀏覽器

直接訪問：
```
https://prompt-scribe-api.zeabur.app/api/v1/tags?limit=5
```

### 預期結果

```json
{
  "data": [
    {
      "id": "302",
      "name": "1girl",
      "danbooru_cat": 0,
      "post_count": 96138304,
      "main_category": "CHARACTER_RELATED",
      "sub_category": "CHARACTER_COUNT",
      "confidence": null,
      "classification_source": "needs_reclassification"
    }
  ],
  "total": 140782,
  "limit": 5,
  "offset": 0
}
```

---

## 📋 功能測試清單

### 創建 .env.local 後測試

#### 標籤搜尋頁面 (`/tags`)
- [ ] 頁面正常載入
- [ ] 顯示實際的標籤資料（不是空的）
- [ ] 搜尋建議正常顯示
- [ ] 分類篩選顯示實際分類
- [ ] 熱門標籤側邊欄顯示資料

#### 搜尋功能
- [ ] 輸入關鍵字（如 "girl"）看到即時建議
- [ ] 點擊建議可選擇標籤
- [ ] 已選標籤正確顯示
- [ ] 搜尋歷史記錄功能

#### 詳情彈窗
- [ ] 點擊 ⓘ 按鈕打開詳情
- [ ] 顯示主分類和子分類
- [ ] 顯示使用次數
- [ ] 相關標籤推薦正確

#### 工作區整合
- [ ] 從標籤頁選擇標籤
- [ ] 切換到工作區頁面
- [ ] 已選標籤正確顯示
- [ ] 複製 Prompt 功能正常
- [ ] Toast 通知顯示

---

## 🚀 完成後的效果

### 預期行為

1. **進入標籤頁** (`/tags`)
   - 載入畫面顯示 Skeleton
   - 載入完成後顯示實際標籤

2. **搜尋標籤**
   - 輸入 "girl" → 顯示包含 "girl" 的標籤
   - 輸入 "long" → 顯示 "long_hair", "long_sleeves" 等

3. **篩選功能**
   - 選擇 "CHARACTER_RELATED" → 只顯示角色相關標籤
   - 選擇 "使用次數" 排序 → 最熱門的標籤在前

4. **查看詳情**
   - 點擊任何標籤的 ⓘ 按鈕
   - 彈出詳情窗口顯示完整資訊

5. **工作區同步**
   - 選擇的標籤自動儲存到 localStorage
   - 跨頁面狀態同步
   - 可以在工作區頁面查看

---

## 💡 故障排除

### 如果標籤頁面是空的

**原因**: API 可能無法連接或環境變數未設置

**解決方法**:
1. 檢查 `.env.local` 文件是否存在
2. 檢查環境變數值是否正確
3. 重啟開發伺服器
4. 查看瀏覽器控制台錯誤訊息

### 如果顯示錯誤

**原因**: API 回應格式不匹配

**解決方法**:
1. 查看瀏覽器控制台的錯誤訊息
2. 檢查 Network 面板的 API 回應
3. 確認 `lib/api/tags.ts` 的資料處理邏輯

---

## 📞 需要協助

如果遇到問題，請：
1. 查看瀏覽器控制台錯誤
2. 查看 Network 面板的 API 請求
3. 提供錯誤訊息以便診斷

---

**下一步**: 創建 `.env.local` 文件並測試！


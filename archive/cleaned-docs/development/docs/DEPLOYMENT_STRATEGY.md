# 資料庫部署策略

**版本**: v1.0  
**日期**: 2025-10-13  
**狀態**: 生產就緒  

---

## 📋 部署概述

### 當前狀態
- **資料庫品質**: 生產就緒 (96.56% 覆蓋率)
- **測試通過率**: 80% (8/10)
- **核心功能**: 完整可用
- **性能表現**: <30ms 查詢響應

### 部署目標
- 安全、穩定地將資料庫部署到生產環境
- 確保零停機時間或最小停機時間
- 建立監控和回滾機制
- 提供完整的部署文檔

---

## 🎯 部署策略選項

### 選項 A: 藍綠部署 (推薦)
**適用場景**: 有完整備份和回滾能力
**優點**: 零停機時間，快速回滾
**缺點**: 需要額外資源

### 選項 B: 滾動更新
**適用場景**: 資源有限，可接受短暫停機
**優點**: 資源效率高
**缺點**: 有短暫停機時間

### 選項 C: 金絲雀部署
**適用場景**: 需要漸進式驗證
**優點**: 風險最低，可逐步驗證
**缺點**: 部署時間較長

---

## 🚀 推薦部署方案

### 階段 1: 預部署準備
1. **備份現有資料庫**
   ```bash
   # 創建完整備份
   cp output/tags.db output/tags_backup_$(date +%Y%m%d_%H%M%S).db
   ```

2. **環境驗證**
   - 檢查目標環境資源
   - 驗證網路連接
   - 確認權限設置

3. **部署包準備**
   - 資料庫文件 (`output/tags.db`)
   - 測試工具套件
   - 監控腳本
   - 回滾腳本

### 階段 2: 部署執行
1. **部署新資料庫**
   ```bash
   # 停止應用服務
   systemctl stop prompt-scribe-app
   
   # 備份現有資料庫
   cp /var/lib/prompt-scribe/tags.db /var/lib/prompt-scribe/tags_backup.db
   
   # 部署新資料庫
   cp output/tags.db /var/lib/prompt-scribe/tags.db
   
   # 設置權限
   chown prompt-scribe:prompt-scribe /var/lib/prompt-scribe/tags.db
   chmod 644 /var/lib/prompt-scribe/tags.db
   
   # 啟動應用服務
   systemctl start prompt-scribe-app
   ```

2. **即時驗證**
   ```bash
   # 運行快速健康檢查
   python stage1/quick_health_check.py
   
   # 驗證關鍵功能
   python stage1/validate_core_functions.py
   ```

### 階段 3: 部署後驗證
1. **功能測試**
   - 標籤分類功能
   - 查詢性能測試
   - 錯誤處理驗證

2. **性能監控**
   - 查詢響應時間
   - 記憶體使用情況
   - 錯誤率監控

3. **用戶驗證**
   - 關鍵用戶測試
   - 反饋收集
   - 問題記錄

---

## 📊 部署檢查清單

### 部署前檢查
- [ ] 資料庫品質測試通過
- [ ] 備份策略確認
- [ ] 回滾計劃準備
- [ ] 監控工具配置
- [ ] 團隊通知完成

### 部署中檢查
- [ ] 服務正常停止
- [ ] 資料庫成功替換
- [ ] 權限正確設置
- [ ] 服務成功啟動
- [ ] 健康檢查通過

### 部署後檢查
- [ ] 功能測試通過
- [ ] 性能指標正常
- [ ] 錯誤日誌清潔
- [ ] 用戶反饋收集
- [ ] 監控數據確認

---

## 🔧 部署工具

### 1. 健康檢查腳本
```python
# quick_health_check.py
import sqlite3
import time

def health_check():
    start_time = time.time()
    conn = sqlite3.connect('/var/lib/prompt-scribe/tags.db')
    cursor = conn.cursor()
    
    # 基本連接測試
    cursor.execute("SELECT COUNT(*) FROM tags_final")
    total_tags = cursor.fetchone()[0]
    
    # 性能測試
    cursor.execute("SELECT * FROM tags_final WHERE post_count > 1000000 LIMIT 10")
    high_freq_tags = cursor.fetchall()
    
    conn.close()
    
    response_time = time.time() - start_time
    
    return {
        'status': 'healthy' if response_time < 0.1 else 'slow',
        'total_tags': total_tags,
        'response_time': response_time,
        'high_freq_tags_count': len(high_freq_tags)
    }
```

### 2. 回滾腳本
```bash
#!/bin/bash
# rollback.sh

echo "開始回滾..."
systemctl stop prompt-scribe-app

if [ -f "/var/lib/prompt-scribe/tags_backup.db" ]; then
    cp /var/lib/prompt-scribe/tags_backup.db /var/lib/prompt-scribe/tags.db
    echo "資料庫回滾完成"
else
    echo "錯誤: 找不到備份文件"
    exit 1
fi

systemctl start prompt-scribe-app
echo "服務已重啟，回滾完成"
```

### 3. 監控腳本
```python
# monitor.py
import sqlite3
import time
import logging

def monitor_database():
    while True:
        try:
            conn = sqlite3.connect('/var/lib/prompt-scribe/tags.db')
            cursor = conn.cursor()
            
            # 監控指標
            cursor.execute("SELECT COUNT(*) FROM tags_final")
            total_tags = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(classification_confidence) FROM tags_final")
            avg_confidence = cursor.fetchone()[0]
            
            conn.close()
            
            logging.info(f"監控數據: 總標籤數={total_tags}, 平均信心度={avg_confidence:.3f}")
            
        except Exception as e:
            logging.error(f"監控錯誤: {e}")
        
        time.sleep(300)  # 每5分鐘檢查一次
```

---

## 🚨 風險管理

### 主要風險
1. **資料庫損壞**: 備份和回滾機制
2. **性能下降**: 性能監控和預警
3. **功能異常**: 功能測試和驗證
4. **用戶影響**: 漸進式部署和快速回滾

### 風險緩解
- **完整備份**: 部署前創建多個備份
- **快速回滾**: 自動化回滾腳本
- **監控預警**: 實時性能監控
- **分階段部署**: 降低影響範圍

---

## 📈 成功指標

### 技術指標
- 查詢響應時間 < 50ms
- 錯誤率 < 0.1%
- 資料庫可用性 > 99.9%
- 記憶體使用 < 80%

### 業務指標
- 用戶滿意度 > 90%
- 功能使用率正常
- 投訴數量 < 5%
- 系統穩定性良好

---

## 📞 聯絡資訊

**部署負責人**: [待指定]  
**技術支援**: [待指定]  
**緊急聯絡**: [待指定]  

**部署時間窗口**: [待商定]  
**預計部署時長**: 30-60 分鐘  
**回滾時間**: < 5 分鐘  

---

## 📝 部署記錄

### 部署歷史
| 版本 | 日期 | 狀態 | 備註 |
|------|------|------|------|
| v1.0 | 2025-10-13 | 待部署 | 初始生產版本 |

### 問題記錄
- [待記錄部署過程中的問題和解決方案]

---

*此文檔將在部署過程中持續更新*

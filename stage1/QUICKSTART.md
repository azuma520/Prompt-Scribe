# 快速開始指南

## 一鍵執行

```bash
cd stage1
python run_pipeline.py
```

執行時間：約 5-10 秒

## 輸出結果

執行完成後，在 `output/` 目錄查看：

1. **tags.db** - SQLite 資料庫
   - 140,782 個唯一標籤
   - 完整的主分類和副分類
   
2. **classification_report.txt** - 分類統計報告

3. **pipeline.log** - 完整執行日誌

## 查詢範例

```bash
# 使用 Python 查詢
python -c "import sqlite3; conn = sqlite3.connect('output/tags.db'); 
result = conn.execute('SELECT name, main_category, sub_category, post_count FROM tags_final WHERE main_category IS NOT NULL ORDER BY post_count DESC LIMIT 10').fetchall(); 
[print(f'{r[0]:20} {r[1]:20} {r[2] if r[2] else \"\":15} {r[3]:>12,}') for r in result]; 
conn.close()"
```

## 性能指標

- **處理速度：** 5.3 秒（86 萬筆記錄）
- **記憶體：** ~100MB
- **TOP 30 覆蓋率：** 100%
- **加權覆蓋率：** 62.1%

## 驗證測試

```bash
# 運行分類器測試
python test_classifier.py

# 運行最終驗證
python final_validation.py

# 檢查高頻標籤
python check_real_tags.py
```

## 常見問題

**Q: 為什麼整體覆蓋率只有 29.5%？**  
A: 因為包含大量低頻罕見標籤。關鍵指標是 TOP 30 覆蓋率（100%）和加權覆蓋率（62.1%）。

**Q: 如何提升覆蓋率？**  
A: 分析未分類的高頻標籤，在 `src/classifier/rules/` 中添加關鍵字。

**Q: 資料庫在哪裡？**  
A: `stage1/output/tags.db`

**Q: 如何查看分類結果？**  
A: 使用 SQLite 工具或運行 `check_real_tags.py`

---

**就是這麼簡單！** 🚀


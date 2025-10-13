#!/usr/bin/env python3
"""
修復 JSON 解析失敗的標籤
重新處理批次 29 中失敗的標籤
"""

import sqlite3
import json
import time
from openai import OpenAI
from llm_config import LLM_CONFIG

def get_failed_tags():
    """獲取 JSON 解析失敗的標籤"""
    conn = sqlite3.connect('output/tags.db')
    
    # 找到應該被批次 29 處理但失敗的標籤
    # 根據使用次數範圍估算
    failed_tags = conn.execute('''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 100000 AND post_count < 1000000
        ORDER BY post_count DESC
        LIMIT 25 OFFSET 560
    ''').fetchall()
    
    conn.close()
    return failed_tags

def classify_with_retry(tags, max_retries=3):
    """使用增強的容錯機制分類標籤"""
    client = OpenAI(
        base_url=LLM_CONFIG["base_url"],
        api_key=LLM_CONFIG["api_key"]
    )
    
    # 創建簡化的提示詞，避免複雜輸出
    prompt = f"""請將以下標籤分類。對於每個標籤，提供：主分類、副分類（可選）、信心度。

主分類選項：
CHARACTER_RELATED, ACTION_POSE, OBJECTS, ENVIRONMENT, COMPOSITION, VISUAL_EFFECTS, 
ART_STYLE, ADULT_CONTENT, THEME_CONCEPT, TECHNICAL, QUALITY

標籤列表：
{', '.join(tags)}

請用純 JSON 格式回答（不要使用 markdown）：
{{"classifications":[{{"tag":"標籤名","main_category":"主分類","sub_category":"副分類或null","confidence":0.95,"reasoning":"簡短理由"}}]}}"""

    for attempt in range(max_retries):
        try:
            print(f"嘗試 {attempt + 1}/{max_retries}...")
            
            completion = client.chat.completions.create(
                extra_headers=LLM_CONFIG["extra_headers"],
                model=LLM_CONFIG["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = completion.choices[0].message.content
            
            # 增強的 JSON 提取和清理
            # 1. 移除 markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # 2. 清理無效轉義字符
            import re
            # 移除無效的 \escape 序列（保留合法的 \n, \t, \", \\, \/ 等）
            content = re.sub(r'\\(?!["\\/bfnrtu])', '', content)
            
            # 3. 嘗試解析
            try:
                parsed = json.loads(content)
                return parsed.get('classifications', [])
            except json.JSONDecodeError as e:
                print(f"JSON 解析錯誤: {e}")
                print(f"清理後的內容前 500 字符: {content[:500]}")
                
                # 最後嘗試：手動修復常見問題
                content = content.replace('\n', ' ').replace('\r', ' ')
                content = re.sub(r'\s+', ' ', content)
                
                try:
                    parsed = json.loads(content)
                    return parsed.get('classifications', [])
                except:
                    if attempt < max_retries - 1:
                        print(f"重試...")
                        time.sleep(2)
                        continue
                    else:
                        print(f"所有重試都失敗，跳過這批標籤")
                        return []
                        
        except Exception as e:
            print(f"請求異常: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return []
    
    return []

def save_classifications(classifications):
    """保存分類結果到資料庫"""
    conn = sqlite3.connect('output/tags.db')
    cursor = conn.cursor()
    
    updated = 0
    for item in classifications:
        tag_name = item.get('tag')
        main_cat = item.get('main_category')
        sub_cat = item.get('sub_category')
        confidence = item.get('confidence', 0.0)
        reasoning = item.get('reasoning', '')
        
        if main_cat:
            cursor.execute('''
                UPDATE tags_final 
                SET main_category = ?,
                    sub_category = ?,
                    classification_source = 'json_fix_batch',
                    classification_confidence = ?,
                    classification_reasoning = ?,
                    classification_timestamp = datetime('now')
                WHERE name = ? 
                AND danbooru_cat = 0 
                AND main_category IS NULL
            ''', (main_cat, sub_cat, confidence, reasoning, tag_name))
            
            if cursor.rowcount > 0:
                updated += 1
                print(f"[OK] {tag_name} -> {main_cat}/{sub_cat or 'N/A'} (信心度: {confidence:.3f})")
    
    conn.commit()
    conn.close()
    
    return updated

def main():
    print("="*80)
    print("修復 JSON 解析失敗的標籤")
    print("="*80)
    
    # 獲取失敗的標籤
    failed_tags = get_failed_tags()
    tag_names = [name for name, _ in failed_tags]
    
    print(f"\n找到 {len(tag_names)} 個可能失敗的標籤")
    print(f"標籤列表: {', '.join(tag_names[:10])}...")
    
    if not tag_names:
        print("沒有找到失敗的標籤")
        return
    
    # 批量處理
    batch_size = 20
    total_updated = 0
    
    for i in range(0, len(tag_names), batch_size):
        batch = tag_names[i:i+batch_size]
        print(f"\n處理批次 {i//batch_size + 1} ({len(batch)} 個標籤)")
        
        classifications = classify_with_retry(batch)
        
        if classifications:
            updated = save_classifications(classifications)
            total_updated += updated
            print(f"批次完成: 更新 {updated} 個標籤")
        
        time.sleep(2)
    
    print(f"\n{'='*80}")
    print(f"修復完成")
    print(f"成功更新: {total_updated} 個標籤")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()


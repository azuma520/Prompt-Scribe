#!/usr/bin/env python3
"""
DeepSeek V3.1 批次標籤分類器
使用免費的 DeepSeek V3.1 API 進行大規模標籤分類
"""

import sqlite3
import requests
import json
import time
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
import os

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 簡單的 .env 加載（避免外部依賴）
def _load_dotenv_if_present(env_path: str = ".env") -> None:
    if os.path.exists(env_path):
        try:
            # 使用 utf-8-sig 自動移除 BOM
            with open(env_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().lstrip("\ufeff")  # 再保險去除 BOM
                        v = v.strip()
                        # 無條件覆寫，確保值生效
                        os.environ[k] = v
        except Exception:
            pass

# 嘗試載入當前與上層目錄的 .env
_load_dotenv_if_present()
_load_dotenv_if_present(os.path.join("..", ".env"))

@dataclass
class ClassificationResult:
    tag_name: str
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    success: bool = False
    error: str = ""

class DeepSeekClassifier:
    def __init__(self, api_key: str = None):
        """
        初始化 DeepSeek 分類器
        
        Args:
            api_key: DeepSeek API 密鑰（如果需要的話）
        """
        # 從環境變量讀取（優先）
        if not api_key:
            api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        }
        # 可選 OpenRouter 排名標頭
        referer = os.environ.get("OPENROUTER_REFERER", "")
        title = os.environ.get("OPENROUTER_TITLE", "")
        if referer:
            self.headers["HTTP-Referer"] = referer
        if title:
            self.headers["X-Title"] = title
        
        # 分類系統定義
        self.main_categories = {
            'CHARACTER_RELATED': '人物相關',
            'ACTION_POSE': '動作姿勢', 
            'OBJECTS': '物件道具',
            'ENVIRONMENT': '環境場景',
            'COMPOSITION': '構圖視角',
            'VISUAL_EFFECTS': '視覺效果',
            'ART_STYLE': '藝術風格',
            'ADULT_CONTENT': '成人內容',
            'THEME_CONCEPT': '主題概念',
            'TECHNICAL': '技術標籤'
        }
        
        self.sub_categories = {
            'CHARACTER_RELATED': {
                'CLOTHING': '服裝',
                'HAIR': '頭髮',
                'BODY_PARTS': '身體部位',
                'ACCESSORIES': '配飾',
                'CHARACTER_COUNT': '角色數量'
            },
            'ACTION_POSE': {
                'EXPRESSION': '表情',
                'GESTURE': '手勢',
                'BODY_POSE': '身體姿勢',
                'INTERACTION': '互動'
            },
            'OBJECTS': {
                'WEAPONS': '武器',
                'VEHICLES': '載具',
                'FURNITURE': '家具',
                'FOOD': '食物',
                'ANIMALS': '動物',
                'MISCELLANEOUS': '雜項'
            },
            'ENVIRONMENT': {
                'INDOOR': '室內',
                'OUTDOOR': '室外',
                'NATURE': '自然',
                'URBAN': '都市',
                'FANTASY': '奇幻'
            },
            'COMPOSITION': {
                'CAMERA_ANGLE': '拍攝角度',
                'FRAMING': '構圖',
                'PERSPECTIVE': '透視',
                'CROP': '裁切'
            },
            'VISUAL_EFFECTS': {
                'LIGHTING': '光影',
                'COLORS': '色彩',
                'EFFECTS': '特效',
                'RENDERING': '渲染'
            },
            'ART_STYLE': {
                'ANIME': '動漫風格',
                'REALISTIC': '寫實風格',
                'CARTOON': '卡通風格',
                'PAINTERLY': '繪畫風格'
            },
            'ADULT_CONTENT': {
                'SEXUAL': '性行為',
                'EXPLICIT_BODY': '裸露身體',
                'SUGGESTIVE': '暗示性',
                'CENSORSHIP': '審查相關'
            },
            'THEME_CONCEPT': {
                'SEASON': '季節',
                'HOLIDAY': '節日',
                'TIME': '時間',
                'WEATHER': '天氣',
                'CONCEPT': '抽象概念'
            },
            'TECHNICAL': {
                'METADATA': '元數據',
                'QUALITY': '品質',
                'SOURCE': '來源',
                'COPYRIGHT': '版權'
            }
        }

    def create_classification_prompt(self, tags: List[str]) -> str:
        """創建分類 prompt"""
        
        main_cats = "\n".join([f"- {code}: {name}" for code, name in self.main_categories.items()])
        sub_cats = "\n".join([
            f"  {main_code}:\n" + "\n".join([f"    - {sub_code}: {sub_name}" for sub_code, sub_name in subs.items()])
            for main_code, subs in self.sub_categories.items()
        ])
        
        return f"""你是 Danbooru 標籤分類專家。請將以下標籤分類到適當的主分類和副分類。

主分類選項：
{main_cats}

副分類選項：
{sub_cats}

分類規則：
1. 優先考慮標籤的主要用途和含義
2. 如果有多個可能的分類，選擇最符合的
3. 如果不確定，選擇最接近的分類
4. 對於成人內容，請謹慎分類

標籤列表：
{', '.join(tags)}

請以 JSON 格式回答，格式如下：
{{
  "classifications": [
    {{
      "tag": "標籤名稱",
      "main_category": "主分類代碼",
      "sub_category": "副分類代碼或null",
      "confidence": 0.95,
      "reasoning": "分類理由"
    }}
  ]
}}

注意：
- 每個標籤都要有分類結果
- confidence 範圍 0-1
- 如果沒有合適的副分類，sub_category 設為 null
- reasoning 要簡潔明確"""

    def classify_batch(self, tags: List[str], max_retries: int = 3) -> List[ClassificationResult]:
        """
        批次分類標籤
        
        Args:
            tags: 要分類的標籤列表
            max_retries: 最大重試次數
            
        Returns:
            分類結果列表
        """
        results = []
        
        try:
            prompt = self.create_classification_prompt(tags)
            
            payload = {
                "model": os.environ.get("DEEPSEEK_MODEL", "deepseek/deepseek-chat"),
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000,
                "stream": False
            }
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"發送批次請求，包含 {len(tags)} 個標籤，嘗試 {attempt + 1}/{max_retries}")
                    
                    response = requests.post(
                        self.base_url,
                        headers=self.headers,
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # 解析 JSON 響應
                        try:
                            parsed = json.loads(content)
                            classifications = parsed.get('classifications', [])
                            
                            # 轉換為結果對象
                            for item in classifications:
                                result_obj = ClassificationResult(
                                    tag_name=item['tag'],
                                    main_category=item.get('main_category'),
                                    sub_category=item.get('sub_category'),
                                    confidence=item.get('confidence', 0.0),
                                    reasoning=item.get('reasoning', ''),
                                    success=True
                                )
                                results.append(result_obj)
                            
                            logger.info(f"成功分類 {len(results)} 個標籤")
                            return results
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 解析錯誤: {e}")
                            logger.error(f"響應內容: {content[:500]}...")
                            
                    else:
                        logger.error(f"API 請求失敗: {response.status_code} - {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"請求異常: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"等待 {wait_time:.1f} 秒後重試...")
                    time.sleep(wait_time)
            
            # 如果所有重試都失敗，創建失敗結果
            for tag in tags:
                results.append(ClassificationResult(
                    tag_name=tag,
                    success=False,
                    error="API 請求失敗"
                ))
                
        except Exception as e:
            logger.error(f"批次分類異常: {e}")
            for tag in tags:
                results.append(ClassificationResult(
                    tag_name=tag,
                    success=False,
                    error=str(e)
                ))
        
        return results

    def process_all_unclassified_tags(self, db_path: str, batch_size: int = 100):
        """
        處理所有未分類標籤
        
        Args:
            db_path: 數據庫路徑
            batch_size: 批次大小
        """
        conn = sqlite3.connect(db_path)
        
        try:
            # 獲取所有未分類標籤
            query = """
                SELECT name, post_count
                FROM tags_final 
                WHERE danbooru_cat = 0 
                  AND main_category IS NULL
                ORDER BY post_count DESC
            """
            
            cursor = conn.execute(query)
            all_tags = cursor.fetchall()
            
            logger.info(f"找到 {len(all_tags)} 個未分類標籤")
            
            # 分批處理
            total_processed = 0
            total_success = 0
            
            for i in range(0, len(all_tags), batch_size):
                batch = all_tags[i:i + batch_size]
                tag_names = [tag[0] for tag in batch]
                
                logger.info(f"處理批次 {i//batch_size + 1}/{(len(all_tags) + batch_size - 1)//batch_size}")
                logger.info(f"標籤範圍: {tag_names[0]} 到 {tag_names[-1]}")
                
                # 分類
                results = self.classify_batch(tag_names)
                
                # 保存結果
                success_count = self.save_results(conn, results)
                
                total_processed += len(results)
                total_success += success_count
                
                logger.info(f"批次完成: {success_count}/{len(results)} 成功")
                logger.info(f"總進度: {total_success}/{total_processed} 成功")
                
                # 避免 API 限制
                if i + batch_size < len(all_tags):
                    time.sleep(1)
            
            logger.info(f"處理完成！總共處理 {total_processed} 個標籤，成功 {total_success} 個")
            
        finally:
            conn.close()

    def save_results(self, conn: sqlite3.Connection, results: List[ClassificationResult]) -> int:
        """保存分類結果到數據庫"""
        success_count = 0
        
        for result in results:
            if result.success and result.main_category:
                try:
                    conn.execute("""
                        UPDATE tags_final 
                        SET main_category = ?, 
                            sub_category = ?,
                            classification_source = 'deepseek_v3.1',
                            classification_confidence = ?,
                            classification_reasoning = ?
                        WHERE name = ?
                    """, (
                        result.main_category,
                        result.sub_category,
                        result.confidence,
                        result.reasoning,
                        result.tag_name
                    ))
                    success_count += 1
                except Exception as e:
                    logger.error(f"保存標籤 {result.tag_name} 失敗: {e}")
        
        conn.commit()
        return success_count

def main():
    """主函數"""
    print("="*80)
    print("DeepSeek V3.1 標籤分類器")
    print("="*80)
    
    # 檢查數據庫
    db_path = "output/tags.db"
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"✓ 數據庫文件找到: {db_path}")
    except Exception as e:
        print(f"✗ 數據庫錯誤: {e}")
        return
    
    # 初始化分類器
    classifier = DeepSeekClassifier()
    
    print("\n開始處理未分類標籤...")
    print("注意：這可能需要數小時，請確保網絡連接穩定")
    
    # 處理所有未分類標籤
    classifier.process_all_unclassified_tags(db_path, batch_size=50)  # 較小批次避免超時
    
    print("\n處理完成！")

if __name__ == "__main__":
    main()

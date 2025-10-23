#!/usr/bin/env python3
"""
Qwen3 Next 80B A3B Thinking 標籤分類器
使用 OpenRouter API 進行大規模標籤分類
"""

import sqlite3
import json
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from openai import OpenAI

from llm_config import LLM_CONFIG, validate_config

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """分類結果"""
    tag_name: str
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    success: bool = False
    error: str = ""


class QwenClassifier:
    """Qwen3 標籤分類器"""
    
    def __init__(self):
        """初始化分類器"""
        if not validate_config():
            raise ValueError("配置驗證失敗")
        
        # 初始化 OpenAI 客戶端（OpenRouter 相容）
        self.client = OpenAI(
            base_url=LLM_CONFIG["base_url"],
            api_key=LLM_CONFIG["api_key"]
        )
        
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
            'TECHNICAL': '技術標籤',
            'QUALITY': '品質等級'
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
5. 每個標籤都必須有分類結果

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
    
    def classify_batch(self, tags: List[str], max_retries: int = None) -> List[ClassificationResult]:
        """批次分類標籤"""
        if max_retries is None:
            max_retries = LLM_CONFIG["max_retries"]
        
        results = []
        
        try:
            prompt = self.create_classification_prompt(tags)
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"發送批次請求，包含 {len(tags)} 個標籤，嘗試 {attempt + 1}/{max_retries}")
                    
                    completion = self.client.chat.completions.create(
                        extra_headers=LLM_CONFIG["extra_headers"],
                        model=LLM_CONFIG["model"],
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=LLM_CONFIG["temperature"],
                        max_tokens=LLM_CONFIG["max_tokens"]
                    )
                    
                    content = completion.choices[0].message.content
                    
                    # 解析 JSON 響應
                    try:
                        # 嘗試提取 JSON（可能被包在 markdown code block 中）
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        
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
                        
                except Exception as e:
                    logger.error(f"請求異常: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"等待 {wait_time:.1f} 秒後重試...")
                    time.sleep(wait_time)
            
            # 如果所有重試都失敗，創建失敗結果
            if not results:
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
    
    def process_unclassified_tags(self, db_path: str, min_post_count: int = 1000000, 
                                   limit: int = None) -> Dict:
        """處理未分類標籤"""
        conn = sqlite3.connect(db_path)
        
        try:
            # 獲取未分類標籤
            query = f"""
                SELECT name, post_count
                FROM tags_final 
                WHERE danbooru_cat = 0 
                  AND main_category IS NULL
                  AND post_count >= {min_post_count}
                ORDER BY post_count DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = conn.execute(query)
            all_tags = cursor.fetchall()
            
            logger.info(f"找到 {len(all_tags)} 個未分類標籤（post_count >= {min_post_count:,}）")
            
            if not all_tags:
                logger.warning("沒有找到符合條件的未分類標籤")
                return {"total": 0, "success": 0, "failed": 0}
            
            # 分批處理
            batch_size = LLM_CONFIG["batch_size"]
            total_processed = 0
            total_success = 0
            total_failed = 0
            
            for i in range(0, len(all_tags), batch_size):
                batch = all_tags[i:i + batch_size]
                tag_names = [tag[0] for tag in batch]
                
                logger.info(f"\n處理批次 {i//batch_size + 1}/{(len(all_tags) + batch_size - 1)//batch_size}")
                logger.info(f"標籤範圍: {tag_names[0]} 到 {tag_names[-1]}")
                
                # 分類
                results = self.classify_batch(tag_names)
                
                # 保存結果
                success_count, failed_count = self.save_results(conn, results)
                
                total_processed += len(results)
                total_success += success_count
                total_failed += failed_count
                
                logger.info(f"批次完成: {success_count} 成功, {failed_count} 失敗")
                logger.info(f"總進度: {total_success}/{total_processed} 成功")
                
                # 避免 API 限制
                if i + batch_size < len(all_tags):
                    time.sleep(1)
            
            logger.info(f"\n處理完成！")
            logger.info(f"總共處理: {total_processed} 個標籤")
            logger.info(f"成功: {total_success} ({total_success/total_processed*100:.1f}%)")
            logger.info(f"失敗: {total_failed} ({total_failed/total_processed*100:.1f}%)")
            
            return {
                "total": total_processed,
                "success": total_success,
                "failed": total_failed
            }
            
        finally:
            conn.close()
    
    def save_results(self, conn: sqlite3.Connection, results: List[ClassificationResult]) -> tuple:
        """保存分類結果到數據庫"""
        success_count = 0
        failed_count = 0
        
        for result in results:
            if result.success and result.main_category:
                try:
                    conn.execute("""
                        UPDATE tags_final 
                        SET main_category = ?, 
                            sub_category = ?,
                            classification_source = ?,
                            classification_confidence = ?,
                            classification_reasoning = ?,
                            classification_timestamp = CURRENT_TIMESTAMP
                        WHERE name = ?
                    """, (
                        result.main_category,
                        result.sub_category,
                        'qwen3_80b',
                        result.confidence,
                        result.reasoning,
                        result.tag_name
                    ))
                    success_count += 1
                except Exception as e:
                    logger.error(f"保存標籤 {result.tag_name} 失敗: {e}")
                    failed_count += 1
            else:
                logger.warning(f"跳過失敗的標籤: {result.tag_name} - {result.error}")
                failed_count += 1
        
        conn.commit()
        return success_count, failed_count


def main():
    """主函數"""
    print("="*80)
    print("Qwen3 Next 80B A3B Thinking 標籤分類器")
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
    try:
        classifier = QwenClassifier()
    except ValueError as e:
        print(f"✗ 初始化失敗: {e}")
        return
    
    print("\n開始處理超高頻未分類標籤（post_count >= 1M）...")
    print("注意：這可能需要數小時，請確保網絡連接穩定\n")
    
    # 處理超高頻未分類標籤
    results = classifier.process_unclassified_tags(
        db_path, 
        min_post_count=1000000
    )
    
    print("\n" + "="*80)
    print("處理完成！")
    print("="*80)
    print(f"總處理: {results['total']} 個標籤")
    print(f"成功: {results['success']} 個")
    print(f"失敗: {results['failed']} 個")


if __name__ == "__main__":
    main()


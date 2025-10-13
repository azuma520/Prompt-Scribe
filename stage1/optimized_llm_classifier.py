#!/usr/bin/env python3
"""
優化版 LLM 標籤分類器
基於現有分類經驗和策略優化的提示詞
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


class OptimizedLLMClassifier:
    """優化版 LLM 標籤分類器"""
    
    def __init__(self, use_low_freq_prompt: bool = False):
        """初始化分類器
        
        Args:
            use_low_freq_prompt: 是否使用低頻標籤專用提示詞
        """
        if not validate_config():
            raise ValueError("配置驗證失敗")
        
        # 初始化 OpenAI 客戶端
        self.client = OpenAI(
            base_url=LLM_CONFIG["base_url"],
            api_key=LLM_CONFIG["api_key"]
        )
        
        self.use_low_freq_prompt = use_low_freq_prompt
        
        # 分類系統定義（完整版，包含所有副分類）
        self.category_system = {
            'CHARACTER_RELATED': {
                'description': '人物相關 - 描述角色外觀、服裝、身體特徵',
                'sub_categories': {
                    'CLOTHING': '服裝 - 所有衣物、鞋子、帽子',
                    'HAIR': '頭髮 - 髮型、髮色、髮飾',
                    'BODY_PARTS': '身體部位 - 眼睛、手、腳、身體特徵',
                    'ACCESSORIES': '配飾 - 首飾、眼鏡、包包等裝飾品',
                    'CHARACTER_COUNT': '角色數量 - 1girl, 2boys 等',
                    'COLORS': '顏色相關 - 與人物相關的顏色描述',
                    'COSMETICS': '化妝品 - 口紅、指甲油等'
                },
                'examples': [
                    'dress → CLOTHING',
                    'long_hair → HAIR', 
                    'blue_eyes → BODY_PARTS',
                    'necklace → ACCESSORIES',
                    '1girl → CHARACTER_COUNT',
                    'red_lips → COLORS',
                    'lipstick → COSMETICS'
                ]
            },
            'ACTION_POSE': {
                'description': '動作姿態 - 角色的動作、表情、姿勢',
                'sub_categories': {
                    'EXPRESSION': '表情 - 笑容、哭泣、生氣等面部表情',
                    'GESTURE': '手勢 - 手部動作、指向、握拳等',
                    'BODY_POSE': '身體姿勢 - 坐姿、站姿、躺姿',
                    'INTERACTION': '互動 - 角色之間的互動行為',
                    'PROPS': '道具互動 - 與物品的互動'
                },
                'examples': [
                    'smile → EXPRESSION',
                    'pointing → GESTURE',
                    'sitting → BODY_POSE',
                    'kiss → INTERACTION',
                    'holding_weapon → PROPS'
                ]
            },
            'OBJECTS': {
                'description': '物件道具 - 場景中的物品',
                'sub_categories': {
                    'WEAPONS': '武器 - 刀劍槍砲等',
                    'VEHICLES': '載具 - 車輛、船隻、飛機',
                    'FURNITURE': '家具 - 椅子、桌子、床',
                    'FOOD': '食物 - 飲食相關',
                    'ANIMALS': '動物 - 貓狗鳥等生物',
                    'MISCELLANEOUS': '雜項 - 其他物品',
                    'MATERIALS': '材質 - 繩子、鏈條、木材等材料'
                },
                'examples': [
                    'sword → WEAPONS',
                    'car → VEHICLES',
                    'chair → FURNITURE',
                    'cake → FOOD',
                    'cat → ANIMALS',
                    'book → MISCELLANEOUS',
                    'rope → MATERIALS'
                ]
            },
            'ENVIRONMENT': {
                'description': '環境場景 - 背景和環境描述',
                'sub_categories': {
                    'INDOOR': '室內環境',
                    'OUTDOOR': '室外環境',
                    'NATURE': '自然景觀',
                    'URBAN': '都市環境',
                    'FANTASY': '奇幻場景'
                },
                'examples': [
                    'room → INDOOR',
                    'sky → OUTDOOR',
                    'forest → NATURE',
                    'city → URBAN',
                    'castle → FANTASY'
                ]
            },
            'COMPOSITION': {
                'description': '構圖視角 - 拍攝角度和構圖方式',
                'sub_categories': {
                    'CAMERA_ANGLE': '拍攝角度 - from_above, from_below',
                    'FRAMING': '構圖框架 - portrait, full_body',
                    'PERSPECTIVE': '透視關係',
                    'CROP': '裁切方式'
                },
                'examples': [
                    'from_above → CAMERA_ANGLE',
                    'portrait → FRAMING',
                    'looking_at_viewer → PERSPECTIVE'
                ]
            },
            'VISUAL_EFFECTS': {
                'description': '視覺效果 - 光影、色彩、特效',
                'sub_categories': {
                    'LIGHTING': '光影效果',
                    'COLORS': '色彩效果',
                    'EFFECTS': '視覺特效',
                    'RENDERING': '渲染風格',
                    'SHAPES': '形狀圖案'
                },
                'examples': [
                    'sunlight → LIGHTING',
                    'colorful → COLORS',
                    'sparkle → EFFECTS',
                    'diamond_(shape) → SHAPES'
                ]
            },
            'ART_STYLE': {
                'description': '藝術風格 - 畫風類型',
                'sub_categories': {
                    'ANIME': '動漫風格',
                    'REALISTIC': '寫實風格',
                    'CARTOON': '卡通風格',
                    'PAINTERLY': '繪畫風格'
                },
                'examples': [
                    'anime → ANIME',
                    'photorealistic → REALISTIC',
                    'chibi → CARTOON',
                    'watercolor → PAINTERLY'
                ]
            },
            'ADULT_CONTENT': {
                'description': '成人內容 - 18+ 相關標籤',
                'sub_categories': {
                    'SEXUAL': '性行為相關',
                    'EXPLICIT_BODY': '裸露身體部位',
                    'SUGGESTIVE': '暗示性內容',
                    'CENSORSHIP': '審查相關'
                },
                'examples': [
                    'sex → SEXUAL',
                    'nipples → EXPLICIT_BODY',
                    'revealing_clothes → SUGGESTIVE',
                    'censored → CENSORSHIP'
                ]
            },
            'THEME_CONCEPT': {
                'description': '主題概念 - 抽象概念和主題',
                'sub_categories': {
                    'SEASON': '季節',
                    'HOLIDAY': '節日',
                    'TIME': '時間',
                    'WEATHER': '天氣',
                    'CONCEPT': '抽象概念'
                },
                'examples': [
                    'spring → SEASON',
                    'christmas → HOLIDAY',
                    'night → TIME',
                    'rain → WEATHER',
                    'dream → CONCEPT'
                ]
            },
            'TECHNICAL': {
                'description': '技術標籤 - 元數據和技術規格',
                'sub_categories': {
                    'METADATA': '元數據',
                    'QUALITY': '品質標籤',
                    'SOURCE': '來源標籤',
                    'FRAMING': '技術框架'
                },
                'examples': [
                    'highres → METADATA',
                    'masterpiece → QUALITY',
                    'translated → SOURCE',
                    'letterboxed → FRAMING'
                ]
            }
        }
    
    def create_low_freq_guidance(self) -> str:
        """創建低頻標籤專用指導"""
        return """

# 🔸 特別注意：低頻標籤處理指南

您現在處理的是**低頻標籤** (1K-10K 使用次數)，這些標籤具有特殊性：

## 標籤特點

1. **高度特殊化**
   - 非常具體或冷門的描述
   - 可能是罕見概念、新創詞
   - 某些可能是拼寫變體

2. **文化和語境依賴**
   - 日文詞彙（如 wa_maid, jiangshi）
   - 遊戲/動漫特定標籤（括號標註來源）
   - 網路迷因和次文化詞彙

3. **多重屬性可能性高**
   - 某些標籤難以單一分類
   - 可能同時具有多個特徵
   - 優先選擇最主要的屬性

## 處理原則

### 1. 語義理解優先
- 基於標籤的字面含義和通用用法
- 不要過度解讀或猜測
- 遊戲/作品特定性作為次要考慮

### 2. 信心度評估（調整後）
- **0.85-1.00**: 非常確定（標籤含義清晰）
- **0.75-0.85**: 確定（合理推斷）
- **0.65-0.75**: 較為確定（基於字面含義，低頻標籤可接受）
- **0.60-0.65**: 勉強確定（最低可接受線）
- **<0.60**: 不要使用（留給人工處理）

### 3. 特殊情況處理

**遊戲特定標籤** (帶括號):
```
例如: bangboo_(zenless_zone_zero)
處理: 提取 "bangboo" 的通用含義分類
reasoning: "Bangboo 是角色/生物類型，來源遊戲為 Zenless Zone Zero"
```

**日文詞彙**:
```
例如: wa_maid (和風女僕)
處理: wa_ 前綴表示日式風格，maid 是女僕
分類: CHARACTER_RELATED/CLOTHING
reasoning: "日式女僕服裝"
```

**模糊語義**:
```
例如: goblin (哥布林)
處理: 可能是角色、生物、或概念
分類: 選擇最常見用法 (CHARACTER_RELATED)
confidence: 0.75 (因為有多種可能)
reasoning: "哥布林通常指角色類型，但也可能是生物/怪物"
```

## 輸出要求

- 每個標籤都必須有分類結果
- 信心度最低 0.60（低於此則標記為無法分類）
- reasoning 要說明分類依據
- 如果是低頻且語義模糊，在 reasoning 中註明
"""
    
    def create_optimized_prompt(self, tags: List[str]) -> str:
        """創建優化的分類 prompt"""
        
        # 構建分類系統說明
        category_descriptions = []
        for main_code, info in self.category_system.items():
            category_descriptions.append(f"\n## {main_code}: {info['description']}")
            category_descriptions.append("副分類:")
            for sub_code, sub_desc in info['sub_categories'].items():
                category_descriptions.append(f"  - {sub_code}: {sub_desc}")
            category_descriptions.append("範例:")
            for example in info['examples'][:3]:  # 只顯示前3個範例
                category_descriptions.append(f"  {example}")
        
        category_system_text = "\n".join(category_descriptions)
        
        # 如果使用低頻提示詞，添加額外指導
        low_freq_guidance = self.create_low_freq_guidance() if self.use_low_freq_prompt else ""
        
        return f"""你是專業的 Danbooru 標籤分類專家。請根據以下完整的分類系統，將標籤分類到最合適的主分類和副分類。

# 分類系統
{category_system_text}
{low_freq_guidance}

# 分類策略和優先級

1. **優先考慮標籤的主要用途**
   - 分析標籤在實際圖片中最常見的用途
   - 選擇最能代表標籤核心含義的分類

2. **顏色相關標籤的處理**
   - 如果顏色與人物特徵相關（如 red_lips, blue_eyes），歸入 CHARACTER_RELATED/COLORS
   - 如果顏色與服裝相關（如 blue_dress），歸入 CHARACTER_RELATED/CLOTHING
   - 如果顏色與視覺效果相關（如 colorful），歸入 VISUAL_EFFECTS/COLORS

3. **身體部位和動作的區分**
   - 純粹的身體部位描述（如 hands, feet）→ CHARACTER_RELATED/BODY_PARTS
   - 涉及動作的描述（如 hands_up, kicking）→ ACTION_POSE/GESTURE 或 BODY_POSE

4. **服裝和配飾的區分**
   - 主要衣物（dress, shirt, skirt）→ CHARACTER_RELATED/CLOTHING
   - 裝飾性配件（necklace, bracelet, glasses）→ CHARACTER_RELATED/ACCESSORIES

5. **材質標籤**
   - rope, chain, leather 等材質詞 → OBJECTS/MATERIALS

6. **成人內容的謹慎處理**
   - 明確的性行為 → ADULT_CONTENT/SEXUAL
   - 身體裸露 → ADULT_CONTENT/EXPLICIT_BODY
   - 暗示性但未明確 → ADULT_CONTENT/SUGGESTIVE

7. **信心度評估**
   - 非常確定（標籤含義明確）: 0.90-1.0
   - 確定（分類合理）: 0.80-0.89
   - 較為確定（有其他可能但這個最佳）: 0.70-0.79
   - 勉強確定（多個分類都合理，低頻可接受）: 0.60-0.69

# 待分類標籤
{', '.join(tags)}

# 輸出格式
請以 JSON 格式回答，**不要使用 markdown code block**，直接輸出 JSON：
{{
  "classifications": [
    {{
      "tag": "標籤名稱",
      "main_category": "主分類代碼",
      "sub_category": "副分類代碼或null",
      "confidence": 0.95,
      "reasoning": "簡短的分類理由（1-2句）"
    }}
  ]
}}

注意事項：
- 每個標籤都必須有分類結果
- confidence 範圍 0-1，根據確定程度評估
- 如果沒有合適的副分類，sub_category 設為 null
- reasoning 要簡潔明確，說明為何選擇此分類
- 直接輸出 JSON，不要包含在 ```json ``` 中"""
    
    def classify_batch(self, tags: List[str], max_retries: int = None) -> List[ClassificationResult]:
        """批次分類標籤"""
        if max_retries is None:
            max_retries = LLM_CONFIG["max_retries"]
        
        results = []
        
        try:
            prompt = self.create_optimized_prompt(tags)
            
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
                        error="所有重試都失敗"
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
    
    def save_to_database(self, results: List[ClassificationResult], source_name: str = "optimized_llm") -> int:
        """保存分類結果到資料庫"""
        conn = sqlite3.connect('output/tags.db')
        cursor = conn.cursor()
        
        updated_count = 0
        
        for result in results:
            if result.success and result.main_category:
                # 更新資料庫
                cursor.execute('''
                    UPDATE tags_final 
                    SET main_category = ?,
                        sub_category = ?,
                        classification_source = ?,
                        classification_confidence = ?,
                        classification_reasoning = ?,
                        classification_timestamp = datetime('now')
                    WHERE name = ? 
                    AND danbooru_cat = 0 
                    AND main_category IS NULL
                ''', (
                    result.main_category,
                    result.sub_category,
                    source_name,
                    result.confidence,
                    result.reasoning,
                    result.tag_name
                ))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                    logger.info(f"[OK] {result.tag_name} -> {result.main_category}/{result.sub_category or 'N/A'} (信心度: {result.confidence:.3f})")
        
        conn.commit()
        conn.close()
        
        return updated_count


def batch_process_medium_frequency_tags(batch_size: int = 20, limit: int = None):
    """批量處理中頻率標籤 (100K-1M)"""
    print("="*80)
    print("LLM 批量處理 - 中高頻未分類標籤")
    print("="*80)
    
    conn = sqlite3.connect('output/tags.db')
    
    # 獲取中高頻未分類標籤
    query = '''
        SELECT name, post_count
        FROM tags_final 
        WHERE danbooru_cat = 0 
        AND main_category IS NULL
        AND post_count >= 100000 AND post_count < 1000000
        ORDER BY post_count DESC
    '''
    
    if limit:
        query += f' LIMIT {limit}'
    
    unclassified = conn.execute(query).fetchall()
    conn.close()
    
    total_tags = len(unclassified)
    print(f"\n找到 {total_tags} 個中高頻未分類標籤 (100K-1M)")
    
    if total_tags == 0:
        print("沒有需要處理的標籤")
        return
    
    # 初始化分類器
    classifier = OptimizedLLMClassifier()
    
    # 批次處理
    total_updated = 0
    total_batches = (total_tags + batch_size - 1) // batch_size
    
    for batch_idx in range(0, total_tags, batch_size):
        batch_tags = [tag for tag, _ in unclassified[batch_idx:batch_idx + batch_size]]
        batch_num = batch_idx // batch_size + 1
        
        print(f"\n處理批次 {batch_num}/{total_batches} ({len(batch_tags)} 個標籤)")
        
        # 分類
        results = classifier.classify_batch(batch_tags)
        
        # 保存到資料庫
        updated = classifier.save_to_database(results, "optimized_llm_batch")
        total_updated += updated
        
        print(f"批次 {batch_num} 完成: 更新 {updated} 個標籤")
        
        # 避免 API 限流
        if batch_idx + batch_size < total_tags:
            time.sleep(2)
    
    print(f"\n{'='*80}")
    print(f"批量處理完成")
    print(f"總處理標籤: {total_tags}")
    print(f"成功更新: {total_updated}")
    print(f"成功率: {total_updated/total_tags*100:.2f}%")
    print(f"{'='*80}")


if __name__ == "__main__":
    import sys
    
    # 根據命令行參數決定處理數量
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
        print(f"測試模式: 處理 {limit} 個標籤")
        batch_process_medium_frequency_tags(batch_size=20, limit=limit)
    else:
        print("完整模式: 處理所有中高頻標籤")
        user_input = input("確定要處理所有標籤嗎？(y/n): ")
        if user_input.lower() == 'y':
            batch_process_medium_frequency_tags(batch_size=20)
        else:
            print("已取消")

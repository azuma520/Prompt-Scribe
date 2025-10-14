# 🚀 API 優化快速開始指南

基於我們的討論和需求分析，本指南將幫助您快速開始 LLM 友好的 API 開發。

---

## 📋 計畫總覽

### 核心改進點

| 面向 | 改進前 | 改進後 | 效果 |
|------|--------|--------|------|
| LLM API 調用 | 2-3 次 | 1 次 | 簡化 60% |
| 開發時間 | 2-3 週 | 1 週 | 加速 50% |
| 初期成本 | $5 | $0 | 節省 100% |
| 複雜度 | 高 | 低 | 降低 70% |

### 開發策略

```
Week 1: 關鍵字搜尋 API    → 80% 需求覆蓋
Week 2: LLM 專用端點      → 90% 需求覆蓋  
Week 3-4: 測試和部署      → 生產就緒
未來: 向量搜尋（可選）    → 95%+ 需求覆蓋
```

---

## 🎯 Phase 1: 基礎 API 開發（本週）

### Step 1: 專案設置

```bash
# 建立 API 專案結構
mkdir -p prompt-scribe-api
cd prompt-scribe-api

# 建立目錄結構
mkdir -p api/{routers/{v1,llm,admin},services,models,tests,data}

# 建立核心檔案
touch api/main.py
touch api/config.py
touch api/requirements.txt
touch api/routers/__init__.py
touch api/routers/v1/__init__.py
touch api/routers/llm/__init__.py
touch api/services/__init__.py
touch api/models/__init__.py
```

### Step 2: 安裝依賴

```bash
# requirements.txt
cat > api/requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
supabase==2.3.0
python-dotenv==1.0.0
pydantic==2.5.0
pyyaml==6.0.1
httpx==0.26.0
python-multipart==0.0.6
EOF

# 安裝
pip install -r api/requirements.txt
```

### Step 3: 配置環境

```bash
# .env
cat > api/.env << 'EOF'
# Supabase 配置
SUPABASE_URL=https://fumuvmbhmmzkenizksyq.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# API 配置
API_TITLE=Prompt-Scribe API
API_VERSION=2.0.0
API_HOST=0.0.0.0
API_PORT=8000

# 快取配置
ENABLE_CACHE=true
CACHE_TTL=3600

# 日誌配置
LOG_LEVEL=INFO
EOF
```

### Step 4: 實作第一個端點

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.v1 import tags
from routers.llm import recommendations
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=os.getenv("API_TITLE", "Prompt-Scribe API"),
    version=os.getenv("API_VERSION", "2.0.0"),
    description="LLM 友好的 Danbooru 標籤 API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(tags.router, prefix="/api/v1", tags=["Tags"])
app.include_router(recommendations.router, prefix="/api/llm", tags=["LLM"])

@app.get("/")
async def root():
    return {
        "message": "Prompt-Scribe API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

```python
# api/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    
    # API
    api_title: str = "Prompt-Scribe API"
    api_version: str = "2.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Cache
    enable_cache: bool = True
    cache_ttl: int = 3600
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

```python
# api/services/supabase_client.py
from supabase import create_client, Client
from functools import lru_cache
from config import get_settings

@lru_cache()
def get_supabase_client() -> Client:
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )

@lru_cache()
def get_supabase_admin_client() -> Client:
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
```

### Step 5: 實作基礎標籤查詢

```python
# api/routers/v1/tags.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from services.supabase_client import get_supabase_client

router = APIRouter()

@router.get("/tags")
async def get_tags(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_popularity: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    查詢標籤列表
    
    - **name**: 標籤名稱篩選（模糊匹配）
    - **category**: 分類篩選
    - **min_popularity**: 最低流行度
    - **limit**: 返回數量（最多 100）
    - **offset**: 分頁偏移
    """
    try:
        client = get_supabase_client()
        query = client.table('tags_final').select('*', count='exact')
        
        # 篩選條件
        if name:
            query = query.ilike('name', f'%{name}%')
        if category:
            query = query.eq('main_category', category)
        if min_popularity > 0:
            query = query.gte('post_count', min_popularity)
        
        # 分頁和排序
        response = query.order('post_count', desc=True).range(offset, offset + limit - 1).execute()
        
        return {
            "data": response.data,
            "total": response.count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags/{tag_name}")
async def get_tag_detail(tag_name: str):
    """取得特定標籤的詳細資訊"""
    try:
        client = get_supabase_client()
        response = client.table('tags_final').select('*').eq('name', tag_name).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 6: 測試基礎功能

```bash
# 啟動 API
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 測試端點
curl http://localhost:8000/health
curl "http://localhost:8000/api/v1/tags?limit=5"
curl "http://localhost:8000/api/v1/tags/1girl"
```

---

## 🤖 Phase 2: LLM 專用端點（下週）

### Step 1: 建立同義詞字典

```yaml
# api/data/keyword_synonyms.yaml
character:
  girl: [1girl, female, woman, girl_character]
  boy: [1boy, male, man, boy_character]
  alone: [solo, single, one_person, solitary]
  people: [2people, 3people, multiple, group]

emotion:
  happy: [smile, smiling, cheerful, joyful, happy_expression]
  sad: [crying, tears, melancholy, sad_expression]
  lonely: [solo, alone, isolated, loneliness, solitary]

style:
  cyberpunk: [neon, futuristic, sci-fi, technology, cyber, digital, tech]
  anime: [manga, japanese_style, illustration, drawn, animated]
  realistic: [photorealistic, photo, real, photograph, photographic]

environment:
  city: [urban, cityscape, street, buildings, downtown, metropolitan]
  nature: [forest, mountain, outdoor, landscape, wilderness, natural]
  room: [bedroom, living_room, indoor, interior, indoors]
  school: [classroom, school_building, campus, academy]

time:
  night: [nighttime, evening, dark, moonlight, night_time]
  day: [daytime, sunlight, bright, sunny, day_time]
  sunset: [dusk, twilight, evening_glow, golden_hour]

clothing:
  uniform: [school_uniform, military_uniform, outfit, costume]
  dress: [gown, skirt, clothing, formal_dress]
  casual: [casual_clothes, everyday_wear, comfortable]

action:
  sitting: [seated, sit, sitting_down, sitting_on]
  standing: [stand, standing_up, upright, standing_on]
  running: [run, sprint, jogging, running_motion]
  looking: [looking_at_viewer, eye_contact, gaze, stare]
```

### Step 2: 實作關鍵字擴展服務

```python
# api/services/keyword_expander.py
import yaml
from pathlib import Path
from typing import List, Set, Dict
from functools import lru_cache

class KeywordExpander:
    def __init__(self, synonyms_file: str = "data/keyword_synonyms.yaml"):
        self.synonyms = self._load_synonyms(synonyms_file)
    
    def _load_synonyms(self, file_path: str) -> Dict[str, List[str]]:
        """載入同義詞字典"""
        file_path = Path(__file__).parent.parent / file_path
        if not file_path.exists():
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 扁平化字典
        flat_synonyms = {}
        for category, words in data.items():
            for word, synonyms in words.items():
                flat_synonyms[word.lower()] = [s.lower() for s in synonyms]
        
        return flat_synonyms
    
    def expand(self, query: str) -> Set[str]:
        """擴展查詢關鍵字"""
        keywords = query.lower().replace(',', ' ').split()
        expanded = set()
        
        for keyword in keywords:
            # 加入原始關鍵字
            expanded.add(keyword)
            
            # 加入同義詞
            if keyword in self.synonyms:
                expanded.update(self.synonyms[keyword])
        
        return expanded
    
    def extract_and_expand(self, text: str) -> Dict[str, any]:
        """提取並擴展關鍵字，返回詳細資訊"""
        original_keywords = text.lower().replace(',', ' ').split()
        expanded_keywords = self.expand(text)
        
        return {
            "original": original_keywords,
            "expanded": list(expanded_keywords),
            "expansion_count": len(expanded_keywords) - len(original_keywords)
        }

@lru_cache()
def get_keyword_expander():
    return KeywordExpander()
```

### Step 3: 實作 LLM 推薦端點

```python
# api/routers/llm/recommendations.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from services.supabase_client import get_supabase_client
from services.keyword_expander import get_keyword_expander
import time

router = APIRouter()

class RecommendTagsRequest(BaseModel):
    description: str = Field(..., description="用戶的圖像描述")
    max_tags: int = Field(10, ge=1, le=50, description="最多返回標籤數")
    exclude_adult: bool = Field(True, description="排除成人內容")
    min_popularity: int = Field(100, ge=0, description="最低流行度")
    balance_categories: bool = Field(True, description="平衡分類")

class TagRecommendation(BaseModel):
    tag: str
    confidence: float
    popularity_tier: str
    post_count: int
    category: str
    subcategory: Optional[str]
    match_reason: str
    usage_context: str
    weight: int
    related_tags: List[str] = []

@router.post("/recommend-tags", response_model=Dict)
async def recommend_tags(request: RecommendTagsRequest):
    """
    🤖 LLM 專用的智能標籤推薦
    
    根據自然語言描述，推薦最適合的標籤組合。
    包含詳細的解釋和使用建議，適合 LLM 直接使用。
    """
    start_time = time.time()
    
    try:
        # 1. 關鍵字提取和擴展
        expander = get_keyword_expander()
        keyword_info = expander.extract_and_expand(request.description)
        expanded_keywords = keyword_info["expanded"]
        
        # 2. 構建資料庫查詢
        client = get_supabase_client()
        
        # 使用 OR 查詢匹配多個關鍵字
        or_conditions = []
        for keyword in expanded_keywords:
            or_conditions.append(f"name.ilike.%{keyword}%")
        
        query = client.table('tags_final').select('*')
        
        # 基本篩選
        if request.exclude_adult:
            query = query.neq('main_category', 'ADULT_CONTENT')
        if request.min_popularity > 0:
            query = query.gte('post_count', request.min_popularity)
        
        # 關鍵字匹配（使用 OR）
        if or_conditions:
            query = query.or_(','.join(or_conditions[:10]))  # 限制條件數量
        
        # 執行查詢
        response = query.order('post_count', desc=True).limit(request.max_tags * 3).execute()
        
        if not response.data:
            return {
                "query": request.description,
                "recommended_tags": [],
                "category_distribution": {},
                "quality_assessment": {
                    "overall_score": 0,
                    "warnings": ["未找到匹配的標籤，請嘗試更具體的描述"]
                },
                "metadata": {
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "total_candidates": 0
                }
            }
        
        # 3. 智能排序和篩選
        recommendations = []
        category_counts = {}
        
        for tag_data in response.data[:request.max_tags * 2]:
            # 計算相關性分數
            relevance_score = calculate_relevance(
                tag_data['name'], 
                expanded_keywords, 
                keyword_info["original"]
            )
            
            # 計算流行度等級
            popularity_tier = get_popularity_tier(tag_data['post_count'])
            
            # 生成解釋
            match_reason = generate_match_reason(
                tag_data['name'],
                expanded_keywords,
                keyword_info["original"]
            )
            
            # 生成使用建議
            usage_context = generate_usage_context(tag_data['main_category'])
            
            rec = TagRecommendation(
                tag=tag_data['name'],
                confidence=relevance_score,
                popularity_tier=popularity_tier,
                post_count=tag_data['post_count'],
                category=tag_data['main_category'] or 'UNKNOWN',
                subcategory=tag_data.get('sub_category'),
                match_reason=match_reason,
                usage_context=usage_context,
                weight=int(relevance_score * 10),
                related_tags=[]  # 未來可以添加
            )
            
            recommendations.append(rec)
            
            # 統計分類
            category = tag_data['main_category'] or 'UNKNOWN'
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 4. 分類平衡（如果啟用）
        if request.balance_categories:
            recommendations = balance_by_category(recommendations, request.max_tags)
        else:
            recommendations = recommendations[:request.max_tags]
        
        # 5. 品質評估
        quality = assess_quality(recommendations, category_counts)
        
        # 6. 生成建議的 prompt
        suggested_prompt = ", ".join([r.tag for r in recommendations])
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "query": request.description,
            "recommended_tags": [r.dict() for r in recommendations],
            "category_distribution": category_counts,
            "quality_assessment": quality,
            "suggested_prompt": suggested_prompt,
            "metadata": {
                "processing_time_ms": processing_time,
                "total_candidates": len(response.data),
                "algorithm": "keyword_matching_v1",
                "cache_hit": False,
                "keywords_extracted": keyword_info["original"],
                "keywords_expanded": list(expanded_keywords)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 輔助函數
def calculate_relevance(tag_name: str, expanded_keywords: Set[str], original_keywords: List[str]) -> float:
    """計算相關性分數"""
    # 完全匹配原始關鍵字
    if tag_name in original_keywords:
        return 1.0
    
    # 前綴匹配原始關鍵字
    for keyword in original_keywords:
        if tag_name.startswith(keyword):
            return 0.9
    
    # 包含原始關鍵字
    for keyword in original_keywords:
        if keyword in tag_name:
            return 0.8
    
    # 匹配擴展關鍵字
    for keyword in expanded_keywords:
        if keyword in tag_name or tag_name in keyword:
            return 0.7
    
    return 0.5

def get_popularity_tier(post_count: int) -> str:
    """獲取流行度等級"""
    if post_count > 100000:
        return "very_popular"
    elif post_count > 10000:
        return "popular"
    elif post_count > 1000:
        return "moderate"
    else:
        return "niche"

def generate_match_reason(tag_name: str, expanded: Set[str], original: List[str]) -> str:
    """生成匹配原因"""
    # 檢查是否匹配原始關鍵字
    for keyword in original:
        if keyword in tag_name:
            return f"直接匹配關鍵字 '{keyword}'"
    
    # 檢查是否為同義詞擴展
    for keyword in original:
        for exp in expanded:
            if exp in tag_name and exp != keyword:
                return f"通過同義詞擴展: '{keyword}' → '{exp}'"
    
    return "相關標籤"

def generate_usage_context(category: str) -> str:
    """生成使用建議"""
    contexts = {
        'CHARACTER': '角色核心標籤，影響人物基本特徵和數量',
        'CHARACTER_RELATED': '角色相關標籤，描述外觀、服裝、特徵等細節',
        'ACTION_POSE': '動作姿態標籤，影響人物的動作和表情',
        'ENVIRONMENT': '環境標籤，設定場景背景、時間、地點',
        'ART_STYLE': '藝術風格標籤，影響整體畫風和視覺呈現',
        'OBJECTS': '物件標籤，添加場景中的物品和道具',
        'ARTIST': '藝術家標籤，模仿特定藝術家的風格',
        'COPYRIGHT': '版權標籤，指定特定作品或系列',
        'QUALITY': '品質標籤，控制圖像的解析度和品質',
        'TECHNICAL': '技術標籤，控制生成參數',
        'THEME_CONCEPT': '主題概念標籤，設定整體氛圍和主題',
        'VISUAL_EFFECTS': '視覺效果標籤，添加特殊效果'
    }
    return contexts.get(category, '通用標籤')

def balance_by_category(recommendations: List[TagRecommendation], max_tags: int) -> List[TagRecommendation]:
    """平衡分類分佈"""
    # 簡單的平衡策略：每個分類最多取 max_tags/3
    category_limits = {}
    max_per_category = max(3, max_tags // 3)
    
    balanced = []
    for rec in recommendations:
        category = rec.category
        current_count = category_limits.get(category, 0)
        
        if current_count < max_per_category:
            balanced.append(rec)
            category_limits[category] = current_count + 1
        
        if len(balanced) >= max_tags:
            break
    
    return balanced

def assess_quality(recommendations: List[TagRecommendation], category_counts: Dict[str, int]) -> Dict:
    """評估推薦品質"""
    if not recommendations:
        return {
            "overall_score": 0,
            "balance_score": 0,
            "popularity_score": 0,
            "warnings": ["無推薦結果"]
        }
    
    # 計算平均流行度
    avg_popularity = sum(r.post_count for r in recommendations) / len(recommendations)
    popularity_score = min(100, int((avg_popularity / 10000) * 50) + 50)
    
    # 計算分類平衡
    num_categories = len(category_counts)
    balance_score = min(100, num_categories * 25)
    
    # 整體分數
    overall_score = int((popularity_score + balance_score) / 2)
    
    warnings = []
    if num_categories < 2:
        warnings.append("建議添加更多分類的標籤以豐富畫面")
    if popularity_score < 50:
        warnings.append("部分標籤流行度較低，可能影響生圖品質")
    
    return {
        "overall_score": overall_score,
        "balance_score": balance_score,
        "popularity_score": popularity_score,
        "warnings": warnings
    }
```

### Step 7: 執行和測試

```bash
# 啟動 API
uvicorn main:app --reload

# 測試 LLM 端點
curl -X POST http://localhost:8000/api/llm/recommend-tags \
  -H "Content-Type: application/json" \
  -d '{
    "description": "a lonely girl in cyberpunk city at night",
    "max_tags": 8,
    "exclude_adult": true
  }'
```

---

## 📊 預期結果

### 成功指標

- ✅ API 響應時間 < 500ms
- ✅ 關鍵字擴展準確率 > 80%
- ✅ LLM 推薦相關性 > 85%
- ✅ 所有端點測試通過

### 交付物

**Week 1**:
- ✅ FastAPI 專案結構
- ✅ 3-4 個基礎端點
- ✅ Supabase 整合
- ✅ 基本測試

**Week 2**:
- ✅ LLM 推薦端點
- ✅ 品質驗證端點
- ✅ 關鍵字擴展系統
- ✅ 完整文檔

---

## 🎯 下一步行動

1. **立即開始**: 建立 FastAPI 專案結構
2. **今天完成**: 實作基礎端點並測試 Supabase 連接
3. **明天完成**: 實作關鍵字擴展系統
4. **本週末**: 完成第一個 LLM 推薦端點

**準備好開始了嗎？切換到 Agent 模式，我們開始實作！** 🚀

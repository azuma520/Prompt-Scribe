#!/usr/bin/env python3
"""
小批量文字標籤分類測試（OpenRouter / OpenAI SDK）
- 從 output/tags.db 取 25 個未分類（danbooru_cat=0 且 main_category IS NULL）的標籤
- 以嚴格 JSON Prompt 要求模型輸出 classifications 陣列
- 解析與統計 JSON 可解析率、欄位完整度、合法率
"""

import os
import json
import sqlite3
import re
from typing import Any, Dict, List
from pathlib import Path

# -------- .env loading (multi-path, utf-8-sig) --------
_loaded_env_files: List[str] = []
_parsed_keys: List[str] = []


def _load_env_file(env_path: Path) -> None:
    if env_path.exists():
        try:
            with env_path.open("r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip().lstrip("\ufeff")] = v.strip()
            _loaded_env_files.append(str(env_path))
        except Exception:
            pass


def _load_dotenv_multi() -> None:
    here = Path(__file__).parent
    cwd = Path.cwd()
    for p in [here / ".env", here.parent / ".env", cwd / ".env", cwd / "stage1/.env"]:
        _load_env_file(p)


_load_dotenv_multi()

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODEL = os.environ.get("DEEPSEEK_MODEL", "google/gemini-2.5-flash-lite-preview-09-2025")
REFERER = os.environ.get("OPENROUTER_REFERER", "")
TITLE = os.environ.get("OPENROUTER_TITLE", "")

if not API_KEY:
    print("找不到 DEEPSEEK_API_KEY，請確認 .env 設定。已載入:", ", ".join(_loaded_env_files) or "(無)")
    raise SystemExit(1)

# -------- OpenAI SDK (OpenRouter) --------
try:
    from openai import OpenAI
except Exception:
    print("請先安裝: pip install openai")
    raise

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

# -------- DB --------
DB_PATH = Path(__file__).parent / "output" / "tags.db"
if not DB_PATH.exists():
    print("找不到資料庫:", str(DB_PATH))
    raise SystemExit(1)

conn = sqlite3.connect(str(DB_PATH))

rows = conn.execute(
    """
    SELECT name FROM tags_final
    WHERE danbooru_cat = 0 AND (main_category IS NULL OR main_category = '')
    ORDER BY post_count DESC
    LIMIT 25
    """
).fetchall()

TAGS: List[str] = [r[0] for r in rows]
if not TAGS:
    print("沒有未分類的標籤可測試。")
    raise SystemExit(0)

# -------- Allowed enums --------
MAIN_SET = {
    "CHARACTER_RELATED", "ACTION_POSE", "OBJECTS", "ENVIRONMENT", "COMPOSITION",
    "VISUAL_EFFECTS", "ART_STYLE", "ADULT_CONTENT", "THEME_CONCEPT", "TECHNICAL",
}
SUB_ENUM: Dict[str, List[str]] = {
    "CHARACTER_RELATED": ["CLOTHING", "HAIR", "BODY_PARTS", "ACCESSORIES", "CHARACTER_COUNT"],
    "ACTION_POSE": ["EXPRESSION", "GESTURE", "BODY_POSE", "INTERACTION"],
    "OBJECTS": ["WEAPONS", "VEHICLES", "FURNITURE", "FOOD", "ANIMALS", "MISCELLANEOUS"],
    "ENVIRONMENT": ["INDOOR", "OUTDOOR", "NATURE", "URBAN", "FANTASY"],
    "COMPOSITION": ["CAMERA_ANGLE", "FRAMING", "PERSPECTIVE", "CROP"],
    "VISUAL_EFFECTS": ["LIGHTING", "COLORS", "EFFECTS", "RENDERING"],
    "ART_STYLE": ["ANIME", "REALISTIC", "CARTOON", "PAINTERLY"],
    "ADULT_CONTENT": ["SEXUAL", "EXPLICIT_BODY", "SUGGESTIVE", "CENSORSHIP"],
    "THEME_CONCEPT": ["SEASON", "HOLIDAY", "TIME", "WEATHER", "CONCEPT"],
    "TECHNICAL": ["METADATA", "QUALITY", "SOURCE", "COPYRIGHT"],
}

# Synonym map for mains
MAIN_SYNONYM_REVERSE = {
    "CHARACTER": "CHARACTER_RELATED",
    "CHARACTER_FEATURE": "CHARACTER_RELATED",
    "PERSON": "CHARACTER_RELATED",
    "PEOPLE": "CHARACTER_RELATED",
    "ACTION": "ACTION_POSE",
    "POSE": "ACTION_POSE",
    "OBJECT": "OBJECTS",
    "ITEM": "OBJECTS",
    "BACKGROUND": "ENVIRONMENT",
    "SCENE": "ENVIRONMENT",
    "COMPOSE": "COMPOSITION",
    "LAYOUT": "COMPOSITION",
    "EFFECT": "VISUAL_EFFECTS",
    "VISUAL": "VISUAL_EFFECTS",
    "STYLE": "ART_STYLE",
    "ART": "ART_STYLE",
    "ADULT": "ADULT_CONTENT",
    "NSFW": "ADULT_CONTENT",
    "THEME": "THEME_CONCEPT",
    "CONCEPT": "THEME_CONCEPT",
    "META": "TECHNICAL",
    "TECH": "TECHNICAL",
}

# -------- Prompt --------
SYSTEM_MSG = (
    "你是 Danbooru 標籤分類專家。將文字標籤歸類到 main_category 與 sub_category。"
    "main_category 必須屬於集合：CHARACTER_RELATED, ACTION_POSE, OBJECTS, ENVIRONMENT, COMPOSITION, VISUAL_EFFECTS, ART_STYLE, ADULT_CONTENT, THEME_CONCEPT, TECHNICAL。"
    "sub_category 僅能取對應列舉，否則一律 null。"
    "僅回 JSON：{""classifications"": [{""tag"": ""..."", ""main_category"": ""..."", ""sub_category"": null|""..."", ""confidence"": 0.0-1.0}]}。"
)
USER_MSG = (
    "請將以下標籤分類；遇到不確定副類別時 sub_category=null。\n"
    f"標籤（以逗號分隔）：{', '.join(TAGS)}\n"
    "僅回前述 JSON。"
)

# -------- Call --------
headers = {}
if REFERER:
    headers["HTTP-Referer"] = REFERER
if TITLE:
    headers["X-Title"] = TITLE

resp = client.chat.completions.create(
    model=os.environ.get("DEEPSEEK_MODEL", MODEL),
    messages=[
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": USER_MSG},
    ],
    extra_headers=headers,
    temperature=0.0,
    max_tokens=2000,
    response_format={"type": "json_object"},
    extra_body={"response_format": {"type": "json_object"}},
)

# -------- Helpers --------

def extract_json_any(content_obj: Any) -> str:
    if isinstance(content_obj, (dict, list)):
        return json.dumps(content_obj, ensure_ascii=False)
    text = str(content_obj or "")
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return m.group(0)
    m2 = re.search(r"\[[\s\S]*\]", text)
    return m2.group(0) if m2 else text

# de-structure response
try:
    data = getattr(resp, "model_dump", lambda: {})()
    if not data:
        data = getattr(resp, "dict", lambda: {})()
except Exception:
    data = {}

choices = (data.get("choices") or [])
content = None
if choices:
    ch0 = choices[0]
    try:
        msg = ch0.get("message", {})
        content = msg.get("content")
    except Exception:
        content = None

raw = extract_json_any(content)
print("原始 content(前400):", raw[:400])

# Normalize to {"classifications": [...]}
parsed_ok = False
classified: List[Dict[str, Any]] = []
try:
    obj = json.loads(raw)
    if isinstance(obj, list):
        classified = obj
    elif isinstance(obj, dict):
        classified = obj.get("classifications", [])
    parsed_ok = isinstance(classified, list)
except Exception:
    parsed_ok = False

# -------- Validate & coerce --------
required = ["tag", "main_category", "confidence"]
coerced = 0
normalized: List[Dict[str, Any]] = []

def norm_token(s: str) -> str:
    s = (s or "").upper()
    s = re.sub(r"[^A-Z0-9]+", "_", s).strip("_")
    return s

if parsed_ok:
    for item in classified:
        if not all(k in item for k in required):
            continue
        tag = str(item.get("tag"))
        mc_raw = str(item.get("main_category", ""))
        mc_norm = norm_token(mc_raw)
        if mc_norm not in MAIN_SET:
            mc_norm = MAIN_SYNONYM_REVERSE.get(mc_norm, mc_norm)
        if mc_norm not in MAIN_SET:
            lower = mc_raw.strip().lower()
            mapping = {
                "character": "CHARACTER_RELATED", "character_related": "CHARACTER_RELATED", "character_feature": "CHARACTER_RELATED",
                "action": "ACTION_POSE", "pose": "ACTION_POSE",
                "object": "OBJECTS", "item": "OBJECTS",
                "environment": "ENVIRONMENT", "scene": "ENVIRONMENT", "background": "ENVIRONMENT",
                "composition": "COMPOSITION", "layout": "COMPOSITION",
                "visual_effects": "VISUAL_EFFECTS", "visual": "VISUAL_EFFECTS", "effects": "VISUAL_EFFECTS",
                "art_style": "ART_STYLE", "style": "ART_STYLE", "art": "ART_STYLE",
                "adult": "ADULT_CONTENT", "nsfw": "ADULT_CONTENT", "adult_content": "ADULT_CONTENT",
                "theme": "THEME_CONCEPT", "concept": "THEME_CONCEPT", "theme_concept": "THEME_CONCEPT",
                "technical": "TECHNICAL", "meta": "TECHNICAL", "tech": "TECHNICAL",
            }
            mc_norm = mapping.get(lower, mc_norm)
        if mc_norm not in MAIN_SET:
            continue
        sc = item.get("sub_category", None)
        if sc is None:
            pass
        else:
            sc_norm = norm_token(str(sc))
            if sc_norm not in set(SUB_ENUM.get(mc_norm, [])):
                sc = None
                coerced += 1
            else:
                sc = sc_norm
        normalized.append({
            "tag": tag,
            "main_category": mc_norm,
            "sub_category": sc,
            "confidence": float(item.get("confidence", 0.0)),
        })

# -------- Report --------
print("載入 .env:", ", ".join(_loaded_env_files) or "(無)")
print("模型:", os.environ.get("DEEPSEEK_MODEL", MODEL))
print("取得標籤數:", len(TAGS))
print("JSON 可解析:", parsed_ok)
print("合規項數:", len(normalized))
print("副類別自動設為 null 項數:", coerced)
for item in normalized[:5]:
    print("-", item.get("tag"), "->", item.get("main_category"), "/", item.get("sub_category"), "conf=", item.get("confidence"))

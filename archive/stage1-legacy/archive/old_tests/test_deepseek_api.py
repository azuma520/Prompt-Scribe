#!/usr/bin/env python3
"""
使用 OpenAI SDK 透過 OpenRouter 測試 DeepSeek 模型連線與分類
"""

import os
import json
from typing import Dict, Any, List
from pathlib import Path

# 簡易 .env 載入（支援多路徑）

_loaded_env_files: List[str] = []
_parsed_keys: List[str] = []


def _load_env_file(env_path: Path) -> None:
    global _loaded_env_files, _parsed_keys
    if env_path.exists():
        try:
            with env_path.open("r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().lstrip("\ufeff")
                        v = v.strip()
                        os.environ[k] = v
                        if k not in _parsed_keys:
                            _parsed_keys.append(k)
            _loaded_env_files.append(str(env_path))
        except Exception:
            pass


def _load_dotenv_multi() -> None:
    here = Path(__file__).parent
    cwd = Path.cwd()
    candidates = [
        here / ".env",
        here.parent / ".env",
        cwd / ".env",
        cwd / "stage1/.env",
    ]
    seen = set()
    for p in candidates:
        if str(p) in seen:
            continue
        seen.add(str(p))
        _load_env_file(p)


_load_dotenv_multi()

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek/deepseek-chat-v3.1:free")
REFERER = os.environ.get("OPENROUTER_REFERER", "")
TITLE = os.environ.get("OPENROUTER_TITLE", "")

# 延遲匯入，避免未安裝時的啟動錯誤
try:
    from openai import OpenAI
except Exception as e:
    print("缺少 openai 套件，請先安裝: pip install openai")
    raise


def _choice_content(choice: Any) -> str:
    # 嘗試多種結構取得內容
    try:
        msg = getattr(choice, "message", None)
        if msg is not None:
            c = getattr(msg, "content", None)
            if c:
                return str(c)
    except Exception:
        pass
    try:
        # 字典結構
        if isinstance(choice, dict):
            return str(choice.get("message", {}).get("content") or "")
    except Exception:
        pass
    return ""


def _to_dict(obj: Any) -> Dict[str, Any]:
    try:
        return obj.model_dump()  # pydantic v2
    except Exception:
        pass
    try:
        return obj.dict()  # pydantic v1
    except Exception:
        pass
    try:
        return json.loads(obj.json())
    except Exception:
        pass
    # 最後一招：轉字串再不處理
    return {"raw": str(obj)}


def make_client() -> Any:
    if not API_KEY:
        print("未找到環境變數 DEEPSEEK_API_KEY")
        print("當前工作目錄:", str(Path.cwd()))
        print("已載入的 .env 檔案:", ", ".join(_loaded_env_files) or "(無)")
        print("解析到的鍵名:", ", ".join(_parsed_keys) or "(無)")
        raise SystemExit(1)
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)


def test_ping() -> bool:
    print("== 測試 OpenRouter 連線 ==")
    print("環境變數 DEEPSEEK_API_KEY 是否存在:", bool(API_KEY))
    client = make_client()
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Ping"}],
            extra_headers={
                **({"HTTP-Referer": REFERER} if REFERER else {}),
                **({"X-Title": TITLE} if TITLE else {}),
            },
            max_tokens=16,
            temperature=0.1,
        )
        data = _to_dict(resp)
        print("原始回應(精簡):", json.dumps(data, ensure_ascii=False)[:500])
        # 安全取 content
        content = ""
        try:
            choices = data.get("choices") or []
            if choices:
                content = _choice_content(choices[0])
        except Exception:
            pass
        print("回覆內容(截斷):", (content or "").strip()[:120])
        return True
    except Exception as e:
        print("連線失敗:", str(e)[:300])
        return False


def test_classify_sample() -> bool:
    print("\n== 測試小樣本分類 ==")
    client = make_client()
    prompt = (
        "請將以下標籤分類為 main_category 與 sub_category, JSON 格式: "
        "{'classifications': [{'tag':'...','main_category':'...','sub_category':null,'confidence':0.9,'reasoning':'...'}]}。"
        "標籤: 1girl, long_hair, dress, smile, solo, orchard, broken_staff"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                **({"HTTP-Referer": REFERER} if REFERER else {}),
                **({"X-Title": TITLE} if TITLE else {}),
            },
            temperature=0.1,
            max_tokens=1500,
        )
        data = _to_dict(resp)
        content = ""
        try:
            choices = data.get("choices") or []
            if choices:
                content = _choice_content(choices[0])
        except Exception:
            pass
        if not content:
            print("原始回應(精簡):", json.dumps(data, ensure_ascii=False)[:800])
            print("未獲得 content, 可能需調整 model 或回應格式。")
            return False
        print("原始回覆(前500字):\n", content[:500])
        try:
            parsed: Dict[str, Any] = json.loads(content)
            cl = parsed.get("classifications", [])
            print("解析到項目數:", len(cl))
            for item in cl[:5]:
                print("-", item.get("tag"), "->", item.get("main_category"), "/", item.get("sub_category"))
            return True
        except json.JSONDecodeError:
            print("JSON 解析失敗; 請檢查模型輸出格式是否需微調 prompt。")
            return False
    except Exception as e:
        print("分類失敗:", str(e)[:300])
        return False


def main() -> None:
    print("OpenRouter DeepSeek 測試 (SDK 版本)")
    ok = test_ping()
    if ok:
        test_classify_sample()


if __name__ == "__main__":
    main()

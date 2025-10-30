# -*- coding: utf-8 -*-
import pytest
from importlib import util as _import_util

# 動態載入，避免匯入 services 套件造成副作用（需要 config/supabase）
_spec = _import_util.spec_from_file_location(
    "inspire_tone_linter", "src/api/services/inspire_tone_linter.py"
)
_mod = _import_util.module_from_spec(_spec)  # type: ignore[arg-type]
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

InspireToneLinter = _mod.InspireToneLinter


def test_forbidden_phrase_detection():
    linter = InspireToneLinter()
    reply = "感謝您的輸入，我們的系統將為您提供建議。"
    is_valid, violations, metrics = linter.lint(reply)
    assert not is_valid
    assert metrics["forbidden_hits"] >= 1
    assert any("禁語" in v for v in violations)


def test_sentence_and_length_limits():
    linter = InspireToneLinter()
    # 首句超過 18 字、總長超過 80 字、句子超過 3 句
    reply = (
        "這一段話會比較長一點點，確實明顯超過十八個字，而且我們還要繼續增加字數，確保超過八十個字。"
        "第二句也在這裡。第三句也在這裡。第四句也在這裡，補一些內容讓總長再多一些。"
    )
    is_valid, violations, metrics = linter.lint(reply)
    assert not is_valid
    assert metrics["sentence_count"] > 3
    assert metrics["first_sentence_length"] > linter.MAX_FIRST_SENTENCE_LENGTH
    assert metrics["total_length"] > linter.MAX_TOTAL_LENGTH
    assert any("首句過長" in v for v in violations)
    assert any("句子過多" in v for v in violations)
    assert any("回覆過長" in v for v in violations)


def test_emoji_limit():
    linter = InspireToneLinter()
    reply = "好的！這個感覺很不錯 😊✨"
    is_valid, violations, metrics = linter.lint(reply)
    assert not is_valid
    assert metrics["emoji_count"] > linter.MAX_EMOJI_PER_REPLY
    assert any("Emoji 過多" in v for v in violations)


def test_suggest_rewrite():
    linter = InspireToneLinter()
    reply = "感謝您的輸入。這一段話會比較長一點點，超過十八個字。😊✨"
    is_valid, violations, metrics = linter.lint(reply)
    suggestion = linter.suggest_rewrite(reply, violations)
    # 應該有建議產生（避免編碼問題，僅檢查非空）
    assert isinstance(suggestion, str) and suggestion.strip() != ""



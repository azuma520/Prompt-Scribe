"""
Inspire Agent 語氣 Linter
記錄語氣指標，供分析和優化參考

【重要】
- 模式：log_only（只記錄，不干預）
- 不攔截 Agent 回應
- 不強制語氣規則
- 定期分析記錄，人工優化

【原則】
保持 Agent 靈活性，避免過度限制自然對話
"""

import re
from typing import Tuple, List

class InspireToneLinter:
    """語氣品質檢查器"""
    
    def __init__(self):
        # 禁語（機械式、客服化的說法）
        self.FORBIDDEN_PHRASES = [
            r"感謝您的輸入",
            r"根據系統分析",
            r"請稍候",
            r"已收到您的需求",
            r"檢測到",
            r"系統將",
            r"感謝使用",
            r"我們的系統",
            r"根據您的描述",
            r"經過分析",
            r"為您提供",
            r"請您",
            r"非常抱歉",
            r"讓我為您",
        ]
        
        # 推薦用語（親切朋友風格）
        self.RECOMMENDED_PHRASES = [
            "收到！",
            "這個感覺",
            "讓我幫你",
            "給你",
            "試試看",
            "怎麼樣",
            "好的！",
            "太棒了",
            "很有畫面感",
        ]
        
        # 語氣指標
        self.MAX_SENTENCES_PER_REPLY = 3
        self.MAX_FIRST_SENTENCE_LENGTH = 18  # 字數
        self.MAX_TOTAL_LENGTH = 80  # 字數
        self.MAX_EMOJI_PER_REPLY = 1
    
    def lint(self, reply: str) -> Tuple[bool, List[str], dict]:
        """
        檢查語氣品質
        
        Returns:
            (is_valid, violations, metrics)
        """
        
        violations = []
        metrics = {
            "total_length": len(reply),
            "sentence_count": 0,
            "first_sentence_length": 0,
            "emoji_count": 0,
            "forbidden_hits": 0
        }
        
        # 檢查 1: 禁語
        for pattern in self.FORBIDDEN_PHRASES:
            if re.search(pattern, reply):
                violations.append(f"包含禁語：{pattern}")
                metrics["forbidden_hits"] += 1
        
        # 檢查 2: 句子數量和長度
        sentences = self._split_sentences(reply)
        metrics["sentence_count"] = len(sentences)
        
        if sentences:
            metrics["first_sentence_length"] = len(sentences[0])
            
            if len(sentences[0]) > self.MAX_FIRST_SENTENCE_LENGTH:
                violations.append(
                    f"首句過長（{len(sentences[0])} > {self.MAX_FIRST_SENTENCE_LENGTH} 字）"
                )
        
        if len(sentences) > self.MAX_SENTENCES_PER_REPLY:
            violations.append(
                f"句子過多（{len(sentences)} > {self.MAX_SENTENCES_PER_REPLY}）"
            )
        
        # 檢查 3: 總長度
        if len(reply) > self.MAX_TOTAL_LENGTH:
            violations.append(
                f"回覆過長（{len(reply)} > {self.MAX_TOTAL_LENGTH} 字）"
            )
        
        # 檢查 4: Emoji 數量
        emoji_count = self._count_emoji(reply)
        metrics["emoji_count"] = emoji_count
        
        if emoji_count > self.MAX_EMOJI_PER_REPLY:
            violations.append(
                f"Emoji 過多（{emoji_count} > {self.MAX_EMOJI_PER_REPLY}）"
            )
        
        is_valid = len(violations) == 0
        
        return is_valid, violations, metrics
    
    def suggest_rewrite(self, reply: str, violations: List[str]) -> str:
        """建議改寫"""
        
        suggestions = []
        
        if any("禁語" in v for v in violations):
            suggestions.append("移除客服化用語，改用口語化表達")
        
        if any("過長" in v for v in violations):
            suggestions.append("精簡內容，每句話說一個重點")
        
        if any("Emoji" in v for v in violations):
            suggestions.append("減少 Emoji，一個回合最多一個")
        
        return "\n".join(suggestions)
    
    def _split_sentences(self, text: str) -> List[str]:
        """分句（中文）"""
        # 簡化版：按標點符號分句
        sentences = re.split(r'[。！？\n]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _count_emoji(self, text: str) -> int:
        """計算 Emoji 數量"""
        # 簡化版：匹配常見 Emoji Unicode 範圍
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        return len(emoji_pattern.findall(text))


# ============================================
# 使用範例（log_only 模式）— 僅示意，不在匯入時執行
# ============================================
if False:  # 避免在測試或匯入時引用未定義的 router
    async def check_agent_reply_log_only(reply: str) -> str:
        linter = InspireToneLinter()
        is_valid, violations, metrics = linter.lint(reply)
        logger.info(f"📊 語氣指標：{metrics}")
        if not is_valid:
            logger.debug(f"💡 語氣參考：{violations}")
        return reply

    @router.post("/api/inspire/start")
    async def start_inspire(request: dict):
        agent_reply = result.final_output
        checked_reply = await check_agent_reply_log_only(agent_reply)
        return {"response": checked_reply}


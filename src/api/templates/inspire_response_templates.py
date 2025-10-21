"""
Inspire Agent 回應模板（可複用原子模組）
確保語氣一致、格式統一
"""

from typing import List, Dict

class InspireResponseTemplates:
    """Inspire 回應模板庫"""
    
    # ============================================
    # A. 三卡方向卡片（短版原子模組）
    # ============================================
    
    @staticmethod
    def format_direction_cards(ideas: List[Dict]) -> str:
        """
        格式化三選一方向卡片
        
        Args:
            ideas: [
                {
                    "title": str,
                    "concept": str,
                    "vibe": str,  # 三個形容詞
                    "main_tags": [str]
                }
            ]
        """
        
        # 固定開場詞（保持簡潔）
        intro_phrases = [
            "給你三個方向：",
            "收到！三個方向：",
            "來看三個方向：",
        ]
        
        # 隨機選一個（避免重複感）
        import random
        intro = random.choice(intro_phrases)
        
        cards = [intro]
        
        for i, idea in enumerate(ideas[:3], 1):  # 最多 3 個
            # 提取三個形容詞（從 vibe 或 concept）
            adjectives = idea.get("vibe", "").split("、")[:3]
            adjectives_str = "、".join(adjectives)
            
            # 卡片格式（每張最多 3 行）
            card = f"""
{i}️⃣ {idea['title']}
{idea['concept'][:30]}...
→ {adjectives_str}   [更夢幻] [更寫實] [少人像] [加夜景]
""".strip()
            
            cards.append(card)
        
        return "\n\n".join(cards)
    
    # ============================================
    # B. 定稿輸出（短版原子模組）
    # ============================================
    
    @staticmethod
    def format_final_output(final_data: Dict) -> str:
        """
        格式化最終輸出
        
        Args:
            final_data: {
                "title": str,
                "positive_prompt": str,
                "negative_prompt": str,
                "parameters": {
                    "cfg_scale": float,
                    "steps": int,
                    "sampler": str
                },
                "usage_tips": str,
                "quality_score": int
            }
        """
        
        output = f"""好的！給你完整版 ✨
【{final_data['title']}】

Prompt：
{final_data['positive_prompt']}

負面：
{final_data['negative_prompt']}

參數：
• CFG {final_data['parameters']['cfg_scale']}｜Steps {final_data['parameters']['steps']}｜Sampler {final_data['parameters']['sampler']}

💡 Tip：{final_data['usage_tips']}
品質分數：{final_data['quality_score']}/100 ⭐"""
        
        return output.strip()
    
    # ============================================
    # C. 澄清問題（自然友好版）
    # ============================================
    
    @staticmethod
    def format_clarification(questions: List[str], context: str = "") -> str:
        """
        格式化澄清問題（避免審問感）
        
        Args:
            questions: 問題列表（最多 3 個）
            context: 上下文提示
        """
        
        # 開場詞（友好、自然）
        intros = [
            f"{context}讓我幫你具體化 😊",
            f"{context}幾個小問題：",
            f"{context}補充一下細節：",
        ]
        
        import random
        intro = random.choice(intros)
        
        # 格式化問題（最多 3 個）
        formatted_questions = []
        for q in questions[:3]:
            formatted_questions.append(f"• {q}")
        
        return f"{intro}\n\n" + "\n".join(formatted_questions)
    
    # ============================================
    # D. 品質修正提示（統一話術）
    # ============================================
    
    @staticmethod
    def format_quality_fix_notice(score: int) -> str:
        """品質修正提示"""
        
        if score >= 85:
            return ""  # 不需要提示
        
        elif score >= 70:
            return "我先幫你把小問題修好（分類平衡），再給你完整版。"
        
        else:  # score < 70
            return "這組有幾個地方打架，我幫你換成更穩的搭配，畫面會乾淨很多 👌"
    
    # ============================================
    # E. 安全改寫（風險內容替代）
    # ============================================
    
    @staticmethod
    def format_safety_alternative() -> str:
        """安全替代卡片開場"""
        return "這題材容易踩線，我改用象徵表達，效果也很棒👇"
    
    @staticmethod
    def get_safe_alternative_ideas() -> List[Dict]:
        """安全替代方向（固定三個）"""
        return [
            {
                "title": "光影意象",
                "concept": "抽象的光影流動，傳達情緒而非具象",
                "vibe": "抽象、光影、情緒",
                "main_tags": [
                    "abstract", "light", "glow", "particles",
                    "artistic", "conceptual", "minimalist",
                    "soft_colors", "ethereal", "atmospheric"
                ]
            },
            {
                "title": "自然元素",
                "concept": "花朵、葉子、水流等自然元素的組合",
                "vibe": "自然、療癒、和諧",
                "main_tags": [
                    "nature", "flowers", "leaves", "water",
                    "peaceful", "natural_beauty", "soft_focus",
                    "warm_colors", "gentle", "wholesome"
                ]
            },
            {
                "title": "抽象幾何",
                "concept": "幾何圖案構成的視覺語言，現代藝術感",
                "vibe": "幾何、現代、設計",
                "main_tags": [
                    "geometric", "abstract", "pattern", "modern_art",
                    "colorful", "design", "minimal", "artistic",
                    "contemporary", "clean"
                ]
            }
        ]
    
    # ============================================
    # F. 降級話術（資料庫失敗）
    # ============================================
    
    @staticmethod
    def format_fallback_notice() -> str:
        """資料庫失敗優雅降級"""
        return "我直接用靈感先帶你看三個方向，再補細節。"
    
    # ============================================
    # G. 成本限制話術（縮短版）
    # ============================================
    
    @staticmethod
    def format_cost_limit_notice() -> str:
        """成本限制提示"""
        return "這回合我們走捷徑，直接定一個最接近的給你。"
    
    # ============================================
    # H. 選擇確認（簡短）
    # ============================================
    
    @staticmethod
    def format_selection_confirm(selection: int, title: str) -> str:
        """確認選擇"""
        return f"收到！就用「{title}」這個方向 👌"
    
    # ============================================
    # I. 調整確認（簡短）
    # ============================================
    
    @staticmethod
    def format_adjustment_confirm(adjustment: str, changes: List[str]) -> str:
        """確認調整"""
        
        # 簡短描述變更
        if len(changes) <= 2:
            changes_str = "、".join(changes)
        else:
            changes_str = f"{changes[0]}、{changes[1]} 等 {len(changes)} 項"
        
        return f"好！{adjustment}（{changes_str}）"


# ============================================
# 使用範例
# ============================================

if __name__ == "__main__":
    templates = InspireResponseTemplates()
    
    # 範例 1: 三卡方向
    ideas = [
        {
            "title": "月下獨舞",
            "concept": "月光下獨自起舞的少女，裙擺如星光散落",
            "vibe": "孤獨、夢幻、優雅",
            "main_tags": ["1girl", "dancing", "moonlight"]
        },
        {
            "title": "星空遠望",
            "concept": "站在山巔仰望星河，背影透露孤獨與希望",
            "vibe": "孤獨、遼闊、希望",
            "main_tags": ["1girl", "from_behind", "starry_sky"]
        },
        {
            "title": "夢境漂浮",
            "concept": "漂浮在夢幻空間，四周是破碎的記憶碎片",
            "vibe": "孤獨、夢幻、超現實",
            "main_tags": ["1girl", "floating", "surreal"]
        }
    ]
    
    print(templates.format_direction_cards(ideas))
    print("\n" + "="*50 + "\n")
    
    # 範例 2: 定稿輸出
    final_data = {
        "title": "月下獨舞·夢幻版",
        "positive_prompt": "1girl, solo, dancing, moonlight, ...",
        "negative_prompt": "nsfw, child, loli, gore, lowres, ...",
        "parameters": {
            "cfg_scale": 8.0,
            "steps": 35,
            "sampler": "DPM++ 2M Karras"
        },
        "usage_tips": "夢幻風格建議 CFG 7-9",
        "quality_score": 88
    }
    
    print(templates.format_final_output(final_data))


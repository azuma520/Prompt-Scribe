#!/usr/bin/env python3
"""
規則自動提取器
從已處理的標籤中提取分類規則模式
"""

import sqlite3
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

from config import DB_PATH, OUTPUT_DIR


class AutoRuleExtractor:
    """規則自動提取器 - 從已分類標籤中提取規則"""
    
    def __init__(self, min_pattern_count: int = 5, min_confidence: float = 0.95):
        """初始化提取器
        
        Args:
            min_pattern_count: 最少模式出現次數
            min_confidence: 最低信心度要求
        """
        self.db_path = DB_PATH
        self.min_pattern_count = min_pattern_count
        self.min_confidence = min_confidence
        self.extracted_rules = []
    
    def extract_suffix_rules(self) -> List[Dict]:
        """提取後綴規則（如 _day, _hair, _eyes）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 獲取高信心度的已分類標籤
        cursor.execute("""
            SELECT name, main_category, sub_category, classification_confidence
            FROM tags_final
            WHERE main_category IS NOT NULL
            AND classification_confidence >= ?
            AND name LIKE '%\_%'
        """, (self.min_confidence,))
        
        tags = cursor.fetchall()
        conn.close()
        
        # 按後綴分組
        suffix_patterns = defaultdict(list)
        for name, main_cat, sub_cat, confidence in tags:
            if '_' in name:
                suffix = '_' + name.rsplit('_', 1)[-1]
                suffix_patterns[suffix].append({
                    'name': name,
                    'main_category': main_cat,
                    'sub_category': sub_cat,
                    'confidence': confidence
                })
        
        # 生成規則
        rules = []
        for suffix, tags_list in suffix_patterns.items():
            if len(tags_list) >= self.min_pattern_count:
                # 檢查分類一致性
                categories = [f"{t['main_category']}/{t['sub_category']}" for t in tags_list]
                category_counter = Counter(categories)
                most_common_cat, count = category_counter.most_common(1)[0]
                
                consistency = count / len(tags_list)
                if consistency >= 0.90:  # 90% 一致性
                    main_cat, sub_cat = most_common_cat.split('/')
                    rules.append({
                        'type': 'suffix',
                        'pattern': suffix,
                        'main_category': main_cat,
                        'sub_category': sub_cat if sub_cat != 'None' else None,
                        'support_count': len(tags_list),
                        'consistency': consistency,
                        'avg_confidence': sum(t['confidence'] for t in tags_list) / len(tags_list),
                        'examples': [t['name'] for t in tags_list[:5]]
                    })
        
        return sorted(rules, key=lambda x: x['support_count'], reverse=True)
    
    def extract_prefix_rules(self) -> List[Dict]:
        """提取前綴規則（如 white_, blue_, red_）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, main_category, sub_category, classification_confidence
            FROM tags_final
            WHERE main_category IS NOT NULL
            AND classification_confidence >= ?
            AND name LIKE '%\_%'
        """, (self.min_confidence,))
        
        tags = cursor.fetchall()
        conn.close()
        
        # 按前綴分組
        prefix_patterns = defaultdict(list)
        for name, main_cat, sub_cat, confidence in tags:
            if '_' in name:
                prefix = name.split('_', 1)[0] + '_'
                prefix_patterns[prefix].append({
                    'name': name,
                    'main_category': main_cat,
                    'sub_category': sub_cat,
                    'confidence': confidence
                })
        
        # 生成規則
        rules = []
        for prefix, tags_list in prefix_patterns.items():
            if len(tags_list) >= self.min_pattern_count:
                categories = [f"{t['main_category']}/{t['sub_category']}" for t in tags_list]
                category_counter = Counter(categories)
                most_common_cat, count = category_counter.most_common(1)[0]
                
                consistency = count / len(tags_list)
                if consistency >= 0.90:
                    main_cat, sub_cat = most_common_cat.split('/')
                    rules.append({
                        'type': 'prefix',
                        'pattern': prefix,
                        'main_category': main_cat,
                        'sub_category': sub_cat if sub_cat != 'None' else None,
                        'support_count': len(tags_list),
                        'consistency': consistency,
                        'avg_confidence': sum(t['confidence'] for t in tags_list) / len(tags_list),
                        'examples': [t['name'] for t in tags_list[:5]]
                    })
        
        return sorted(rules, key=lambda x: x['support_count'], reverse=True)
    
    def extract_contains_rules(self) -> List[Dict]:
        """提取包含規則（如包含 'girl', 'boy', 'animal'）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, main_category, sub_category, classification_confidence
            FROM tags_final
            WHERE main_category IS NOT NULL
            AND classification_confidence >= ?
        """, (self.min_confidence,))
        
        tags = cursor.fetchall()
        conn.close()
        
        # 常見詞彙
        common_words = [
            'girl', 'boy', 'hair', 'eye', 'dress', 'skirt', 'shirt', 
            'weapon', 'sword', 'gun', 'animal', 'cat', 'dog', 'bird',
            'background', 'sky', 'cloud', 'water', 'fire'
        ]
        
        # 按包含詞彙分組
        contains_patterns = defaultdict(list)
        for name, main_cat, sub_cat, confidence in tags:
            for word in common_words:
                if word in name:
                    contains_patterns[word].append({
                        'name': name,
                        'main_category': main_cat,
                        'sub_category': sub_cat,
                        'confidence': confidence
                    })
        
        # 生成規則
        rules = []
        for word, tags_list in contains_patterns.items():
            if len(tags_list) >= self.min_pattern_count:
                categories = [f"{t['main_category']}/{t['sub_category']}" for t in tags_list]
                category_counter = Counter(categories)
                most_common_cat, count = category_counter.most_common(1)[0]
                
                consistency = count / len(tags_list)
                if consistency >= 0.85:  # 85% 一致性（稍微寬鬆）
                    main_cat, sub_cat = most_common_cat.split('/')
                    rules.append({
                        'type': 'contains',
                        'pattern': word,
                        'main_category': main_cat,
                        'sub_category': sub_cat if sub_cat != 'None' else None,
                        'support_count': len(tags_list),
                        'consistency': consistency,
                        'avg_confidence': sum(t['confidence'] for t in tags_list) / len(tags_list),
                        'examples': [t['name'] for t in tags_list[:5]]
                    })
        
        return sorted(rules, key=lambda x: x['support_count'], reverse=True)
    
    def extract_all_rules(self) -> Dict[str, List[Dict]]:
        """提取所有類型的規則"""
        print("提取後綴規則...")
        suffix_rules = self.extract_suffix_rules()
        print(f"找到 {len(suffix_rules)} 個後綴規則")
        
        print("提取前綴規則...")
        prefix_rules = self.extract_prefix_rules()
        print(f"找到 {len(prefix_rules)} 個前綴規則")
        
        print("提取包含規則...")
        contains_rules = self.extract_contains_rules()
        print(f"找到 {len(contains_rules)} 個包含規則")
        
        self.extracted_rules = {
            'suffix': suffix_rules,
            'prefix': prefix_rules,
            'contains': contains_rules
        }
        
        return self.extracted_rules
    
    def generate_python_code(self, output_file: str = 'output/extracted_rules.py'):
        """生成 Python 規則代碼"""
        if not self.extracted_rules:
            self.extract_all_rules()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('#!/usr/bin/env python3\n')
            f.write('"""\n')
            f.write('自動提取的分類規則\n')
            f.write(f'生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('"""\n\n')
            
            # 後綴規則
            f.write('# 後綴規則\n')
            f.write('SUFFIX_RULES = {\n')
            for rule in self.extracted_rules['suffix'][:20]:  # 前 20 個
                sub_cat = f'"{rule["sub_category"]}"' if rule['sub_category'] else 'None'
                f.write(f'    "{rule["pattern"]}": ("{rule["main_category"]}", {sub_cat}),  ')
                f.write(f'# 支持度: {rule["support_count"]}, 一致性: {rule["consistency"]:.1%}\n')
            f.write('}\n\n')
            
            # 前綴規則
            f.write('# 前綴規則\n')
            f.write('PREFIX_RULES = {\n')
            for rule in self.extracted_rules['prefix'][:20]:
                sub_cat = f'"{rule["sub_category"]}"' if rule['sub_category'] else 'None'
                f.write(f'    "{rule["pattern"]}": ("{rule["main_category"]}", {sub_cat}),  ')
                f.write(f'# 支持度: {rule["support_count"]}, 一致性: {rule["consistency"]:.1%}\n')
            f.write('}\n\n')
            
            # 包含規則
            f.write('# 包含規則\n')
            f.write('CONTAINS_RULES = {\n')
            for rule in self.extracted_rules['contains'][:20]:
                sub_cat = f'"{rule["sub_category"]}"' if rule['sub_category'] else 'None'
                f.write(f'    "{rule["pattern"]}": ("{rule["main_category"]}", {sub_cat}),  ')
                f.write(f'# 支持度: {rule["support_count"]}, 一致性: {rule["consistency"]:.1%}\n')
            f.write('}\n\n')
            
            # 分類函數
            f.write('def apply_rules(tag_name: str) -> tuple:\n')
            f.write('    """應用提取的規則\n')
            f.write('    \n')
            f.write('    Returns:\n')
            f.write('        (main_category, sub_category) or (None, None)\n')
            f.write('    """\n')
            f.write('    # 後綴匹配\n')
            f.write('    for suffix, (main_cat, sub_cat) in SUFFIX_RULES.items():\n')
            f.write('        if tag_name.endswith(suffix):\n')
            f.write('            return (main_cat, sub_cat)\n')
            f.write('    \n')
            f.write('    # 前綴匹配\n')
            f.write('    for prefix, (main_cat, sub_cat) in PREFIX_RULES.items():\n')
            f.write('        if tag_name.startswith(prefix):\n')
            f.write('            return (main_cat, sub_cat)\n')
            f.write('    \n')
            f.write('    # 包含匹配\n')
            f.write('    for word, (main_cat, sub_cat) in CONTAINS_RULES.items():\n')
            f.write('        if word in tag_name:\n')
            f.write('            return (main_cat, sub_cat)\n')
            f.write('    \n')
            f.write('    return (None, None)\n')
        
        print(f"Python 規則代碼已生成: {output_path}")
    
    def generate_report(self, output_file: str = 'output/RULE_EXTRACTION_LOG.md'):
        """生成規則提取報告"""
        if not self.extracted_rules:
            self.extract_all_rules()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('# 規則自動提取記錄\n\n')
            f.write(f'**生成時間**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            f.write('---\n\n')
            
            # 總結
            total_rules = sum(len(rules) for rules in self.extracted_rules.values())
            f.write('## 📊 提取總結\n\n')
            f.write(f'- **總規則數**: {total_rules}\n')
            f.write(f'- **後綴規則**: {len(self.extracted_rules["suffix"])}\n')
            f.write(f'- **前綴規則**: {len(self.extracted_rules["prefix"])}\n')
            f.write(f'- **包含規則**: {len(self.extracted_rules["contains"])}\n\n')
            
            # 後綴規則
            f.write('## 後綴規則 (Top 20)\n\n')
            f.write('| 模式 | 主分類 | 副分類 | 支持度 | 一致性 | 平均信心度 |\n')
            f.write('|------|--------|--------|--------|--------|----------|\n')
            for rule in self.extracted_rules['suffix'][:20]:
                f.write(f'| `{rule["pattern"]}` | {rule["main_category"]} | {rule["sub_category"] or "N/A"} | ')
                f.write(f'{rule["support_count"]} | {rule["consistency"]:.1%} | {rule["avg_confidence"]:.3f} |\n')
            f.write('\n')
            
            # 前綴規則
            f.write('## 前綴規則 (Top 20)\n\n')
            f.write('| 模式 | 主分類 | 副分類 | 支持度 | 一致性 | 平均信心度 |\n')
            f.write('|------|--------|--------|--------|--------|----------|\n')
            for rule in self.extracted_rules['prefix'][:20]:
                f.write(f'| `{rule["pattern"]}` | {rule["main_category"]} | {rule["sub_category"] or "N/A"} | ')
                f.write(f'{rule["support_count"]} | {rule["consistency"]:.1%} | {rule["avg_confidence"]:.3f} |\n')
            f.write('\n')
            
            # 包含規則
            f.write('## 包含規則 (Top 20)\n\n')
            f.write('| 模式 | 主分類 | 副分類 | 支持度 | 一致性 | 平均信心度 |\n')
            f.write('|------|--------|--------|--------|--------|----------|\n')
            for rule in self.extracted_rules['contains'][:20]:
                f.write(f'| `{rule["pattern"]}` | {rule["main_category"]} | {rule["sub_category"] or "N/A"} | ')
                f.write(f'{rule["support_count"]} | {rule["consistency"]:.1%} | {rule["avg_confidence"]:.3f} |\n')
            f.write('\n')
            
            # 範例
            f.write('## 規則範例\n\n')
            for rule_type, rules in self.extracted_rules.items():
                if rules:
                    f.write(f'### {rule_type.capitalize()} 範例\n\n')
                    for rule in rules[:3]:
                        f.write(f'**模式**: `{rule["pattern"]}`\n')
                        f.write(f'- 分類: {rule["main_category"]}/{rule["sub_category"] or "N/A"}\n')
                        f.write(f'- 範例: {", ".join(rule["examples"])}\n\n')
        
        print(f"規則提取報告已生成: {output_path}")


if __name__ == "__main__":
    # 測試
    print("開始提取規則...")
    extractor = AutoRuleExtractor(min_pattern_count=5, min_confidence=0.90)
    
    rules = extractor.extract_all_rules()
    
    print("\n生成報告和代碼...")
    extractor.generate_report()
    extractor.generate_python_code()
    
    print("\n完成！")


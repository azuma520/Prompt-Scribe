#!/usr/bin/env python3
"""
資料分析腳本 - 分析 Danbooru 標籤 CSV 檔案
"""
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

# Danbooru 分類對照
DANBOORU_CATEGORIES = {
    0: 'General (一般)',
    1: 'Artist (藝術家)',
    3: 'Copyright (版權/作品)',
    4: 'Character (角色)',
    5: 'Meta (元資料)',
    6: 'Kontext (指令)',  # 特殊分類
    7: 'Technical (技術)',  # 新增
}

def analyze_csv_file(file_path: Path) -> Dict:
    """分析單個 CSV 檔案"""
    print(f"\n{'='*60}")
    print(f"[分析] 檔案: {file_path.name}")
    print(f"{'='*60}")
    
    stats = {
        'file_name': file_path.name,
        'total_lines': 0,
        'category_distribution': Counter(),
        'sample_tags': defaultdict(list),
        'top_tags': [],
        'field_structure': None,
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 讀取第一行判斷欄位結構
            first_line = f.readline().strip()
            fields = first_line.split(',')
            stats['field_structure'] = f"欄位數: {len(fields)}"
            
            # 重新開始讀取
            f.seek(0)
            reader = csv.reader(f)
            
            for row in reader:
                stats['total_lines'] += 1
                
                if len(row) >= 2:
                    tag_name = row[0]
                    try:
                        category = int(row[1])
                        stats['category_distribution'][category] += 1
                        
                        # 收集樣本（每個分類最多5個）
                        if len(stats['sample_tags'][category]) < 5:
                            post_count = int(row[2]) if len(row) >= 3 else 0
                            stats['sample_tags'][category].append((tag_name, post_count))
                    except ValueError:
                        pass
            
            # 排序 top tags
            all_tags = []
            f.seek(0)
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    try:
                        tag_name = row[0]
                        post_count = int(row[2])
                        all_tags.append((tag_name, post_count))
                    except ValueError:
                        pass
            
            stats['top_tags'] = sorted(all_tags, key=lambda x: x[1], reverse=True)[:10]
        
        # 輸出統計
        print(f"[統計] 總行數: {stats['total_lines']:,}")
        print(f"[結構] 欄位結構: {stats['field_structure']}")
        print(f"\n[分布] 分類分布:")
        for cat_id, count in sorted(stats['category_distribution'].items()):
            cat_name = DANBOORU_CATEGORIES.get(cat_id, f'Unknown ({cat_id})')
            percentage = (count / stats['total_lines']) * 100
            print(f"  {cat_name:30} {count:8,} ({percentage:5.1f}%)")
        
        print(f"\n[熱門] Top 10 熱門標籤:")
        for i, (tag, count) in enumerate(stats['top_tags'][:10], 1):
            print(f"  {i:2}. {tag:30} {count:10,}")
        
        print(f"\n[樣本] 各分類樣本標籤:")
        for cat_id in sorted(stats['sample_tags'].keys()):
            cat_name = DANBOORU_CATEGORIES.get(cat_id, f'Unknown ({cat_id})')
            print(f"\n  {cat_name}:")
            for tag, count in stats['sample_tags'][cat_id]:
                print(f"    - {tag:40} (使用次數: {count:,})")
        
        return stats
        
    except Exception as e:
        print(f"[錯誤] 錯誤: {e}")
        return stats


def analyze_json_file(file_path: Path) -> Dict:
    """分析 JSON 檔案"""
    print(f"\n{'='*60}")
    print(f"[分析] 檔案: {file_path.name}")
    print(f"{'='*60}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"[JSON] JSON 陣列，包含 {len(data)} 個項目")
            if len(data) > 0:
                print(f"\n[結構] 第一個項目的結構:")
                first_item = data[0]
                for key, value in first_item.items():
                    value_preview = str(value)[:50]
                    print(f"  - {key}: {value_preview}...")
        
        return {'file_name': file_path.name, 'items': len(data) if isinstance(data, list) else 1}
    
    except Exception as e:
        print(f"[錯誤] 錯誤: {e}")
        return {}


def main():
    """主函式"""
    data_dir = Path('data/raw')
    
    print("="*60)
    print("[工具] Danbooru 標籤資料分析工具")
    print("="*60)
    
    # 分析 CSV 檔案
    csv_files = sorted(data_dir.glob('*.csv'))
    csv_stats = []
    
    for csv_file in csv_files:
        stats = analyze_csv_file(csv_file)
        csv_stats.append(stats)
    
    # 分析 JSON 檔案
    json_files = sorted(data_dir.glob('*.json'))
    for json_file in json_files:
        analyze_json_file(json_file)
    
    # 總結報告
    print(f"\n{'='*60}")
    print("[總結] 總結報告")
    print(f"{'='*60}")
    
    total_tags = sum(s['total_lines'] for s in csv_stats)
    print(f"\n[統計] 總體統計:")
    print(f"  - CSV 檔案數量: {len(csv_files)}")
    print(f"  - JSON 檔案數量: {len(json_files)}")
    print(f"  - 標籤總數: {total_tags:,}")
    
    # 合併分類統計
    total_category_dist = Counter()
    for stats in csv_stats:
        total_category_dist.update(stats['category_distribution'])
    
    print(f"\n[分布] 總體分類分布:")
    for cat_id, count in sorted(total_category_dist.items()):
        cat_name = DANBOORU_CATEGORIES.get(cat_id, f'Unknown ({cat_id})')
        percentage = (count / total_tags) * 100 if total_tags > 0 else 0
        print(f"  {cat_name:30} {count:10,} ({percentage:5.1f}%)")
    
    # 重點觀察
    general_count = total_category_dist[0]
    general_percentage = (general_count / total_tags) * 100 if total_tags > 0 else 0
    
    print(f"\n[發現] 關鍵發現:")
    print(f"  - 一般標籤 (category=0) 數量: {general_count:,}")
    print(f"  - 一般標籤佔比: {general_percentage:.1f}%")
    print(f"  - **這些是需要進行細分類的主要目標**")
    
    # 估算 LLM 成本
    print(f"\n[成本] LLM 分類成本估算:")
    print(f"  如果全部使用 LLM 分類一般標籤:")
    print(f"    - GPT-4 Turbo (~$0.01/1K tokens): ${(general_count * 100 / 1000) * 0.01:.2f}")
    print(f"    - GPT-3.5 Turbo (~$0.001/1K tokens): ${(general_count * 100 / 1000) * 0.001:.2f}")
    print(f"\n  如果使用規則分類 70%，LLM 分類 30%:")
    print(f"    - GPT-4 Turbo: ${(general_count * 0.3 * 100 / 1000) * 0.01:.2f}")
    print(f"    - GPT-3.5 Turbo: ${(general_count * 0.3 * 100 / 1000) * 0.001:.2f}")


if __name__ == '__main__':
    main()


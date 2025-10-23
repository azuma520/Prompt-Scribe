#!/usr/bin/env python3
"""
測試規則分類器

快速驗證分類器是否正常工作
"""

import sys
sys.path.insert(0, 'src')

from classifier import RuleBasedClassifier, MAIN_CATEGORIES, SUB_CATEGORIES


def test_main_categories():
    """測試主分類"""
    print("="*60)
    print("測試主分類規則")
    print("="*60)
    
    classifier = RuleBasedClassifier()
    
    test_cases = [
        # CHARACTER_RELATED
        ('1girl', 'CHARACTER_RELATED'),
        ('long_hair', 'CHARACTER_RELATED'),
        ('school_uniform', 'CHARACTER_RELATED'),
        ('blue_eyes', 'CHARACTER_RELATED'),
        
        # OBJECTS
        ('sword', 'OBJECTS'),
        ('book', 'OBJECTS'),
        ('flower', 'OBJECTS'),
        
        # ENVIRONMENT
        ('indoors', 'ENVIRONMENT'),
        ('forest', 'ENVIRONMENT'),
        ('night', 'ENVIRONMENT'),
        
        # COMPOSITION
        ('from_above', 'COMPOSITION'),
        ('close-up', 'COMPOSITION'),
        ('looking_at_viewer', 'COMPOSITION'),
        
        # VISUAL_EFFECTS
        ('backlighting', 'VISUAL_EFFECTS'),
        ('glowing', 'VISUAL_EFFECTS'),
        
        # ART_STYLE
        ('anime', 'ART_STYLE'),
        ('sketch', 'ART_STYLE'),
        
        # ACTION_POSE
        ('sitting', 'ACTION_POSE'),
        ('smile', 'ACTION_POSE'),
        
        # QUALITY
        ('masterpiece', 'QUALITY'),
        ('best_quality', 'QUALITY'),
        
        # TECHNICAL
        ('highres', 'TECHNICAL'),
        ('4k', 'TECHNICAL'),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for tag, expected in test_cases:
        main_cat, sub_cat = classifier.classify(tag)
        status = "[OK]" if main_cat == expected else "[FAIL]"
        print(f"{status} {tag:25} -> Main: {main_cat:20} (Expected: {expected})")
        if main_cat == expected:
            correct += 1
    
    print(f"\n準確率: {correct}/{total} ({correct/total*100:.1f}%)")
    return correct == total


def test_sub_categories():
    """測試副分類"""
    print("\n" + "="*60)
    print("測試副分類規則")
    print("="*60)
    
    classifier = RuleBasedClassifier()
    
    test_cases = [
        # CHARACTER_RELATED 副分類
        ('1girl', 'CHARACTER_RELATED', 'CHARACTER_COUNT'),
        ('solo', 'CHARACTER_RELATED', 'CHARACTER_COUNT'),
        ('long_hair', 'CHARACTER_RELATED', 'HAIR'),
        ('ponytail', 'CHARACTER_RELATED', 'HAIR'),
        ('school_uniform', 'CHARACTER_RELATED', 'CLOTHING'),
        ('dress', 'CHARACTER_RELATED', 'CLOTHING'),
        
        # ACTION_POSE 副分類
        ('sitting', 'ACTION_POSE', 'POSE'),
        ('standing', 'ACTION_POSE', 'POSE'),
        ('smile', 'ACTION_POSE', 'EXPRESSION'),
        ('blush', 'ACTION_POSE', 'EXPRESSION'),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for tag, expected_main, expected_sub in test_cases:
        main_cat, sub_cat = classifier.classify(tag)
        main_ok = main_cat == expected_main
        sub_ok = sub_cat == expected_sub
        status = "[OK]" if (main_ok and sub_ok) else "[FAIL]"
        sub_cat_str = sub_cat if sub_cat else "None"
        print(f"{status} {tag:20} -> Main: {main_cat:20} Sub: {sub_cat_str:15} (Expected: {expected_sub})")
        if main_ok and sub_ok:
            correct += 1
    
    print(f"\n準確率: {correct}/{total} ({correct/total*100:.1f}%)")
    return correct == total


def test_real_tags():
    """測試真實標籤（從 danbooru.csv 取樣）"""
    print("\n" + "="*60)
    print("測試真實標籤")
    print("="*60)
    
    classifier = RuleBasedClassifier()
    
    # 從實際資料取樣的熱門標籤
    real_tags = [
        '1girl', 'highres', 'solo', 'long_hair', 'breasts',
        'looking_at_viewer', 'blush', 'smile', 'open_mouth', 'short_hair',
        'blue_eyes', 'blonde_hair', 'simple_background', 'white_background',
        'dress', 'thighhighs', 'school_uniform', 'twintails', 'red_eyes',
        'sitting', 'large_breasts', 'standing', 'hair_ornament', 'skirt',
    ]
    
    for tag in real_tags:
        main_cat, sub_cat = classifier.classify(tag)
        main_cat_str = main_cat if main_cat else "UNCLASSIFIED"
        sub_info = f" -> {sub_cat}" if sub_cat else ""
        print(f"{tag:25} -> {main_cat_str:20}{sub_info}")
    
    stats = classifier.get_stats()
    print(f"\n統計：")
    print(f"  總處理: {stats['total_processed']}")
    print(f"  已分類: {stats['classified']}")
    print(f"  未分類: {stats['unclassified']}")
    print(f"  覆蓋率: {stats['coverage_rate']}")


def main():
    """主函式"""
    print("Prompt-Scribe 規則分類器測試\n")
    
    # 顯示分類架構
    print("分類架構：")
    print(f"主分類：{len(MAIN_CATEGORIES)} 個")
    for code, name in MAIN_CATEGORIES.items():
        sub_count = len(SUB_CATEGORIES.get(code, {}))
        sub_info = f" ({sub_count} 個副分類)" if sub_count > 0 else ""
        print(f"  - {code}: {name}{sub_info}")
    print()
    
    # 執行測試
    test1_passed = test_main_categories()
    test2_passed = test_sub_categories()
    test_real_tags()
    
    print("\n" + "="*60)
    if test1_passed and test2_passed:
        print("[SUCCESS] All tests passed!")
    else:
        print("[WARNING] Some tests failed, rules need adjustment")
    print("="*60)


if __name__ == '__main__':
    main()


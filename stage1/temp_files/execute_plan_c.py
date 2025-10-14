#!/usr/bin/env python3
"""
Plan C 主執行器
一鍵啟動完整的 Plan C 執行流程
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """檢查執行環境"""
    logger.info("檢查執行環境...")
    
    checks = []
    
    # 1. 檢查 Python 版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        checks.append(("✅", f"Python 版本: {python_version.major}.{python_version.minor}"))
    else:
        checks.append(("❌", f"Python 版本過低: {python_version.major}.{python_version.minor} (需要 3.8+)"))
        return False
    
    # 2. 檢查必需文件
    required_files = [
        'config.py',
        'llm_config.py',
        'optimized_llm_classifier.py',
        'run_plan_c_phase1.py',
        'run_plan_c_phase2.py'
    ]
    
    for file in required_files:
        if Path(file).exists():
            checks.append(("✅", f"文件存在: {file}"))
        else:
            checks.append(("❌", f"缺少文件: {file}"))
            return False
    
    # 3. 檢查數據庫
    if Path('output/tags.db').exists():
        checks.append(("✅", "數據庫文件: output/tags.db"))
    else:
        checks.append(("❌", "缺少數據庫文件: output/tags.db"))
        return False
    
    # 4. 檢查 API 配置
    try:
        from llm_config import LLM_CONFIG
        if LLM_CONFIG['api_key']:
            checks.append(("✅", "API Key 已配置"))
        else:
            checks.append(("❌", "API Key 未設置"))
            return False
    except Exception as e:
        checks.append(("❌", f"LLM 配置錯誤: {e}"))
        return False
    
    # 顯示檢查結果
    print("\n" + "="*60)
    print("環境檢查結果")
    print("="*60)
    for emoji, message in checks:
        print(f"{emoji} {message}")
    print("="*60 + "\n")
    
    return all(check[0] == "✅" for check in checks)


def get_current_stats():
    """獲取當前統計"""
    try:
        import sqlite3
        conn = sqlite3.connect('output/tags.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tags_final")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tags_final WHERE main_category IS NOT NULL")
        classified = cursor.fetchone()[0]
        
        coverage = (classified / total * 100) if total > 0 else 0.0
        
        conn.close()
        
        return {
            'total': total,
            'classified': classified,
            'unclassified': total - classified,
            'coverage': coverage
        }
    except Exception as e:
        logger.error(f"無法獲取統計: {e}")
        return None


def confirm_execution(stats):
    """確認執行"""
    print("\n" + "🎯"*30)
    print("Plan C 執行計畫")
    print("🎯"*30)
    print(f"\n當前狀態:")
    print(f"  總標籤數: {stats['total']:,}")
    print(f"  已分類: {stats['classified']:,}")
    print(f"  未分類: {stats['unclassified']:,}")
    print(f"  覆蓋率: {stats['coverage']:.2f}%")
    print(f"\n目標:")
    print(f"  覆蓋率: 96.00%+")
    print(f"  預計處理: ~8,500 個標籤")
    print(f"  預計成本: ~$0.88")
    print(f"  預計時間: 13-15 小時")
    print("\n" + "="*60)
    
    response = input("\n是否開始執行 Plan C? (yes/no): ").strip().lower()
    return response in ['yes', 'y', '是']


def execute_phase1():
    """執行 Phase 1"""
    logger.info("\n" + "🚀"*30)
    logger.info("開始執行 Phase 1: 中頻標籤處理")
    logger.info("🚀"*30 + "\n")
    
    import subprocess
    
    result = subprocess.run(
        [sys.executable, 'run_plan_c_phase1.py'],
        capture_output=False
    )
    
    return result.returncode == 0


def execute_phase2():
    """執行 Phase 2"""
    logger.info("\n" + "🚀"*30)
    logger.info("開始執行 Phase 2: 低頻標籤處理")
    logger.info("🚀"*30 + "\n")
    
    import subprocess
    
    result = subprocess.run(
        [sys.executable, 'run_plan_c_phase2.py'],
        capture_output=False
    )
    
    return result.returncode == 0


def generate_final_summary():
    """生成最終總結"""
    stats = get_current_stats()
    
    if not stats:
        logger.error("無法生成最終總結")
        return
    
    print("\n" + "🎉"*30)
    print("Plan C 執行完成！")
    print("🎉"*30)
    print(f"\n最終結果:")
    print(f"  覆蓋率: {stats['coverage']:.2f}%")
    print(f"  已分類標籤: {stats['classified']:,}")
    print(f"  未分類標籤: {stats['unclassified']:,}")
    
    if stats['coverage'] >= 96.0:
        print("\n✅ 目標達成！覆蓋率 >= 96%")
        print("\n下一步:")
        print("  1. 查看最終報告: output/96_PERCENT_ACHIEVEMENT.md")
        print("  2. 運行品質檢查: python quality_consistency_checker.py")
        print("  3. 準備 Stage 2")
    else:
        print(f"\n⚠️ 目標未完全達成 (目標 96.00%, 實際 {stats['coverage']:.2f}%)")
        print(f"  還需處理 ~{stats['unclassified']:,} 個標籤")
    
    print("\n" + "="*90 + "\n")


def main():
    """主函數"""
    print("\n" + "="*90)
    print(" "*30 + "Plan C 執行器")
    print("="*90 + "\n")
    
    # 1. 檢查環境
    if not check_environment():
        logger.error("環境檢查失敗，請修復問題後重試")
        return 1
    
    # 2. 獲取當前統計
    stats = get_current_stats()
    if not stats:
        logger.error("無法獲取當前統計")
        return 1
    
    # 3. 確認執行
    if not confirm_execution(stats):
        logger.info("用戶取消執行")
        return 0
    
    start_time = time.time()
    
    try:
        # 4. 執行 Phase 1
        if stats['coverage'] < 91.5:
            logger.info("需要執行 Phase 1（中頻標籤處理）")
            if not execute_phase1():
                logger.error("Phase 1 執行失敗")
                return 1
            
            # 更新統計
            stats = get_current_stats()
            logger.info(f"Phase 1 完成，當前覆蓋率: {stats['coverage']:.2f}%")
        else:
            logger.info("Phase 1 已完成，跳過")
        
        # 5. 執行 Phase 2
        if stats['coverage'] < 96.0:
            logger.info("需要執行 Phase 2（低頻標籤處理）")
            
            # 詢問是否繼續
            if stats['coverage'] >= 91.5:
                response = input("\nPhase 1 已完成，是否繼續執行 Phase 2? (yes/no): ").strip().lower()
                if response not in ['yes', 'y', '是']:
                    logger.info("用戶選擇不繼續")
                    return 0
            
            if not execute_phase2():
                logger.error("Phase 2 執行失敗")
                return 1
        else:
            logger.info("Phase 2 已完成，目標已達成")
        
        # 6. 生成最終總結
        total_time = time.time() - start_time
        logger.info(f"\n總執行時間: {total_time/3600:.2f} 小時")
        
        generate_final_summary()
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n\n用戶中斷執行")
        logger.info("進度已保存，可以重新運行此腳本繼續")
        return 1
    except Exception as e:
        logger.error(f"執行異常: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())


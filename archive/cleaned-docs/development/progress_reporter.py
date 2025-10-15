#!/usr/bin/env python3
"""
進度報告生成器
自動生成各階段的進度報告文檔
"""

import sqlite3
from typing import List, Dict
from datetime import datetime
from pathlib import Path

from config import DB_PATH, OUTPUT_DIR


class ProgressReporter:
    """進度報告生成器"""
    
    def __init__(self):
        """初始化報告生成器"""
        self.db_path = DB_PATH
        self.output_dir = OUTPUT_DIR
    
    def get_overall_stats(self) -> Dict:
        """獲取整體統計數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 總標籤數
        cursor.execute("SELECT COUNT(*) FROM tags_final")
        total_tags = cursor.fetchone()[0]
        
        # 已分類標籤數
        cursor.execute("""
            SELECT COUNT(*) FROM tags_final
            WHERE main_category IS NOT NULL
        """)
        classified_tags = cursor.fetchone()[0]
        
        # 覆蓋率
        coverage = (classified_tags / total_tags * 100) if total_tags > 0 else 0.0
        
        # 平均信心度
        cursor.execute("""
            SELECT AVG(classification_confidence)
            FROM tags_final
            WHERE main_category IS NOT NULL
            AND classification_confidence IS NOT NULL
        """)
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # 按頻率範圍統計
        frequency_ranges = []
        ranges = [
            ('50K-100K', 50000, 100000),
            ('30K-50K', 30000, 50000),
            ('20K-30K', 20000, 30000),
            ('10K-20K', 10000, 20000),
            ('5K-10K', 5000, 10000),
            ('3K-5K', 3000, 5000),
            ('1K-3K', 1000, 3000)
        ]
        
        for range_name, min_count, max_count in ranges:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN main_category IS NOT NULL THEN 1 ELSE 0 END) as classified
                FROM tags_final
                WHERE post_count >= ? AND post_count < ?
            """, (min_count, max_count))
            
            total, classified = cursor.fetchone()
            if total > 0:
                frequency_ranges.append({
                    'range': range_name,
                    'total': total,
                    'classified': classified or 0,
                    'unclassified': total - (classified or 0),
                    'coverage': ((classified or 0) / total * 100)
                })
        
        conn.close()
        
        return {
            'total_tags': total_tags,
            'classified_tags': classified_tags,
            'unclassified_tags': total_tags - classified_tags,
            'coverage': coverage,
            'avg_confidence': avg_confidence,
            'frequency_ranges': frequency_ranges
        }
    
    def generate_phase1_report(self, phase_stats: List[Dict],
                               total_processed: int, total_success: int):
        """生成 Phase 1 進度報告"""
        output_file = self.output_dir / 'PLAN_C_PHASE1_PROGRESS.md'
        
        overall_stats = self.get_overall_stats()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Plan C Phase 1 進度報告\n\n")
            f.write(f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 整體進度
            f.write("## 📊 整體進度\n\n")
            f.write(f"- **當前覆蓋率**: {overall_stats['coverage']:.2f}%\n")
            f.write(f"- **已分類標籤**: {overall_stats['classified_tags']:,} / {overall_stats['total_tags']:,}\n")
            f.write(f"- **未分類標籤**: {overall_stats['unclassified_tags']:,}\n")
            f.write(f"- **平均信心度**: {overall_stats['avg_confidence']:.3f}\n\n")
            
            # Phase 1 統計
            f.write("## 🎯 Phase 1 統計 (中頻標籤 10K-100K)\n\n")
            f.write(f"- **總處理**: {total_processed:,} 個標籤\n")
            f.write(f"- **總成功**: {total_success:,} 個\n")
            f.write(f"- **成功率**: {(total_success/total_processed*100 if total_processed > 0 else 0):.1f}%\n\n")
            
            # 各 Phase 詳情
            if phase_stats:
                f.write("### Phase 詳情\n\n")
                f.write("| Phase | 處理數 | 成功數 | 成功率 | 平均信心度 | 耗時 |\n")
                f.write("|-------|--------|--------|--------|-----------|------|\n")
                
                for stats in phase_stats:
                    duration_str = f"{stats['duration']/60:.1f} 分鐘" if stats['duration'] < 3600 else f"{stats['duration']/3600:.1f} 小時"
                    f.write(f"| {stats['phase']} | {stats['processed']:,} | {stats['success']:,} | {stats['success_rate']:.1%} | {stats['avg_confidence']:.3f} | {duration_str} |\n")
                f.write("\n")
            
            # 頻率範圍覆蓋率
            f.write("## 📈 頻率範圍覆蓋率\n\n")
            f.write("| 頻率範圍 | 總數 | 已分類 | 未分類 | 覆蓋率 |\n")
            f.write("|---------|------|--------|--------|--------|\n")
            
            for freq_range in overall_stats['frequency_ranges']:
                status_emoji = "✅" if freq_range['coverage'] >= 95 else "🚧" if freq_range['coverage'] >= 50 else "⏳"
                f.write(f"| {freq_range['range']} | {freq_range['total']:,} | {freq_range['classified']:,} | {freq_range['unclassified']:,} | {status_emoji} {freq_range['coverage']:.1f}% |\n")
            f.write("\n")
            
            # 下一步
            f.write("## 🎯 下一步計畫\n\n")
            if overall_stats['coverage'] < 91.5:
                f.write("- 繼續完成 Phase 1 的剩餘 phase\n")
                f.write("- 目標: 達到 91.5% 覆蓋率\n")
            elif overall_stats['coverage'] < 96.0:
                f.write("- Phase 1 已完成，準備開始 Phase 2\n")
                f.write("- 目標: 處理低頻標籤 (1K-10K)\n")
                f.write("- 預期達成: 96%+ 覆蓋率\n")
            else:
                f.write("- 🎉 已達成 96%+ 覆蓋率目標！\n")
                f.write("- 進入品質優化和審查階段\n")
            f.write("\n")
        
        print(f"Phase 1 進度報告已生成: {output_file}")
    
    def generate_phase1_final_report(self, phase_stats: List[Dict],
                                     total_processed: int, total_success: int,
                                     total_duration: float):
        """生成 Phase 1 最終報告"""
        output_file = self.output_dir / 'PLAN_C_PHASE1_FINAL_REPORT.md'
        
        overall_stats = self.get_overall_stats()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Plan C Phase 1 最終報告\n\n")
            f.write(f"**完成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 執行總結
            f.write("## 🎉 執行總結\n\n")
            f.write(f"- **總處理標籤**: {total_processed:,} 個\n")
            f.write(f"- **成功處理**: {total_success:,} 個\n")
            f.write(f"- **整體成功率**: {(total_success/total_processed*100 if total_processed > 0 else 0):.1f}%\n")
            f.write(f"- **總耗時**: {total_duration/3600:.2f} 小時\n")
            f.write(f"- **平均處理速度**: {total_processed/(total_duration/3600):.0f} 個/小時\n\n")
            
            # 達成成果
            f.write("## ✅ 達成成果\n\n")
            f.write(f"- **當前覆蓋率**: {overall_stats['coverage']:.2f}%\n")
            f.write(f"- **已分類標籤**: {overall_stats['classified_tags']:,}\n")
            f.write(f"- **平均信心度**: {overall_stats['avg_confidence']:.3f}\n\n")
            
            # 各 Phase 詳細統計
            f.write("## 📊 各 Phase 詳細統計\n\n")
            f.write("| Phase | 處理數 | 成功數 | 失敗數 | 成功率 | 平均信心度 | 耗時 |\n")
            f.write("|-------|--------|--------|--------|--------|-----------|------|\n")
            
            for stats in phase_stats:
                duration_str = f"{stats['duration']/60:.1f} 分鐘" if stats['duration'] < 3600 else f"{stats['duration']/3600:.1f} 小時"
                f.write(f"| {stats['phase']} | {stats['processed']:,} | {stats['success']:,} | {stats['failed']:,} | {stats['success_rate']:.1%} | {stats['avg_confidence']:.3f} | {duration_str} |\n")
            f.write("\n")
            
            # 品質評估
            f.write("## 📈 品質評估\n\n")
            
            if phase_stats:
                avg_success_rate = sum(s['success_rate'] for s in phase_stats) / len(phase_stats)
                avg_confidence = sum(s['avg_confidence'] for s in phase_stats) / len(phase_stats)
            else:
                avg_success_rate = 0.0
                avg_confidence = 0.0
            
            f.write(f"- **平均成功率**: {avg_success_rate:.1%}")
            if avg_success_rate >= 0.95:
                f.write(" ✅ 優秀\n")
            elif avg_success_rate >= 0.90:
                f.write(" ⚠️ 良好\n")
            else:
                f.write(" 🛑 需要改進\n")
            
            f.write(f"- **平均信心度**: {avg_confidence:.3f}")
            if avg_confidence >= 0.85:
                f.write(" ✅ 優秀\n")
            elif avg_confidence >= 0.75:
                f.write(" ⚠️ 良好\n")
            else:
                f.write(" 🛑 需要改進\n")
            f.write("\n")
            
            # 中頻標籤完成狀態
            f.write("## 🎯 中頻標籤完成狀態\n\n")
            
            medium_freq_ranges = [r for r in overall_stats['frequency_ranges'] if r['range'] in ['50K-100K', '30K-50K', '20K-30K', '10K-20K']]
            
            f.write("| 頻率範圍 | 總數 | 已分類 | 未分類 | 覆蓋率 | 狀態 |\n")
            f.write("|---------|------|--------|--------|--------|------|\n")
            
            for freq_range in medium_freq_ranges:
                if freq_range['coverage'] >= 95:
                    status = "✅ 完成"
                elif freq_range['coverage'] >= 80:
                    status = "🚧 接近完成"
                else:
                    status = "⏳ 進行中"
                f.write(f"| {freq_range['range']} | {freq_range['total']:,} | {freq_range['classified']:,} | {freq_range['unclassified']:,} | {freq_range['coverage']:.1f}% | {status} |\n")
            f.write("\n")
            
            # 下一階段計畫
            f.write("## 🚀 Phase 2 準備\n\n")
            f.write("Phase 1 (中頻標籤) 已完成，現在準備進入 Phase 2。\n\n")
            f.write("### Phase 2 目標\n\n")
            f.write("- **處理範圍**: 低頻標籤 (1K-10K post_count)\n")
            f.write("- **預計標籤數**: ~7,159 個\n")
            f.write("- **預計覆蓋率提升**: +5.08%\n")
            f.write("- **目標覆蓋率**: 96.63%\n\n")
            f.write("### 執行方式\n\n")
            f.write("```bash\n")
            f.write("python run_plan_c_phase2.py\n")
            f.write("```\n\n")
        
        print(f"Phase 1 最終報告已生成: {output_file}")
    
    def generate_phase2_report(self, phase_stats: List[Dict],
                               total_processed: int, total_success: int):
        """生成 Phase 2 進度報告"""
        output_file = self.output_dir / 'PLAN_C_PHASE2_PROGRESS.md'
        
        overall_stats = self.get_overall_stats()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Plan C Phase 2 進度報告\n\n")
            f.write(f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 整體進度
            f.write("## 📊 整體進度\n\n")
            f.write(f"- **當前覆蓋率**: {overall_stats['coverage']:.2f}%\n")
            f.write(f"- **距離目標 (96%)**: {96.0 - overall_stats['coverage']:.2f}%\n")
            f.write(f"- **已分類標籤**: {overall_stats['classified_tags']:,} / {overall_stats['total_tags']:,}\n")
            f.write(f"- **未分類標籤**: {overall_stats['unclassified_tags']:,}\n")
            f.write(f"- **平均信心度**: {overall_stats['avg_confidence']:.3f}\n\n")
            
            # Phase 2 統計
            f.write("## 🎯 Phase 2 統計 (低頻標籤 1K-10K)\n\n")
            f.write(f"- **總處理**: {total_processed:,} 個標籤\n")
            f.write(f"- **總成功**: {total_success:,} 個\n")
            f.write(f"- **成功率**: {(total_success/total_processed*100 if total_processed > 0 else 0):.1f}%\n\n")
            
            # 各 Phase 詳情
            if phase_stats:
                f.write("### Phase 詳情\n\n")
                f.write("| Phase | 處理數 | 成功數 | 成功率 | 平均信心度 | 耗時 |\n")
                f.write("|-------|--------|--------|--------|-----------|------|\n")
                
                for stats in phase_stats:
                    duration_str = f"{stats['duration']/60:.1f} 分鐘" if stats['duration'] < 3600 else f"{stats['duration']/3600:.1f} 小時"
                    f.write(f"| {stats['phase']} | {stats['processed']:,} | {stats['success']:,} | {stats['success_rate']:.1%} | {stats['avg_confidence']:.3f} | {duration_str} |\n")
                f.write("\n")
            
            # 低頻標籤覆蓋率
            f.write("## 📈 低頻標籤覆蓋率\n\n")
            
            low_freq_ranges = [r for r in overall_stats['frequency_ranges'] if r['range'] in ['5K-10K', '3K-5K', '1K-3K']]
            
            f.write("| 頻率範圍 | 總數 | 已分類 | 未分類 | 覆蓋率 |\n")
            f.write("|---------|------|--------|--------|--------|\n")
            
            for freq_range in low_freq_ranges:
                status_emoji = "✅" if freq_range['coverage'] >= 80 else "🚧" if freq_range['coverage'] >= 50 else "⏳"
                f.write(f"| {freq_range['range']} | {freq_range['total']:,} | {freq_range['classified']:,} | {freq_range['unclassified']:,} | {status_emoji} {freq_range['coverage']:.1f}% |\n")
            f.write("\n")
            
            # 進度評估
            if overall_stats['coverage'] >= 96.0:
                f.write("## 🎉 目標達成！\n\n")
                f.write(f"- 已達成 96%+ 覆蓋率目標！\n")
                f.write(f"- 當前覆蓋率: {overall_stats['coverage']:.2f}%\n")
                f.write(f"- 進入品質審查和優化階段\n\n")
            else:
                f.write("## 🎯 下一步\n\n")
                remaining = overall_stats['unclassified_tags']
                f.write(f"- 繼續處理剩餘 {remaining:,} 個未分類標籤\n")
                f.write(f"- 距離 96% 目標還需: {96.0 - overall_stats['coverage']:.2f}%\n\n")
        
        print(f"Phase 2 進度報告已生成: {output_file}")
    
    def generate_milestone_report(self, milestone: int):
        """生成里程碑報告
        
        Args:
            milestone: 里程碑百分比 (91, 92, 93, 94, 95, 96)
        """
        output_file = self.output_dir / f'{milestone}_PERCENT_MILESTONE.md'
        
        overall_stats = self.get_overall_stats()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 🎉 {milestone}% 覆蓋率里程碑達成！\n\n")
            f.write(f"**達成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 📊 當前統計\n\n")
            f.write(f"- **覆蓋率**: {overall_stats['coverage']:.2f}%\n")
            f.write(f"- **已分類標籤**: {overall_stats['classified_tags']:,}\n")
            f.write(f"- **未分類標籤**: {overall_stats['unclassified_tags']:,}\n")
            f.write(f"- **平均信心度**: {overall_stats['avg_confidence']:.3f}\n\n")
            
            # 里程碑評語
            if milestone == 91:
                f.write("## 🎯 意義\n\n")
                f.write("這標誌著中頻標籤處理的初步成功，我們已經覆蓋了大部分高價值標籤！\n\n")
            elif milestone == 92:
                f.write("## 🎯 意義\n\n")
                f.write("92% 是 Plan C 的第一個重要里程碑！繼續保持這個勢頭！\n\n")
            elif milestone == 96:
                f.write("## 🎉 目標達成！\n\n")
                f.write("恭喜達成 Plan C 的主要目標！這是一個重大成就！\n\n")
                f.write("### 下一步\n\n")
                f.write("- 品質審查和優化\n")
                f.write("- 準備 Stage 2 遷移\n")
                f.write("- 慶祝這個成功！🎊\n\n")
        
        print(f"{milestone}% 里程碑報告已生成: {output_file}")


if __name__ == "__main__":
    # 測試
    reporter = ProgressReporter()
    
    # 生成測試報告
    test_stats = [
        {
            'phase': 'Test Phase 1',
            'processed': 300,
            'success': 285,
            'failed': 15,
            'success_rate': 0.95,
            'avg_confidence': 0.88,
            'duration': 1800  # 30 分鐘
        }
    ]
    
    print("生成測試進度報告...")
    reporter.generate_phase1_report(test_stats, 300, 285)


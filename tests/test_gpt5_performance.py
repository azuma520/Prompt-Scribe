#!/usr/bin/env python3
"""
GPT-5 Mini 性能測試
測試回應時間、Token 使用和成本
"""
import sys
import os
import asyncio
import time
from statistics import mean, stdev, median
from typing import List, Dict, Any

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

from services.gpt5_nano_client import GPT5NanoClient

# 測試描述
TEST_DESCRIPTIONS = [
    "一個長髮藍眼的動漫女孩",
    "戶外場景，日落",
    "穿著校服的女孩",
    "masterpiece, high quality",
    "cat ears girl smiling",
    "城市夜景，霓虹燈",
    "櫻花樹下的女孩",
    "可愛的貓耳女僕",
    "cyberpunk city at night",
    "beautiful anime artwork"
]

async def performance_test(num_requests: int = 10):
    """性能測試"""
    print("="*60)
    print(f"⚡ GPT-5 Mini 性能測試 ({num_requests} 次請求)")
    print("="*60)
    
    client = GPT5NanoClient()
    
    if not client.is_available():
        print("❌ GPT-5 客戶端不可用")
        return False
    
    print(f"\n📊 測試配置:")
    print(f"  - 模型: {client.model}")
    print(f"  - 請求數: {num_requests}")
    print(f"  - 測試描述: {len(TEST_DESCRIPTIONS)} 種")
    
    # 收集數據
    response_times = []
    tag_counts = []
    confidences = []
    successes = 0
    failures = 0
    
    print(f"\n🔄 開始測試...")
    print("-"*60)
    
    for i in range(num_requests):
        description = TEST_DESCRIPTIONS[i % len(TEST_DESCRIPTIONS)]
        
        print(f"\n  [{i+1}/{num_requests}] 測試: {description[:30]}...")
        
        try:
            start_time = time.time()
            result = await client.generate_tags(description)
            elapsed = time.time() - start_time
            
            if result:
                tags = result.get('tags', [])
                confidence = result.get('confidence', 0)
                
                response_times.append(elapsed)
                tag_counts.append(len(tags))
                confidences.append(confidence)
                successes += 1
                
                print(f"    ✅ 成功 ({elapsed:.2f}秒)")
                print(f"       標籤: {len(tags)}個, 信心度: {confidence:.2f}")
            else:
                failures += 1
                print(f"    ❌ 失敗: 返回 None")
                
        except Exception as e:
            failures += 1
            print(f"    ❌ 錯誤: {e}")
    
    # 統計分析
    print(f"\n{'='*60}")
    print(f"📊 性能統計結果")
    print(f"{'='*60}")
    
    if not response_times:
        print("❌ 沒有成功的測試數據")
        return False
    
    # 回應時間統計
    print(f"\n⏱️  回應時間:")
    print(f"  - 平均: {mean(response_times):.2f}秒")
    print(f"  - 中位數: {median(response_times):.2f}秒")
    print(f"  - 標準差: {stdev(response_times):.2f}秒" if len(response_times) > 1 else "  - 標準差: N/A")
    print(f"  - 最快: {min(response_times):.2f}秒")
    print(f"  - 最慢: {max(response_times):.2f}秒")
    
    # 標籤統計
    print(f"\n🏷️  標籤數量:")
    print(f"  - 平均: {mean(tag_counts):.1f}個")
    print(f"  - 中位數: {median(tag_counts):.0f}個")
    print(f"  - 範圍: {min(tag_counts)}-{max(tag_counts)}個")
    
    # 信心度統計
    print(f"\n📈 信心度:")
    print(f"  - 平均: {mean(confidences):.3f}")
    print(f"  - 中位數: {median(confidences):.3f}")
    print(f"  - 範圍: {min(confidences):.2f}-{max(confidences):.2f}")
    
    # 成功率
    total = successes + failures
    success_rate = (successes / total * 100) if total > 0 else 0
    
    print(f"\n✅ 成功率:")
    print(f"  - 成功: {successes}/{total}")
    print(f"  - 失敗: {failures}/{total}")
    print(f"  - 成功率: {success_rate:.1f}%")
    
    # 成本估算
    avg_tokens = 284  # 基於之前的測試
    cost_per_1k_input = 0.020  # gpt-5-mini 價格
    cost_per_1k_output = 0.080
    
    estimated_cost_per_request = (avg_tokens / 1000) * cost_per_1k_output
    total_estimated_cost = estimated_cost_per_request * successes
    
    print(f"\n💰 成本估算:")
    print(f"  - 每請求: ~${estimated_cost_per_request:.6f}")
    print(f"  - {successes} 次請求: ~${total_estimated_cost:.4f}")
    print(f"  - 預估 1,000 次: ~${estimated_cost_per_request * 1000:.2f}")
    print(f"  - 預估 10,000 次: ~${estimated_cost_per_request * 10000:.2f}")
    
    # 性能評級
    print(f"\n{'='*60}")
    print(f"📊 性能評級")
    print(f"{'='*60}")
    
    # 回應時間評級
    avg_time = mean(response_times)
    time_rating = "優秀" if avg_time < 2 else "良好" if avg_time < 3 else "可接受" if avg_time < 5 else "需優化"
    time_emoji = "⭐⭐⭐⭐⭐" if avg_time < 2 else "⭐⭐⭐⭐" if avg_time < 3 else "⭐⭐⭐" if avg_time < 5 else "⭐⭐"
    
    print(f"  回應時間: {time_rating} {time_emoji}")
    print(f"    ({avg_time:.2f}秒平均)")
    
    # 標籤質量評級
    avg_tags = mean(tag_counts)
    tags_rating = "優秀" if avg_tags >= 10 else "良好" if avg_tags >= 8 else "可接受" if avg_tags >= 5 else "需優化"
    tags_emoji = "⭐⭐⭐⭐⭐" if avg_tags >= 10 else "⭐⭐⭐⭐" if avg_tags >= 8 else "⭐⭐⭐" if avg_tags >= 5 else "⭐⭐"
    
    print(f"  標籤數量: {tags_rating} {tags_emoji}")
    print(f"    ({avg_tags:.1f}個平均)")
    
    # 信心度評級
    avg_conf = mean(confidences)
    conf_rating = "優秀" if avg_conf >= 0.9 else "良好" if avg_conf >= 0.85 else "可接受" if avg_conf >= 0.8 else "需優化"
    conf_emoji = "⭐⭐⭐⭐⭐" if avg_conf >= 0.9 else "⭐⭐⭐⭐" if avg_conf >= 0.85 else "⭐⭐⭐" if avg_conf >= 0.8 else "⭐⭐"
    
    print(f"  信心度: {conf_rating} {conf_emoji}")
    print(f"    ({avg_conf:.3f}平均)")
    
    # 可靠性評級
    reliability_rating = "優秀" if success_rate >= 99 else "良好" if success_rate >= 95 else "可接受" if success_rate >= 90 else "需優化"
    reliability_emoji = "⭐⭐⭐⭐⭐" if success_rate >= 99 else "⭐⭐⭐⭐" if success_rate >= 95 else "⭐⭐⭐" if success_rate >= 90 else "⭐⭐"
    
    print(f"  可靠性: {reliability_rating} {reliability_emoji}")
    print(f"    ({success_rate:.1f}%成功率)")
    
    # 總體評級
    ratings = [time_rating, tags_rating, conf_rating, reliability_rating]
    excellent_count = ratings.count("優秀")
    
    print(f"\n總體評價:")
    if excellent_count >= 3:
        print(f"  🏆 優秀 - GPT-5 Mini 表現卓越！")
    elif excellent_count >= 2 or "良好" in ratings:
        print(f"  ✅ 良好 - GPT-5 Mini 可以投入生產")
    elif "可接受" in ratings:
        print(f"  ⚠️ 可接受 - 建議優化後再部署")
    else:
        print(f"  ❌ 需優化 - 不建議立即部署")
    
    print(f"\n{'='*60}")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        num_tests = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        success = asyncio.run(performance_test(num_tests))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 測試被中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

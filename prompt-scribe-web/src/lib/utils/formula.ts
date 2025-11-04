// Prompt 公式構建工具

import type { InspirationCard } from '@/types/inspire';

/**
 * 從靈感卡構建完整 Prompt
 * 基於 AI 人像創作公式
 */
export function buildPromptFromCard(card: InspirationCard): string {
  const parts: string[] = [];

  // 1. 人物主體（必填）
  parts.push(card.subject);

  // 2. 服裝造型
  if (card.outfit) parts.push(card.outfit);

  // 3. 場景
  parts.push(card.scene);

  // 4. 人像回調
  if (card.callback) parts.push(card.callback);

  // 5. 光線
  if (card.lighting) parts.push(card.lighting);

  // 6. 鏡頭
  if (card.lens) parts.push(card.lens);

  // 7. 機位角度
  if (card.angle) parts.push(card.angle);

  // 8. 構圖
  if (card.composition) parts.push(card.composition);

  // 9. 風格
  parts.push(card.style);

  // 10. 輔助詞
  if (card.extra) parts.push(card.extra);

  return parts.join(', ');
}

/**
 * 格式化為帶權重的 Prompt
 */
export function buildPromptWithWeights(card: InspirationCard): string {
  const weight = card.confidence_score || 1.0;
  const prompt = buildPromptFromCard(card);

  // 為高信心度的元素添加權重
  if (weight >= 0.9) {
    return `(${prompt}:1.2)`;
  } else if (weight >= 0.8) {
    return `(${prompt}:1.1)`;
  }

  return prompt;
}

/**
 * 格式化為 JSON 字串（美化）
 */
export function formatCardAsJSON(card: InspirationCard): string {
  return JSON.stringify(card, null, 2);
}


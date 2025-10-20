// Inspire 功能型別定義

/**
 * 靈感卡片結構
 * 基於 AI 人像創作公式
 */
export interface InspirationCard {
  // 核心元素
  subject: string;              // 人物主體
  outfit?: string;              // 服裝造型
  scene: string;                // 場景環境
  callback?: string;            // 表情、動作

  // 視覺技術
  lighting?: string;            // 光影設定
  lens?: string;                // 鏡頭類型
  angle?: string;               // 機位角度
  composition?: string;         // 構圖方式

  // 風格與氛圍
  style: string;                // 畫面風格
  extra?: string;               // 特殊元素

  // 元數據
  source_tags: string[];        // 來源標籤
  confidence_score?: number;    // AI 信心度 (0-1)
}

/**
 * Inspire 生成請求
 */
export interface InspireGenerateRequest {
  input: string;
  session_id: string;
  mode?: 'auto' | 'emotion' | 'theme';
  round?: number;
}

/**
 * Inspire 生成回應
 */
export interface InspireGenerateResponse {
  mode: 'emotion' | 'theme';
  round: number;
  cards: InspirationCard[];
  suggestions?: string[];
}

/**
 * 反饋請求
 */
export interface InspireFeedbackRequest {
  session_id: string;
  selected_card?: InspirationCard;
  feedback: string;
  next_action: 'refine' | 'regenerate' | 'finalize';
}

/**
 * 反饋回應
 */
export interface InspireFeedbackResponse {
  status: 'success' | 'error';
  refined_cards?: InspirationCard[];
  final_result?: InspirationCard;
  message?: string;
}

/**
 * Inspire 狀態
 */
export type InspireState =
  | 'idle'
  | 'generating'
  | 'showing'
  | 'feedback'
  | 'refining'
  | 'finalized';

/**
 * Inspire Session
 */
export interface InspirationSession {
  session_id: string;
  created_at: string;
  mode: 'emotion' | 'theme';
  current_round: number;
  cards: InspirationCard[];
  selected_card?: InspirationCard;
  final_result?: InspirationCard;
}


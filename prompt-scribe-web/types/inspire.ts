/**
 * Inspire Agent 前端類型定義
 * 
 * 對應後端 API 的返回結構
 */

// ==================== 基礎類型 ====================

/**
 * 訊息角色
 */
export type MessageRole = 'user' | 'assistant'

/**
 * 對話階段
 */
export type InspirePhase = 
  | 'idle'           // 空閒（尚未開始）
  | 'understanding'  // 理解階段
  | 'exploring'      // 探索階段
  | 'refining'       // 精煉階段
  | 'completed'      // 完成

/**
 * 響應類型
 */
export type ResponseType = 
  | 'message'        // 純文字訊息
  | 'question'       // 澄清問題
  | 'directions'     // 創意方向
  | 'completed'      // 完成（包含最終結果）

// ==================== 訊息相關 ====================

/**
 * 對話訊息
 */
export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  data?: any  // 可能包含結構化數據
}

// ==================== 創意方向 ====================

/**
 * 單個創意方向
 */
export interface Direction {
  title: string                    // 標題
  concept: string                  // 概念描述
  core_mood: string                // 核心情緒
  visual_elements: string[]        // 視覺元素
  main_tags: string[]              // 主要標籤（10+ 個）
  style_notes: string              // 風格註記
  atmosphere: string               // 氛圍描述
  emoji?: string                   // 表情符號（可選）
}

// ==================== 最終輸出 ====================

/**
 * 推薦參數
 */
export interface GenerationParameters {
  cfg_scale: number | string       // CFG Scale (e.g., "7-9")
  steps: number                    // Steps
  sampler: string                  // 採樣器
  size: string                     // 尺寸 (e.g., "512x768")
}

/**
 * 最終 Prompt 輸出
 */
export interface FinalPrompt {
  title: string                    // 標題
  concept: string                  // 概念描述
  positive_prompt: string          // 正面 Prompt
  negative_prompt: string          // 負面 Prompt
  main_tags: string[]              // 主要標籤列表
  parameters: GenerationParameters // 推薦參數
  usage_tips?: string              // 使用提示
  quality_score?: number           // 品質分數（可選）
}

// ==================== API 響應 ====================

/**
 * Inspire API 通用響應結構
 */
export interface InspireResponse {
  session_id: string               // 會話 ID
  type: ResponseType               // 響應類型
  message: string                  // Agent 訊息
  phase: InspirePhase              // 當前階段
  data?: {
    directions?: Direction[]       // 創意方向列表
    final_output?: FinalPrompt     // 最終輸出
    question?: string              // 澄清問題
    options?: string[]             // 選項（如果是問題）
  }
  metadata: {
    turn_count: number             // 對話輪次
    processing_time_ms: number     // 處理時間（毫秒）
    total_cost?: number            // 總成本
    total_tokens?: number          // 總 token 數
  }
}

/**
 * 開始對話請求
 */
export interface StartConversationRequest {
  message: string                  // 用戶輸入
  user_access_level?: string       // 用戶訪問級別（預設：all-ages）
}

/**
 * 繼續對話請求
 */
export interface ContinueConversationRequest {
  session_id: string               // 會話 ID
  message: string                  // 用戶回應
}

/**
 * 會話狀態查詢響應
 */
export interface SessionStatusResponse {
  session_id: string
  phase: InspirePhase
  turn_count: number
  created_at: string
  updated_at: string
  status: 'active' | 'completed' | 'abandoned'
}

// ==================== 前端狀態 ====================

/**
 * Inspire Agent 前端狀態
 */
export interface InspireAgentState {
  // 會話狀態
  sessionId: string | null
  messages: Message[]
  phase: InspirePhase
  
  // 數據狀態
  directions: Direction[] | null
  selectedDirection: Direction | null
  finalPrompt: FinalPrompt | null
  
  // UI 狀態
  isLoading: boolean
  error: Error | null
  
  // 元數據
  metadata: {
    turnCount: number
    processingTime: number
    totalCost: number
  }
}

/**
 * Inspire Agent Hook 返回值
 */
export interface UseInspireAgentReturn extends InspireAgentState {
  // API 方法
  startConversation: (message: string) => Promise<void>
  continueConversation: (message: string) => Promise<void>
  selectDirection: (directionIndex: number) => void
  reset: () => void
  
  // 輔助方法
  canStart: boolean
  canContinue: boolean
  hasDirections: boolean
  isCompleted: boolean
}

// ==================== 組件 Props ====================

/**
 * ConversationPanel Props
 */
export interface ConversationPanelProps {
  messages: Message[]
  isLoading: boolean
  onSend: (message: string) => void
  disabled?: boolean
}

/**
 * ContentPanel Props
 */
export interface ContentPanelProps {
  phase: InspirePhase
  directions: Direction[] | null
  finalPrompt: FinalPrompt | null
  onSelectDirection: (index: number) => void
  isLoading: boolean
}

/**
 * DirectionCard Props
 */
export interface DirectionCardProps {
  direction: Direction
  index: number
  isSelected: boolean
  onSelect: () => void
}

/**
 * FinalPromptView Props
 */
export interface FinalPromptViewProps {
  prompt: FinalPrompt
  onCopy: (text: string) => void
  onDownload: () => void
  onReset: () => void
}

/**
 * EmptyState Props
 */
export interface EmptyStateProps {
  onStartWithExample: (message: string) => void
}

// ==================== 常量 ====================

/**
 * 預設範例
 */
export interface ExamplePrompt {
  label: string
  prompt: string
  emoji: string
  description?: string
}

/**
 * API 端點
 */
export const INSPIRE_API_ENDPOINTS = {
  START: '/api/inspire/start',
  CONTINUE: '/api/inspire/continue',
  STATUS: '/api/inspire/status',
} as const

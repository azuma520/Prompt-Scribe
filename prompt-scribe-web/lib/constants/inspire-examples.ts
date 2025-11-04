import type { ExamplePrompt } from '@/types/inspire'

/**
 * 預設範例 Prompts
 * 用於快速開始和展示系統能力
 */
export const EXAMPLE_PROMPTS: ExamplePrompt[] = [
  {
    label: '櫻花樹下的和服少女',
    prompt: '櫻花樹下的和服少女，溫柔寧靜的氛圍',
    emoji: '🌸',
    description: '日式唯美風格，適合展現傳統與自然的和諧',
  },
  {
    label: '賽博龐克城市夜景',
    prompt: '霓虹燈閃爍的賽博龐克城市，孤獨的少女在街頭',
    emoji: '🌃',
    description: '未來科技風格，展現都市的疏離與夢幻',
  },
  {
    label: '夢幻星空下的場景',
    prompt: '浩瀚星空下，少女站在草原上，夢幻又孤獨',
    emoji: '✨',
    description: '奇幻夢境風格，營造超現實的氛圍',
  },
]

/**
 * API 配置
 */
export const INSPIRE_CONFIG = {
  // API 端點（使用環境變數或預設值）
  API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // 超時設定（毫秒）
  REQUEST_TIMEOUT: 120000, // 120 秒
  
  // 重試設定
  MAX_RETRIES: 2,
  RETRY_DELAY: 2000, // 2 秒
  
  // UI 設定
  MAX_MESSAGES_DISPLAY: 50, // 最多顯示 50 條訊息
  TYPING_ANIMATION_DELAY: 50, // 打字動畫延遲（毫秒）
  
  // 持久化設定
  STORAGE_KEYS: {
    LAST_SESSION: 'inspire_last_session',
    MESSAGES: 'inspire_messages',
    PREFERENCES: 'inspire_preferences',
  },
} as const

/**
 * 階段對應的中文名稱
 */
export const PHASE_LABELS: Record<string, string> = {
  idle: '等待開始',
  understanding: '理解中',
  exploring: '探索中',
  refining: '精煉中',
  completed: '已完成',
}

/**
 * 階段對應的描述
 */
export const PHASE_DESCRIPTIONS: Record<string, string> = {
  idle: '描述你想要的感覺，讓 AI 幫你創作',
  understanding: 'AI 正在理解你的創作意圖...',
  exploring: 'AI 正在生成創意方向...',
  refining: 'AI 正在精煉你的 Prompt...',
  completed: '你的創作 Prompt 已完成！',
}


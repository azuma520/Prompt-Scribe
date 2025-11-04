'use client'

import { useReducer, useCallback, useEffect } from 'react'
import { toast } from 'sonner'
import type {
  InspireAgentState,
  UseInspireAgentReturn,
  InspireResponse,
  Message,
  Direction,
  InspirePhase,
} from '@/types/inspire'
import { adaptResponseToMessages, adaptDirections } from '../../src/features/inspire/adapters'

// ==================== 初始狀態 ====================

const initialState: InspireAgentState = {
  sessionId: null,
  messages: [],
  phase: 'idle',
  directions: null,
  selectedDirection: null,
  finalPrompt: null,
  isLoading: false,
  error: null,
  metadata: {
    turnCount: 0,
    processingTime: 0,
    totalCost: 0,
  },
}

// ==================== Action Types ====================

type Action =
  | { type: 'CONVERSATION_START'; payload: { userMessage: string } }
  | { type: 'RESPONSE_RECEIVED'; payload: InspireResponse }
  | { type: 'DIRECTION_SELECTED'; payload: { direction: Direction; index: number } }
  | { type: 'ERROR'; payload: Error }
  | { type: 'RESET' }
  | { type: 'SET_LOADING'; payload: boolean }

// ==================== Reducer ====================

function inspireAgentReducer(
  state: InspireAgentState,
  action: Action
): InspireAgentState {
  switch (action.type) {
    case 'CONVERSATION_START':
      return {
        ...state,
        isLoading: true,
        error: null,
        messages: [
          ...state.messages,
          {
            id: `user-${Date.now()}`,
            role: 'user',
            content: action.payload.userMessage,
            timestamp: new Date(),
          },
        ],
      }

    case 'RESPONSE_RECEIVED': {
      const response = action.payload
      console.log('Reducer 處理響應:', response)
      console.log('提取的 directions:', response.data?.directions)
      console.log('當前 messages 數量:', state.messages.length)

      // 🔑 使用 adapter 正規化 API 響應
      console.log('🧩 原始 API 響應:', JSON.stringify(response, null, 2))
      const adaptedMessages = adaptResponseToMessages(response)
      console.log('🧩 Adapter 處理後的 messages:', JSON.stringify(adaptedMessages, null, 2))

      // 轉換為 Message 格式
      const newMessages: Message[] = adaptedMessages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(),
        data: msg.raw,
      }))

      // 適配 directions
      const adaptedDirections = adaptDirections(response.data?.directions || [])

      const newState = {
        ...state,
        sessionId: response.session_id,
        messages: [...state.messages, ...newMessages], // 🔑 不可變更新
        phase: response.phase,
        directions: adaptedDirections,
        finalPrompt: response.data?.final_output || state.finalPrompt,
        isLoading: false,
        metadata: {
          turnCount: response.metadata.turn_count,
          processingTime: response.metadata.processing_time_ms,
          totalCost: response.metadata.total_cost || 0,
        },
      }
      
      console.log('更新後的狀態:', {
        messagesLength: newState.messages.length,
        messages: newState.messages.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 50) + '...' }))
      })
      return newState
    }

    case 'DIRECTION_SELECTED':
      return {
        ...state,
        selectedDirection: action.payload.direction,
        isLoading: true,
      }

    case 'ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      }

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }

    case 'RESET':
      return initialState

    default:
      return state
  }
}

// ==================== Hook ====================

/**
 * Inspire Agent Hook
 * 
 * 管理 Inspire Agent 的完整狀態和 API 交互
 */
export function useInspireAgent(): UseInspireAgentReturn {
  const [state, dispatch] = useReducer(inspireAgentReducer, initialState)

  // ==================== API 方法 ====================

  /**
   * 開始新對話
   */
  const startConversation = useCallback(async (message: string) => {
    console.log('startConversation 被調用:', message)
    
    if (!message.trim()) {
      toast.error('請輸入描述')
      return
    }

    try {
      // 發送用戶訊息（樂觀更新）
      dispatch({ type: 'CONVERSATION_START', payload: { userMessage: message } })

      // 調用 API (通過 Next.js API 路由)
      console.log('發送請求到 Next.js API 路由: /api/inspire/start')
      
      const response = await fetch('/api/inspire/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          user_access_level: 'all-ages',
        }),
      })

      console.log('API 響應狀態:', response.status, response.statusText)

      if (!response.ok) {
        const error = await response.json()
        console.error('API 錯誤響應:', error)
        throw new Error(error.detail || '開始對話失敗')
      }

      const data: InspireResponse = await response.json()
      console.log('API 成功響應:', data)
      console.log('響應數據結構:', {
        session_id: data.session_id,
        type: data.type,
        message: data.message,
        phase: data.phase,
        data: data.data,
        directions: data.data?.directions,
        final_output: data.data?.final_output
      })

      // 更新狀態
      dispatch({ type: 'RESPONSE_RECEIVED', payload: data })

      // 根據響應類型顯示提示
      if (data.type === 'directions') {
        toast.success('創意方向已生成！請選擇一個方向')
      } else if (data.type === 'question') {
        toast.info('需要更多資訊')
      }
    } catch (error) {
      console.error('Start conversation error:', error)
      console.error('錯誤詳情:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        error
      })
      dispatch({
        type: 'ERROR',
        payload: error instanceof Error ? error : new Error('未知錯誤'),
      })
      toast.error(error instanceof Error ? error.message : '發生錯誤')
    }
  }, [])

  /**
   * 繼續對話
   */
  const continueConversation = useCallback(
    async (message: string) => {
      if (!state.sessionId) {
        toast.error('會話不存在')
        return
      }

      if (!message.trim()) {
        toast.error('請輸入回應')
        return
      }

      try {
        // 發送用戶訊息（樂觀更新）
        dispatch({ type: 'CONVERSATION_START', payload: { userMessage: message } })

        // 調用 API (通過 Next.js API 路由)
        console.log('發送請求到 Next.js API 路由: /api/inspire/continue')
        const response = await fetch('/api/inspire/continue', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: state.sessionId,
            message,
          }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || '繼續對話失敗')
        }

        const data: InspireResponse = await response.json()

        // 更新狀態
        dispatch({ type: 'RESPONSE_RECEIVED', payload: data })

        // 根據響應類型顯示提示
        if (data.type === 'completed') {
          toast.success('🎉 創作完成！')
        } else if (data.type === 'directions') {
          toast.success('創意方向已生成！')
        }
      } catch (error) {
        console.error('Continue conversation error:', error)
        dispatch({
          type: 'ERROR',
          payload: error instanceof Error ? error : new Error('未知錯誤'),
        })
        toast.error(error instanceof Error ? error.message : '發生錯誤')
      }
    },
    [state.sessionId]
  )

  /**
   * 選擇創意方向
   */
  const selectDirection = useCallback(
    (directionIndex: number) => {
      if (!state.directions || directionIndex >= state.directions.length) {
        toast.error('無效的方向')
        return
      }

      const direction = state.directions[directionIndex]

      // 更新選中狀態
      dispatch({
        type: 'DIRECTION_SELECTED',
        payload: { direction, index: directionIndex },
      })

      // 發送選擇到後端
      const message = `選擇方向 ${directionIndex + 1}：${direction.title}`
      continueConversation(message)

      toast.info(`已選擇：${direction.title}`)
    },
    [state.directions, continueConversation]
  )

  /**
   * 重置狀態
   */
  const reset = useCallback(() => {
    dispatch({ type: 'RESET' })
    toast.info('已重置')
  }, [])

  // ==================== 輔助屬性 ====================

  const canStart = !state.isLoading && state.phase === 'idle'
  const canContinue = !state.isLoading && state.sessionId !== null
  const hasDirections = state.directions !== null && state.directions.length > 0
  const isCompleted = state.phase === 'completed'

  // ==================== 持久化（可選）====================

  // 保存 session_id 到 localStorage
  useEffect(() => {
    if (state.sessionId) {
      localStorage.setItem('inspire_last_session', state.sessionId)
      localStorage.setItem('inspire_messages', JSON.stringify(state.messages))
    }
  }, [state.sessionId, state.messages])

  // ==================== 返回值 ====================

  // 調試日誌：檢查返回的狀態
  console.log('useInspireAgent 返回狀態:', {
    messagesLength: state.messages.length,
    messages: state.messages.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 30) + '...' })),
    phase: state.phase,
    directionsLength: state.directions?.length,
    isLoading: state.isLoading
  })

  return {
    ...state,
    startConversation,
    continueConversation,
    selectDirection,
    reset,
    canStart,
    canContinue,
    hasDirections,
    isCompleted,
  }
}


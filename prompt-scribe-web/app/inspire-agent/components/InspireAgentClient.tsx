'use client'

import { useInspireAgent } from '@/lib/hooks/useInspireAgent'
import { ConversationPanel } from './ConversationPanel'
import { ContentPanel } from './ContentPanel'
import { Button } from '@/components/ui/button'
import { AlertCircle, RotateCcw } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

/**
 * Inspire Agent 主容器組件
 * 整合所有子組件，管理完整狀態
 */
export function InspireAgentClient() {
  const agent = useInspireAgent()

  // 處理發送（根據狀態決定是開始還是繼續）
  const handleSend = (message: string) => {
    if (agent.phase === 'idle') {
      agent.startConversation(message)
    } else {
      agent.continueConversation(message)
    }
  }

  // 處理範例點擊（從 EmptyState）
  const handleExampleClick = (prompt: string) => {
    agent.startConversation(prompt)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 錯誤提示 */}
      {agent.error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>發生錯誤</AlertTitle>
          <AlertDescription className="flex items-center justify-between">
            <span>{agent.error.message}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={agent.reset}
              className="ml-4"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              重試
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* 主布局 */}
      <div className="flex flex-col lg:flex-row gap-6 min-h-[80vh]">
        {/* 對話面板 - 左側（桌面）/ 底部（移動） */}
        <div
          className="w-full lg:w-[35%] order-2 lg:order-1 lg:sticky lg:top-4"
          style={{ height: 'calc(100vh - 8rem)' }}
        >
          <ConversationPanel
            messages={agent.messages}
            isLoading={agent.isLoading}
            onSend={handleSend}
            disabled={!agent.canStart && !agent.canContinue}
          />
        </div>

        {/* 主內容面板 - 右側（桌面）/ 上方（移動） */}
        <div className="w-full lg:w-[65%] order-1 lg:order-2">
          <ContentPanel
            phase={agent.phase}
            directions={agent.directions}
            finalPrompt={agent.finalPrompt}
          />
        </div>
      </div>

      {/* 調試資訊（開發模式） */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-8 p-4 bg-muted rounded-lg text-xs font-mono">
          <p>Session ID: {agent.sessionId || '無'}</p>
          <p>Phase: {agent.phase}</p>
          <p>Turn Count: {agent.metadata.turnCount}</p>
          <p>Has Directions: {agent.hasDirections ? '是' : '否'}</p>
          <p>Is Completed: {agent.isCompleted ? '是' : '否'}</p>
          <p>Is Loading: {agent.isLoading ? '是' : '否'}</p>
        </div>
      )}
    </div>
  )
}


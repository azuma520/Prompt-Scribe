'use client'

import { EmptyState } from './EmptyState'
import { DirectionCard } from './DirectionCard'
import { FinalPromptView } from './FinalPromptView'
import { Skeleton } from '@/components/ui/skeleton'
import { InspirePhase, Direction, FinalPrompt } from '@/types/inspire'
import { useInspireAgent } from '@/lib/hooks/useInspireAgent'

interface ContentPanelProps {
  phase: InspirePhase
  directions: Direction[] | null
  finalPrompt: FinalPrompt | null
}

/**
 * 主內容面板組件
 * 根據當前階段顯示不同內容
 */
export function ContentPanel({
  phase,
  directions,
  finalPrompt,
}: ContentPanelProps) {
  const { selectDirection, selectedDirection, isLoading, startConversation } = useInspireAgent()
  // 載入中骨架屏
  if (isLoading && phase !== 'idle' && !directions && !finalPrompt) {
    return (
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <Skeleton className="h-8 w-64 mx-auto" />
          <Skeleton className="h-4 w-96 mx-auto" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    )
  }

  // 顯示最終結果
  if (phase === 'completed' && finalPrompt) {
    return (
      <FinalPromptView
        prompt={finalPrompt}
        onCopy={(text) => {
          // 已在 FinalPromptView 中處理
        }}
        onDownload={() => {
          // 已在 FinalPromptView 中處理
        }}
        onReset={() => {
          // 需要從父組件處理
          window.location.reload()
        }}
      />
    )
  }

  // 顯示創意方向
  if (directions && directions.length > 0) {
    return (
      <div className="p-4">
        <h2 className="text-2xl font-bold mb-6 text-center text-foreground">
          💡 這些方向如何？選一個我們繼續聊！
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {directions.map((direction, index) => (
            <DirectionCard
              key={index}
              direction={direction}
              index={index}
              isSelected={selectedDirection?.title === direction.title}
              onSelect={() => selectDirection(index)}
            />
          ))}
        </div>
      </div>
    )
  }

  // 顯示空狀態（初始狀態）
  if (phase === 'idle') {
    return <EmptyState onStartConversation={startConversation} />
  }

  // 等待中狀態（已發送請求但還沒收到響應）
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">AI 正在思考...</h3>
          <p className="text-sm text-muted-foreground">
            {phase === 'understanding' && '理解你的創作意圖'}
            {phase === 'exploring' && '生成創意方向'}
            {phase === 'refining' && '精煉你的 Prompt'}
          </p>
        </div>
      </div>
    </div>
  )
}


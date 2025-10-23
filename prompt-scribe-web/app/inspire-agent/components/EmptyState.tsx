'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Sparkles } from 'lucide-react'
import { EXAMPLE_PROMPTS } from '@/lib/constants/inspire-examples'

interface EmptyStateProps {
  onStartConversation: (message: string) => void
}

/**
 * 空狀態組件
 * 顯示在用戶尚未開始對話時
 */
export function EmptyState({ onStartConversation }: EmptyStateProps) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="max-w-2xl w-full border-dashed">
        <CardContent className="pt-12 pb-12">
          <div className="text-center space-y-8">
            {/* 圖標和標題 */}
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                  <Sparkles className="w-10 h-10 text-primary" />
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-bold mb-2">
                  描述你想要的感覺...
                </h2>
                <p className="text-muted-foreground">
                  像和朋友聊天一樣，告訴 AI 你想要什麼樣的畫面或氛圍
                </p>
              </div>
            </div>

            {/* 預設範例 */}
            <div className="space-y-4">
              <p className="text-sm font-medium text-muted-foreground">
                或者試試這些範例：
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {EXAMPLE_PROMPTS.map((example) => (
                  <Button
                    key={example.label}
                    variant="outline"
                    className="h-auto py-4 px-4 flex-col items-start text-left hover:bg-primary/5 hover:border-primary/50 transition-all"
                    onClick={() => {
                      console.log('範例按鈕被點擊:', example.prompt)
                      onStartConversation(example.prompt)
                    }}
                  >
                    <span className="text-2xl mb-2">{example.emoji}</span>
                    <span className="font-medium text-sm mb-1">
                      {example.label}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {example.description}
                    </span>
                  </Button>
                ))}
              </div>
            </div>

            {/* 提示 */}
            <div className="text-xs text-muted-foreground space-y-1">
              <p>💡 提示：你可以描述情緒、氛圍、場景或角色特徵</p>
              <p>⚡ 平均只需 2-4 輪對話就能完成</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


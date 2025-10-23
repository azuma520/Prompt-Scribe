'use client'

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { DirectionCardProps } from '@/types/inspire'

/**
 * 單個創意方向卡片組件
 */
export function DirectionCard({
  direction,
  index,
  isSelected,
  onSelect,
}: DirectionCardProps) {
  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-300 hover:shadow-lg group',
        isSelected && 'ring-2 ring-primary shadow-xl',
        'hover:scale-[1.02]'
      )}
      onClick={onSelect}
    >
      <CardHeader>
        <CardTitle className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{direction.emoji || '🎨'}</span>
            <span className="text-base">
              方向 {index + 1}：{direction.title}
            </span>
          </div>
          {isSelected && (
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
              <Check className="w-4 h-4 text-primary-foreground" />
            </div>
          )}
        </CardTitle>
        <CardDescription className="text-sm">
          {direction.concept}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 核心情緒 */}
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1.5">
            核心情緒
          </p>
          <p className="text-sm">{direction.core_mood}</p>
        </div>

        {/* 主要標籤 */}
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">
            主要標籤 ({direction.main_tags.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {direction.main_tags.slice(0, 10).map((tag, idx) => (
              <Badge
                key={idx}
                variant="secondary"
                className="text-xs px-2 py-0.5 font-normal"
              >
                {tag}
              </Badge>
            ))}
            {direction.main_tags.length > 10 && (
              <Badge
                variant="outline"
                className="text-xs px-2 py-0.5 font-normal"
              >
                +{direction.main_tags.length - 10} 更多
              </Badge>
            )}
          </div>
        </div>

        {/* 風格特點 */}
        {direction.style_notes && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">
              風格特點
            </p>
            <p className="text-sm text-muted-foreground">
              {direction.style_notes}
            </p>
          </div>
        )}

        {/* 氛圍描述 */}
        {direction.atmosphere && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">
              氛圍
            </p>
            <p className="text-sm text-muted-foreground">
              {direction.atmosphere}
            </p>
          </div>
        )}
      </CardContent>

      <CardFooter>
        <Button
          className="w-full"
          variant={isSelected ? 'default' : 'outline'}
          size="sm"
        >
          {isSelected ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              已選擇
            </>
          ) : (
            '選擇這個方向'
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

/**
 * 方向列表組件
 */
export function DirectionsView({
  directions,
  selectedIndex,
  onSelect,
}: {
  directions: any[]
  selectedIndex: number | null
  onSelect: (index: number) => void
}) {
  return (
    <div className="space-y-6">
      {/* 標題 */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">✨ 為你生成了 {directions.length} 個創意方向</h2>
        <p className="text-muted-foreground">
          選擇一個你最喜歡的方向，AI 會為你生成完整的 Prompt
        </p>
      </div>

      {/* 方向卡片網格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {directions.map((direction, index) => (
          <DirectionCard
            key={index}
            direction={direction}
            index={index}
            isSelected={selectedIndex === index}
            onSelect={() => onSelect(index)}
          />
        ))}
      </div>
    </div>
  )
}


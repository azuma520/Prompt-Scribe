'use client'

import { RecommendedTag } from '@/types/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Plus, CheckCircle2, TrendingUp, Layers } from 'lucide-react'
import { cn } from '@/lib/utils'

interface RecommendResultsProps {
  tags: RecommendedTag[]
  selectedTags: Set<string>
  onTagSelect: (tag: RecommendedTag) => void
  onAddAll: () => void
  executionTime?: number
}

export function RecommendResults({
  tags,
  selectedTags,
  onTagSelect,
  onAddAll,
  executionTime,
}: RecommendResultsProps) {
  if (tags.length === 0) {
    return null
  }

  // 按分類分組
  const groupedTags = tags.reduce((acc, tag) => {
    const category = tag.category || 'OTHER'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(tag)
    return acc
  }, {} as Record<string, RecommendedTag[]>)

  const categories = Object.keys(groupedTags).sort()

  // 計算平均信心度
  const avgConfidence = tags.reduce((sum, tag) => sum + tag.confidence, 0) / tags.length

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-primary" />
              推薦結果
            </CardTitle>
            <CardDescription>
              找到 {tags.length} 個相關標籤
              {executionTime && ` · 耗時 ${executionTime.toFixed(2)}s`}
              {' · 平均信心度 '}
              <span className={cn(
                'font-semibold',
                avgConfidence >= 0.8 ? 'text-green-600' : avgConfidence >= 0.6 ? 'text-yellow-600' : 'text-orange-600'
              )}>
                {(avgConfidence * 100).toFixed(0)}%
              </span>
            </CardDescription>
          </div>
          <Button onClick={onAddAll} variant="outline" size="sm">
            <Plus className="w-4 h-4 mr-1" />
            全部加入
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px] pr-4">
          <div className="space-y-6">
            {categories.map((category) => (
              <div key={category} className="space-y-3">
                {/* 分類標題 */}
                <div className="flex items-center gap-2 pb-2 border-b">
                  <Badge variant="outline" className="font-semibold">
                    {category}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {groupedTags[category].length} 個標籤
                  </span>
                </div>

                {/* 標籤卡片 */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {groupedTags[category].map((tag) => {
                    const isSelected = selectedTags.has(tag.tag)
                    const confidenceColor =
                      tag.confidence >= 0.8
                        ? 'text-green-600'
                        : tag.confidence >= 0.6
                        ? 'text-yellow-600'
                        : 'text-orange-600'

                    return (
                      <button
                        key={tag.tag}
                        onClick={() => onTagSelect(tag)}
                        className={cn(
                          'relative flex items-center justify-between p-3 rounded-lg border transition-all',
                          'hover:shadow-md hover:scale-[1.02]',
                          isSelected
                            ? 'bg-primary/10 border-primary'
                            : 'bg-background hover:bg-accent'
                        )}
                      >
                        <div className="flex-1 text-left space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm">{tag.tag}</span>
                            {isSelected && (
                              <CheckCircle2 className="w-4 h-4 text-primary" />
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span className={confidenceColor}>
                              信心度 {(tag.confidence * 100).toFixed(0)}%
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              {tag.post_count >= 1000000
                                ? `${(tag.post_count / 1000000).toFixed(1)}M`
                                : tag.post_count >= 1000
                                ? `${(tag.post_count / 1000).toFixed(1)}K`
                                : tag.post_count}
                            </span>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant={isSelected ? 'secondary' : 'ghost'}
                          className="ml-2"
                          onClick={(e) => {
                            e.stopPropagation()
                            onTagSelect(tag)
                          }}
                        >
                          {isSelected ? (
                            <CheckCircle2 className="w-4 h-4" />
                          ) : (
                            <Plus className="w-4 h-4" />
                          )}
                        </Button>
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}


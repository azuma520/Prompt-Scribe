'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Sparkles, Loader2 } from 'lucide-react'

interface DescribeInputProps {
  onGenerate: (description: string, options: GenerateOptions) => void
  isLoading?: boolean
}

export interface GenerateOptions {
  maxTags: number
  minPopularity: number
  excludeAdult: boolean
}

const EXAMPLE_PROMPTS = [
  '一個穿著校服的可愛女孩，長髮飄逸，微笑著',
  '未來科技風格的都市夜景，霓虹燈光',
  '森林中的精靈，白色長裙，夢幻氛圍',
  '賽博龐克風格的女戰士，機械手臂',
]

export function DescribeInput({ onGenerate, isLoading = false }: DescribeInputProps) {
  const [description, setDescription] = useState('')
  const [maxTags, setMaxTags] = useState(20)
  const [minPopularity, setMinPopularity] = useState(100)
  const [excludeAdult, setExcludeAdult] = useState(true)

  const handleGenerate = () => {
    if (!description.trim()) return

    onGenerate(description, {
      maxTags,
      minPopularity,
      excludeAdult,
    })
  }

  const handleExampleClick = (example: string) => {
    setDescription(example)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          描述你的想法
        </CardTitle>
        <CardDescription>
          用自然語言描述你想要生成的圖像，AI 會為你推薦最適合的標籤組合
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 描述輸入區 */}
        <div className="space-y-2">
          <Label htmlFor="description">圖像描述</Label>
          <Textarea
            id="description"
            placeholder="例如：一個穿著校服的可愛女孩，長髮飄逸，微笑著..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="resize-none"
          />
        </div>

        {/* 範例提示 */}
        <div className="space-y-2">
          <Label className="text-sm text-muted-foreground">快速範例</Label>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_PROMPTS.map((example, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleExampleClick(example)}
                className="text-xs"
              >
                {example.slice(0, 20)}...
              </Button>
            ))}
          </div>
        </div>

        {/* 進階設定 */}
        <div className="space-y-4 pt-4 border-t">
          <Label className="text-sm font-semibold">進階設定</Label>

          {/* 標籤數量 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="maxTags" className="text-sm">
                標籤數量
              </Label>
              <span className="text-sm text-muted-foreground">{maxTags} 個</span>
            </div>
            <Slider
              id="maxTags"
              min={5}
              max={30}
              step={5}
              value={[maxTags]}
              onValueChange={(value) => setMaxTags(value[0])}
              disabled={isLoading}
            />
          </div>

          {/* 最低熱度 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="minPopularity" className="text-sm">
                最低熱度
              </Label>
              <span className="text-sm text-muted-foreground">
                {minPopularity >= 1000 ? `${(minPopularity / 1000).toFixed(0)}K` : minPopularity}
              </span>
            </div>
            <Slider
              id="minPopularity"
              min={100}
              max={10000}
              step={100}
              value={[minPopularity]}
              onValueChange={(value) => setMinPopularity(value[0])}
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground">
              熱度越高的標籤使用越廣泛，但可能較不具特色
            </p>
          </div>

          {/* 排除成人內容 */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="excludeAdult" className="text-sm">
                排除成人內容
              </Label>
              <p className="text-xs text-muted-foreground">
                過濾掉可能包含成人內容的標籤
              </p>
            </div>
            <Switch
              id="excludeAdult"
              checked={excludeAdult}
              onCheckedChange={setExcludeAdult}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* 生成按鈕 */}
        <Button
          className="w-full"
          size="lg"
          onClick={handleGenerate}
          disabled={!description.trim() || isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              生成中...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2" />
              生成標籤建議
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}


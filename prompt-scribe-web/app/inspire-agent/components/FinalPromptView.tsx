'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Copy, Download, RefreshCw, Check } from 'lucide-react'
import { toast } from 'sonner'
import type { FinalPromptViewProps } from '@/types/inspire'

/**
 * 最終 Prompt 展示組件
 */
export function FinalPromptView({
  prompt,
  onCopy,
  onDownload,
  onReset,
}: FinalPromptViewProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null)

  // 複製到剪貼板
  const handleCopy = async (text: string, section: string) => {
    try {
      await navigator.clipboard.writeText(text)
      onCopy(text)
      setCopiedSection(section)
      toast.success(`${section}已複製！`)
      
      // 2 秒後重置
      setTimeout(() => setCopiedSection(null), 2000)
    } catch (error) {
      toast.error('複製失敗')
    }
  }

  // 下載為 JSON
  const handleDownload = () => {
    const data = {
      title: prompt.title,
      positive_prompt: prompt.positive_prompt,
      negative_prompt: prompt.negative_prompt,
      parameters: prompt.parameters,
      created_at: new Date().toISOString(),
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `inspire-prompt-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    onDownload()
    toast.success('已下載配置文件')
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* 標題和描述 */}
      <div className="text-center space-y-3">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center">
            <span className="text-3xl">🎉</span>
          </div>
        </div>
        <h2 className="text-3xl font-bold">你的創作 Prompt 已完成！</h2>
        <p className="text-xl text-muted-foreground">{prompt.title}</p>
        {prompt.concept && (
          <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
            {prompt.concept}
          </p>
        )}
      </div>

      {/* 正面 Prompt */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-lg">
            <span>正面 Prompt</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleCopy(prompt.positive_prompt, '正面 Prompt')}
            >
              {copiedSection === '正面 Prompt' ? (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  已複製
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-2" />
                  複製
                </>
              )}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-32 w-full rounded-md border p-4">
            <p className="text-sm font-mono leading-relaxed whitespace-pre-wrap">
              {prompt.positive_prompt}
            </p>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* 負面 Prompt */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-lg">
            <span>負面 Prompt</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleCopy(prompt.negative_prompt, '負面 Prompt')}
            >
              {copiedSection === '負面 Prompt' ? (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  已複製
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-2" />
                  複製
                </>
              )}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-24 w-full rounded-md border p-4">
            <p className="text-sm font-mono leading-relaxed text-muted-foreground whitespace-pre-wrap">
              {prompt.negative_prompt}
            </p>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* 推薦參數 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">推薦參數</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">
                CFG Scale
              </p>
              <p className="text-2xl font-bold">{prompt.parameters.cfg_scale}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Steps</p>
              <p className="text-2xl font-bold">{prompt.parameters.steps}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">
                Sampler
              </p>
              <p className="text-lg font-mono">{prompt.parameters.sampler}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Size</p>
              <p className="text-lg font-mono">{prompt.parameters.size}</p>
            </div>
          </div>

          {/* 使用提示 */}
          {prompt.usage_tips && (
            <>
              <Separator className="my-4" />
              <div className="space-y-2">
                <p className="text-sm font-medium">💡 使用提示</p>
                <p className="text-sm text-muted-foreground">
                  {prompt.usage_tips}
                </p>
              </div>
            </>
          )}

          {/* 品質分數 */}
          {prompt.quality_score !== undefined && (
            <>
              <Separator className="my-4" />
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">品質分數</p>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${prompt.quality_score}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold">
                    {prompt.quality_score}/100
                  </span>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* 操作按鈕 */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
        <Button
          size="lg"
          onClick={() => handleCopy(prompt.positive_prompt, '正面 Prompt')}
          className="gap-2"
        >
          <Copy className="w-4 h-4" />
          複製正面 Prompt
        </Button>
        <Button
          size="lg"
          variant="outline"
          onClick={handleDownload}
          className="gap-2"
        >
          <Download className="w-4 h-4" />
          下載完整配置
        </Button>
        <Button
          size="lg"
          variant="outline"
          onClick={onReset}
          className="gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          重新生成
        </Button>
      </div>
    </div>
  )
}


'use client'

import { useState, useCallback } from 'react'
import { DescribeInput, GenerateOptions } from './DescribeInput'
import { RecommendResults } from './RecommendResults'
import { QualityPanel } from './QualityPanel'
import { useInspire } from '@/lib/hooks/useInspire'
import { useWorkspace } from '@/lib/hooks/useWorkspace'
import { RecommendedTag } from '@/types/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Copy, Trash2, X, Download, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'

export function InspireClientNew() {
  const {
    isLoading,
    isValidating,
    recommendedTags,
    validationResult,
    executionTime,
    generate,
    validate,
    clear: clearInspire,
  } = useInspire()

  const {
    tags: selectedTags,
    addTag,
    removeTag,
    clearAll,
    copyToClipboard,
    formatPrompt,
  } = useWorkspace()

  const [selectedTagNames, setSelectedTagNames] = useState<Set<string>>(new Set())

  /**
   * 處理生成標籤
   */
  const handleGenerate = useCallback(
    (description: string, options: GenerateOptions) => {
      // 清空之前的選擇
      setSelectedTagNames(new Set())
      clearAll()

      // 生成新的推薦
      generate(description, {
        maxTags: options.maxTags,
        minPopularity: options.minPopularity,
        excludeAdult: options.excludeAdult,
      })
    },
    [generate, clearAll]
  )

  /**
   * 處理標籤選擇
   */
  const handleTagSelect = useCallback(
    (tag: RecommendedTag) => {
      const newSet = new Set(selectedTagNames)

      if (newSet.has(tag.tag)) {
        // 移除標籤
        newSet.delete(tag.tag)
        const tagToRemove = selectedTags.find((t) => t.name === tag.tag)
        if (tagToRemove) {
          removeTag(tagToRemove.id)
        }
      } else {
        // 添加標籤
        newSet.add(tag.tag)
        addTag({
          id: `inspire-${tag.tag}`,
          name: tag.tag,
          danbooru_cat: 0,
          post_count: tag.post_count,
          main_category: tag.category,
          sub_category: tag.subcategory || null,
          confidence: tag.confidence,
          classification_source: 'inspire',
        })
      }

      setSelectedTagNames(newSet)
    },
    [selectedTagNames, selectedTags, addTag, removeTag]
  )

  /**
   * 添加所有推薦標籤
   */
  const handleAddAll = useCallback(() => {
    const newSet = new Set<string>()

    recommendedTags.forEach((tag) => {
      newSet.add(tag.tag)
      addTag({
        id: `inspire-${tag.tag}`,
        name: tag.tag,
        danbooru_cat: 0,
        post_count: tag.post_count,
        main_category: tag.category,
        sub_category: tag.subcategory || null,
        confidence: tag.confidence,
        classification_source: 'inspire',
      })
    })

    setSelectedTagNames(newSet)
    toast.success(`已添加 ${recommendedTags.length} 個標籤`)
  }, [recommendedTags, addTag])

  /**
   * 驗證當前選中的標籤
   */
  const handleValidate = useCallback(() => {
    const tagNames = selectedTags.map((t) => t.name)
    validate(tagNames)
  }, [selectedTags, validate])

  /**
   * 複製 Prompt
   */
  const handleCopy = useCallback(async () => {
    const success = await copyToClipboard()
    if (success) {
      toast.success('已複製到剪貼簿！')
    } else {
      toast.error('複製失敗，請重試')
    }
  }, [copyToClipboard])

  /**
   * 下載 Prompt
   */
  const handleDownload = useCallback(() => {
    const prompt = formatPrompt()
    const blob = new Blob([prompt], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `prompt-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('下載成功！')
  }, [formatPrompt])

  /**
   * 清空所有
   */
  const handleClearAll = useCallback(() => {
    clearAll()
    clearInspire()
    setSelectedTagNames(new Set())
    toast.info('已清空所有內容')
  }, [clearAll, clearInspire])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：輸入和推薦結果 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 描述輸入 */}
          <DescribeInput onGenerate={handleGenerate} isLoading={isLoading} />

          {/* 推薦結果 */}
          {recommendedTags.length > 0 && (
            <RecommendResults
              tags={recommendedTags}
              selectedTags={selectedTagNames}
              onTagSelect={handleTagSelect}
              onAddAll={handleAddAll}
              executionTime={executionTime}
            />
          )}

          {/* 品質驗證 */}
          {selectedTags.length > 0 && (
            <QualityPanel
              result={validationResult}
              isValidating={isValidating}
              onValidate={handleValidate}
            />
          )}
        </div>

        {/* 右側：工作區 */}
        <div className="lg:col-span-1 space-y-6">
          {/* 已選標籤 */}
          <Card className="sticky top-4">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-lg">
                工作區 ({selectedTags.length})
              </CardTitle>
              {selectedTags.length > 0 && (
                <Button variant="ghost" size="sm" onClick={clearAll}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              {selectedTags.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  <p>還沒有選擇任何標籤</p>
                  <p className="text-xs mt-2">從推薦結果中選擇標籤</p>
                </div>
              ) : (
                <>
                  {/* 標籤列表 */}
                  <ScrollArea className="h-[300px]">
                    <div className="flex flex-wrap gap-2">
                      {selectedTags.map((tag) => (
                        <Badge
                          key={tag.id}
                          variant="secondary"
                          className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors"
                          onClick={() => removeTag(tag.id)}
                        >
                          {tag.name}
                          <X className="w-3 h-3 ml-1" />
                        </Badge>
                      ))}
                    </div>
                  </ScrollArea>

                  <Separator />

                  {/* Prompt 預覽 */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Prompt 預覽</span>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={handleCopy}>
                          <Copy className="w-3 h-3" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={handleDownload}>
                          <Download className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                    <pre className="whitespace-pre-wrap break-all text-xs bg-muted p-3 rounded-md max-h-[150px] overflow-y-auto">
                      {formatPrompt()}
                    </pre>
                  </div>

                  <Separator />

                  {/* 操作按鈕 */}
                  <div className="space-y-2">
                    <Button
                      variant="default"
                      size="sm"
                      className="w-full"
                      onClick={handleCopy}
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      複製 Prompt
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={handleValidate}
                      disabled={isValidating}
                    >
                      <RefreshCw className={`w-4 h-4 mr-2 ${isValidating ? 'animate-spin' : ''}`} />
                      檢查品質
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* 快速操作 */}
          {(recommendedTags.length > 0 || selectedTags.length > 0) && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">快速操作</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={handleClearAll}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  清空所有
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}


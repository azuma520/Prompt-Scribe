'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useWorkspace } from '@/features/workspace/useWorkspace'
import { toast } from 'sonner'
import { Copy, Trash2, X } from 'lucide-react'
import { AdvancedTagSearch } from '@/features/search/components/AdvancedTagSearch'
import { getTags } from '@/lib/api/tags'
import { Tag } from '@/types/api'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle, Loader2 } from 'lucide-react'

export function WorkspaceClient() {
  const { tags: selectedTags, removeTag, clearAll, copyToClipboard, formatPrompt } = useWorkspace()
  const [initialTags, setInitialTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadTags() {
      try {
        const tags = await getTags()
        setInitialTags(tags)
      } catch (e) {
        setError(e instanceof Error ? e.message : '無法載入標籤資料')
        console.error('Failed to load tags:', e)
      } finally {
        setLoading(false)
      }
    }
    loadTags()
  }, [])

  const handleCopy = async () => {
    const success = await copyToClipboard()
    if (success) {
      toast.success('已複製到剪貼簿！')
    } else {
      toast.error('複製失敗，請重試')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* 左側：標籤搜尋區域 */}
      <div className="lg:col-span-2">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>載入失敗</AlertTitle>
            <AlertDescription>
              無法連接到 API 伺服器。請檢查網路連接或稍後再試。
              <br />
              <span className="text-xs text-muted-foreground">{error}</span>
            </AlertDescription>
          </Alert>
        ) : (
          <AdvancedTagSearch initialTags={initialTags} showSelectedTags={false} />
        )}
      </div>

      {/* 右側：工作區 */}
      <div className="space-y-4 lg:sticky lg:top-8">
        {/* 已選標籤 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              已選標籤 ({selectedTags.length})
            </CardTitle>
            {selectedTags.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearAll}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                清空
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {selectedTags.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                從左側搜尋並添加標籤
              </p>
            ) : (
              <ScrollArea className="h-48">
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
            )}
          </CardContent>
        </Card>

        {/* Prompt 預覽 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Prompt 預覽</CardTitle>
            {selectedTags.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
              >
                <Copy className="w-4 h-4 mr-1" />
                複製
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {selectedTags.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                選擇標籤後會顯示生成的 Prompt
              </p>
            ) : (
              <div className="bg-muted p-3 rounded-md text-sm">
                <code className="leading-relaxed whitespace-pre-wrap break-words">
                  {formatPrompt()}
                </code>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

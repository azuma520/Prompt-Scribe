'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useWorkspace } from '@/lib/hooks/useWorkspace'
import { toast } from 'sonner'
import { Copy, Trash2, X } from 'lucide-react'

export function WorkspaceClient() {
  const { tags: selectedTags, removeTag, clearAll, copyToClipboard, formatPrompt } = useWorkspace()

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
        <Card>
          <CardHeader>
            <CardTitle>標籤搜尋</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              從標籤搜尋頁面選擇標籤，或直接在這裡搜尋。
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 右側：工作區 */}
      <div className="space-y-4">
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
                還沒有選擇任何標籤
              </p>
            ) : (
              <ScrollArea className="h-32">
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
              <div className="bg-muted p-3 rounded-md">
                <code className="text-sm">{formatPrompt()}</code>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

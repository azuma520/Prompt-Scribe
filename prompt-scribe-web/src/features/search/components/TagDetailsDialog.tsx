'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tag } from '@/types/api'
import { Hash, TrendingUp, FolderOpen, Plus, ExternalLink } from 'lucide-react'

interface TagDetailsDialogProps {
  tag: Tag | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onAddToWorkspace?: (tag: Tag) => void
  relatedTags?: Tag[]
}

export function TagDetailsDialog({
  tag,
  open,
  onOpenChange,
  onAddToWorkspace,
  relatedTags = []
}: TagDetailsDialogProps) {
  if (!tag) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Hash className="w-6 h-6" />
            {tag.name}
          </DialogTitle>
          <DialogDescription>
            標籤詳細資訊和相關推薦
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* 基本資訊 */}
          <div className="space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <FolderOpen className="w-4 h-4" />
              基本資訊
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">主分類</p>
                <Badge variant="outline">{tag.main_category || 'N/A'}</Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">子分類</p>
                <Badge variant="secondary">{tag.sub_category || 'N/A'}</Badge>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">使用次數</p>
              <p className="text-2xl font-bold">{tag.post_count?.toLocaleString() || 'N/A'}</p>
            </div>
          </div>

          <Separator />

          {/* 統計資訊 */}
          <div className="space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              使用統計
            </h3>
            <div className="bg-muted/50 p-4 rounded-lg space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">受歡迎程度</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ 
                        width: `${Math.min(100, ((tag.post_count || 0) / 10000) * 100)}%` 
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {Math.min(100, Math.round(((tag.post_count || 0) / 10000) * 100))}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* 相關標籤 */}
          {relatedTags.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold">相關標籤</h3>
              <div className="flex flex-wrap gap-2">
                {relatedTags.slice(0, 10).map((relatedTag) => (
                  <Badge
                    key={relatedTag.id}
                    variant="secondary"
                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  >
                    {relatedTag.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <Separator />

          {/* 操作按鈕 */}
          <div className="flex gap-3">
            <Button 
              className="flex-1"
              onClick={() => onAddToWorkspace?.(tag)}
            >
              <Plus className="w-4 h-4 mr-2" />
              添加到工作區
            </Button>
            <Button variant="outline" asChild>
              <a
                href={`https://danbooru.donmai.us/posts?tags=${tag.name}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                查看範例
              </a>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

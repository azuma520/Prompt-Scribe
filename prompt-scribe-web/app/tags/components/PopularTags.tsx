import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tag } from '@/types/api'
import { TrendingUp } from 'lucide-react'

interface PopularTagsProps {
  tags: Tag[]
}

export function PopularTags({ tags }: PopularTagsProps) {
  return (
    <Card className="sticky top-20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="w-5 h-5" />
          熱門標籤
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[calc(100vh-200px)]">
          <div className="space-y-2">
            {tags.map((tag, index) => (
              <div
                key={tag.id}
                className="flex items-center justify-between p-2 rounded-md hover:bg-accent transition-colors cursor-pointer group"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span className="text-xs text-muted-foreground w-6 flex-shrink-0">
                    #{index + 1}
                  </span>
                  <span className="text-sm font-medium truncate group-hover:text-primary">
                    {tag.name}
                  </span>
                </div>
                <Badge variant="outline" className="text-xs flex-shrink-0">
                  {tag.post_count?.toLocaleString()}
                </Badge>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

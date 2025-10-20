'use client'

import { useState, useMemo } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tag } from '@/types/api'

interface TagSearchProps {
  initialTags: Tag[]
}

export function TagSearch({ initialTags }: TagSearchProps) {
  const [query, setQuery] = useState('')
  const [selectedTags, setSelectedTags] = useState<Tag[]>([])

  const filteredTags = useMemo(() => {
    if (!query) return initialTags.slice(0, 20)
    
    return initialTags
      .filter(tag => 
        tag.name.toLowerCase().includes(query.toLowerCase()) ||
        tag.category.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, 20)
  }, [query, initialTags])

  const handleTagSelect = (tag: Tag) => {
    if (!selectedTags.find(t => t.id === tag.id)) {
      setSelectedTags([...selectedTags, tag])
    }
  }

  const handleTagRemove = (tagId: string) => {
    setSelectedTags(selectedTags.filter(t => t.id !== tagId))
  }

  return (
    <div className="space-y-6">
      {/* 搜尋輸入框 */}
      <div className="relative">
        <Input
          type="text"
          placeholder="搜尋標籤..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10"
        />
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
          🔍
        </div>
      </div>

      {/* 已選標籤 */}
      {selectedTags.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium">已選標籤</h3>
          <div className="flex flex-wrap gap-2">
            {selectedTags.map((tag) => (
              <Badge
                key={tag.id}
                variant="secondary"
                className="cursor-pointer"
                onClick={() => handleTagRemove(tag.id)}
              >
                {tag.name} ×
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* 搜尋結果 */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium">搜尋結果</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
          {filteredTags.map((tag) => (
            <Button
              key={tag.id}
              variant="outline"
              size="sm"
              onClick={() => handleTagSelect(tag)}
              className="justify-start"
            >
              {tag.name}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}

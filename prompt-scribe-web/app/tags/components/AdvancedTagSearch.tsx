'use client'

import { useState, useMemo, useCallback } from 'react'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { TagDetailsDialog } from './TagDetailsDialog'
import { useSearchHistory } from '@/lib/hooks/useSearchHistory'
import { useWorkspace } from '@/lib/hooks/useWorkspace'
import { Tag } from '@/types/api'
import { Search, X, TrendingUp, Hash, Filter, Info } from 'lucide-react'

interface AdvancedTagSearchProps {
  initialTags: Tag[]
}

type SortOption = 'name' | 'post_count' | 'category'
type FilterCategory = 'all' | string

export function AdvancedTagSearch({ initialTags }: AdvancedTagSearchProps) {
  const [query, setQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('post_count')
  const [filterCategory, setFilterCategory] = useState<FilterCategory>('all')
  const [detailsTag, setDetailsTag] = useState<Tag | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  
  // 使用搜尋歷史 Hook
  const { history: searchHistory, addToHistory } = useSearchHistory()
  
  // 使用工作區 Hook
  const { tags: selectedTags, addTag, removeTag, clearAll } = useWorkspace()

  // 獲取所有分類
  const categories = useMemo(() => {
    const cats = new Set<string>()
    initialTags.forEach(tag => {
      if (tag.main_category) cats.add(tag.main_category)
      if (tag.sub_category) cats.add(tag.sub_category)
    })
    return Array.from(cats).sort()
  }, [initialTags])

  // 過濾和排序標籤
  const filteredAndSortedTags = useMemo(() => {
    let tags = initialTags

    // 分類篩選
    if (filterCategory !== 'all') {
      tags = tags.filter(tag => 
        tag.main_category === filterCategory || 
        tag.sub_category === filterCategory
      )
    }

    // 搜尋過濾
    if (query) {
      const lowerQuery = query.toLowerCase()
      tags = tags.filter(tag => 
        tag.name.toLowerCase().includes(lowerQuery) ||
        tag.main_category?.toLowerCase().includes(lowerQuery) ||
        tag.sub_category?.toLowerCase().includes(lowerQuery)
      )
    }

    // 排序
    tags = [...tags].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'post_count':
          return (b.post_count || 0) - (a.post_count || 0)
        case 'category':
          const catA = a.main_category || a.sub_category || ''
          const catB = b.main_category || b.sub_category || ''
          return catA.localeCompare(catB)
        default:
          return 0
      }
    })

    return tags.slice(0, 100)
  }, [initialTags, query, filterCategory, sortBy])

  // 搜尋建議（前10個）
  const searchSuggestions = useMemo(() => {
    return filteredAndSortedTags.slice(0, 10)
  }, [filteredAndSortedTags])

  const handleTagSelect = useCallback((tag: Tag) => {
    addTag(tag)
    
    // 添加到搜尋歷史
    if (query) {
      addToHistory(query)
    }
  }, [addTag, query, addToHistory])

  const handleTagRemove = useCallback((tagId: string) => {
    removeTag(tagId)
  }, [removeTag])

  const handleClearAll = useCallback(() => {
    clearAll()
  }, [clearAll])

  const handleSearchFromHistory = useCallback((historyQuery: string) => {
    setQuery(historyQuery)
  }, [])

  const handleShowDetails = useCallback((tag: Tag) => {
    setDetailsTag(tag)
    setDialogOpen(true)
  }, [])

  const handleAddToWorkspaceFromDialog = useCallback((tag: Tag) => {
    handleTagSelect(tag)
    setDialogOpen(false)
  }, [handleTagSelect])

  // 獲取相關標籤（同分類的熱門標籤）
  const getRelatedTags = useCallback((tag: Tag) => {
    return initialTags
      .filter(t => 
        (t.main_category === tag.main_category || t.sub_category === tag.sub_category) && 
        t.id !== tag.id
      )
      .sort((a, b) => (b.post_count || 0) - (a.post_count || 0))
      .slice(0, 10)
  }, [initialTags])

  return (
    <div className="space-y-6">
      {/* 搜尋和篩選區域 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            標籤搜尋
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Command 搜尋組件 */}
          <Command className="rounded-lg border shadow-md">
            <CommandInput
              placeholder="搜尋標籤名稱或分類..."
              value={query}
              onValueChange={setQuery}
            />
            <CommandList>
              <CommandEmpty>找不到相關標籤</CommandEmpty>
              
              {/* 搜尋歷史 */}
              {!query && searchHistory.length > 0 && (
                <CommandGroup heading="最近搜尋">
                  {searchHistory.map((historyQuery, index) => (
                    <CommandItem
                      key={index}
                      onSelect={() => handleSearchFromHistory(historyQuery)}
                      className="cursor-pointer"
                    >
                      <Search className="mr-2 h-4 w-4 opacity-50" />
                      {historyQuery}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
              
              {/* 搜尋建議 */}
              {query && searchSuggestions.length > 0 && (
                <CommandGroup heading="搜尋建議">
                  {searchSuggestions.map((tag) => (
                    <CommandItem
                      key={tag.id}
                      onSelect={() => handleTagSelect(tag)}
                      className="cursor-pointer"
                    >
                      <Hash className="mr-2 h-4 w-4" />
                      <span className="flex-1">{tag.name}</span>
                      <Badge variant="outline" className="ml-2 text-xs">
                        {tag.sub_category || tag.main_category || 'OTHER'}
                      </Badge>
                      <span className="ml-2 text-xs text-muted-foreground">
                        {tag.post_count?.toLocaleString()}
                      </span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>

          {/* 篩選選項 */}
          <div className="flex flex-wrap gap-3">
            {/* 分類篩選 */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <Select value={filterCategory} onValueChange={setFilterCategory}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="選擇分類" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">所有分類</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 排序選項 */}
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-muted-foreground" />
              <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="排序方式" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="post_count">使用次數</SelectItem>
                  <SelectItem value="name">名稱</SelectItem>
                  <SelectItem value="category">分類</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 統計資訊 */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>總標籤: {initialTags.length.toLocaleString()}</span>
            {query && <span>搜尋結果: {filteredAndSortedTags.length}</span>}
            {filterCategory !== 'all' && <span>分類: {filterCategory}</span>}
          </div>
        </CardContent>
      </Card>

      {/* 已選標籤 */}
      {selectedTags.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">
                已選標籤 ({selectedTags.length})
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearAll}
                className="h-8"
              >
                <X className="w-4 h-4 mr-1" />
                清空
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {selectedTags.map((tag) => (
                <Badge
                  key={tag.id}
                  variant="secondary"
                  className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors px-3 py-1"
                  onClick={() => handleTagRemove(tag.id)}
                >
                  {tag.name}
                  <X className="w-3 h-3 ml-1" />
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 搜尋結果 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">搜尋結果</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="grid" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="grid">網格檢視</TabsTrigger>
              <TabsTrigger value="list">列表檢視</TabsTrigger>
            </TabsList>

            {/* 網格檢視 */}
            <TabsContent value="grid">
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                {filteredAndSortedTags.map((tag) => (
                  <div key={tag.id} className="relative group">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleTagSelect(tag)}
                      className="w-full justify-start hover:bg-primary hover:text-primary-foreground transition-colors"
                      disabled={selectedTags.some(t => t.id === tag.id)}
                    >
                      <span className="truncate">{tag.name}</span>
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute -top-1 -right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity bg-background border"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleShowDetails(tag)
                      }}
                    >
                      <Info className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </TabsContent>

            {/* 列表檢視 */}
            <TabsContent value="list">
              <div className="space-y-2">
                {filteredAndSortedTags.map((tag) => (
                  <div
                    key={tag.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <Hash className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                      <span className="font-medium truncate">{tag.name}</span>
                      <Badge variant="outline" className="flex-shrink-0">
                        {tag.sub_category || tag.main_category || 'OTHER'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-sm text-muted-foreground">
                        {tag.post_count?.toLocaleString()}
                      </span>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleShowDetails(tag)
                        }}
                      >
                        <Info className="w-4 h-4" />
                      </Button>
                      {selectedTags.some(t => t.id === tag.id) ? (
                        <Badge variant="secondary">已選</Badge>
                      ) : (
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => handleTagSelect(tag)}
                        >
                          添加
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>

          {/* 空狀態 */}
          {filteredAndSortedTags.length === 0 && (
            <div className="text-center py-12">
              <Search className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">找不到符合條件的標籤</p>
              <p className="text-sm text-muted-foreground mt-2">
                試試調整搜尋關鍵字或篩選條件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 標籤詳情彈窗 */}
      <TagDetailsDialog
        tag={detailsTag}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onAddToWorkspace={handleAddToWorkspaceFromDialog}
        relatedTags={detailsTag ? getRelatedTags(detailsTag) : []}
      />
    </div>
  )
}

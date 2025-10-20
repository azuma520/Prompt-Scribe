import { getTags } from '@/lib/api/tags'
import { AdvancedTagSearch } from './components/AdvancedTagSearch'
import { PopularTags } from './components/PopularTags'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'

export default async function TagsPage() {
  // 伺服器端獲取初始資料
  let initialTags = []
  let error = null

  try {
    initialTags = await getTags()
  } catch (e) {
    error = e instanceof Error ? e.message : '無法載入標籤資料'
    console.error('Failed to load tags:', e)
  }

  // 如果有錯誤，顯示錯誤訊息
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold mb-2">標籤搜尋</h1>
            <p className="text-muted-foreground">
              搜尋和探索超過 140,000+ AI 圖像生成標籤
            </p>
          </div>
          
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>載入失敗</AlertTitle>
            <AlertDescription>
              無法連接到 API 伺服器。請檢查網路連接或稍後再試。
              <br />
              <span className="text-xs text-muted-foreground">{error}</span>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-2">標籤搜尋</h1>
          <p className="text-muted-foreground">
            搜尋和探索超過 140,000+ AI 圖像生成標籤
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 左側：搜尋主區域 */}
          <div className="lg:col-span-3">
            <AdvancedTagSearch initialTags={initialTags} />
          </div>
          
          {/* 右側：熱門標籤側邊欄 */}
          <div className="lg:col-span-1">
            <PopularTags tags={initialTags.slice(0, 20)} />
          </div>
        </div>
      </div>
    </div>
  )
}

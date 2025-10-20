import { Metadata } from 'next'

export const metadata: Metadata = {
  title: '標籤搜尋 | Prompt-Scribe',
  description: '搜尋和探索 AI 圖像生成標籤，找到最適合的標籤組合。',
}

export default function TagsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background">
      {children}
    </div>
  )
}

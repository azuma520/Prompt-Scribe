import { Metadata } from 'next'

export const metadata: Metadata = {
  title: '工作區 | Prompt-Scribe',
  description: '管理和組織你的標籤，創建完美的 AI 圖像生成 Prompt。',
}

export default function WorkspaceLayout({
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

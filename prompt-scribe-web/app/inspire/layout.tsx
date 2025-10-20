import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Inspire 靈感生成 | Prompt-Scribe',
  description: '使用 AI 生成創意靈感卡片，為你的創作提供無限靈感。',
}

export default function InspireLayout({
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

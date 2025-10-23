// Inspire Agent 主頁面 - Server Component

import { InspireAgentClient } from './components/InspireAgentClient'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowLeft, Sparkles } from 'lucide-react'

export const metadata = {
  title: '✨ Inspire Agent - AI 創作夥伴',
  description: '用自然對話的方式，將模糊的情緒和感覺轉化為高品質的圖像生成 Prompt',
}

export default function InspireAgentPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                返回首頁
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <h1 className="text-xl font-bold text-primary">
                Inspire Agent
              </h1>
              <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                Beta
              </span>
            </div>
            <div className="w-24" /> {/* 佔位，保持標題居中 */}
          </div>
        </div>
      </header>

      {/* 主內容 - 使用 Client Component */}
      <InspireAgentClient />

      {/* Footer */}
      <footer className="border-t bg-background/95 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center space-y-2">
            <p className="text-sm text-muted-foreground">
              Made with ❤️ by Prompt-Scribe Team | Powered by{' '}
              <a
                href="https://platform.openai.com/docs/guides/agents"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                OpenAI Agents
              </a>
            </p>
            <p className="text-xs text-muted-foreground">
              🎨 讓創作更簡單 · 平均只需 2-4 輪對話
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}


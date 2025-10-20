// Inspire 主頁面 - Server Component

import { InspireClientNew } from './components/InspireClientNew';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function InspirePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                返回首頁
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-primary">
              ✨ Inspire 智能標籤推薦
            </h1>
            <div className="w-24" /> {/* 佔位，保持標題居中 */}
          </div>
        </div>
      </header>

      {/* 主內容 - 使用新的 Client Component */}
      <InspireClientNew />

      {/* Footer */}
      <footer className="border-t bg-background/95 mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-sm text-center text-muted-foreground">
            Made with ❤️ by Prompt-Scribe Team | Powered by{' '}
            <a
              href="https://prompt-scribe-api.zeabur.app/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Prompt-Scribe API
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}


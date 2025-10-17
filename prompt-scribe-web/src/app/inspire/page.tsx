// Inspire 主頁面

'use client';

import { InputBox } from './components/InputBox';
import { InspirationCards } from './components/InspirationCards';
import { ResultPanel } from './components/ResultPanel';
import { ErrorDisplay } from './components/ErrorDisplay';
import { useInspiration } from '@/lib/hooks/useInspiration';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function InspirePage() {
  const {
    state,
    cards,
    selectedCard,
    finalResult,
    errorMessage,
    generateCards,
    selectCard,
    reset,
    isGenerating,
  } = useInspiration();

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
              ✨ Inspire 靈感生成
            </h1>
            <div className="w-24" /> {/* 佔位，保持標題居中 */}
          </div>
        </div>
      </header>

      {/* 主內容 */}
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* 輸入區域 */}
        <section>
          <InputBox
            onSubmit={generateCards}
            loading={isGenerating}
            disabled={state !== 'idle' && state !== 'showing'}
          />
        </section>

        {/* 錯誤顯示 */}
        {errorMessage && (
          <section>
            <ErrorDisplay 
              error={errorMessage} 
              onRetry={() => {
                // 重新嘗試最後的輸入（如果有保存的話）
                if (cards.length > 0) {
                  // 這裡可以保存最後的輸入，暫時先清除錯誤
                  reset();
                }
              }}
            />
          </section>
        )}

        {/* 靈感卡片區域 */}
        {(state === 'showing' || state === 'finalized') && (
          <section>
            <InspirationCards
              cards={cards}
              selectedCard={selectedCard}
              onCardSelect={(card, _index) => selectCard(card)}
              loading={false}
            />
          </section>
        )}

        {/* 最終結果區域 */}
        {finalResult && (
          <section className="max-w-3xl mx-auto">
            <ResultPanel card={finalResult} onReset={reset} />
          </section>
        )}

        {/* 使用提示（初始狀態） */}
        {state === 'idle' && cards.length === 0 && (
          <section className="max-w-2xl mx-auto text-center py-12 space-y-6">
            <div className="text-6xl animate-bounce">✨</div>
            <h2 className="text-2xl font-bold text-primary">
              開始你的創作旅程
            </h2>
            <p className="text-muted-foreground">
              在上方輸入框中描述你想要的感覺或主題，
              <br />
              AI 會為你生成 3 張精美的靈感卡片
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="p-4 bg-primary/5 rounded-lg">
                <p className="font-medium mb-2">💭 情緒描述</p>
                <p className="text-sm text-muted-foreground">
                  「孤獨又夢幻的感覺」
                </p>
              </div>
              <div className="p-4 bg-primary/5 rounded-lg">
                <p className="font-medium mb-2">🎨 主題描述</p>
                <p className="text-sm text-muted-foreground">
                  「賽博龐克城市夜景」
                </p>
              </div>
              <div className="p-4 bg-primary/5 rounded-lg">
                <p className="font-medium mb-2">🌟 場景描述</p>
                <p className="text-sm text-muted-foreground">
                  「櫻花樹下的女孩」
                </p>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t bg-background/95 mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-sm text-center text-muted-foreground">
            Made with ❤️ by Prompt-Scribe Team | Powered by{' '}
            <a
              href="https://prompt-scribe-api.vercel.app/docs"
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


'use client'

import { InputBox } from './InputBox';
import { InspirationCards } from './InspirationCards';
import { ResultPanel } from './ResultPanel';
import { ErrorDisplay } from './ErrorDisplay';
import { useInspiration } from '@/lib/hooks/useInspiration';

export function InspireClient() {
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
  );
}

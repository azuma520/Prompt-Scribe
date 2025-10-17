// 靈感卡片容器組件

'use client';

import { InspirationCard } from './InspirationCard';
import { Loader } from './Loader';
import { cn } from '@/lib/utils';
import type { InspirationCard as ICard } from '@/types/inspire';

interface InspirationCardsProps {
  cards: ICard[];
  selectedCard?: ICard | null;
  onCardSelect: (card: ICard, index: number) => void;
  loading?: boolean;
  className?: string;
}

export function InspirationCards({
  cards,
  selectedCard,
  onCardSelect,
  loading = false,
  className,
}: InspirationCardsProps) {
  if (loading) {
    return <Loader />;
  }

  if (cards.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-muted-foreground">尚未生成靈感卡</p>
        <p className="text-sm text-muted-foreground mt-2">
          在上方輸入框描述你想要的感覺或主題
        </p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-primary">🎴 靈感卡片</h2>
        <p className="text-sm text-muted-foreground">
          已生成 {cards.length} 張靈感卡
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card, index) => (
          <div
            key={index}
            className="animate-in fade-in slide-in-from-bottom-4"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <InspirationCard
              card={card}
              selected={selectedCard === card}
              onSelect={c => onCardSelect(c, index)}
            />
          </div>
        ))}
      </div>

      {selectedCard && (
        <div className="text-center py-4">
          <p className="text-sm text-muted-foreground">
            已選擇卡片 ✓ 滾動到下方查看結果
          </p>
        </div>
      )}
    </div>
  );
}


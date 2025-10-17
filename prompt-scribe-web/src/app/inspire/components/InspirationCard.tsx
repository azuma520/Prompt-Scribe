// 單張靈感卡組件

'use client';

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { InspirationCard as ICard } from '@/types/inspire';
import { Check } from 'lucide-react';

interface InspirationCardProps {
  card: ICard;
  selected?: boolean;
  onSelect?: (card: ICard) => void;
  variant?: 'default' | 'compact';
  showConfidence?: boolean;
  className?: string;
}

export function InspirationCard({
  card,
  selected = false,
  onSelect,
  variant = 'default',
  showConfidence = true,
  className,
}: InspirationCardProps) {
  const isCompact = variant === 'compact';

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-105',
        selected &&
          'ring-2 ring-primary shadow-[0_0_0_3px_rgba(var(--primary),0.2)]',
        'group',
        className
      )}
      onClick={() => onSelect?.(card)}
    >
      <CardHeader className={isCompact ? 'pb-3' : undefined}>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-xl font-bold text-primary group-hover:text-primary/80 transition-colors">
            {card.subject}
          </CardTitle>
          {selected && (
            <div className="bg-primary text-primary-foreground rounded-full p-1">
              <Check className="w-4 h-4" />
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className={isCompact ? 'pb-3' : 'space-y-3'}>
        {/* 場景 */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">場景</p>
          <p className="text-base">{card.scene}</p>
        </div>

        {/* 風格 */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">風格</p>
          <p className="text-base">{card.style}</p>
        </div>

        {/* 標籤 */}
        {!isCompact && card.source_tags.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-2">
            {card.source_tags.slice(0, 5).map(tag => (
              <Badge
                key={tag}
                variant="secondary"
                className="bg-primary/10 text-primary border-primary/20"
              >
                {tag}
              </Badge>
            ))}
            {card.source_tags.length > 5 && (
              <Badge variant="outline">+{card.source_tags.length - 5}</Badge>
            )}
          </div>
        )}

        {/* 信心度 */}
        {showConfidence && card.confidence_score && (
          <div className="flex items-center gap-2 pt-2">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-500"
                style={{ width: `${card.confidence_score * 100}%` }}
              />
            </div>
            <span className="text-sm text-muted-foreground tabular-nums">
              {Math.round(card.confidence_score * 100)}%
            </span>
          </div>
        )}
      </CardContent>

      {!isCompact && (
        <CardFooter>
          <Button
            className="w-full"
            variant={selected ? 'default' : 'outline'}
            onClick={e => {
              e.stopPropagation();
              onSelect?.(card);
            }}
          >
            {selected ? '已選擇 ✓' : '選擇此卡'}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}


// Inspire 載入動畫組件

'use client';

import { cn } from '@/lib/utils';

interface LoaderProps {
  message?: string;
  showShimmer?: boolean;
  className?: string;
}

export function Loader({
  message = '正在為您生成靈感卡...',
  showShimmer = true,
  className,
}: LoaderProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12',
        className
      )}
    >
      {/* Shimmer 卡片骨架 */}
      {showShimmer && (
        <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {[1, 2, 3].map(i => (
            <div
              key={i}
              className="h-64 rounded-2xl bg-gradient-to-r from-muted via-muted/50 to-muted bg-[length:200%_100%] animate-[shimmer_2s_ease-in-out_infinite]"
              style={{ animationDelay: `${i * 200}ms` }}
            />
          ))}
        </div>
      )}

        {/* 載入訊息 */}
        <div className="text-center space-y-4">
          <p className="text-lg font-medium text-primary">{message}</p>

          {/* 浮動表情符號 */}
          <div className="text-5xl animate-bounce">✨</div>

          {/* 進度點 */}
          <div className="flex items-center justify-center gap-2">
            <div
              className="w-2 h-2 bg-primary rounded-full animate-pulse"
              style={{ animationDelay: '0ms' }}
            />
            <div
              className="w-2 h-2 bg-primary rounded-full animate-pulse"
              style={{ animationDelay: '200ms' }}
            />
            <div
              className="w-2 h-2 bg-primary rounded-full animate-pulse"
              style={{ animationDelay: '400ms' }}
            />
          </div>

          {/* 額外提示 */}
          <p className="text-sm text-muted-foreground mt-4">
            正在分析您的描述並生成靈感卡...
          </p>
        </div>
    </div>
  );
}


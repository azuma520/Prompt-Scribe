// 錯誤顯示組件

'use client';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorDisplayProps {
  error: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorDisplay({ error, onRetry, className }: ErrorDisplayProps) {
  return (
    <div className={cn('w-full max-w-3xl mx-auto', className)}>
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>生成失敗</AlertTitle>
        <AlertDescription className="mt-2">
          <p className="mb-4">{error}</p>
          
          <div className="space-y-2">
            <p className="text-sm font-medium">可能的解決方案：</p>
            <ul className="text-sm space-y-1 ml-4">
              <li>• 檢查網路連接</li>
              <li>• 確認 API 服務正常</li>
              <li>• 嘗試重新輸入描述</li>
              <li>• 稍後再試</li>
            </ul>
          </div>

          {onRetry && (
            <div className="mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                重新嘗試
              </Button>
            </div>
          )}
        </AlertDescription>
      </Alert>
    </div>
  );
}

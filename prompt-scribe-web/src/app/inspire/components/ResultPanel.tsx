// 結果面板組件

'use client';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { buildPromptFromCard } from '@/lib/utils/formula';
import type { InspirationCard } from '@/types/inspire';
import { Copy, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';

interface ResultPanelProps {
  card: InspirationCard;
  onCopy?: (format: 'json' | 'prompt') => void;
  onReset?: () => void;
  className?: string;
}

export function ResultPanel({
  card,
  onCopy,
  onReset,
  className,
}: ResultPanelProps) {
  const prompt = buildPromptFromCard(card);

  const handleCopy = async (format: 'json' | 'prompt') => {
    const content =
      format === 'json' ? JSON.stringify(card, null, 2) : prompt;

    await navigator.clipboard.writeText(content);

    toast.success('已複製！', {
      description: `${format === 'json' ? 'JSON' : 'Prompt'} 已複製到剪貼簿`,
      duration: 2000,
    });

    onCopy?.(format);
  };

  return (
    <Card className={cn('animate-in slide-in-from-bottom-4', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl font-bold text-primary flex items-center gap-2">
            📋 最終結果
          </CardTitle>
          {onReset && (
            <Button variant="ghost" size="sm" onClick={onReset}>
              <RotateCcw className="w-4 h-4 mr-2" />
              重新開始
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="prompt" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="prompt">Prompt 格式</TabsTrigger>
            <TabsTrigger value="json">JSON 格式</TabsTrigger>
          </TabsList>

          {/* Prompt Tab */}
          <TabsContent value="prompt" className="space-y-4">
            <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 min-h-[150px]">
              <pre className="text-sm whitespace-pre-wrap font-sans">
                {prompt}
              </pre>
            </div>

            <Button
              onClick={() => handleCopy('prompt')}
              className="w-full"
              size="lg"
            >
              <Copy className="w-4 h-4 mr-2" />
              複製 Prompt
            </Button>
          </TabsContent>

          {/* JSON Tab */}
          <TabsContent value="json" className="space-y-4">
            <div className="bg-muted rounded-lg p-4 max-h-[400px] overflow-auto">
              <pre className="text-xs font-mono">
                {JSON.stringify(card, null, 2)}
              </pre>
            </div>

            <Button
              onClick={() => handleCopy('json')}
              className="w-full"
              size="lg"
              variant="outline"
            >
              <Copy className="w-4 h-4 mr-2" />
              複製 JSON
            </Button>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}


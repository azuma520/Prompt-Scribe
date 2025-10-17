# 📦 Inspire 組件文檔

> **Inspire 模塊的所有 React 組件規格說明**

**版本**: 1.0.0  
**更新日期**: 2025-10-17

---

## 📋 組件清單

### 核心組件（6 個）

1. **InputBox** - 使用者輸入框
2. **InspirationCards** - 靈感卡展示容器
3. **InspirationCard** - 單張靈感卡
4. **FeedbackPanel** - 反饋對話面板
5. **ResultPanel** - 最終結果展示
6. **Loader** - 載入動畫

### 共用組件（3 個）

7. **CopyButton** - 複製按鈕
8. **ToastProvider** - Toast 通知
9. **LoadingShimmer** - Shimmer 載入效果

---

## 🎨 組件詳細規格

### 1. InputBox（輸入框組件）

#### 用途
接收使用者的情緒或主題描述輸入

#### Props
```typescript
interface InputBoxProps {
  value?: string;
  onChange?: (value: string) => void;
  onSubmit: (input: string) => void;
  loading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  className?: string;
}
```

#### 實作範例
```tsx
'use client';

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function InputBox({
  value: controlledValue,
  onChange,
  onSubmit,
  loading = false,
  disabled = false,
  placeholder = "描述你想要的感覺或主題...",
  maxLength = 500,
  className,
}: InputBoxProps) {
  const [internalValue, setInternalValue] = useState('');
  const value = controlledValue ?? internalValue;
  
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (onChange) {
      onChange(newValue);
    } else {
      setInternalValue(newValue);
    }
  };
  
  const handleSubmit = () => {
    if (value.trim()) {
      onSubmit(value.trim());
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  return (
    <div className={cn("relative w-full max-w-3xl mx-auto", className)}>
      <Textarea
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled || loading}
        maxLength={maxLength}
        className="inspire-input min-h-[120px] pr-32 resize-none"
      />
      
      {/* 字數統計 */}
      <div className="absolute bottom-16 right-4 text-caption text-muted-foreground">
        {value.length} / {maxLength}
      </div>
      
      {/* 提交按鈕 */}
      <Button
        onClick={handleSubmit}
        disabled={disabled || loading || !value.trim()}
        className="inspire-button-primary absolute bottom-4 right-4"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin">⏳</span>
            生成中...
          </span>
        ) : (
          <span>生成靈感卡 ✨</span>
        )}
      </Button>
      
      {/* 提示文字 */}
      <p className="mt-2 text-caption text-muted-foreground text-center">
        按 Ctrl+Enter 快速提交
      </p>
    </div>
  );
}
```

#### 使用範例
```tsx
<InputBox
  onSubmit={handleGenerate}
  loading={isGenerating}
  placeholder="例如：孤獨又夢幻的感覺"
/>
```

---

### 2. InspirationCard（靈感卡組件）

#### 用途
展示單張靈感卡的所有資訊

#### Props
```typescript
interface InspirationCardProps {
  card: InspirationCard;
  selected?: boolean;
  onSelect?: (card: InspirationCard) => void;
  onViewDetails?: (card: InspirationCard) => void;
  variant?: 'default' | 'compact';
  showConfidence?: boolean;
  className?: string;
}
```

#### 實作範例
```tsx
'use client';

import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { Check, Eye } from 'lucide-react';

export function InspirationCard({
  card,
  selected = false,
  onSelect,
  onViewDetails,
  variant = 'default',
  showConfidence = true,
  className,
}: InspirationCardProps) {
  const isCompact = variant === 'compact';
  
  return (
    <Card
      className={cn(
        "inspire-card cursor-pointer group",
        selected && "selected",
        isCompact && "p-4",
        className
      )}
      onClick={() => onSelect?.(card)}
    >
      <CardHeader className={isCompact ? "pb-3" : undefined}>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-heading-3 text-inspire-dark 
                                group-hover:text-inspire transition-colors">
            {card.subject}
          </CardTitle>
          {selected && (
            <div className="bg-inspire text-white rounded-full p-1">
              <Check className="w-4 h-4" />
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className={isCompact ? "pb-3" : undefined}>
        {/* 場景 */}
        <div className="mb-3">
          <p className="text-body-small text-muted-foreground mb-1">
            場景
          </p>
          <p className="text-body text-foreground">
            {card.scene}
          </p>
        </div>
        
        {/* 風格 */}
        <div className="mb-3">
          <p className="text-body-small text-muted-foreground mb-1">
            風格
          </p>
          <p className="text-body text-foreground">
            {card.style}
          </p>
        </div>
        
        {/* 標籤 */}
        {!isCompact && (
          <div className="flex flex-wrap gap-2 mb-3">
            {card.source_tags.slice(0, 5).map((tag) => (
              <Badge 
                key={tag}
                variant="secondary"
                className="bg-inspire-light/20 text-inspire-dark 
                           border border-inspire/30"
              >
                {tag}
              </Badge>
            ))}
            {card.source_tags.length > 5 && (
              <Badge variant="outline">
                +{card.source_tags.length - 5}
              </Badge>
            )}
          </div>
        )}
        
        {/* 信心度 */}
        {showConfidence && card.confidence_score && (
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-inspire transition-all duration-500"
                style={{ width: `${card.confidence_score * 100}%` }}
              />
            </div>
            <span className="text-caption text-muted-foreground tabular-nums">
              {Math.round(card.confidence_score * 100)}%
            </span>
          </div>
        )}
      </CardContent>
      
      {!isCompact && (
        <CardFooter className="flex gap-2">
          <Button
            variant="default"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(card);
            }}
          >
            {selected ? '已選擇' : '選擇'}
          </Button>
          
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={(e) => {
                  e.stopPropagation();
                  onViewDetails?.(card);
                }}
              >
                <Eye className="w-4 h-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>查看詳情</TooltipContent>
          </Tooltip>
        </CardFooter>
      )}
    </Card>
  );
}
```

---

### 3. InspirationCards（卡片容器組件）

#### 用途
管理和展示多張靈感卡

#### Props
```typescript
interface InspirationCardsProps {
  cards: InspirationCard[];
  selectedIndex?: number;
  onCardSelect: (card: InspirationCard, index: number) => void;
  loading?: boolean;
  className?: string;
}
```

#### 實作範例
```tsx
'use client';

import { InspirationCard } from './InspirationCard';
import { cn } from '@/lib/utils';

export function InspirationCards({
  cards,
  selectedIndex,
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
        <p className="text-body text-muted-foreground">
          尚未生成靈感卡
        </p>
      </div>
    );
  }
  
  return (
    <div className={cn("space-y-4", className)}>
      <h2 className="text-heading-2 text-inspire-dark font-bold mb-6">
        🎴 靈感卡片
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card, index) => (
          <div 
            key={index}
            className="animate-fade-in"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <InspirationCard
              card={card}
              selected={selectedIndex === index}
              onSelect={(c) => onCardSelect(c, index)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 4. FeedbackPanel（反饋面板組件）

#### 用途
收集使用者反饋並提供對話式引導

#### Props
```typescript
interface FeedbackPanelProps {
  onFeedback: (feedback: string, action: FeedbackAction) => void;
  suggestions?: string[];
  loading?: boolean;
  className?: string;
}

type FeedbackAction = 'refine' | 'regenerate' | 'finalize';
```

#### 實作範例
```tsx
'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { Sparkles, RefreshCw, Check } from 'lucide-react';

export function FeedbackPanel({
  onFeedback,
  suggestions = [],
  loading = false,
  className,
}: FeedbackPanelProps) {
  const [feedback, setFeedback] = useState('');
  
  const handleAction = (action: FeedbackAction) => {
    onFeedback(feedback, action);
    if (action !== 'finalize') {
      setFeedback('');
    }
  };
  
  return (
    <Card className={cn("animate-slide-up", className)}>
      <CardHeader>
        <CardTitle className="text-heading-3 text-inspire-dark flex items-center gap-2">
          💬 反饋與調整
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* AI 建議 */}
        {suggestions.length > 0 && (
          <div className="space-y-2">
            <p className="text-body-small text-muted-foreground">
              AI 建議：
            </p>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <div 
                  key={index}
                  className="bg-inspire-light/10 border border-inspire/20 
                             rounded-lg p-3 text-body-small
                             animate-slide-left"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* 反饋輸入 */}
        <div>
          <Textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="告訴我你想要調整的方向..."
            disabled={loading}
            className="min-h-[100px]"
          />
        </div>
        
        {/* 快速操作按鈕 */}
        <div className="flex flex-wrap gap-2">
          <Badge 
            variant="outline" 
            className="cursor-pointer hover:bg-muted"
            onClick={() => setFeedback('想要更夢幻一點')}
          >
            更夢幻
          </Badge>
          <Badge 
            variant="outline"
            className="cursor-pointer hover:bg-muted"
            onClick={() => setFeedback('想要更現實一點')}
          >
            更現實
          </Badge>
          <Badge 
            variant="outline"
            className="cursor-pointer hover:bg-muted"
            onClick={() => setFeedback('改變場景')}
          >
            改變場景
          </Badge>
          <Badge 
            variant="outline"
            className="cursor-pointer hover:bg-muted"
            onClick={() => setFeedback('調整風格')}
          >
            調整風格
          </Badge>
        </div>
        
        {/* 操作按鈕 */}
        <div className="flex gap-3 pt-2">
          <Button
            onClick={() => handleAction('refine')}
            disabled={loading || !feedback.trim()}
            className="flex-1"
            variant="default"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            精煉調整
          </Button>
          
          <Button
            onClick={() => handleAction('regenerate')}
            disabled={loading}
            className="flex-1"
            variant="outline"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            重新生成
          </Button>
          
          <Button
            onClick={() => handleAction('finalize')}
            disabled={loading}
            variant="secondary"
          >
            <Check className="w-4 h-4 mr-2" />
            確認
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

### 5. ResultPanel（結果面板組件）

#### 用途
展示最終確認的靈感卡，提供複製功能

#### Props
```typescript
interface ResultPanelProps {
  card: InspirationCard;
  onCopy?: (format: 'json' | 'prompt') => void;
  onSave?: (card: InspirationCard) => void;
  onReset?: () => void;
  className?: string;
}
```

#### 實作範例
```tsx
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';
import { buildPromptFromCard } from '@/lib/formula';
import { Copy, Save, RotateCcw } from 'lucide-react';

export function ResultPanel({
  card,
  onCopy,
  onSave,
  onReset,
  className,
}: ResultPanelProps) {
  const { toast } = useToast();
  const prompt = buildPromptFromCard(card);
  
  const handleCopy = async (format: 'json' | 'prompt') => {
    const content = format === 'json' 
      ? JSON.stringify(card, null, 2)
      : prompt;
      
    await navigator.clipboard.writeText(content);
    
    toast({
      title: "已複製！",
      description: `${format === 'json' ? 'JSON' : 'Prompt'} 已複製到剪貼簿`,
      duration: 2000,
    });
    
    onCopy?.(format);
  };
  
  return (
    <Card className={cn("animate-scale-in", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-heading-3 text-inspire-dark flex items-center gap-2">
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
            <div className="bg-inspire-light/10 border border-inspire/30 
                            rounded-lg p-4 min-h-[200px]">
              <pre className="text-body text-foreground whitespace-pre-wrap font-sans">
                {prompt}
              </pre>
            </div>
            
            <Button
              onClick={() => handleCopy('prompt')}
              className="w-full inspire-button-primary"
            >
              <Copy className="w-4 h-4 mr-2" />
              複製 Prompt
            </Button>
          </TabsContent>
          
          {/* JSON Tab */}
          <TabsContent value="json" className="space-y-4">
            <div className="bg-muted rounded-lg p-4 max-h-[400px] overflow-auto">
              <pre className="text-body-small font-mono text-foreground">
                {JSON.stringify(card, null, 2)}
              </pre>
            </div>
            
            <Button
              onClick={() => handleCopy('json')}
              className="w-full inspire-button-primary"
            >
              <Copy className="w-4 h-4 mr-2" />
              複製 JSON
            </Button>
          </TabsContent>
        </Tabs>
        
        {/* 儲存按鈕 */}
        {onSave && (
          <Button
            onClick={() => onSave(card)}
            variant="outline"
            className="w-full mt-4"
          >
            <Save className="w-4 h-4 mr-2" />
            儲存到收藏
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
```

---

### 6. Loader（載入動畫組件）

#### 用途
在生成靈感卡時顯示載入動畫

#### Props
```typescript
interface LoaderProps {
  message?: string;
  showShimmer?: boolean;
  className?: string;
}
```

#### 實作範例
```tsx
'use client';

import { cn } from '@/lib/utils';

export function Loader({
  message = "正在為您生成靈感卡...",
  showShimmer = true,
  className,
}: LoaderProps) {
  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-12",
      className
    )}>
      {/* Shimmer 卡片骨架 */}
      {showShimmer && (
        <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {[1, 2, 3].map((i) => (
            <div 
              key={i}
              className="shimmer-effect h-64 rounded-2xl"
              style={{ animationDelay: `${i * 200}ms` }}
            />
          ))}
        </div>
      )}
      
      {/* 載入訊息（打字效果） */}
      <div className="text-center space-y-4">
        <p className="text-body text-inspire-dark font-medium typing-effect max-w-md mx-auto">
          {message}
        </p>
        
        {/* 浮動圖標 */}
        <div className="text-5xl float-element">
          ✨
        </div>
        
        {/* 進度提示 */}
        <div className="flex items-center justify-center gap-2">
          <div className="w-2 h-2 bg-inspire rounded-full animate-pulse" 
               style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-inspire rounded-full animate-pulse" 
               style={{ animationDelay: '200ms' }} />
          <div className="w-2 h-2 bg-inspire rounded-full animate-pulse" 
               style={{ animationDelay: '400ms' }} />
        </div>
      </div>
    </div>
  );
}
```

---

### 7. CopyButton（複製按鈕組件）

#### 用途
統一的複製按鈕，帶 Toast 反饋

#### Props
```typescript
interface CopyButtonProps {
  content: string;
  label?: string;
  successMessage?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
}
```

#### 實作範例
```tsx
'use client';

import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';

export function CopyButton({
  content,
  label = "複製",
  successMessage = "已複製到剪貼簿",
  variant = 'default',
  size = 'default',
  className,
}: CopyButtonProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  
  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    
    setCopied(true);
    toast({
      title: "✅ " + successMessage,
      duration: 2000,
    });
    
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <Button
      onClick={handleCopy}
      variant={variant}
      size={size}
      className={cn(className)}
    >
      {copied ? (
        <>
          <Check className="w-4 h-4 mr-2" />
          已複製
        </>
      ) : (
        <>
          <Copy className="w-4 h-4 mr-2" />
          {label}
        </>
      )}
    </Button>
  );
}
```

---

## 🎯 組件組合範例

### 完整頁面組裝

```tsx
// app/inspire/page.tsx

'use client';

import { useState } from 'react';
import { InputBox } from './components/InputBox';
import { InspirationCards } from './components/InspirationCards';
import { FeedbackPanel } from './components/FeedbackPanel';
import { ResultPanel } from './components/ResultPanel';
import { useInspiration } from './hooks/useInspiration';

export default function InspirePage() {
  const {
    state,
    cards,
    selectedCard,
    finalResult,
    generateCards,
    selectCard,
    provideFeedback,
    finalize,
  } = useInspiration();
  
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* 輸入區域 */}
      <InputBox
        onSubmit={generateCards}
        loading={state === 'generating'}
      />
      
      {/* 靈感卡片 */}
      {state === 'showing' && (
        <InspirationCards
          cards={cards}
          selectedIndex={cards.findIndex(c => c === selectedCard)}
          onCardSelect={selectCard}
        />
      )}
      
      {/* 反饋面板 */}
      {selectedCard && !finalResult && (
        <FeedbackPanel
          onFeedback={provideFeedback}
          suggestions={["選擇一張你最喜歡的卡片", "或告訴我想要調整的方向"]}
          loading={state === 'refining'}
        />
      )}
      
      {/* 最終結果 */}
      {finalResult && (
        <ResultPanel
          card={finalResult}
          onReset={() => window.location.reload()}
        />
      )}
    </div>
  );
}
```

---

## ✅ 組件檢查清單

### 開發檢查

- [ ] 所有組件都有 TypeScript 類型定義
- [ ] 所有組件都有 Props 介面
- [ ] 使用語意化的 Tailwind Token
- [ ] 支援深色模式
- [ ] 響應式設計（mobile-first）
- [ ] 無障礙支援（ARIA 標籤、鍵盤導航）
- [ ] 錯誤狀態處理
- [ ] 載入狀態處理
- [ ] 空狀態處理

### 測試檢查

- [ ] 單元測試（組件渲染）
- [ ] 互動測試（點擊、輸入）
- [ ] 無障礙測試（axe-core）
- [ ] 視覺回歸測試（可選）

### 文檔檢查

- [ ] 組件用途說明
- [ ] Props 完整文檔
- [ ] 使用範例
- [ ] 常見用法
- [ ] 注意事項

---

## 📚 參考資料

- [shadcn/ui 文檔](https://ui.shadcn.com/)
- [Tailwind CSS 文檔](https://tailwindcss.com/docs)
- [Radix UI 文檔](https://www.radix-ui.com/)
- [Framer Motion 文檔](https://www.framer.com/motion/)

---

**組件文檔完成 - 所有組件規格清晰定義！** 📦

**版本**: 1.0.0  
**維護者**: Prompt-Scribe Team  
**最後更新**: 2025-10-17


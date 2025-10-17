// Inspire 輸入框組件

'use client';

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Sparkles } from 'lucide-react';

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

export function InputBox({
  value: controlledValue,
  onChange,
  onSubmit,
  loading = false,
  disabled = false,
  placeholder = '描述你想要的感覺或主題...',
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
    <div className={cn('relative w-full max-w-3xl mx-auto', className)}>
      <Textarea
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled || loading}
        maxLength={maxLength}
        className="min-h-[120px] pr-32 resize-none text-base"
      />

      {/* 字數統計 */}
      <div className="absolute bottom-16 right-4 text-sm text-muted-foreground">
        {value.length} / {maxLength}
      </div>

      {/* 提交按鈕 */}
      <Button
        onClick={handleSubmit}
        disabled={disabled || loading || !value.trim()}
        className="absolute bottom-4 right-4"
        size="lg"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin">⏳</span>
            生成中...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            生成靈感卡
          </span>
        )}
      </Button>

      {/* 提示文字 */}
      <p className="mt-2 text-sm text-muted-foreground text-center">
        💡 提示：按 Ctrl+Enter 快速提交 | 例如：「孤獨又夢幻的感覺」
      </p>
    </div>
  );
}


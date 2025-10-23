'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send, RotateCcw } from 'lucide-react'
import { MessageBubble } from './MessageBubble'
import { Message } from '@/types/inspire'

interface ConversationPanelProps {
  messages: Message[]
  isLoading: boolean
  onSend: (message: string) => void
  disabled?: boolean
}

/**
 * 對話面板組件
 * 顯示對話歷史和輸入框
 */
export function ConversationPanel({
  messages,
  isLoading,
  onSend,
  disabled = false,
}: ConversationPanelProps) {
  const [input, setInput] = useState('')
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 調試日誌
  console.log('ConversationPanel 渲染:', {
    messagesLength: messages.length,
    messages: messages,
    isLoading
  })

  // 強制重新渲染調試
  useEffect(() => {
    console.log('ConversationPanel useEffect - messages 變化:', {
      messagesLength: messages.length,
      messages: messages.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 30) + '...' }))
    })
  }, [messages])

  // 自動滾動到底部
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        '[data-radix-scroll-area-viewport]'
      )
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages, isLoading])

  // 處理發送
  const handleSend = () => {
    const trimmedInput = input.trim()
    if (!trimmedInput || isLoading || disabled) return

    onSend(trimmedInput)
    setInput('')
    
    // 重新聚焦到輸入框
    setTimeout(() => {
      textareaRef.current?.focus()
    }, 100)
  }

  // 處理鍵盤事件
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl/Cmd + Enter 發送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-card border border-border rounded-lg shadow-sm">
      {/* 標題 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="font-semibold text-sm">對話歷史</h3>
        <span className="text-xs text-muted-foreground">
          {messages.length} 條訊息
        </span>
      </div>

      {/* 對話區域 */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
            開始對話後，歷史記錄會顯示在這裡
          </div>
        ) : (
          <div>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
                <span>AI 正在思考...</span>
              </div>
            )}
          </div>
        )}
      </ScrollArea>

      {/* 輸入區域 */}
      <div className="p-4 border-t border-border">
        <div className="space-y-2">
          <Textarea
            ref={textareaRef}
            id="inspire-message-input"
            name="inspire-message-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              messages.length === 0
                ? '描述你想要的感覺... (Ctrl+Enter 發送)'
                : '輸入你的回應... (Ctrl+Enter 發送)'
            }
            className="min-h-[80px] resize-none"
            disabled={isLoading || disabled}
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              <kbd className="px-1 py-0.5 text-xs bg-muted rounded">Ctrl</kbd> +{' '}
              <kbd className="px-1 py-0.5 text-xs bg-muted rounded">Enter</kbd>{' '}
              發送
            </p>
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || disabled}
              size="sm"
              className="gap-2"
            >
              {isLoading ? (
                <>
                  <RotateCcw className="w-4 h-4 animate-spin" />
                  發送中...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  發送
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}


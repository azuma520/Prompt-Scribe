'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Home() {
  const [input, setInput] = useState('')
  
  const suggestions = [
    { icon: '🌸', text: '日系風格' },
    { icon: '🌃', text: '賽博朋克' },
    { icon: '🧙', text: '魔法幻想' },
    { icon: '🚀', text: '科幻未來' },
  ]
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('提交:', input)
    // TODO: 導航到 Inspire 頁面
  }

  return (
    <main className="relative min-h-screen w-full overflow-hidden">
      {/* 背景層 - 靜態漸變 */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 via-background to-pink-500/20" />
      
      {/* 內容層 */}
      <div className="relative z-10">
        {/* Hero Section */}
        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-5xl mx-auto text-center space-y-12">
            {/* 標題區 */}
            <div className="space-y-6">
              {/* 主標題 - 靜態漸變 + 微光效果 */}
              <h1 className="relative text-6xl md:text-7xl lg:text-8xl font-bold">
                <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                  🎨 Prompt-Scribe
                </span>
              </h1>
              
              {/* 副標題 - 靜態漸變 */}
              <p className="text-2xl md:text-3xl font-medium bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                AI 智能提示詞助手
              </p>
              
              {/* 說明文字 */}
              <p className="text-lg md:text-xl text-muted-foreground/80 max-w-2xl mx-auto">
                輕鬆生成高品質 Prompt，讓你的創意不再受限於表達
              </p>
            </div>
            
            {/* 輸入區域 */}
            <div className="space-y-8">
              <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="描述你想要的畫面，例如：櫻花樹下的和服少女..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="h-14 text-lg"
                  />
                  <Button type="submit" size="lg" className="h-14 px-8">
                    生成
                  </Button>
                </div>
              </form>
              
              {/* 快速建議 */}
              <div className="flex gap-3 justify-center flex-wrap">
                {suggestions.map((suggestion, i) => (
                  <Button
                    key={i}
                    variant="outline"
                    size="lg"
                    onClick={() => setInput(suggestion.text)}
                    className="gap-2 hover:bg-purple-500/10 hover:border-purple-500/50 transition-colors"
                  >
                    <span className="text-xl">{suggestion.icon}</span>
                    <span>{suggestion.text}</span>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Value Props Section */}
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* 統計卡片 1 */}
              <Card className="bg-card/80 backdrop-blur-sm border-purple-500/20 hover:border-purple-500/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-center text-lg">專業標籤庫</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center space-y-2">
                    <div className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                      140K
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Danbooru 專業標籤
                    </p>
                  </div>
                </CardContent>
              </Card>
              
              {/* 特色卡片 2 */}
              <Card className="bg-card/80 backdrop-blur-sm border-purple-500/20 hover:border-purple-500/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-center text-lg">AI 智能生成</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center space-y-2">
                    <div className="text-5xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                      GPT-5
                    </div>
                    <p className="text-sm text-muted-foreground">
                      最新 AI 模型驅動
                    </p>
                  </div>
                </CardContent>
              </Card>
              
              {/* 特色卡片 3 */}
              <Card className="bg-card/80 backdrop-blur-sm border-purple-500/20 hover:border-purple-500/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-center text-lg">即時生成</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center space-y-2">
                    <div className="text-5xl font-bold text-primary">
                      &lt; 3s
                    </div>
                    <p className="text-sm text-muted-foreground">
                      平均生成時間
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

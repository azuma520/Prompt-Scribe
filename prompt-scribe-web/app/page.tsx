import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      <div className="container mx-auto px-4 py-8 sm:py-12 md:py-16">
        <div className="max-w-4xl mx-auto text-center space-y-6 sm:space-y-8">
          {/* 標題 */}
          <div className="space-y-3 sm:space-y-4">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight">
              🎨 Prompt-Scribe
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground">
              AI 標籤推薦系統
            </p>
          </div>

          {/* 功能卡片 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mt-8 sm:mt-12">
            {/* Inspire 功能 */}
            <Link href="/inspire">
              <Card className="hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2 group-hover:text-primary transition-colors">
                    ✨ Inspire 靈感
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    AI 靈感卡生成
                    <br />
                    對話式引導創作
                  </p>
                  <div className="mt-4">
                    <Button className="w-full" size="lg">
                      開始創作 →
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </Link>

            {/* 標籤搜尋 */}
            <Link href="/tags">
              <Card className="hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2 group-hover:text-primary transition-colors">
                    🔍 標籤搜尋
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    搜尋和瀏覽標籤
                    <br />
                    140,000+ 標籤資料庫
                  </p>
                  <div className="mt-4">
                    <Button className="w-full" size="lg">
                      開始搜尋 →
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </Link>

            {/* 工作區 */}
            <Link href="/workspace">
              <Card className="hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2 group-hover:text-primary transition-colors">
                    🛠️ 工作區
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    管理和組織標籤
                    <br />
                    創建完美 Prompt
                  </p>
                  <div className="mt-4">
                    <Button className="w-full" size="lg">
                      開始工作 →
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>

          {/* 簡介 */}
          <div className="mt-12 p-6 bg-primary/5 rounded-lg">
            <p className="text-sm text-muted-foreground">
              💡 <strong>什麼是 Inspire？</strong>
              <br />
              輸入你想要的感覺或主題，AI 會為你生成結構化的靈感卡片，
              幫助你快速構建完整的 Prompt。
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

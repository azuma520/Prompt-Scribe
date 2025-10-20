import Link from 'next/link'
import { ThemeToggle } from './ThemeToggle'
import { Button } from '@/components/ui/button'

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-2xl">🎨</span>
          <span className="font-bold text-xl hidden sm:inline-block">
            Prompt-Scribe
          </span>
        </Link>

        {/* 導航連結 */}
        <nav className="hidden md:flex items-center space-x-6">
          <Link href="/tags">
            <Button variant="ghost">標籤搜尋</Button>
          </Link>
          <Link href="/inspire">
            <Button variant="ghost">Inspire 靈感</Button>
          </Link>
          <Link href="/workspace">
            <Button variant="ghost">工作區</Button>
          </Link>
        </nav>

        {/* 右側操作 */}
        <div className="flex items-center space-x-2">
          <ThemeToggle />
          
          {/* 移動端菜單按鈕 */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <span className="text-xl">☰</span>
          </Button>
        </div>
      </div>
    </header>
  )
}

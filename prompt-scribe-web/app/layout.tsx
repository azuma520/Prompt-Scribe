import type { Metadata } from 'next'
import { Noto_Sans_TC } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from '@/components/ui/sonner'
import { Header } from '@/components/shared/Header'

const notoSansTC = Noto_Sans_TC({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-noto-sans-tc',
})

export const metadata: Metadata = {
  title: {
    default: 'Prompt-Scribe - AI 標籤推薦系統',
    template: '%s | Prompt-Scribe'
  },
  description: '智能 AI 圖像生成標籤推薦工具 - Inspire 靈感生成',
  keywords: ['AI', '標籤推薦', '圖像生成', 'Prompt', '靈感生成'],
  authors: [{ name: 'Prompt-Scribe Team' }],
  creator: 'Prompt-Scribe Team',
  openGraph: {
    type: 'website',
    locale: 'zh_TW',
    url: 'https://prompt-scribe.vercel.app',
    title: 'Prompt-Scribe - AI 標籤推薦系統',
    description: '智能 AI 圖像生成標籤推薦工具',
    siteName: 'Prompt-Scribe',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Prompt-Scribe - AI 標籤推薦系統',
    description: '智能 AI 圖像生成標籤推薦工具',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-TW" suppressHydrationWarning>
      <body className={`${notoSansTC.className} antialiased`}>
        <Providers>
          <div className="relative flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}

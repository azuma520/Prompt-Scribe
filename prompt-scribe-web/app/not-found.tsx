import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">404</CardTitle>
          <CardDescription>
            找不到您要的頁面
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-muted-foreground mb-4">
            抱歉，您要尋找的頁面不存在。
          </p>
          <Button asChild>
            <Link href="/">
              返回首頁
            </Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

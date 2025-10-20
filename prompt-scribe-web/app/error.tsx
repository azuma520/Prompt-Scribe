'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Alert className="max-w-md">
        <AlertDescription className="text-center">
          <h2 className="text-lg font-semibold mb-2">出現錯誤</h2>
          <p className="text-muted-foreground mb-4">
            很抱歉，發生了未預期的錯誤。
          </p>
          <Button onClick={reset} variant="outline">
            重試
          </Button>
        </AlertDescription>
      </Alert>
    </div>
  )
}

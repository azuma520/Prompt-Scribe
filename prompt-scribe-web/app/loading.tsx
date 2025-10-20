import { Skeleton } from '@/components/ui/skeleton'

export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Skeleton className="h-8 w-8 mx-auto mb-4 rounded-full" />
        <p className="text-muted-foreground">載入中...</p>
      </div>
    </div>
  )
}

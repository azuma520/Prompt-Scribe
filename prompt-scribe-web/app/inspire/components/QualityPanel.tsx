'use client'

import { ValidationResult } from '@/types/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Shield,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Loader2,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface QualityPanelProps {
  result: ValidationResult | null
  isValidating: boolean
  onValidate: () => void
  onApplySuggestions?: () => void
}

export function QualityPanel({
  result,
  isValidating,
  onValidate,
  onApplySuggestions,
}: QualityPanelProps) {
  // 如果沒有結果且不在驗證中，顯示驗證按鈕
  if (!result && !isValidating) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary" />
            品質驗證
          </CardTitle>
          <CardDescription>
            檢查標籤組合的品質，發現衝突和冗餘
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={onValidate} className="w-full" size="lg">
            <Shield className="w-4 h-4 mr-2" />
            開始驗證
          </Button>
        </CardContent>
      </Card>
    )
  }

  // 驗證中
  if (isValidating) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary" />
            品質驗證
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <span className="ml-3 text-muted-foreground">正在檢查品質...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  // 顯示驗證結果
  if (!result) return null

  const scoreColor =
    result.overall_score >= 80
      ? 'text-green-600'
      : result.overall_score >= 60
      ? 'text-yellow-600'
      : 'text-red-600'

  const hasIssues = (result.issues?.length || 0) > 0
  const hasConflicts = (result.conflict_tags?.length || 0) > 0
  const hasRedundant = (result.redundant_tags?.length || 0) > 0
  const hasSuggestions = (result.suggestions?.length || 0) > 0

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-primary" />
              品質驗證結果
            </CardTitle>
            <CardDescription>
              整體評分：
              <span className={cn('font-bold text-lg ml-2', scoreColor)}>
                {result.overall_score}/100
              </span>
            </CardDescription>
          </div>
          {hasSuggestions && onApplySuggestions && (
            <Button onClick={onApplySuggestions} size="sm">
              <CheckCircle2 className="w-4 h-4 mr-1" />
              套用建議
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {/* 整體狀態 */}
            {result.overall_score >= 80 ? (
              <Alert>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <AlertTitle>品質良好</AlertTitle>
                <AlertDescription>
                  您的標籤組合品質很好，沒有發現明顯的問題。
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>發現問題</AlertTitle>
                <AlertDescription>
                  您的標籤組合存在一些問題，建議進行優化。
                </AlertDescription>
              </Alert>
            )}

            {/* 衝突標籤 */}
            {hasConflicts && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <h4 className="font-semibold text-sm">衝突標籤</h4>
                  <Badge variant="destructive">{result.conflict_tags!.length}</Badge>
                </div>
                <div className="space-y-2">
                  {result.conflict_tags!.map((conflict, index) => (
                    <div
                      key={index}
                      className="p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900"
                    >
                      <div className="flex flex-wrap gap-2">
                        {conflict.map((tag) => (
                          <Badge key={tag} variant="destructive">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        這些標籤可能存在語義衝突
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 冗餘標籤 */}
            {hasRedundant && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-yellow-600" />
                  <h4 className="font-semibold text-sm">冗餘標籤</h4>
                  <Badge variant="secondary">{result.redundant_tags!.length}</Badge>
                </div>
                <div className="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-900">
                  <div className="flex flex-wrap gap-2">
                    {result.redundant_tags!.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    這些標籤可能過於相似或重複
                  </p>
                </div>
              </div>
            )}

            {/* 問題列表 */}
            {hasIssues && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                  <h4 className="font-semibold text-sm">發現的問題</h4>
                  <Badge variant="outline">{result.issues!.length}</Badge>
                </div>
                <ul className="space-y-1">
                  {result.issues!.map((issue, index) => (
                    <li
                      key={index}
                      className="text-sm text-muted-foreground pl-4 border-l-2 border-orange-300"
                    >
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 優化建議 */}
            {hasSuggestions && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-blue-600" />
                  <h4 className="font-semibold text-sm">優化建議</h4>
                  <Badge variant="outline">{result.suggestions!.length}</Badge>
                </div>
                <ul className="space-y-2">
                  {result.suggestions!.map((suggestion, index) => (
                    <li
                      key={index}
                      className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 text-sm"
                    >
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* 重新驗證按鈕 */}
        <div className="mt-4 pt-4 border-t">
          <Button onClick={onValidate} variant="outline" className="w-full">
            <Shield className="w-4 h-4 mr-2" />
            重新驗證
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}


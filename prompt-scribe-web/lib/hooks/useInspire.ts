'use client'

import { useState, useCallback } from 'react'
import { RecommendedTag, RecommendTagsResponse, ValidationResult } from '@/types/api'
import { recommendTags, validatePrompt } from '@/lib/api/inspire'
import { toast } from 'sonner'

interface UseInspireOptions {
  onSuccess?: (response: RecommendTagsResponse) => void
  onError?: (error: Error) => void
}

export function useInspire(options?: UseInspireOptions) {
  const [isLoading, setIsLoading] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [recommendedTags, setRecommendedTags] = useState<RecommendedTag[]>([])
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [executionTime, setExecutionTime] = useState<number | undefined>()
  const [lastDescription, setLastDescription] = useState('')

  /**
   * 生成標籤推薦
   */
  const generate = useCallback(
    async (
      description: string,
      opts?: {
        maxTags?: number
        minPopularity?: number
        excludeAdult?: boolean
      }
    ) => {
      if (!description.trim()) {
        toast.error('請輸入描述')
        return
      }

      setIsLoading(true)
      setLastDescription(description)
      setValidationResult(null) // 清空之前的驗證結果

      try {
               const response = await recommendTags(description, {
                 maxTags: opts?.maxTags,
                 min_popularity: opts?.minPopularity || 100,
                 exclude_adult: opts?.excludeAdult,
               })

        setRecommendedTags(response.recommended_tags)
        setExecutionTime(response.metadata.processing_time_ms / 1000) // 轉換為秒

        toast.success(`成功生成 ${response.recommended_tags.length} 個標籤建議`)

        options?.onSuccess?.(response)
      } catch (error) {
        console.error('Generate tags error:', error)
        toast.error(error instanceof Error ? error.message : '生成失敗，請重試')
        options?.onError?.(error as Error)
      } finally {
        setIsLoading(false)
      }
    },
    [options]
  )

  /**
   * 驗證標籤品質
   */
  const validate = useCallback(async (tags: string[]) => {
    if (tags.length === 0) {
      toast.error('請先選擇標籤')
      return
    }

    setIsValidating(true)

    try {
      const result = await validatePrompt(tags)
      setValidationResult(result)

      if (result.overall_score >= 80) {
        toast.success('品質驗證通過！')
      } else if (result.overall_score >= 60) {
        toast.warning('發現一些問題，建議優化')
      } else {
        toast.error('品質較差，建議重新調整')
      }
    } catch (error) {
      console.error('Validate prompt error:', error)
      toast.error(error instanceof Error ? error.message : '驗證失敗，請重試')
    } finally {
      setIsValidating(false)
    }
  }, [])

  /**
   * 清空結果
   */
  const clear = useCallback(() => {
    setRecommendedTags([])
    setValidationResult(null)
    setExecutionTime(undefined)
    setLastDescription('')
  }, [])

  /**
   * 重新生成（使用上次的描述）
   */
  const regenerate = useCallback(
    async (opts?: {
      maxTags?: number
      minPopularity?: number
      excludeAdult?: boolean
    }) => {
      if (!lastDescription) {
        toast.error('沒有可重新生成的描述')
        return
      }

      await generate(lastDescription, opts)
    },
    [lastDescription, generate]
  )

  return {
    // 狀態
    isLoading,
    isValidating,
    recommendedTags,
    validationResult,
    executionTime,
    lastDescription,

    // 方法
    generate,
    validate,
    clear,
    regenerate,
  }
}


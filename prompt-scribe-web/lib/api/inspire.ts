import { RecommendTagsRequest, RecommendTagsResponse, ValidationResult } from '@/types/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://prompt-scribe-api.zeabur.app'

/**
 * 智能標籤推薦
 * @param description 使用者描述
 * @param options 可選參數
 * @returns 推薦標籤列表
 */
export async function recommendTags(
  description: string,
  options?: {
    maxTags?: number
    min_popularity?: number
    exclude_adult?: boolean
  }
): Promise<RecommendTagsResponse> {
  try {
    const request: RecommendTagsRequest = {
      description,
      max_tags: options?.maxTags || 20,
      min_popularity: options?.min_popularity || 100,
      exclude_adult: options?.exclude_adult !== undefined ? options.exclude_adult : true
    }

    console.log('Recommending tags:', request)

    const response = await fetch(`${API_BASE_URL}/api/llm/recommend-tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Recommend tags error:', response.status, errorText)
      throw new Error(`推薦標籤失敗: ${response.status}`)
    }

    const result = await response.json()
    console.log('Recommended tags response:', result)
    console.log('Recommended tags count:', result.recommended_tags?.length || 0)
    console.log('Full response structure:', JSON.stringify(result, null, 2))

    return result
  } catch (error) {
    console.error('Error recommending tags:', error)
    throw error
  }
}

/**
 * 驗證 Prompt 品質
 * @param tags 標籤列表
 * @returns 驗證結果（衝突、冗餘、建議）
 */
export async function validatePrompt(tags: string[]): Promise<ValidationResult> {
  try {
    console.log('Validating prompt:', tags)

    const response = await fetch(`${API_BASE_URL}/api/llm/validate-prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ tags }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Validate prompt error:', response.status, errorText)
      throw new Error(`驗證 Prompt 失敗: ${response.status}`)
    }

    const result = await response.json()
    console.log('Validation result:', result)

    return result
  } catch (error) {
    console.error('Error validating prompt:', error)
    throw error
  }
}

/**
 * 格式化標籤為 Prompt
 * @param tags 標籤列表
 * @param options 格式化選項
 * @returns 格式化後的 Prompt 字串
 */
export function formatPrompt(
  tags: string[],
  options?: {
    weighted?: boolean
    separator?: string
    weights?: Record<string, number>
  }
): string {
  const separator = options?.separator || ', '

  if (options?.weighted && options?.weights) {
    // 權重版本: (tag:weight)
    return tags
      .map(tag => {
        const weight = options.weights![tag] || 1.0
        return weight !== 1.0 ? `(${tag}:${weight.toFixed(1)})` : tag
      })
      .join(separator)
  }

  // 簡潔版本: tag1, tag2, tag3
  return tags.join(separator)
}

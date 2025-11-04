import { Tag, TagsResponse } from '@/types/api'
import { mockTags } from './mockTags'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://prompt-scribe-api.zeabur.app'
const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true'
const MAX_API_LIMIT = 100 // API 限制最大值

// 處理標籤，添加 category 顯示欄位
function processTag(tag: Tag): Tag {
  return {
    ...tag,
    category: tag.sub_category || tag.main_category || 'OTHER'
  }
}

// 確保 limit 不超過 API 限制
function validateLimit(limit: number): number {
  return Math.min(Math.max(1, limit), MAX_API_LIMIT)
}

export async function getTags(limit: number = 100): Promise<Tag[]> {
  // 驗證並限制 limit 參數
  const validLimit = validateLimit(limit)
  
  // 如果啟用模擬資料模式，直接返回模擬資料
  if (USE_MOCK_DATA) {
    console.log('Using mock data')
    return mockTags.slice(0, validLimit)
  }

  try {
    console.log(`Fetching tags from: ${API_BASE_URL}/api/v1/tags?limit=${validLimit}`)
    
    const response = await fetch(`${API_BASE_URL}/api/v1/tags?limit=${validLimit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      // 移除 cache 設定，讓瀏覽器處理快取
    })
    
    console.log('Response status:', response.status)
    console.log('Response headers:', Object.fromEntries(response.headers.entries()))
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('API Error:', response.status, errorText)
      throw new Error(`API Error: ${response.status} ${errorText}`)
    }
    
    const result: TagsResponse = await response.json()
    console.log('Fetched tags count:', result.data.length, 'Total:', result.total)
    
    return result.data.map(processTag)
  } catch (error) {
    console.error('Error fetching tags:', error)
    // 拋出錯誤，讓調用者決定如何處理
    throw error
  }
}

export async function searchTags(query: string): Promise<Tag[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ keywords: [query] }),
      cache: 'no-store' // 動態搜尋不快取
    })
    
    if (!response.ok) {
      throw new Error('Failed to search tags')
    }
    
    const result: TagsResponse = await response.json()
    return result.data.map(processTag)
  } catch (error) {
    console.error('Error searching tags:', error)
    return []
  }
}

export async function getPopularTags(limit: number = 20): Promise<Tag[]> {
  const validLimit = validateLimit(limit)
  
  try {
    // API 預設就是按 post_count 排序
    const response = await fetch(`${API_BASE_URL}/api/v1/tags?limit=${validLimit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to fetch popular tags: ${response.status} ${errorText}`)
    }
    
    const result: TagsResponse = await response.json()
    return result.data.map(processTag)
  } catch (error) {
    console.error('Error fetching popular tags:', error)
    throw error
  }
}

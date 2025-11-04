'use client'

import { useState, useEffect, useCallback } from 'react'
import { Tag } from '@/types/api'

const STORAGE_KEY = 'workspace-tags'

export function useWorkspace() {
  const [tags, setTags] = useState<Tag[]>([])

  // 從 localStorage 載入
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        setTags(JSON.parse(stored))
      }
    } catch (error) {
      console.error('Failed to load workspace:', error)
    }
  }, [])

  // 儲存到 localStorage
  const saveTags = useCallback((newTags: Tag[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newTags))
    } catch (error) {
      console.error('Failed to save workspace:', error)
    }
  }, [])

  // 添加標籤
  const addTag = useCallback((tag: Tag) => {
    setTags((prev) => {
      // 避免重複
      if (prev.find(t => t.id === tag.id)) {
        return prev
      }
      const newTags = [...prev, tag]
      saveTags(newTags)
      return newTags
    })
  }, [saveTags])

  // 批量添加標籤
  const addTags = useCallback((newTags: Tag[]) => {
    setTags((prev) => {
      const existingIds = new Set(prev.map(t => t.id))
      const uniqueNewTags = newTags.filter(t => !existingIds.has(t.id))
      const allTags = [...prev, ...uniqueNewTags]
      saveTags(allTags)
      return allTags
    })
  }, [saveTags])

  // 移除標籤
  const removeTag = useCallback((tagId: string) => {
    setTags((prev) => {
      const newTags = prev.filter(t => t.id !== tagId)
      saveTags(newTags)
      return newTags
    })
  }, [saveTags])

  // 清空所有標籤
  const clearAll = useCallback(() => {
    setTags([])
    saveTags([])
  }, [saveTags])

  // 重新排序
  const reorderTags = useCallback((startIndex: number, endIndex: number) => {
    setTags((prev) => {
      const result = Array.from(prev)
      const [removed] = result.splice(startIndex, 1)
      result.splice(endIndex, 0, removed)
      saveTags(result)
      return result
    })
  }, [saveTags])

  // 格式化為 Prompt
  const formatPrompt = useCallback(() => {
    return tags.map(t => t.name).join(', ')
  }, [tags])

  // 複製到剪貼簿
  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(formatPrompt())
      return true
    } catch (error) {
      console.error('Failed to copy:', error)
      return false
    }
  }, [formatPrompt])

  return {
    tags,
    addTag,
    addTags,
    removeTag,
    clearAll,
    reorderTags,
    formatPrompt,
    copyToClipboard,
  }
}

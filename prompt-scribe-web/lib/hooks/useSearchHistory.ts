'use client'

import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'tag-search-history'
const MAX_HISTORY = 10

export function useSearchHistory() {
  const [history, setHistory] = useState<string[]>([])

  // 從 localStorage 載入歷史
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        setHistory(JSON.parse(stored))
      }
    } catch (error) {
      console.error('Failed to load search history:', error)
    }
  }, [])

  // 添加搜尋記錄
  const addToHistory = useCallback((query: string) => {
    const trimmed = query.trim()
    if (!trimmed) return

    setHistory((prev) => {
      // 移除重複並添加到開頭
      const filtered = prev.filter(item => item !== trimmed)
      const newHistory = [trimmed, ...filtered].slice(0, MAX_HISTORY)
      
      // 儲存到 localStorage
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory))
      } catch (error) {
        console.error('Failed to save search history:', error)
      }
      
      return newHistory
    })
  }, [])

  // 清除歷史
  const clearHistory = useCallback(() => {
    setHistory([])
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch (error) {
      console.error('Failed to clear search history:', error)
    }
  }, [])

  // 移除單個記錄
  const removeFromHistory = useCallback((query: string) => {
    setHistory((prev) => {
      const newHistory = prev.filter(item => item !== query)
      
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory))
      } catch (error) {
        console.error('Failed to update search history:', error)
      }
      
      return newHistory
    })
  }, [])

  return {
    history,
    addToHistory,
    clearHistory,
    removeFromHistory,
  }
}

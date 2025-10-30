import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SearchHistoryState {
  history: string[]
  addToHistory: (query: string) => void
}

export const useSearchHistory = create<SearchHistoryState>()(
  persist(
    (set) => ({
      history: [],
      addToHistory: (query) =>
        set((state) => {
          const newHistory = [query, ...state.history.filter((item) => item !== query)]
          return { history: newHistory.slice(0, 10) } // 只保留最近 10 筆紀錄
        }),
    }),
    {
      name: 'prompt-scribe-search-history',
    }
  )
)

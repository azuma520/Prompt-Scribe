import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Tag } from '@/types/api'

interface WorkspaceState {
  tags: Tag[]
  addTag: (tag: Tag) => void
  removeTag: (tagId: string) => void
  clearAll: () => void
  formatPrompt: () => string
  copyToClipboard: () => Promise<boolean>
}

export const useWorkspace = create<WorkspaceState>()(
  persist(
    (set, get) => ({
      tags: [],
      addTag: (tag) =>
        set((state) => {
          if (state.tags.some((t) => t.id === tag.id)) {
            return state // 避免重複加入
          }
          return { tags: [...state.tags, tag] }
        }),
      removeTag: (tagId) =>
        set((state) => ({
          tags: state.tags.filter((t) => t.id !== tagId),
        })),
      clearAll: () => set({ tags: [] }),
      formatPrompt: () => {
        const { tags } = get()
        return tags.map((tag) => tag.name).join(', ')
      },
      copyToClipboard: async () => {
        const prompt = get().formatPrompt()
        if (!prompt) return false
        try {
          await navigator.clipboard.writeText(prompt)
          return true
        } catch (error) {
          console.error('Failed to copy to clipboard:', error)
          return false
        }
      },
    }),
    {
      name: 'prompt-scribe-workspace', // local storage 中的 key
    }
  )
)

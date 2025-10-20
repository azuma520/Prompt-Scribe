'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/shared/ThemeProvider'
import { queryClient } from '@/lib/api/client'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ThemeProvider>
  )
}


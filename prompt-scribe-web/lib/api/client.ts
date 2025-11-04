// /lib/api/client.ts
import { QueryClient } from "@tanstack/react-query";

/**
 * 單例 QueryClient（避免每次 render 重新建立）
 * - CSR：全域單例
 * - SSR/RSC：通常在 Provider 包一層就好，你現有 providers.tsx 直接吃這個即可
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,   // 30s
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});


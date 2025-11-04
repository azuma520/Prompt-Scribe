// Inspire 功能 Hook

'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { v4 as uuidv4 } from 'uuid';
import type {
  InspirationCard,
  InspireState,
  InspirationSession,
} from '@/types/inspire';
import { generateInspirationCards } from '@/lib/api/inspire';

export function useInspiration() {
  const [state, setState] = useState<InspireState>('idle');
  const [session, setSession] = useState<InspirationSession | null>(null);
  const [cards, setCards] = useState<InspirationCard[]>([]);
  const [selectedCard, setSelectedCard] = useState<InspirationCard | null>(
    null
  );
  const [finalResult, setFinalResult] = useState<InspirationCard | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 生成靈感卡
  const generateMutation = useMutation({
    mutationFn: async (input: string) => {
      // 清除之前的錯誤訊息
      setErrorMessage(null);
      
      const sessionId = session?.session_id || uuidv4();

      const response = await generateInspirationCards(input, sessionId);

      return { response, sessionId };
    },
    onMutate: () => {
      setState('generating');
      setErrorMessage(null);
    },
    onSuccess: ({ response, sessionId }) => {
      setCards(response.cards);
      setState('showing');
      setErrorMessage(null);

      // 創建或更新 session
      if (!session) {
        setSession({
          session_id: sessionId,
          created_at: new Date().toISOString(),
          mode: response.mode,
          current_round: response.round,
          cards: response.cards,
        });
      }
    },
    onError: error => {
      console.error('生成失敗:', error);
      setState('idle');
      
      // 設置友善的錯誤訊息
      const message = error instanceof Error ? error.message : '生成失敗，請稍後再試';
      setErrorMessage(message);
    },
  });

  // 選擇卡片
  const selectCard = (card: InspirationCard) => {
    setSelectedCard(card);
    setFinalResult(card);
    setState('finalized');
  };

  // 重置
  const reset = () => {
    setState('idle');
    setCards([]);
    setSelectedCard(null);
    setFinalResult(null);
    setSession(null);
    setErrorMessage(null);
  };

  return {
    state,
    session,
    cards,
    selectedCard,
    finalResult,
    errorMessage,

    // Actions
    generateCards: (input: string) => generateMutation.mutate(input),
    selectCard,
    reset,

    // Mutation 狀態
    isGenerating: generateMutation.isPending,
    error: generateMutation.error,
  };
}


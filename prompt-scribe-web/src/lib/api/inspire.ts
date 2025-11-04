// Inspire API 客戶端

import { API_BASE_URL } from './client';
import { getNetworkErrorMessage } from '@/lib/utils/network';
import type {
  InspirationCard,
  InspireGenerateRequest,
  InspireGenerateResponse,
  InspireFeedbackRequest,
  InspireFeedbackResponse,
} from '@/types/inspire';
import type { RecommendTagsResponse } from '@/types/api';

/**
 * 生成靈感卡（MVP 版本）
 * 複用現有的推薦 API，然後組合成靈感卡格式
 */
export async function generateInspirationCards(
  input: string,
  sessionId: string
): Promise<InspireGenerateResponse> {
  try {
    console.log('生成靈感卡，輸入:', input, 'Session ID:', sessionId);
    console.log('API URL:', `${API_BASE_URL}/api/llm/recommend-tags`);
    
    // 調用真實的 Zeabur API
    const response = await fetch(`${API_BASE_URL}/api/llm/recommend-tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: input }),
    });

    if (!response.ok) {
      // 提供更詳細的錯誤訊息
      const errorText = await response.text();
      throw new Error(`API 請求失敗 (${response.status}): ${errorText || '請檢查網路連接'}`);
    }

    const data: RecommendTagsResponse = await response.json();

  // 檢查是否有推薦標籤，如果沒有則使用備用方案
  if (!data.recommended_tags || data.recommended_tags.length === 0) {
    console.log('API 返回空結果，使用備用方案');
    const cards = generateFallbackCards(input);
    return {
      mode: detectMode(input),
      round: 1,
      cards,
      suggestions: ['API 暫時無結果，已使用備用方案', '建議稍後再試或重新輸入'],
    };
  }

  // 將推薦標籤轉換為靈感卡格式
  // MVP: 簡化版本，使用固定模板
  const cards = await buildInspirationCardsFromTags(
    input,
    data.recommended_tags
  );

    return {
      mode: detectMode(input),
      round: 1,
      cards,
      suggestions: ['選擇一張你最喜歡的卡片', '或重新輸入其他描述'],
    };
  } catch (error) {
    console.error('生成靈感卡時發生錯誤:', error);
    
    // 使用網路錯誤處理工具
    const errorMessage = getNetworkErrorMessage(error);
    throw new Error(errorMessage);
  }
}

/**
 * 從推薦標籤構建靈感卡
 * MVP 版本：簡單的組合邏輯
 */
async function buildInspirationCardsFromTags(
  input: string,
  recommendedTags: Array<{ tag: string; confidence: number; category?: string }>
): Promise<InspirationCard[]> {
  // 檢查是否有推薦標籤
  if (!recommendedTags || recommendedTags.length === 0) {
    // 如果沒有推薦標籤，使用輸入內容生成基本卡片
    return generateFallbackCards(input);
  }

  // 分類標籤 - 支援中英文
  const sceneKeywords = ['forest', 'city', 'street', 'room', 'outdoor', 'woods', 'urban', 'nature', '室內', '室外', '城市', '森林', '街道'];
  const styleKeywords = ['cinematic', 'anime', 'realistic', 'dreamy', 'artistic', 'dramatic', '電影', '動漫', '現實', '夢幻', '藝術'];
  const characterKeywords = ['girl', 'boy', 'solo', 'person', 'character', '人', '女孩', '男孩', '角色'];

  const sceneTags = recommendedTags
    .filter(t => t.category?.includes('SCENE') || 
                 sceneKeywords.some(keyword => t.tag.toLowerCase().includes(keyword.toLowerCase())))
    .slice(0, 3);

  const styleTags = recommendedTags
    .filter(t => t.category?.includes('STYLE') || 
                 styleKeywords.some(keyword => t.tag.toLowerCase().includes(keyword.toLowerCase())))
    .slice(0, 3);

  const characterTags = recommendedTags
    .filter(t => characterKeywords.some(keyword => t.tag.toLowerCase().includes(keyword.toLowerCase())))
    .slice(0, 2);

  // 生成 3 張卡片（簡化版本）
  const cards: InspirationCard[] = [
    {
      subject: characterTags[0]?.tag || 'lone figure',
      scene: sceneTags[0]?.tag || 'peaceful place',
      style: styleTags[0]?.tag || 'cinematic',
      source_tags: recommendedTags.slice(0, 5).map(t => t.tag),
      confidence_score: recommendedTags[0]?.confidence || 0.8,
    },
    {
      subject: characterTags[1]?.tag || 'silhouette',
      scene: sceneTags[1]?.tag || 'urban setting',
      style: styleTags[1]?.tag || 'dramatic',
      source_tags: recommendedTags.slice(5, 10).map(t => t.tag),
      confidence_score: recommendedTags[1]?.confidence || 0.75,
    },
    {
      subject: 'mysterious character',
      scene: sceneTags[2]?.tag || 'atmospheric location',
      style: styleTags[2]?.tag || 'artistic',
      source_tags: recommendedTags.slice(10, 15).map(t => t.tag),
      confidence_score: recommendedTags[2]?.confidence || 0.7,
    },
  ];

  return cards;
}

/**
 * 提取關鍵字
 */
function extractKeywords(input: string): string[] {
  // 簡單的關鍵字提取：按空格和標點符號分割
  const words = input
    .toLowerCase()
    .replace(/[，。！？、；：""''（）【】]/g, ' ') // 移除中文標點
    .replace(/[,.!?;:""''()[\]{}]/g, ' ') // 移除英文標點
    .split(/\s+/)
    .filter(word => word.length > 0);
  
  return words;
}

/**
 * 備用卡片生成（當 API 沒有返回標籤時）
 */
function generateFallbackCards(input: string): InspirationCard[] {
  const lowerInput = input.toLowerCase();
  
  // 智能標籤映射（基於常見詞彙）
  const tagMappings: Record<string, string[]> = {
    // 情緒相關
    '孤獨': ['lonely', 'alone', 'solitary', 'isolated'],
    '夢幻': ['dreamy', 'ethereal', 'mystical', 'fantasy'],
    '憂鬱': ['melancholy', 'sad', 'blue', 'moody'],
    '浪漫': ['romantic', 'intimate', 'passionate', 'loving'],
    '神秘': ['mysterious', 'enigmatic', 'secretive', 'hidden'],
    
    // 場景相關
    '森林': ['forest', 'woods', 'trees', 'nature'],
    '城市': ['urban', 'city', 'street', 'metropolitan'],
    '海邊': ['beach', 'ocean', 'seaside', 'coastal'],
    '山': ['mountain', 'peak', 'summit', 'alpine'],
    '雨': ['rain', 'rainy', 'stormy', 'wet'],
    
    // 風格相關
    '電影': ['cinematic', 'film', 'movie', 'dramatic'],
    '藝術': ['artistic', 'creative', 'aesthetic', 'artistic'],
    '復古': ['vintage', 'retro', 'classic', 'old'],
    '現代': ['modern', 'contemporary', 'current', 'present'],
  };
  
  // 提取關鍵字並擴展
  const keywords = extractKeywords(input);
  const expandedTags = new Set<string>();
  keywords.forEach(keyword => {
    expandedTags.add(keyword);
    // 添加映射標籤
    if (tagMappings[keyword]) {
      tagMappings[keyword].forEach(tag => expandedTags.add(tag));
    }
  });
  
  const finalTags = Array.from(expandedTags);
  const mode = detectMode(input);
  
  // 根據模式生成不同的卡片
  if (mode === 'emotion') {
    return [
      {
        subject: `${keywords.join(' ')} character, emotional expression`,
        scene: 'atmospheric environment with depth',
        lighting: 'mood lighting, soft shadows',
        style: 'dreamy, artistic, emotional',
        source_tags: finalTags,
        confidence_score: 0.8,
      },
      {
        subject: `${keywords.join(' ')} figure, contemplative pose`,
        scene: 'ethereal landscape, misty atmosphere',
        lighting: 'soft, natural light, gentle glow',
        style: 'cinematic, emotional, expressive',
        source_tags: finalTags,
        confidence_score: 0.7,
      },
      {
        subject: `${keywords.join(' ')} portrait, intimate moment`,
        scene: 'abstract background, flowing elements',
        lighting: 'dramatic shadows, contrast lighting',
        style: 'artistic, expressive, soulful',
        source_tags: finalTags,
        confidence_score: 0.6,
      },
    ];
  } else {
    return [
      {
        subject: `${keywords.join(' ')} scene, detailed composition`,
        scene: 'detailed environment, rich textures',
        lighting: 'professional lighting, balanced exposure',
        style: 'high quality, detailed, realistic',
        source_tags: finalTags,
        confidence_score: 0.8,
      },
      {
        subject: `${keywords.join(' ')} composition, dynamic elements`,
        scene: 'stylized setting, creative arrangement',
        lighting: 'balanced lighting, multiple sources',
        style: 'well composed, artistic, balanced',
        source_tags: finalTags,
        confidence_score: 0.7,
      },
      {
        subject: `${keywords.join(' ')} concept, imaginative design`,
        scene: 'creative environment, unique perspective',
        lighting: 'dynamic lighting, dramatic effects',
        style: 'creative, imaginative, innovative',
        source_tags: finalTags,
        confidence_score: 0.6,
      },
    ];
  }
}

/**
 * 檢測輸入模式（情緒 vs 主題）
 */
function detectMode(input: string): 'emotion' | 'theme' {
  const emotionKeywords = ['感覺', '情緒', '氛圍', 'feeling', 'mood', '孤獨', '夢幻'];
  const hasEmotion = emotionKeywords.some(keyword =>
    input.toLowerCase().includes(keyword.toLowerCase())
  );

  return hasEmotion ? 'emotion' : 'theme';
}

/**
 * 提交反饋（MVP: 暫時返回模擬資料）
 */
export async function submitFeedback(
  request: InspireFeedbackRequest
): Promise<InspireFeedbackResponse> {
  // MVP: 暫時不實作，返回成功狀態
  return {
    status: 'success',
    message: 'MVP 版本暫不支援反饋功能，請重新生成',
  };
}


import { nanoid } from "nanoid";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  type?: string;
  raw?: unknown;
};

/**
 * 將後端 API 響應正規化為標準的 ChatMessage 格式
 * 處理 ResponseOutputText 對象和各種數據格式
 */
export function adaptResponseToMessages(resp: any): ChatMessage[] {
  if (!resp) return [];
  
  // 處理 message 字段
  const messageData = resp.message;
  if (!messageData) return [];
  
  // 如果是數組格式（ResponseOutputText 對象）
  if (Array.isArray(messageData)) {
    return messageData.map((it: any) => ({
      id: it?.id ?? nanoid(),
      role: "assistant" as const,
      type: it?.type ?? "output_text",
      content: extractTextContent(it),
      raw: it,
    }));
  }
  
  // 如果是字符串格式
  if (typeof messageData === "string") {
    return [{
      id: nanoid(),
      role: "assistant" as const,
      type: "text",
      content: messageData,
      raw: messageData,
    }];
  }
  
  // 其他格式，嘗試提取文本內容
  return [{
    id: nanoid(),
    role: "assistant" as const,
    type: "unknown",
    content: extractTextContent(messageData),
    raw: messageData,
  }];
}

/**
 * 從各種對象格式中提取文本內容
 */
function extractTextContent(item: any): string {
  if (!item) return "";
  
  // 如果是 ResponseOutputText 對象
  if (typeof item === "object" && item.text !== undefined) {
    return String(item.text || "");
  }
  
  // 如果有 content 字段
  if (typeof item === "object" && item.content !== undefined) {
    return String(item.content || "");
  }
  
  // 如果是字符串
  if (typeof item === "string") {
    return item;
  }
  
  // 其他情況，轉為字符串
  return String(item);
}

/**
 * 適配 directions 數據
 */
export function adaptDirections(directions: any[]): any[] {
  if (!Array.isArray(directions)) return [];
  
  return directions.map((direction, index) => ({
    id: direction?.id ?? `direction-${index}`,
    title: direction?.title ?? `方向 ${index + 1}`,
    concept: direction?.concept ?? "",
    vibe: direction?.vibe ?? "",
    main_tags: direction?.main_tags ?? [],
    quick_preview: direction?.quick_preview ?? "",
    uniqueness: direction?.uniqueness ?? "",
    ...direction, // 保留原始數據
  }));
}






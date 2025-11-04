// 網路連接檢查工具

/**
 * 檢查網路連接狀態
 */
export async function checkNetworkConnection(): Promise<boolean> {
  try {
    // 嘗試請求一個小的資源來檢查網路
    const response = await fetch('https://www.google.com/favicon.ico', {
      method: 'HEAD',
      mode: 'no-cors',
      cache: 'no-cache',
    });
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * 檢查 API 端點是否可用
 */
export async function checkApiEndpoint(baseUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${baseUrl}/health`, {
      method: 'GET',
      cache: 'no-cache',
    });
    return response.ok;
  } catch (error) {
    // 如果沒有 health 端點，嘗試主端點
    try {
      const response = await fetch(baseUrl, {
        method: 'HEAD',
        cache: 'no-cache',
      });
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * 獲取網路錯誤訊息
 */
export function getNetworkErrorMessage(error: unknown): string {
  if (error instanceof TypeError) {
    if (error.message.includes('fetch')) {
      return '網路連接失敗，請檢查網路連接';
    }
    if (error.message.includes('Failed to fetch')) {
      return '無法連接到伺服器，請稍後再試';
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return '未知錯誤，請稍後再試';
}

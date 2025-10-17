// API 相關型別定義

export interface Tag {
  id: string;
  name: string;
  danbooru_cat: number;
  post_count: number;
  main_category: string | null;
  sub_category: string | null;
  confidence: number | null;
  classification_source: string | null;
}

export interface RecommendTagsRequest {
  description: string;
  top_k?: number;
}

export interface RecommendTagsResponse {
  recommended_tags: Array<{
    tag: string;
    confidence: number;
    category?: string;
  }>;
  description: string;
  execution_time: number;
}

export interface ValidationResult {
  overall_score: number;
  issues: string[];
  suggestions: string[];
  conflict_tags?: string[][];
  redundant_tags?: string[];
}

export interface TagCombination {
  theme: string;
  basic: string;
  extended: string;
  popularity: string;
}


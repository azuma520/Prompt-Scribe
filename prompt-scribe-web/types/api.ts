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
  // 計算屬性
  category?: string; // 用於顯示的分類（從 main_category 或 sub_category 計算）
}

export interface TagsResponse {
  data: Tag[];
  total: number;
  limit: number;
  offset: number;
}

export interface RecommendTagsRequest {
  description: string;
  max_tags?: number;
  min_popularity?: number;
  exclude_adult?: boolean;
}

export interface RecommendedTag {
  tag: string;
  confidence: number;
  popularity_tier: string;
  post_count: number;
  category: string;
  subcategory?: string;
  match_reason: string;
  usage_context: string;
  weight: number;
  related_tags: string[];
}

export interface RecommendTagsResponse {
  query: string;
  recommended_tags: RecommendedTag[];
  category_distribution: Record<string, number>;
  quality_assessment: {
    overall_score: number;
    warnings: string[];
    suggestions: string[];
  };
  suggested_prompt: string;
  metadata: {
    processing_time_ms: number;
    total_candidates: number;
    algorithm: string;
    cache_hit: boolean;
    keywords_extracted?: string[];
    keywords_expanded?: string[];
  };
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


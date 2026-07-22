export type Video = {
  id: string;
  title: string;
  filename: string;
  status: string;
  created_at: string;
};

export type Simulation = {
  id: string;
  video_id: string;
  target_audience: string;
  persona_count: number;
  round_count: number;
  status: string;
  progress_stage: string;
  error_message: string | null;
  transcript_ai_source: AiSource;
  content_analysis_ai_source: AiSource;
  personas_ai_source: AiSource;
  reasons_ai_source: AiSource;
  virality_score: number | null;
  predicted_reach: number | null;
  like_rate: number | null;
  comment_rate: number | null;
  share_rate: number | null;
  cascade_depth: number | null;
  final_verdict: string | null;
  created_at: string;
};

export type AiSource =
  | "real"
  | "real_gemini"
  | "real_anthropic"
  | "real_openrouter"
  | "real_multimodal"
  | "real_text_only"
  | "real_gemini_mm"
  | "real_gemini_text"
  | "real_anthropic_mm"
  | "real_anthropic_text"
  | "real_openrouter_mm"
  | "real_openrouter_text"
  | "fallback";

export type GraphNode = {
  id: string;
  label: string;
  in_target: boolean;
  status: string;
  action: string;
  round: number | null;
  x?: number | null;
  y?: number | null;
};

export type GraphEdge = {
  id: string;
  source: string | null;
  target: string;
  type: string;
  weight: number;
};

export type PersonaDetail = {
  id: string;
  name: string;
  age: number;
  location: string;
  profession: string;
  interests: string[];
  pain_points: string[];
  content_preferences: string[];
  engagement_tendency: number;
  share_probability: number;
  skepticism_level: number;
  in_target: boolean;
  action: string;
  reason: string;
  round: number | null;
};

export type Round = {
  id: string;
  round_number: number;
  active_agents: number;
  new_reach: number;
  likes: number;
  comments: number;
  shares: number;
};

export type Report = {
  summary: string;
  improvement_suggestions: string[];
  best_audience_segments: string[];
  risk_factors: string[];
  ml_verdict_prediction: string | null;
  visual_description: string | null;
} | null;

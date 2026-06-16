export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Profile {
  id: string;
  user_id: string;
  first_name: string | null;
  last_name: string | null;
  title: string | null;
  bio: string | null;
  experience_years: number | null;
}

export interface ParsedData {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  education: string[];
  experience: string[];
}

export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  raw_text: string | null;
  parsed_data: ParsedData | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface SkillGap {
  matched_skills: string[];
  missing_skills: string[];
  match_percentage: number;
  user_skills_count: number;
  target_skills_count: number;
  focus_areas: Record<string, string[]>;
  strengths: string[];
  weaknesses: string[];
  learning_priorities: string[];
  reasoning: string;
}

export interface RoadmapTask {
  id: string;
  roadmap_id: string;
  title: string;
  description: string | null;
  sequence: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  target_role: string;
  tasks: RoadmapTask[];
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  messages: ChatMessage[];
}

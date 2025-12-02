// lib/types.ts
export interface Candidate {
  id: string;
  role: string;
  score: number;
  location: string;
  years_experience: number;
  languages: string;
  skills: string;
}

export interface QueryRequest {
  text: string;
}

export interface QueryResponse {
  candidates: Candidate[];
}
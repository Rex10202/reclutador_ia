// lib/types.ts

// ==================== MÓDULO 1: Análisis de CVs ====================

/** Documento PDF subido por la reclutadora */
export interface UploadedDocument {
  id: string;
  fileName: string;
  fileSize: number;
  uploadedAt: Date;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  errorMessage?: string;
}

/** Atributos extraídos de un CV mediante OCR/NLP */
export interface ExtractedAttributes {
  candidateName: string;
  email?: string;
  phone?: string;
  location?: string;
  role: string;
  yearsExperience: number;
  skills: string[];
  languages: string[];
  education: string[];
  certifications: string[];
  summary?: string;
}

/** Requisitos del puesto especificados por la reclutadora */
export interface JobRequirements {
  title: string;
  description?: string;
  requiredSkills: string[];
  preferredSkills: string[];
  minExperience: number;
  maxExperience?: number;
  location?: string;
  languages?: string[];
  education?: string[];
}

/** Filtros de insight seleccionados por la reclutadora */
export interface InsightFilters {
  prioritizeExperience: boolean;
  prioritizeSkills: boolean;
  prioritizeLocation: boolean;
  prioritizeLanguages: boolean;
  prioritizeEducation: boolean;
  prioritizeCertifications: boolean;
}

/** Resultado de comparación de un CV contra los requisitos */
export interface ComparisonResult {
  documentId: string;
  candidateName: string;
  attributes: ExtractedAttributes;
  overallScore: number; // 0-100
  matchBreakdown: {
    skillsMatch: number;
    experienceMatch: number;
    locationMatch: number;
    languagesMatch: number;
    educationMatch: number;
  };
  matchedSkills: string[];
  missingSkills: string[];
  highlights: string[];
  concerns: string[];
}

/** Resumen estadístico del talento analizado */
export interface TalentSummary {
  totalCandidates: number;
  matchesByRole: number;
  averageExperience: number;
  topSkills: { skill: string; count: number }[];
  locationDistribution: { location: string; count: number }[];
}

/** Candidato con datos de CV analizado */
export interface Candidate {
  id: string;
  documentId?: string;
  name?: string;
  role: string;
  score: number;
  location: string;
  years_experience: number;
  languages: string;
  skills: string;
  matchBreakdown?: ComparisonResult['matchBreakdown'];
}

// ==================== MÓDULO 2: Búsqueda por Lenguaje Natural ====================

export interface QueryRequest {
  text: string;
}

export interface QueryResponse {
  candidates: Candidate[];
}

// ==================== API Requests/Responses ====================

export interface DocumentUploadRequest {
  files: File[];
}

export interface DocumentUploadResponse {
  documents: UploadedDocument[];
}

export interface AnalyzeDocumentsRequest {
  documentIds: string[];
  jobRequirements: JobRequirements;
  filters: InsightFilters;
}

export interface AnalyzeDocumentsResponse {
  results: ComparisonResult[];
  summary: TalentSummary;
}
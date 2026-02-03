// lib/api.ts
import { 
  QueryRequest, 
  QueryResponse,
  AnalyzeDocumentsRequest,
  AnalyzeDocumentsResponse,
  UploadedDocument,
  CVAnalysisResponse,
  JobRequirements,
  InsightFilters
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

function extractErrorMessage(payload: any, fallback: string): string {
  if (!payload) return fallback;

  if (typeof payload === 'string') return payload;

  // FastAPI default
  if (typeof payload.detail === 'string') return payload.detail;
  // FastAPI detail may be an object/list
  if (payload.detail && typeof payload.detail.message === 'string') return payload.detail.message;
  if (payload.detail && typeof payload.detail.error === 'string') return payload.detail.error;

  // Our ErrorResponse shape: { error: { message } }
  if (payload.error && typeof payload.error.message === 'string') return payload.error.message;
  if (typeof payload.message === 'string') return payload.message;

  try {
    return JSON.stringify(payload);
  } catch {
    return fallback;
  }
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  // ==================== MÓDULO 1: Análisis de CVs ====================

  /**
   * Sube múltiples documentos PDF para análisis
   * @param files Array de archivos PDF (1-10 archivos)
   */
  async uploadDocuments(files: File[]): Promise<UploadedDocument[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(response.status, extractErrorMessage(payload, 'Error al subir documentos'));
    }

    // El backend devuelve una lista de objetos CVAnalysisResponse
    const data = await response.json();

    // Mapeamos la respuesta del backend al tipo UploadedDocument del frontend
    return data.map((doc: any) => ({
      id: doc.document_id,
      fileName: doc.filename,
      fileSize: 0, // El backend no devuelve el tamaño, lo actualizaremos en el componente
      uploadedAt: new Date(),
      status: doc.status === 'success' ? 'ready' : 'error',
      errorMessage: doc.error_message,
      analysis: doc.extracted_attributes 
    }));
  },

  /**
   * Analiza los documentos subidos contra los requisitos del puesto
   */
  async analyzeDocuments(
    documentIds: string[],
    jobRequirements: JobRequirements,
    filters: InsightFilters
  ): Promise<AnalyzeDocumentsResponse> {
    const request: AnalyzeDocumentsRequest = {
      documentIds,
      jobRequirements,
      filters,
    };

    // CORRECCIÓN: Agregamos /api al path
    const response = await fetch(`${API_BASE_URL}/api/documents/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(response.status, extractErrorMessage(payload, 'Error al analizar documentos'));
    }

    return response.json();
  },

  /**
   * Obtiene el estado de un documento específico
   */
  async getDocumentStatus(documentId: string): Promise<UploadedDocument> {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(response.status, extractErrorMessage(payload, 'Error al obtener estado'));
    }

    const doc = await response.json();
    
    return {
      id: doc.document_id,
      fileName: doc.filename,
      fileSize: 0,
      uploadedAt: new Date(),
      status: doc.status === 'success' ? 'ready' : 'error',
      errorMessage: doc.error_message,
      analysis: doc.extracted_attributes
    };
  },

  /**
   * Obtiene el análisis (atributos extraídos) de un documento
   */
  async getDocumentAnalysis(documentId: string): Promise<CVAnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(response.status, extractErrorMessage(payload, 'Error al obtener análisis del documento'));
    }

    return response.json();
  },

  /**
   * URL para visualizar/descargar la hoja de vida original
   */
  getDocumentFileUrl(documentId: string): string {
    return `${API_BASE_URL}/api/documents/${documentId}/file`;
  },

  /**
   * Elimina un documento subido
   */
  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(response.status, extractErrorMessage(payload, 'Error al eliminar documento'));
    }
  },

  // ==================== MÓDULO 2: Búsqueda por Lenguaje Natural ====================

  /**
   * Busca candidatos usando lenguaje natural (fallback cuando no se encuentra match)
   */
  async searchCandidates(query: string): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: query } as QueryRequest),
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(response.status, extractErrorMessage(payload, 'Error desconocido'));
    }

    return response.json();
  },
};
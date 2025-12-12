// lib/api.ts
import { 
  QueryRequest, 
  QueryResponse,
  DocumentUploadResponse,
  AnalyzeDocumentsRequest,
  AnalyzeDocumentsResponse,
  UploadedDocument,
  JobRequirements,
  InsightFilters
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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
   * @param files Array de archivos PDF (2-10 archivos)
   */
  async uploadDocuments(files: File[]): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al subir documentos' }));
      throw new ApiError(response.status, error.detail || 'Error en la API');
    }

    return response.json();
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

    const response = await fetch(`${API_BASE_URL}/documents/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al analizar documentos' }));
      throw new ApiError(response.status, error.detail || 'Error en la API');
    }

    return response.json();
  },

  /**
   * Obtiene el estado de un documento específico
   */
  async getDocumentStatus(documentId: string): Promise<UploadedDocument> {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al obtener estado' }));
      throw new ApiError(response.status, error.detail || 'Error en la API');
    }

    return response.json();
  },

  /**
   * Elimina un documento subido
   */
  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al eliminar documento' }));
      throw new ApiError(response.status, error.detail || 'Error en la API');
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
      const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new ApiError(response.status, error.detail || 'Error en la API');
    }

    return response.json();
  },
};
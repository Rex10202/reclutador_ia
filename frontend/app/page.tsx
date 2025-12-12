// app/page.tsx
'use client';

import { useState, useCallback } from 'react';
import { CandidatesCard } from '@/components/CandidatesCard';
import { ProfilePanel } from '@/components/ProfilePanel';
import { SearchBar } from '@/components/SearchBar';
import { DocumentUploader } from '@/components/DocumentUploader';
import { JobDescriptionInput } from '@/components/JobDescriptionInput';
import { InsightFilters } from '@/components/InsightFilters';
import { TalentSummary } from '@/components/TalentSummary';
import { api, ApiError } from '@/lib/api';
import { 
  Candidate, 
  UploadedDocument, 
  JobRequirements, 
  InsightFilters as InsightFiltersType,
  TalentSummary as TalentSummaryType 
} from '@/lib/types';
import { Anchor, Search, FileText, Sparkles } from 'lucide-react';

// Estados iniciales
const INITIAL_JOB_REQUIREMENTS: JobRequirements = {
  title: '',
  description: '',
  requiredSkills: [],
  preferredSkills: [],
  minExperience: 0,
  location: '',
  languages: [],
  education: [],
};

const INITIAL_FILTERS: InsightFiltersType = {
  prioritizeExperience: true,
  prioritizeSkills: true,
  prioritizeLocation: false,
  prioritizeLanguages: false,
  prioritizeEducation: false,
  prioritizeCertifications: false,
};

export default function TalentSearch() {
  // ==================== MÓDULO 1: Análisis de CVs ====================
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [jobRequirements, setJobRequirements] = useState<JobRequirements>(INITIAL_JOB_REQUIREMENTS);
  const [insightFilters, setInsightFilters] = useState<InsightFiltersType>(INITIAL_FILTERS);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [talentSummary, setTalentSummary] = useState<TalentSummaryType | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // ==================== MÓDULO 2: Búsqueda NL (Fallback) ====================
  const [nlQuery, setNlQuery] = useState('');
  const [nlSearching, setNlSearching] = useState(false);
  const [nlError, setNlError] = useState('');
  const [showNlFallback, setShowNlFallback] = useState(false);

  // Manejo de archivos subidos
  const handleFilesSelected = useCallback(async (files: File[]) => {
    // Crear documentos temporales con estado "uploading"
    const newDocs: UploadedDocument[] = files.map((file, idx) => ({
      id: `temp-${Date.now()}-${idx}`,
      fileName: file.name,
      fileSize: file.size,
      uploadedAt: new Date(),
      status: 'uploading' as const,
    }));

    setDocuments(prev => [...prev, ...newDocs]);

    try {
      const response = await api.uploadDocuments(files);
      
      // Actualizar con los IDs reales del servidor
      setDocuments(prev => {
        const withoutTemp = prev.filter(d => !d.id.startsWith('temp-'));
        return [...withoutTemp, ...response.documents];
      });
    } catch (err) {
      // Marcar documentos como error
      setDocuments(prev => 
        prev.map(d => 
          d.id.startsWith('temp-') 
            ? { ...d, status: 'error' as const, errorMessage: 'Error al subir' }
            : d
        )
      );
    }
  }, []);

  // Análisis de documentos
  const handleAnalyze = async () => {
    if (documents.filter(d => d.status === 'ready').length < 2) return;
    if (!jobRequirements.title.trim()) return;

    setAnalyzing(true);
    setAnalysisError('');
    setHasAnalyzed(true);

    try {
      const documentIds = documents.filter(d => d.status === 'ready').map(d => d.id);
      const response = await api.analyzeDocuments(documentIds, jobRequirements, insightFilters);
      
      // Convertir resultados a Candidates para mostrar en las cards
      const candidatesFromResults: Candidate[] = response.results.map(result => ({
        id: result.documentId,
        name: result.candidateName,
        role: result.attributes.role,
        score: result.overallScore / 100, // Normalizar a 0-1
        location: result.attributes.location || 'No especificado',
        years_experience: result.attributes.yearsExperience,
        languages: result.attributes.languages.join('; '),
        skills: result.attributes.skills.join('; '),
        matchBreakdown: result.matchBreakdown,
      }));

      setCandidates(candidatesFromResults);
      setTalentSummary(response.summary);
    } catch (err) {
      if (err instanceof ApiError) {
        setAnalysisError(err.message);
      } else {
        setAnalysisError('Error al analizar los documentos');
      }
    } finally {
      setAnalyzing(false);
    }
  };

  // Búsqueda por lenguaje natural (fallback)
  const handleNlSearch = async () => {
    if (!nlQuery.trim()) return;

    setNlSearching(true);
    setNlError('');

    try {
      const data = await api.searchCandidates(nlQuery);
      setCandidates(data.candidates || []);
      setShowNlFallback(false);
    } catch (err) {
      if (err instanceof ApiError) {
        setNlError(err.message);
      } else {
        setNlError('Error al conectar con el servidor');
      }
    } finally {
      setNlSearching(false);
    }
  };

  // Acciones del panel de perfil
  const handleMarkInterested = (candidateId: string) => {
    console.log('Candidato marcado como interesado:', candidateId);
    // TODO: Implementar persistencia
  };

  const handleAddToList = (candidateId: string) => {
    console.log('Candidato agregado a lista:', candidateId);
    // TODO: Implementar persistencia
  };

  // Validación para habilitar el botón de análisis
  const canAnalyze = 
    documents.filter(d => d.status === 'ready').length >= 2 &&
    jobRequirements.title.trim() !== '' &&
    Object.values(insightFilters).some(Boolean);

  return (
    <div className="flex h-screen w-full bg-gray-50">
      {/* Main Content */}
      <div className={`flex flex-col flex-1 transition-all duration-300 ${selectedCandidate ? 'mr-96' : ''}`}>
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-900 rounded-lg flex items-center justify-center">
                <Anchor className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-blue-900">COTECMAR</h1>
                <p className="text-sm text-gray-500">Módulo de Reclutamiento</p>
              </div>
            </div>
          </div>
        </header>

        {/* Main Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto px-6 py-8">
            {!hasAnalyzed ? (
              /* ========== VISTA INICIAL: Configuración ========== */
              <div className="space-y-8">
                {/* Sección de Upload */}
                <section>
                  <div className="flex items-center gap-3 mb-4">
                    <FileText className="w-6 h-6 text-blue-600" />
                    <h2 className="text-xl font-semibold text-gray-900">
                      1. Sube las hojas de vida
                    </h2>
                  </div>
                  <DocumentUploader
                    documents={documents}
                    onDocumentsChange={setDocuments}
                    onFilesSelected={handleFilesSelected}
                    minFiles={2}
                    maxFiles={10}
                  />
                </section>

                {/* Sección de Perfil del Puesto */}
                <section>
                  <div className="flex items-center gap-3 mb-4">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                    <h2 className="text-xl font-semibold text-gray-900">
                      2. Define el perfil del puesto
                    </h2>
                  </div>
                  <JobDescriptionInput
                    value={jobRequirements}
                    onChange={setJobRequirements}
                  />
                </section>

                {/* Sección de Filtros de Insight */}
                <section>
                  <InsightFilters
                    value={insightFilters}
                    onChange={setInsightFilters}
                  />
                </section>

                {/* Botón de Análisis */}
                <div className="flex justify-center pt-4">
                  <button
                    onClick={handleAnalyze}
                    disabled={!canAnalyze || analyzing}
                    className="flex items-center gap-3 px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                  >
                    {analyzing ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Analizando hojas de vida...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5" />
                        Analizar y encontrar candidatos
                      </>
                    )}
                  </button>
                </div>

                {!canAnalyze && documents.length > 0 && (
                  <p className="text-center text-sm text-gray-500">
                    Completa todos los campos requeridos para iniciar el análisis
                  </p>
                )}
              </div>
            ) : (
              /* ========== VISTA DE RESULTADOS ========== */
              <div className="space-y-6">
                {/* Resumen de Talento */}
                <TalentSummary summary={talentSummary} loading={analyzing} />

                {/* Error */}
                {analysisError && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
                    ❌ {analysisError}
                  </div>
                )}

                {/* Lista de Candidatos */}
                {!analyzing && candidates.length > 0 && (
                  <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-gray-900">
                      Candidatos recomendados
                    </h2>
                    <div className="space-y-3">
                      {candidates.map((candidate, idx) => (
                        <CandidatesCard 
                          key={candidate.id || idx}
                          candidate={candidate} 
                          onClick={() => setSelectedCandidate(candidate)}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Sin resultados */}
                {!analyzing && candidates.length === 0 && !analysisError && (
                  <div className="text-center py-12">
                    <p className="text-gray-500 mb-4">
                      No se encontraron candidatos que coincidan con el perfil buscado.
                    </p>
                    <button
                      onClick={() => setShowNlFallback(true)}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      ¿Intentar con búsqueda por lenguaje natural?
                    </button>
                  </div>
                )}

                {/* Botón para nueva búsqueda */}
                <div className="flex justify-center pt-4">
                  <button
                    onClick={() => {
                      setHasAnalyzed(false);
                      setCandidates([]);
                      setTalentSummary(null);
                      setSelectedCandidate(null);
                    }}
                    className="text-gray-600 hover:text-gray-800 font-medium"
                  >
                    ← Volver a configurar búsqueda
                  </button>
                </div>
              </div>
            )}

            {/* ========== MÓDULO 2: Fallback de Lenguaje Natural ========== */}
            <div className="mt-12 pt-8 border-t border-gray-200">
              <div className="text-center mb-6">
                <p className="text-gray-500 text-sm">
                  ¿No encuentras lo que buscas? Intenta con una búsqueda en lenguaje natural
                </p>
              </div>
              <div className="max-w-2xl mx-auto">
                <SearchBar
                  value={nlQuery}
                  onChange={setNlQuery}
                  onSearch={handleNlSearch}
                  loading={nlSearching}
                />
                {nlError && (
                  <p className="text-red-500 text-sm text-center mt-2">{nlError}</p>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Profile Panel */}
      {selectedCandidate && (
        <div className="fixed right-0 top-0 h-full z-50">
          <ProfilePanel 
            candidate={selectedCandidate} 
            onClose={() => setSelectedCandidate(null)}
            onMarkInterested={handleMarkInterested}
            onAddToList={handleAddToList}
          />
        </div>
      )}
    </div>
  );
}
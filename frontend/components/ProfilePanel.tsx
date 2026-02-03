// components/ProfilePanel.tsx
'use client';

import { useEffect, useMemo, useState } from 'react';
import { X, Star, ListPlus, User, CheckCircle, FileText, Eye, AlertCircle } from 'lucide-react';
import { api, ApiError } from '@/lib/api';
import { Candidate, CVAnalysisResponse, JobRequirements } from '@/lib/types';

interface ProfilePanelProps {
  candidate: Candidate | null;
  jobRequirements?: JobRequirements;
  onClose: () => void;
  onMarkInterested?: (candidateId: string) => void;
  onAddToList?: (candidateId: string) => void;
}

export function ProfilePanel({ 
  candidate, 
  jobRequirements,
  onClose,
  onMarkInterested,
  onAddToList,
}: ProfilePanelProps) {
  const [isInterested, setIsInterested] = useState(false);
  const [addedToList, setAddedToList] = useState(false);

  const [analysis, setAnalysis] = useState<CVAnalysisResponse | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState('');

  const [showCvViewer, setShowCvViewer] = useState(false);

  const candidateId = candidate?.id ?? null;

  const handleMarkInterested = () => {
    setIsInterested(true);
    if (candidateId) onMarkInterested?.(candidateId);
  };

  const handleAddToList = () => {
    setAddedToList(true);
    if (candidateId) onAddToList?.(candidateId);
  };

  const fileUrl = candidateId ? api.getDocumentFileUrl(candidateId) : '';

  useEffect(() => {
    if (!candidateId) return;
    const id = candidateId;
    let cancelled = false;

    async function load() {
      setAnalysis(null);
      setAnalysisError('');
      setAnalysisLoading(true);
      try {
        const data = await api.getDocumentAnalysis(id);
        if (!cancelled) setAnalysis(data);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError) setAnalysisError(err.message);
        else setAnalysisError('No fue posible cargar el análisis del CV');
      } finally {
        if (!cancelled) setAnalysisLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [candidateId]);

  const extracted = useMemo(() => {
    const attrs = analysis?.extracted_attributes || [];
    const get = (type: string) => attrs.find(a => a.attribute_type === type)?.value;
    const skills = (get('skills') || '')
      .split(';')
      .map(s => s.trim())
      .filter(Boolean);

    const languages = (get('languages') || '')
      .split(';')
      .map(s => s.trim())
      .filter(Boolean);

    const yearsExperience = (() => {
      const v = get('years_experience');
      if (!v) return null;
      const num = Number(String(v).trim());
      return Number.isFinite(num) ? num : null;
    })();

    return {
      role: get('role') || null,
      location: get('location') || null,
      yearsExperience,
      skills,
      languages,
      rawPreview: analysis?.raw_text_preview || null,
      all: attrs,
    };
  }, [analysis]);

  const matchView = useMemo(() => {
    const reqSkills = jobRequirements?.requiredSkills || [];
    const extractedSkillsLower = new Set(extracted.skills.map(s => s.toLowerCase()));
    const matchedSkills = reqSkills.filter(s => extractedSkillsLower.has(s.toLowerCase()));
    const missingSkills = reqSkills.filter(s => !extractedSkillsLower.has(s.toLowerCase()));

    const reqLangs = jobRequirements?.languages || [];
    const extractedLangLower = new Set(extracted.languages.map(s => s.toLowerCase()));
    const matchedLanguages = reqLangs.filter(s => extractedLangLower.has(s.toLowerCase()));
    const missingLanguages = reqLangs.filter(s => !extractedLangLower.has(s.toLowerCase()));

    const minExp = jobRequirements?.minExperience && jobRequirements.minExperience > 0 ? jobRequirements.minExperience : null;
    const expOk = minExp === null ? null : (extracted.yearsExperience === null ? null : extracted.yearsExperience >= minExp);

    const requiredLocation = jobRequirements?.location?.trim() ? jobRequirements.location.trim() : null;
    const extractedLocation = extracted.location?.trim() ? extracted.location.trim() : null;
    const locationOk = (() => {
      if (!requiredLocation) return null;
      if (!extractedLocation) return null;
      return extractedLocation.toLowerCase().includes(requiredLocation.toLowerCase());
    })();

    return {
      matchedSkills,
      missingSkills,
      matchedLanguages,
      missingLanguages,
      minExp,
      expOk,
      requiredLocation,
      extractedLocation,
      locationOk,
    };
  }, [jobRequirements, extracted.skills, extracted.languages, extracted.yearsExperience]);

  if (!candidate) return null;

  const skillsArray = candidate.skills?.split(';').map(s => s.trim()).filter(Boolean) || [];
  const displayName = candidate.name || candidate.id;
  const compatibilityPercent = Math.round(candidate.score * 100);
  
  return (
    <div className="w-full md:w-96 h-full bg-white border-l border-gray-200 flex flex-col overflow-hidden shadow-lg">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start z-20">
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
            <User className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{displayName}</h2>
            <p className="text-sm text-gray-500">ID: {candidate.id}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-400 hover:text-gray-600" />
        </button>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* CV actions */}
        <section className="space-y-3">
          <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold">
            Hoja de Vida
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCvViewer(true)}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-colors"
            >
              <Eye className="w-4 h-4" />
              Ver CV
            </button>
            <a
              href={fileUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              <FileText className="w-4 h-4" />
              Abrir
            </a>
          </div>
          <p className="text-xs text-gray-500">
            Se abre el archivo original subido (PDF/DOCX/TXT).
          </p>
        </section>

        {/* Rol y Experiencia */}
        <section className="space-y-3">
          <p className="text-lg font-medium text-gray-900">{candidate.role}</p>
          <p className="text-gray-600">{candidate.location}</p>
          <p className="text-gray-600">
            {candidate.years_experience === null
              ? 'Experiencia: No especificado'
              : `${candidate.years_experience}+ años de experiencia`}
          </p>
        </section>

        {/* Score de Compatibilidad */}
        <section className="bg-gray-50 rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Compatibilidad con el puesto</h3>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${
                    compatibilityPercent >= 70 
                      ? 'bg-green-500' 
                      : compatibilityPercent >= 40 
                        ? 'bg-blue-500' 
                        : 'bg-amber-500'
                  }`}
                  style={{ width: `${compatibilityPercent}%` }}
                />
              </div>
            </div>
            <span className="text-2xl font-bold text-gray-900">{compatibilityPercent}%</span>
          </div>
        </section>
        
        {/* Información General */}
        <section>
          <h3 className="text-sm uppercase tracking-wider text-gray-500 mb-4 font-semibold">
            Información General
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between py-3 border-b border-gray-100">
              <span className="text-gray-500">Localización</span>
              <span className="text-gray-900 font-medium text-right">{candidate.location}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-gray-100">
              <span className="text-gray-500">Experiencia</span>
              <span className="text-gray-900 font-medium">
                {candidate.years_experience === null ? 'No especificado' : `${candidate.years_experience}+ años`}
              </span>
            </div>
            {candidate.languages && (
              <div className="flex justify-between py-3 border-b border-gray-100">
                <span className="text-gray-500">Idiomas</span>
                <span className="text-gray-900 font-medium text-right">{candidate.languages}</span>
              </div>
            )}
          </div>
        </section>
        
        {/* Skills */}
        {skillsArray.length > 0 && (
          <section>
            <h3 className="text-sm uppercase tracking-wider text-gray-500 mb-4 font-semibold">
              Habilidades Técnicas
            </h3>
            <div className="flex flex-wrap gap-2">
              {skillsArray.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-blue-50 text-blue-700 text-sm rounded-lg border border-blue-100"
                >
                  {skill}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Extracted attributes */}
        <section className="space-y-3">
          <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold">
            Extracción del CV
          </h3>

          {analysisLoading && (
            <div className="text-sm text-gray-500">Cargando extracción...</div>
          )}

          {analysisError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{analysisError}</span>
            </div>
          )}

          {!analysisLoading && !analysisError && analysis && (
            <div className="space-y-3">
              {Array.isArray(analysis.warnings) && analysis.warnings.length > 0 && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-900 text-sm">
                  <p className="font-medium mb-1">Advertencias de extracción</p>
                  <ul className="list-disc pl-5 space-y-1">
                    {analysis.warnings.map((w, idx) => (
                      <li key={idx} className="text-blue-800">
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!extracted.role && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
                  No fue posible extraer/verificar el rol desde la hoja de vida.
                </div>
              )}
              {!extracted.location && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
                  No fue posible extraer/verificar la ubicación desde la hoja de vida.
                </div>
              )}
              {extracted.yearsExperience === null && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
                  No fue posible extraer años de experiencia desde la hoja de vida.
                </div>
              )}

              {extracted.role && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Rol detectado</span>
                  <span className="text-gray-900 font-medium text-right">{extracted.role}</span>
                </div>
              )}
              {extracted.location && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Ubicación detectada</span>
                  <span className="text-gray-900 font-medium text-right">{extracted.location}</span>
                </div>
              )}
              {extracted.yearsExperience !== null && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Años de experiencia</span>
                  <span className="text-gray-900 font-medium">{extracted.yearsExperience}</span>
                </div>
              )}

              {extracted.skills.length > 0 && (
                <div>
                  <p className="text-gray-500 text-sm mb-2">Skills detectadas</p>
                  <div className="flex flex-wrap gap-2">
                    {extracted.skills.map((skill, idx) => (
                      <span key={idx} className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs rounded-md border border-gray-200">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {extracted.languages.length > 0 && (
                <div>
                  <p className="text-gray-500 text-sm mb-2">Idiomas detectados</p>
                  <div className="flex flex-wrap gap-2">
                    {extracted.languages.map((lang, idx) => (
                      <span key={idx} className="px-2.5 py-1 bg-green-50 text-green-700 text-xs rounded-md border border-green-100">
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {extracted.rawPreview && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-2">Vista previa del texto extraído</p>
                  <p className="text-xs text-gray-700 whitespace-pre-wrap">{extracted.rawPreview}</p>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Match vs Job Requirements */}
        {jobRequirements && (
          <section className="space-y-3">
            <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold">
              Match con el Perfil
            </h3>

            {jobRequirements.requiredSkills?.length > 0 && (
              <div>
                <p className="text-gray-500 text-sm mb-2">Habilidades requeridas</p>
                <div className="flex flex-wrap gap-2">
                  {jobRequirements.requiredSkills.map((skill) => {
                    const isMatched = matchView.matchedSkills.some(ms => ms.toLowerCase() === skill.toLowerCase());
                    return (
                      <span
                        key={skill}
                        className={`px-2.5 py-1 text-xs rounded-md border ${
                          isMatched
                            ? 'bg-blue-50 text-blue-700 border-blue-100'
                            : 'bg-amber-50 text-amber-800 border-amber-100'
                        }`}
                      >
                        {skill}
                      </span>
                    );
                  })}
                </div>
                {matchView.missingSkills.length > 0 && (
                  <p className="text-xs text-amber-700 mt-2">
                    Faltantes: {matchView.missingSkills.join(', ')}
                  </p>
                )}
              </div>
            )}

            {(jobRequirements.languages ?? []).length > 0 && (
              <div>
                <p className="text-gray-500 text-sm mb-2">Idiomas requeridos</p>
                <div className="flex flex-wrap gap-2">
                  {(jobRequirements.languages ?? []).map((lang) => {
                    const isMatched = matchView.matchedLanguages.some(ml => ml.toLowerCase() === lang.toLowerCase());
                    return (
                      <span
                        key={lang}
                        className={`px-2.5 py-1 text-xs rounded-md border ${
                          isMatched
                            ? 'bg-green-50 text-green-700 border-green-100'
                            : 'bg-amber-50 text-amber-800 border-amber-100'
                        }`}
                      >
                        {lang}
                      </span>
                    );
                  })}
                </div>
                {matchView.missingLanguages.length > 0 && (
                  <p className="text-xs text-amber-700 mt-2">
                    Faltantes: {matchView.missingLanguages.join(', ')}
                  </p>
                )}
              </div>
            )}

            {matchView.minExp !== null && (
              <div className="flex items-center justify-between py-2 border-t border-gray-100">
                <span className="text-gray-500 text-sm">Experiencia mínima</span>
                <span className={`text-sm font-medium ${matchView.expOk === false ? 'text-amber-700' : 'text-gray-900'}`}>
                  {matchView.minExp} años
                </span>
              </div>
            )}

            {matchView.requiredLocation && (
              <div className="flex items-center justify-between py-2 border-t border-gray-100">
                <span className="text-gray-500 text-sm">Ubicación requerida</span>
                <span className={`text-sm font-medium ${matchView.locationOk === false ? 'text-amber-700' : 'text-gray-900'}`}>
                  {matchView.requiredLocation}
                </span>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Actions Footer */}
      <div className="border-t border-gray-200 p-4 space-y-3">
        <button
          onClick={handleMarkInterested}
          disabled={isInterested}
          className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
            isInterested
              ? 'bg-green-100 text-green-700 cursor-default'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isInterested ? (
            <>
              <CheckCircle className="w-5 h-5" />
              Marcado como candidato de interés
            </>
          ) : (
            <>
              <Star className="w-5 h-5" />
              Marcar como candidato de interés
            </>
          )}
        </button>
        <button
          onClick={handleAddToList}
          disabled={addedToList}
          className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all border ${
            addedToList
              ? 'bg-gray-100 text-gray-500 border-gray-200 cursor-default'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
          }`}
        >
          {addedToList ? (
            <>
              <CheckCircle className="w-5 h-5" />
              Agregado a lista
            </>
          ) : (
            <>
              <ListPlus className="w-5 h-5" />
              Agregar a lista
            </>
          )}
        </button>
      </div>

      {/* CV Viewer Modal */}
      {showCvViewer && (
        <div className="fixed inset-0 z-[60] bg-black/40 flex items-center justify-center p-4" onClick={() => setShowCvViewer(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl h-[85vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
              <div>
                <p className="text-sm font-semibold text-gray-900">Hoja de vida</p>
                <p className="text-xs text-gray-500">Documento: {candidate.id}</p>
              </div>
              <button
                onClick={() => setShowCvViewer(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Cerrar"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <iframe
              src={fileUrl}
              title="CV Viewer"
              className="w-full h-full"
            />
          </div>
        </div>
      )}
    </div>
  );
}
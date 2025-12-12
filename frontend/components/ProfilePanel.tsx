// components/ProfilePanel.tsx
'use client';

import { useState } from 'react';
import { X, Star, ListPlus, User, CheckCircle } from 'lucide-react';
import { Candidate } from '@/lib/types';

interface ProfilePanelProps {
  candidate: Candidate | null;
  onClose: () => void;
  onMarkInterested?: (candidateId: string) => void;
  onAddToList?: (candidateId: string) => void;
}

export function ProfilePanel({ 
  candidate, 
  onClose,
  onMarkInterested,
  onAddToList,
}: ProfilePanelProps) {
  const [isInterested, setIsInterested] = useState(false);
  const [addedToList, setAddedToList] = useState(false);
  
  if (!candidate) return null;
  
  const skillsArray = candidate.skills?.split(';').map(s => s.trim()).filter(Boolean) || [];
  const displayName = candidate.name || candidate.id;
  const compatibilityPercent = Math.round(candidate.score * 100);

  const handleMarkInterested = () => {
    setIsInterested(true);
    onMarkInterested?.(candidate.id);
  };

  const handleAddToList = () => {
    setAddedToList(true);
    onAddToList?.(candidate.id);
  };
  
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
        {/* Rol y Experiencia */}
        <section className="space-y-3">
          <p className="text-lg font-medium text-gray-900">{candidate.role}</p>
          <p className="text-gray-600">{candidate.location}</p>
          <p className="text-gray-600">{candidate.years_experience}+ años de experiencia</p>
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
              <span className="text-gray-900 font-medium">{candidate.years_experience}+ años</span>
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
    </div>
  );
}
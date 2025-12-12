// components/JobDescriptionInput.tsx
'use client';

import { useState } from 'react';
import { Briefcase, ChevronDown, ChevronUp, Plus, X } from 'lucide-react';
import { JobRequirements } from '@/lib/types';

interface JobDescriptionInputProps {
  value: JobRequirements;
  onChange: (requirements: JobRequirements) => void;
  disabled?: boolean;
}

const DEFAULT_REQUIREMENTS: JobRequirements = {
  title: '',
  description: '',
  requiredSkills: [],
  preferredSkills: [],
  minExperience: 0,
  maxExperience: undefined,
  location: '',
  languages: [],
  education: [],
};

export function JobDescriptionInput({
  value = DEFAULT_REQUIREMENTS,
  onChange,
  disabled = false,
}: JobDescriptionInputProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [newSkill, setNewSkill] = useState('');
  const [newPreferredSkill, setNewPreferredSkill] = useState('');
  const [newLanguage, setNewLanguage] = useState('');

  const updateField = <K extends keyof JobRequirements>(
    field: K,
    fieldValue: JobRequirements[K]
  ) => {
    onChange({ ...value, [field]: fieldValue });
  };

  const addToArray = (field: 'requiredSkills' | 'preferredSkills' | 'languages' | 'education', item: string) => {
    if (!item.trim()) return;
    const current = value[field] || [];
    if (!current.includes(item.trim())) {
      updateField(field, [...current, item.trim()]);
    }
  };

  const removeFromArray = (field: 'requiredSkills' | 'preferredSkills' | 'languages' | 'education', item: string) => {
    const current = value[field] || [];
    updateField(field, current.filter(i => i !== item));
  };

  const handleKeyDown = (
    e: React.KeyboardEvent,
    field: 'requiredSkills' | 'preferredSkills' | 'languages',
    inputValue: string,
    clearInput: () => void
  ) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addToArray(field, inputValue);
      clearInput();
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-100 rounded-lg">
          <Briefcase className="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">Perfil del Puesto</h3>
          <p className="text-sm text-gray-500">Define los requisitos del candidato ideal</p>
        </div>
      </div>

      {/* Título del puesto */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Título del puesto <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={value.title}
          onChange={(e) => updateField('title', e.target.value)}
          placeholder="Ej: Ingeniero de Software Senior"
          disabled={disabled}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
      </div>

      {/* Descripción opcional */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Descripción del puesto
        </label>
        <textarea
          value={value.description || ''}
          onChange={(e) => updateField('description', e.target.value)}
          placeholder="Describe brevemente las responsabilidades y el contexto del puesto..."
          disabled={disabled}
          rows={3}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed resize-none"
        />
      </div>

      {/* Skills Requeridos */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Habilidades requeridas
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            onKeyDown={(e) => handleKeyDown(e, 'requiredSkills', newSkill, () => setNewSkill(''))}
            placeholder="Ej: Python, React, SAP..."
            disabled={disabled}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          />
          <button
            onClick={() => { addToArray('requiredSkills', newSkill); setNewSkill(''); }}
            disabled={disabled || !newSkill.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>
        {value.requiredSkills.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {value.requiredSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                {skill}
                <button
                  onClick={() => removeFromArray('requiredSkills', skill)}
                  disabled={disabled}
                  className="hover:text-blue-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Experiencia Mínima */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Experiencia mínima (años)
          </label>
          <input
            type="number"
            min={0}
            max={50}
            value={value.minExperience}
            onChange={(e) => updateField('minExperience', parseInt(e.target.value) || 0)}
            disabled={disabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ubicación preferida
          </label>
          <input
            type="text"
            value={value.location || ''}
            onChange={(e) => updateField('location', e.target.value)}
            placeholder="Ej: Bogotá, Cartagena..."
            disabled={disabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          />
        </div>
      </div>

      {/* Toggle para opciones avanzadas */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
      >
        {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        {showAdvanced ? 'Ocultar opciones avanzadas' : 'Mostrar opciones avanzadas'}
      </button>

      {/* Opciones avanzadas */}
      {showAdvanced && (
        <div className="space-y-4 pt-4 border-t border-gray-200">
          {/* Skills Preferidos */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Habilidades preferidas (nice to have)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newPreferredSkill}
                onChange={(e) => setNewPreferredSkill(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'preferredSkills', newPreferredSkill, () => setNewPreferredSkill(''))}
                placeholder="Ej: Docker, AWS..."
                disabled={disabled}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              />
              <button
                onClick={() => { addToArray('preferredSkills', newPreferredSkill); setNewPreferredSkill(''); }}
                disabled={disabled || !newPreferredSkill.trim()}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            {value.preferredSkills.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {value.preferredSkills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {skill}
                    <button
                      onClick={() => removeFromArray('preferredSkills', skill)}
                      disabled={disabled}
                      className="hover:text-gray-900"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Idiomas */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Idiomas requeridos
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newLanguage}
                onChange={(e) => setNewLanguage(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'languages', newLanguage, () => setNewLanguage(''))}
                placeholder="Ej: Inglés, Español..."
                disabled={disabled}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              />
              <button
                onClick={() => { addToArray('languages', newLanguage); setNewLanguage(''); }}
                disabled={disabled || !newLanguage.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            {(value.languages || []).length > 0 && (
              <div className="flex flex-wrap gap-2">
                {value.languages!.map((lang) => (
                  <span
                    key={lang}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                  >
                    {lang}
                    <button
                      onClick={() => removeFromArray('languages', lang)}
                      disabled={disabled}
                      className="hover:text-green-900"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

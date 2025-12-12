// components/InsightFilters.tsx
'use client';

import { 
  Clock, 
  Code, 
  MapPin, 
  Globe, 
  GraduationCap, 
  Award,
  Sparkles
} from 'lucide-react';
import { InsightFilters as InsightFiltersType } from '@/lib/types';

interface InsightFiltersProps {
  value: InsightFiltersType;
  onChange: (filters: InsightFiltersType) => void;
  disabled?: boolean;
}

interface FilterOption {
  key: keyof InsightFiltersType;
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const FILTER_OPTIONS: FilterOption[] = [
  {
    key: 'prioritizeSkills',
    label: 'Skills Técnicos',
    description: 'Priorizar coincidencia de habilidades',
    icon: <Code className="w-5 h-5" />,
    color: 'blue',
  },
  {
    key: 'prioritizeExperience',
    label: 'Experiencia',
    description: 'Valorar años de experiencia',
    icon: <Clock className="w-5 h-5" />,
    color: 'purple',
  },
  {
    key: 'prioritizeLocation',
    label: 'Ubicación',
    description: 'Preferir candidatos de la zona',
    icon: <MapPin className="w-5 h-5" />,
    color: 'green',
  },
  {
    key: 'prioritizeLanguages',
    label: 'Idiomas',
    description: 'Requerir idiomas específicos',
    icon: <Globe className="w-5 h-5" />,
    color: 'amber',
  },
  {
    key: 'prioritizeEducation',
    label: 'Educación',
    description: 'Valorar formación académica',
    icon: <GraduationCap className="w-5 h-5" />,
    color: 'cyan',
  },
  {
    key: 'prioritizeCertifications',
    label: 'Certificaciones',
    description: 'Buscar certificaciones relevantes',
    icon: <Award className="w-5 h-5" />,
    color: 'rose',
  },
];

const colorClasses: Record<string, { active: string; inactive: string; border: string }> = {
  blue: {
    active: 'bg-blue-100 text-blue-700 border-blue-300',
    inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:border-blue-300 hover:bg-blue-50',
    border: 'border-blue-500',
  },
  purple: {
    active: 'bg-purple-100 text-purple-700 border-purple-300',
    inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:border-purple-300 hover:bg-purple-50',
    border: 'border-purple-500',
  },
  green: {
    active: 'bg-green-100 text-green-700 border-green-300',
    inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:border-green-300 hover:bg-green-50',
    border: 'border-green-500',
  },
  amber: {
    active: 'bg-amber-100 text-amber-700 border-amber-300',
    inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:border-amber-300 hover:bg-amber-50',
    border: 'border-amber-500',
  },
  cyan: {
    active: 'bg-cyan-100 text-cyan-700 border-cyan-300',
    inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:border-cyan-300 hover:bg-cyan-50',
    border: 'border-cyan-500',
  },
  rose: {
    active: 'bg-rose-100 text-rose-700 border-rose-300',
    inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:border-rose-300 hover:bg-rose-50',
    border: 'border-rose-500',
  },
};

export function InsightFilters({
  value,
  onChange,
  disabled = false,
}: InsightFiltersProps) {
  const toggleFilter = (key: keyof InsightFiltersType) => {
    onChange({ ...value, [key]: !value[key] });
  };

  const activeCount = Object.values(value).filter(Boolean).length;

  const selectAll = () => {
    const allSelected: InsightFiltersType = {
      prioritizeExperience: true,
      prioritizeSkills: true,
      prioritizeLocation: true,
      prioritizeLanguages: true,
      prioritizeEducation: true,
      prioritizeCertifications: true,
    };
    onChange(allSelected);
  };

  const clearAll = () => {
    const allCleared: InsightFiltersType = {
      prioritizeExperience: false,
      prioritizeSkills: false,
      prioritizeLocation: false,
      prioritizeLanguages: false,
      prioritizeEducation: false,
      prioritizeCertifications: false,
    };
    onChange(allCleared);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Sparkles className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Criterios de Evaluación</h3>
            <p className="text-sm text-gray-500">
              Selecciona qué aspectos priorizar en el análisis
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={selectAll}
            disabled={disabled}
            className="text-xs text-blue-600 hover:text-blue-700 font-medium disabled:text-gray-400"
          >
            Todos
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={clearAll}
            disabled={disabled}
            className="text-xs text-gray-500 hover:text-gray-700 font-medium disabled:text-gray-400"
          >
            Ninguno
          </button>
        </div>
      </div>

      {activeCount === 0 && (
        <p className="text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-lg p-3">
          💡 Selecciona al menos un criterio para personalizar el análisis
        </p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {FILTER_OPTIONS.map((option) => {
          const isActive = value[option.key];
          const colors = colorClasses[option.color];

          return (
            <button
              key={option.key}
              onClick={() => toggleFilter(option.key)}
              disabled={disabled}
              className={`
                flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200
                ${isActive ? colors.active : colors.inactive}
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                ${isActive ? 'shadow-sm' : ''}
              `}
            >
              <div className={`${isActive ? '' : 'text-gray-400'}`}>
                {option.icon}
              </div>
              <span className="font-medium text-sm text-center">{option.label}</span>
              {isActive && (
                <span className="text-xs opacity-75">✓ Activo</span>
              )}
            </button>
          );
        })}
      </div>

      {activeCount > 0 && (
        <p className="text-sm text-gray-500 text-center">
          {activeCount} criterio{activeCount !== 1 ? 's' : ''} seleccionado{activeCount !== 1 ? 's' : ''}
        </p>
      )}
    </div>
  );
}

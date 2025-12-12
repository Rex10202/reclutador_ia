// components/CandidatesCard.tsx
import { MapPin, Clock, Globe, Briefcase, User } from 'lucide-react';
import { Candidate } from '@/lib/types';

interface CandidatesCardProps {
  candidate: Candidate;
  onClick: () => void;
}

export function CandidatesCard({ candidate, onClick }: CandidatesCardProps) {
  const skillsArray = candidate.skills?.split(';').filter(s => s.trim()) || [];
  const displayName = candidate.name || candidate.id;
  const compatibilityPercent = Math.round(candidate.score * 100);
  
  return (
    <div 
      onClick={onClick}
      className="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-lg transition-all duration-200 cursor-pointer"
    >
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <User className="w-6 h-6 text-blue-600" />
        </div>
        
        {/* Info Principal */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                {displayName}
              </h3>
              <p className="text-sm text-gray-500">
                ID: {candidate.id}
              </p>
              <p className="text-sm font-medium text-gray-700 mt-1">
                {candidate.role}
              </p>
            </div>
            
            {/* Barra de Compatibilidad */}
            <div className="flex-shrink-0 w-36">
              <p className="text-xs text-gray-500 mb-1 text-right">Compatibilidad</p>
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full transition-all duration-500 ${
                    compatibilityPercent >= 70 
                      ? 'bg-green-500' 
                      : compatibilityPercent >= 40 
                        ? 'bg-blue-500' 
                        : 'bg-amber-500'
                  }`}
                  style={{ width: `${compatibilityPercent}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1 text-right font-medium">
                {compatibilityPercent}%
              </p>
            </div>
          </div>
          
          {/* Detalles */}
          <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-600">
            <div className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span>{candidate.location}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-gray-400" />
              <span>{candidate.years_experience}+ años de experiencia</span>
            </div>
            {candidate.languages && (
              <div className="flex items-center gap-1.5">
                <Globe className="w-4 h-4 text-gray-400" />
                <span>{candidate.languages}</span>
              </div>
            )}
          </div>
          
          {/* Skills */}
          {skillsArray.length > 0 && (
            <div className="flex items-start gap-2 mt-3">
              <Briefcase className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex flex-wrap gap-1.5">
                {skillsArray.slice(0, 4).map((skill: string, idx: number) => (
                  <span 
                    key={idx} 
                    className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-md border border-gray-200"
                  >
                    {skill.trim()}
                  </span>
                ))}
                {skillsArray.length > 4 && (
                  <span className="px-2 py-0.5 text-gray-400 text-xs">
                    +{skillsArray.length - 4} más
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
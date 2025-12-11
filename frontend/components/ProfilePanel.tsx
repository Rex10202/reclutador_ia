// components/ProfilePanel.tsx
import { X } from 'lucide-react';
import { Candidate } from '@/lib/types';

interface ProfilePanelProps {
  candidate: Candidate | null;
  onClose: () => void;
}

export function ProfilePanel({ candidate, onClose }: ProfilePanelProps) {
  if (!candidate) return null;
  
  const skillsArray = candidate.skills?.split(';').map(s => s.trim()).filter(Boolean) || [];
  
  return (
    <div className="w-full md:w-1/2 h-full bg-gradient-to-br from-slate-900 to-slate-800 border-l border-cyan-500/20 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="sticky top-0 bg-slate-900/95 backdrop-blur-lg border-b border-cyan-500/20 p-6 flex justify-between items-center z-20">
        <h2 className="text-2xl font-bold text-white">{candidate.id}</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors group"
        >
          <X className="w-6 h-6 text-slate-400 group-hover:text-white transition-colors" />
        </button>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* General Info */}
        <section>
          <h3 className="text-sm uppercase tracking-wider text-slate-500 mb-4 font-semibold">Información General</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-3 border-b border-slate-700/50">
              <span className="text-slate-400">Rol</span>
              <span className="text-white font-semibold text-right">{candidate.role}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-slate-700/50">
              <span className="text-slate-400">Score de Compatibilidad</span>
              <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent font-bold">
                {candidate.score.toFixed(3)}
              </span>
            </div>
          </div>
        </section>
        
        {/* Location & Experience */}
        <section>
          <h3 className="text-sm uppercase tracking-wider text-slate-500 mb-4 font-semibold">Ubicación y Experiencia</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-3 border-b border-slate-700/50">
              <span className="text-slate-400">Localización</span>
              <span className="text-white font-semibold text-right">{candidate.location}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-slate-700/50">
              <span className="text-slate-400">Años de Experiencia</span>
              <span className="text-white font-semibold">{candidate.years_experience}+</span>
            </div>
            <div className="flex justify-between py-3 border-b border-slate-700/50">
              <span className="text-slate-400">Idiomas</span>
              <span className="text-white font-semibold text-right">{candidate.languages || '-'}</span>
            </div>
          </div>
        </section>
        
        {/* Skills */}
        <section>
          <h3 className="text-sm uppercase tracking-wider text-slate-500 mb-4 font-semibold">Habilidades Técnicas</h3>
          <div className="flex flex-wrap gap-2">
            {skillsArray.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 text-sm rounded-lg border border-cyan-400/30 hover:border-cyan-400/50 hover:from-cyan-500/30 hover:to-blue-500/30 transition-all duration-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
// components/CandidatesCard.tsx
import { MapPin, Clock, Globe, Briefcase, Sparkles } from 'lucide-react';
import { Candidate } from '@/lib/types';

interface CandidatesCardProps {
  candidate: Candidate;
  onClick: () => void;
}

export function CandidatesCard({ candidate, onClick }: CandidatesCardProps) {
  const skillsArray = candidate.skills?.split(';').filter(s => s.trim()) || [];
  
  return (
    <div 
      onClick={onClick}
      className="group relative bg-gradient-to-br from-slate-800/40 to-slate-900/40 backdrop-blur-sm rounded-2xl p-6 border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300 cursor-pointer hover:translate-x-2 hover:shadow-xl hover:shadow-cyan-500/10"
    >
      {/* Glow effect on hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/5 to-cyan-500/0 opacity-0 group-hover:opacity-100 rounded-2xl transition-opacity duration-300" />
      
      <div className="relative z-10">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-semibold text-white group-hover:text-cyan-400 transition-colors">
              {candidate.id}
            </h3>
            <p className="text-slate-400 text-sm mt-1">{candidate.role}</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-full border border-cyan-400/30">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-400 font-bold text-sm">{candidate.score.toFixed(3)}</span>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-3 mb-3 text-sm text-slate-300">
          <div className="flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-cyan-400" />
            <span>{candidate.location}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>{candidate.years_experience}+ años</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Globe className="w-4 h-4 text-cyan-400" />
            <span>{candidate.languages || '-'}</span>
          </div>
        </div>
        
        {skillsArray.length > 0 && (
          <div className="flex items-start gap-2">
            <Briefcase className="w-4 h-4 text-cyan-400 mt-1 flex-shrink-0" />
            <div className="flex flex-wrap gap-1.5">
              {skillsArray.slice(0, 3).map((skill: string, idx: number) => (
                <span key={idx} className="px-2 py-1 bg-cyan-500/10 text-cyan-300 text-xs rounded-md border border-cyan-500/20">
                  {skill.trim()}
                </span>
              ))}
              {skillsArray.length > 3 && (
                <span className="px-2 py-1 text-slate-400 text-xs">
                  +{skillsArray.length - 3} más
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
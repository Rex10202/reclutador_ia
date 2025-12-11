// app/page.tsx
'use client';

import { useState } from 'react';
import { CandidatesCard } from '@/components/CandidatesCard';
import { ProfilePanel } from '@/components/ProfilePanel';
import { SearchBar } from '@/components/SearchBar';
import { api, ApiError } from '@/lib/api';
import { Candidate } from '@/lib/types';

export default function TalentSearch() {
  const [query, setQuery] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCompact, setIsCompact] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setIsCompact(true);
    setHasSearched(true);
    setCandidates([]); // Limpiar resultados anteriores

    try {
      const data = await api.searchCandidates(query);
      setCandidates(data.candidates || []);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Error al conectar con el servidor');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      {/* Main Content */}
      <div className={`flex flex-col transition-all duration-500 ${selectedCandidate ? 'w-full md:w-1/2' : 'w-full'} relative z-10`}>
        {/* Header */}
        <div className={`flex flex-col items-center justify-center transition-all duration-500 ${isCompact ? 'py-8' : 'flex-1'} px-6`}>
          <div className={`text-center transition-all duration-500 ${isCompact ? 'mb-6' : 'mb-12'}`}>
            <h1 className={`font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent transition-all duration-500 ${isCompact ? 'text-3xl' : 'text-5xl md:text-6xl'} mb-4`}>
              ¿Quieres buscar talento?
            </h1>
            <p className={`text-slate-400 transition-all duration-500 ${isCompact ? 'text-sm' : 'text-lg'} max-w-2xl`}>
              Describe el perfil que necesitas y encuentra los mejores candidatos instantáneamente
            </p>
          </div>

          <SearchBar 
            value={query}
            onChange={setQuery}
            onSearch={handleSearch}
            loading={loading}
          />
        </div>

        {/* Results */}
        {hasSearched && (
          <div className="flex-1 overflow-y-auto px-6 pb-6">
            <div className="max-w-3xl mx-auto">
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
                    <p className="text-cyan-400">Procesando consulta...</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
                  ❌ {error}
                </div>
              )}

              {!loading && !error && candidates.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  No se encontraron candidatos que coincidan con tu búsqueda.
                </div>
              )}

              {!loading && candidates.length > 0 && (
                <div className="space-y-4">
                  <h2 className="text-sm uppercase tracking-wider text-slate-500 font-semibold">
                    Candidatos recomendados ({candidates.length})
                  </h2>
                  {candidates.map((candidate, idx) => (
                    <div
                      key={idx}
                      style={{ animationDelay: `${idx * 0.1}s` }}
                      className="animate-in fade-in slide-in-from-bottom-4 duration-500"
                    >
                      <CandidatesCard 
                        candidate={candidate} 
                        onClick={() => setSelectedCandidate(candidate)}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Profile Panel */}
      {selectedCandidate && (
        <ProfilePanel 
          candidate={selectedCandidate} 
          onClose={() => setSelectedCandidate(null)} 
        />
      )}
    </div>
  );
}
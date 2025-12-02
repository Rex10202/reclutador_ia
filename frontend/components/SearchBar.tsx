// components/SearchBar.tsx
import { Search } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  loading: boolean;
}

export function SearchBar({ value, onChange, onSearch, loading }: SearchBarProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading && value.trim()) {
      onSearch();
    }
  };

  return (
    <div className="w-full max-w-3xl">
      <div className="flex items-center gap-3 bg-slate-800/40 backdrop-blur-xl rounded-2xl p-2 border border-cyan-500/20 focus-within:border-cyan-400/40 focus-within:shadow-lg focus-within:shadow-cyan-500/20 transition-all duration-300">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ej.: Ingeniero con 5+ años en SAP PM y liderazgo de equipo..."
          className="flex-1 bg-transparent px-4 py-3 text-white placeholder-slate-500 outline-none"
        />
        <button
          onClick={onSearch}
          disabled={loading || !value.trim()}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-900 font-semibold rounded-xl hover:from-cyan-400 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:shadow-cyan-500/50 hover:-translate-y-0.5 active:translate-y-0"
        >
          <Search className="w-5 h-5" />
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </div>
    </div>
  );
}
// components/TalentSummary.tsx
'use client';

import { Users, UserCheck, Clock } from 'lucide-react';
import { TalentSummary as TalentSummaryType } from '@/lib/types';

interface TalentSummaryProps {
  summary: TalentSummaryType | null;
  loading?: boolean;
}

interface StatCardProps {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  subLabel?: string;
}

function StatCard({ icon, value, label, subLabel }: StatCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 flex flex-col items-center text-center">
      <div className="mb-2 text-blue-600">
        {icon}
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-600">{label}</p>
      {subLabel && (
        <p className="text-xs text-gray-400 mt-1">{subLabel}</p>
      )}
    </div>
  );
}

function StatCardSkeleton() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 flex flex-col items-center animate-pulse">
      <div className="w-8 h-8 bg-gray-200 rounded mb-2" />
      <div className="w-16 h-8 bg-gray-200 rounded mb-2" />
      <div className="w-24 h-4 bg-gray-200 rounded" />
    </div>
  );
}

export function TalentSummary({ summary, loading = false }: TalentSummaryProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Resumen de talento</h2>
        <div className="grid grid-cols-3 gap-4">
          <StatCardSkeleton />
          <StatCardSkeleton />
          <StatCardSkeleton />
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Resumen de talento</h2>
      
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          icon={<Users className="w-8 h-8" />}
          value={summary.totalCandidates}
          label="total de candidatos"
        />
        <StatCard
          icon={<UserCheck className="w-8 h-8" />}
          value={summary.matchesByRole}
          label="coincidencias"
          subLabel="por rol"
        />
        <StatCard
          icon={<Clock className="w-8 h-8" />}
          value={summary.averageExperience.toFixed(1)}
          label="promedio de"
          subLabel="experiencia"
        />
      </div>

      {/* Top Skills (opcional, mostrar si hay datos) */}
      {summary.topSkills && summary.topSkills.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Skills más comunes</h3>
          <div className="flex flex-wrap gap-2">
            {summary.topSkills.slice(0, 8).map((item) => (
              <span
                key={item.skill}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
              >
                {item.skill}
                <span className="text-blue-400 text-xs">({item.count})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Distribución por ubicación (opcional) */}
      {summary.locationDistribution && summary.locationDistribution.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Distribución por ubicación</h3>
          <div className="space-y-2">
            {summary.locationDistribution.slice(0, 5).map((item) => {
              const percentage = (item.count / summary.totalCandidates) * 100;
              return (
                <div key={item.location} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 w-24 truncate">{item.location}</span>
                  <div className="flex-1 bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 w-8 text-right">{item.count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

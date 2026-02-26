/**
 * Reports Page - Generates PDF reports with styled headers.
 * Available to evaluators and super admins.
 */
import React, { useState, useEffect, useMemo } from 'react';
import { reportService } from '../../services/reportService';
import { modalityService } from '../../services/modalityService';
import { competitorService } from '../../services/competitorService';
import { enrollmentService } from '../../services/enrollmentService';
import { usePlatformSettingsStore, selectLogoUrl, selectPlatformName } from '../../stores/platformSettingsStore';
import { useAuthStore } from '../../stores';
import type { Modality, Competitor } from '../../types';
import type { PDFHeaderOptions } from '../../utils/pdfGenerator';

type ReportType =
  | 'competitor'
  | 'modality'
  | 'attendance'
  | 'ranking'
  | 'training_hours'
  | 'general';

type AttendanceFilter = 'senai' | 'external' | 'all';

interface ReportConfig {
  type: ReportType;
  label: string;
  description: string;
  icon: React.ReactNode;
  requiresModality: boolean;
  requiresCompetitor: boolean;
  hasAttendanceFilter: boolean;
  hasDateFilter: boolean;
}

const REPORT_CONFIGS: ReportConfig[] = [
  {
    type: 'competitor',
    label: 'Por Competidor',
    description: 'Relatório completo com treinamentos, notas e evolução de um competidor.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
    requiresModality: false,
    requiresCompetitor: true,
    hasAttendanceFilter: false,
    hasDateFilter: true,
  },
  {
    type: 'modality',
    label: 'Por Modalidade',
    description: 'Visão geral da modalidade com todos os competidores, médias e horas.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    requiresModality: true,
    requiresCompetitor: false,
    hasAttendanceFilter: false,
    hasDateFilter: false,
  },
  {
    type: 'attendance',
    label: 'Presença',
    description: 'Relatório de presença/frequência com filtro por tipo (SENAI, Externo ou Ambos).',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
    requiresModality: false,
    requiresCompetitor: false,
    hasAttendanceFilter: true,
    hasDateFilter: true,
  },
  {
    type: 'ranking',
    label: 'Ranking',
    description: 'Ranking de competidores por modalidade, ordenados pela média de notas.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
      </svg>
    ),
    requiresModality: true,
    requiresCompetitor: false,
    hasAttendanceFilter: false,
    hasDateFilter: false,
  },
  {
    type: 'training_hours',
    label: 'Horas de Treinamento',
    description: 'Detalhamento de horas por competidor, com divisão SENAI vs Externo.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    requiresModality: false,
    requiresCompetitor: false,
    hasAttendanceFilter: false,
    hasDateFilter: true,
  },
  {
    type: 'general',
    label: 'Relatório Geral',
    description: 'Visão geral de todas as modalidades, competidores e estatísticas da plataforma.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    requiresModality: false,
    requiresCompetitor: false,
    hasAttendanceFilter: false,
    hasDateFilter: false,
  },
];

const ReportsPage: React.FC = () => {
  // Platform settings
  const logoUrl = usePlatformSettingsStore(selectLogoUrl);
  const platformName = usePlatformSettingsStore(selectPlatformName);

  // Auth - role check
  const user = useAuthStore((state) => state.user);
  const isAdmin = user?.role === 'super_admin';

  // Data
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);

  // Selected report and filters
  const [selectedReport, setSelectedReport] = useState<ReportType | null>(null);
  const [selectedModality, setSelectedModality] = useState<string>('');
  const [selectedCompetitor, setSelectedCompetitor] = useState<string>('');
  const [attendanceFilter, setAttendanceFilter] = useState<AttendanceFilter>('all');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // State
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load modalities on mount - filtered by role
  useEffect(() => {
    const loadData = async () => {
      try {
        if (isAdmin) {
          // Admin sees all modalities
          const mods = await modalityService.getAll({ active_only: true });
          setModalities(mods);
        } else {
          // Evaluator sees only their assigned modalities
          const evalMods = await enrollmentService.getMyModalities();
          // getMyModalities returns modality objects; map to Modality type
          const mods: Modality[] = (evalMods || []).map((m: any) => ({
            id: m.id,
            name: m.name,
            code: m.code,
            description: m.description || '',
            is_active: m.is_active ?? true,
            created_at: m.created_at || '',
            updated_at: m.updated_at || '',
          }));
          setModalities(mods);
        }
      } catch (err) {
        console.error('Error loading modalities:', err);
      }
    };
    loadData();
  }, [isAdmin]);

  // Load competitors when modality changes - filtered by role
  useEffect(() => {
    const loadCompetitors = async () => {
      try {
        if (selectedModality) {
          const response = await competitorService.getByModality(selectedModality);
          setCompetitors(response.competitors || []);
        } else if (isAdmin) {
          // Admin can see all competitors
          const response = await competitorService.getAll({ limit: 1000, active_only: true });
          setCompetitors(response.competitors || []);
        } else {
          // Evaluator: load competitors only from their modalities
          const allCompetitors: Competitor[] = [];
          const seenIds = new Set<string>();
          for (const mod of modalities) {
            const response = await competitorService.getByModality(mod.id);
            for (const c of response.competitors || []) {
              if (!seenIds.has(c.id)) {
                seenIds.add(c.id);
                allCompetitors.push(c);
              }
            }
          }
          setCompetitors(allCompetitors);
        }
      } catch (err) {
        console.error('Error loading competitors:', err);
      }
    };
    loadCompetitors();
  }, [selectedModality, isAdmin, modalities]);

  const getHeaderOptions = (): PDFHeaderOptions => ({
    title: '',
    logoUrl,
    platformName,
  });

  // Filter report types by role - "Relatório Geral" only for admin
  const availableReports = useMemo(
    () => (isAdmin ? REPORT_CONFIGS : REPORT_CONFIGS.filter((r) => r.type !== 'general')),
    [isAdmin]
  );

  const selectedConfig = REPORT_CONFIGS.find((r) => r.type === selectedReport);

  const canGenerate = (): boolean => {
    if (!selectedReport) return false;
    if (selectedConfig?.requiresModality && !selectedModality) return false;
    if (selectedConfig?.requiresCompetitor && !selectedCompetitor) return false;
    return true;
  };

  const handleGenerate = async () => {
    if (!canGenerate() || !selectedReport) return;

    setIsGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      const headerOptions = getHeaderOptions();

      switch (selectedReport) {
        case 'competitor':
          await reportService.generateCompetitor(
            selectedCompetitor,
            selectedModality || undefined,
            headerOptions
          );
          break;

        case 'modality':
          await reportService.generateModality(selectedModality, headerOptions);
          break;

        case 'attendance':
          await reportService.generateAttendance(
            {
              modalityId: selectedModality || undefined,
              trainingType: attendanceFilter,
              startDate: startDate || undefined,
              endDate: endDate || undefined,
            },
            headerOptions
          );
          break;

        case 'ranking':
          await reportService.generateRanking(selectedModality, headerOptions);
          break;

        case 'training_hours':
          await reportService.generateTrainingHours(
            {
              modalityId: selectedModality || undefined,
              startDate: startDate || undefined,
              endDate: endDate || undefined,
            },
            headerOptions
          );
          break;

        case 'general':
          await reportService.generateGeneral(headerOptions);
          break;
      }

      setSuccess('Relatório gerado com sucesso! O download foi iniciado automaticamente.');
    } catch (err: any) {
      console.error('Error generating report:', err);
      setError(err?.message || 'Erro ao gerar o relatório. Tente novamente.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Relatórios</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Gere relatórios em PDF com dados detalhados de treinamentos, notas e competidores.
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-3">
          <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-green-700 dark:text-green-300">{success}</p>
          <button onClick={() => setSuccess(null)} className="ml-auto text-green-500 hover:text-green-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Step 1: Select Report Type */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          1. Selecione o tipo de relatório
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableReports.map((config) => (
            <button
              key={config.type}
              onClick={() => {
                setSelectedReport(config.type);
                setError(null);
                setSuccess(null);
              }}
              className={`p-5 rounded-xl border-2 text-left transition-all duration-200 ${
                selectedReport === config.type
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm'
              }`}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`p-2 rounded-lg ${
                    selectedReport === config.type
                      ? 'bg-blue-100 text-blue-600 dark:bg-blue-800 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
                  }`}
                >
                  {config.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3
                    className={`font-semibold ${
                      selectedReport === config.type
                        ? 'text-blue-700 dark:text-blue-300'
                        : 'text-gray-900 dark:text-white'
                    }`}
                  >
                    {config.label}
                  </h3>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                    {config.description}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Filters */}
      {selectedReport && (
        <div className="mb-8 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            2. Configure os filtros
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Modality filter */}
            {(selectedConfig?.requiresModality || selectedReport !== 'general') &&
              selectedReport !== 'competitor' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Modalidade{selectedConfig?.requiresModality && ' *'}
                  </label>
                  <select
                    value={selectedModality}
                    onChange={(e) => setSelectedModality(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {selectedConfig?.requiresModality ? (
                      <option value="">Selecione uma modalidade...</option>
                    ) : isAdmin ? (
                      <option value="">Todas as modalidades</option>
                    ) : (
                      <option value="">Todas as suas modalidades</option>
                    )}
                    {modalities.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name} ({m.code})
                      </option>
                    ))}
                  </select>
                </div>
              )}

            {/* Competitor filter */}
            {selectedConfig?.requiresCompetitor && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Modalidade (filtro)
                  </label>
                  <select
                    value={selectedModality}
                    onChange={(e) => setSelectedModality(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">
                      {isAdmin ? 'Todas as modalidades' : 'Todas as suas modalidades'}
                    </option>
                    {modalities.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name} ({m.code})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Competidor *
                  </label>
                  <select
                    value={selectedCompetitor}
                    onChange={(e) => setSelectedCompetitor(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Selecione um competidor...</option>
                    {competitors.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.full_name}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            {/* Attendance filter */}
            {selectedConfig?.hasAttendanceFilter && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tipo de Treinamento
                </label>
                <div className="flex gap-2">
                  {[
                    { value: 'all' as AttendanceFilter, label: 'Ambos' },
                    { value: 'senai' as AttendanceFilter, label: 'SENAI' },
                    { value: 'external' as AttendanceFilter, label: 'Externo' },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setAttendanceFilter(opt.value)}
                      className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        attendanceFilter === opt.value
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Date filters */}
            {selectedConfig?.hasDateFilter && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Data Início
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Data Fim
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </>
            )}
          </div>

          {/* Generate Button */}
          <div className="mt-6 flex items-center gap-4">
            <button
              onClick={handleGenerate}
              disabled={!canGenerate() || isGenerating}
              className={`inline-flex items-center gap-2 px-6 py-3 rounded-lg text-white font-medium transition-all duration-200 ${
                canGenerate() && !isGenerating
                  ? 'bg-blue-600 hover:bg-blue-700 shadow-sm hover:shadow-md'
                  : 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
              }`}
            >
              {isGenerating ? (
                <>
                  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Gerando relatório...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Gerar PDF
                </>
              )}
            </button>

            {!canGenerate() && selectedReport && (
              <p className="text-sm text-amber-600 dark:text-amber-400">
                {selectedConfig?.requiresModality && !selectedModality
                  ? 'Selecione uma modalidade para gerar o relatório.'
                  : selectedConfig?.requiresCompetitor && !selectedCompetitor
                    ? 'Selecione um competidor para gerar o relatório.'
                    : ''}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Report descriptions info card */}
      {!selectedReport && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-semibold text-blue-800 dark:text-blue-300">
                Como usar os relatórios
              </h3>
              <ul className="mt-2 text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <li>1. Selecione o tipo de relatório desejado acima</li>
                <li>2. Configure os filtros (modalidade, competidor, datas)</li>
                <li>3. Clique em "Gerar PDF" para baixar o relatório</li>
              </ul>
              <div className="mt-3 text-sm text-blue-600 dark:text-blue-400">
                <strong>Tipos disponíveis:</strong>
                <ul className="mt-1 space-y-1 ml-4 list-disc">
                  <li><strong>Por Competidor</strong> - Dados individuais com treinamentos e notas</li>
                  <li><strong>Por Modalidade</strong> - Visão geral com todos os competidores</li>
                  <li><strong>Presença</strong> - Frequência de treinos (SENAI/Externo/Ambos)</li>
                  <li><strong>Ranking</strong> - Classificação por média de notas</li>
                  <li><strong>Horas de Treinamento</strong> - Detalhamento de horas por competidor</li>
                  <li><strong>Relatório Geral</strong> - Panorama completo da plataforma</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsPage;

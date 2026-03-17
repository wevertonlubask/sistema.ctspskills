import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Card, CardHeader, CardBody, Spinner, Alert, Badge } from '../../components/ui';
import {
  analyticsService,
  competitorService,
  modalityService,
  enrollmentService,
} from '../../services';
import { useAuthStore } from '../../stores';
import type { Competitor, Competence, CompetenceEvolutionData } from '../../types';

const SERIES_COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
  '#8B5CF6', '#EC4899', '#06B6D4', '#F97316',
];

type ViewMode = 'geral' | 'criterio' | 'sub_criterio';

interface ModalityOption {
  id: string;
  name: string;
}

// ─── Tooltip customizado ────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg p-3 text-sm min-w-[160px]">
      <p className="font-semibold text-gray-800 dark:text-gray-100 mb-2 truncate max-w-[200px]">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center justify-between gap-4 py-0.5">
          <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-300">
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
            {entry.name}
          </span>
          <span className="font-bold" style={{ color: entry.color }}>{entry.value}</span>
        </div>
      ))}
    </div>
  );
};

// ─── Main page ───────────────────────────────────────────────────────────────
const CompetitorEvolutionPage: React.FC = () => {
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'super_admin';
  const isEvaluatorOrAdmin = isAdmin || user?.role === 'evaluator';

  // View mode
  const [viewMode, setViewMode] = useState<ViewMode>('geral');

  // Selectors state
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [modalities, setModalities] = useState<ModalityOption[]>([]);
  const [competences, setCompetences] = useState<Competence[]>([]);
  // Modalities the current evaluator belongs to (used to filter competitor modalities)
  const [myModalityIds, setMyModalityIds] = useState<Set<string>>(new Set());

  const [selectedCompetitorId, setSelectedCompetitorId] = useState<string>('');
  const [selectedModalityId, setSelectedModalityId] = useState<string>('');
  const [selectedCompetenceId, setSelectedCompetenceId] = useState<string>('');
  const [selectedSubId, setSelectedSubId] = useState<string>('');
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<Set<string>>(new Set());

  // Data state
  const [evolutionData, setEvolutionData] = useState<CompetenceEvolutionData | null>(null);
  const [isLoadingInit, setIsLoadingInit] = useState(true);
  const [isLoadingModalities, setIsLoadingModalities] = useState(false);
  const [isLoadingEvolution, setIsLoadingEvolution] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Load initial data ────────────────────────────────────────────────────
  useEffect(() => {
    const init = async () => {
      try {
        setIsLoadingInit(true);
        if (isAdmin) {
          // Admin: see all competitors
          const compResp = await competitorService.getAll({ limit: 500 });
          setCompetitors(compResp.competitors || []);
        } else if (isEvaluatorOrAdmin) {
          // Evaluator: only competitors from their modalities
          const mods = await enrollmentService.getMyModalities();
          const modIds = new Set<string>((mods || []).map((m: any) => m.id as string));
          setMyModalityIds(modIds);
          const seen = new Set<string>();
          const allCompetitors: Competitor[] = [];
          for (const mod of (mods || [])) {
            const resp = await competitorService.getByModality(mod.id);
            for (const c of resp.competitors || []) {
              if (!seen.has(c.id)) {
                seen.add(c.id);
                allCompetitors.push(c);
              }
            }
          }
          setCompetitors(allCompetitors);
        } else {
          // Competitor role: auto-load own profile + modalities
          const [profile, mods] = await Promise.all([
            competitorService.getMe(),
            enrollmentService.getMyModalities(),
          ]);
          if (profile) setSelectedCompetitorId(profile.id);
          const modOpts: ModalityOption[] = (mods || []).map((m: any) => ({
            id: m.id,
            name: m.name,
          }));
          setModalities(modOpts);
          if (modOpts.length === 1) setSelectedModalityId(modOpts[0].id);
        }
      } catch {
        setError('Erro ao carregar dados iniciais.');
      } finally {
        setIsLoadingInit(false);
      }
    };
    init();
  }, [isAdmin, isEvaluatorOrAdmin]);

  // ── Auto-fill modality when evaluator selects a competitor ──────────────
  const handleCompetitorChange = useCallback(
    async (competitorId: string) => {
      setSelectedCompetitorId(competitorId);
      setSelectedModalityId('');
      setSelectedCompetenceId('');
      setSelectedSubId('');
      setEvolutionData(null);
      setModalities([]);

      if (!competitorId) return;

      try {
        setIsLoadingModalities(true);
        const resp = await enrollmentService.getByCompetitor(competitorId);
        const seen = new Set<string>();
        const mods: ModalityOption[] = (resp.enrollments || [])
          .filter((e) => {
            if (seen.has(e.modality_id)) return false;
            seen.add(e.modality_id);
            // Evaluator: restrict to their own modalities; admin sees all
            if (!isAdmin && myModalityIds.size > 0 && !myModalityIds.has(e.modality_id)) return false;
            return true;
          })
          .map((e) => ({ id: e.modality_id, name: `${e.modality_name}` }));
        setModalities(mods);
        if (mods.length === 1) setSelectedModalityId(mods[0].id);
      } catch {
        setModalities([]);
      } finally {
        setIsLoadingModalities(false);
      }
    },
    [isAdmin, myModalityIds],
  );

  // ── Load competences when modality changes ───────────────────────────────
  useEffect(() => {
    if (!selectedModalityId) {
      setCompetences([]);
      setSelectedCompetenceId('');
      setEvolutionData(null);
      return;
    }
    modalityService.getCompetences(selectedModalityId).then(setCompetences).catch(() => setCompetences([]));
    setSelectedCompetenceId('');
    setEvolutionData(null);
  }, [selectedModalityId]);

  // ── Reset sub-criteria when competence or mode changes ───────────────────
  useEffect(() => {
    setSelectedSubId('');
    setEvolutionData(null);
  }, [selectedCompetenceId, viewMode]);

  // ── Load evolution ───────────────────────────────────────────────────────
  const loadEvolution = useCallback(async () => {
    if (!selectedCompetitorId) return;
    if ((viewMode === 'criterio' || viewMode === 'sub_criterio') && !selectedCompetenceId) return;

    try {
      setIsLoadingEvolution(true);
      setError(null);
      let data: CompetenceEvolutionData;
      if (viewMode === 'geral') {
        data = await analyticsService.getTotalEvolution(
          selectedCompetitorId,
          selectedModalityId || undefined,
        );
      } else {
        data = await analyticsService.getCompetenceEvolution(
          selectedCompetitorId,
          selectedCompetenceId,
          selectedModalityId || undefined,
        );
      }
      setEvolutionData(data);
      // No modo 'criterio' com sub-critérios, displaySeries retorna label=competence_name
      // (série agregada), não os labels brutos das sub-séries.
      if (viewMode === 'criterio' && data.has_sub_competences) {
        setSelectedSeriesIds(new Set([data.competence_name]));
      } else {
        setSelectedSeriesIds(new Set(data.series.map((s) => s.label)));
      }
      // Default sub-criteria to first series
      if (viewMode === 'sub_criterio' && data.has_sub_competences && data.series.length > 0) {
        setSelectedSubId(data.series[0].sub_competence_id ?? data.series[0].label);
      }
    } catch {
      setError('Erro ao carregar dados de evolução.');
      setEvolutionData(null);
    } finally {
      setIsLoadingEvolution(false);
    }
  }, [selectedCompetitorId, selectedCompetenceId, selectedModalityId, viewMode]);

  useEffect(() => {
    loadEvolution();
  }, [loadEvolution]);

  // ── Derive display series from evolutionData + viewMode ──────────────────
  const displaySeries = useMemo(() => {
    if (!evolutionData) return [];
    const { series, has_sub_competences, competence_name, max_score } = evolutionData;

    if (viewMode === 'geral' || !has_sub_competences) {
      return series;
    }

    if (viewMode === 'criterio') {
      // Aggregate all sub-criteria per exam → single series (average, not sum)
      const examMap = new Map<
        string,
        { exam_id: string; exam_name: string; exam_date: string; total: number; count: number }
      >();
      series.forEach((s) => {
        s.points.forEach((p) => {
          const ex = examMap.get(p.exam_id);
          if (ex) {
            ex.total += p.score;
            ex.count += 1;
          } else {
            examMap.set(p.exam_id, {
              exam_id: p.exam_id,
              exam_name: p.exam_name,
              exam_date: p.exam_date,
              total: p.score,
              count: 1,
            });
          }
        });
      });
      const points = Array.from(examMap.values())
        .sort((a, b) => new Date(a.exam_date).getTime() - new Date(b.exam_date).getTime())
        .map((e) => ({
          exam_id: e.exam_id,
          exam_name: e.exam_name,
          exam_date: e.exam_date,
          score: e.count > 0 ? e.total / e.count : 0,
        }));
      return [{ label: competence_name, sub_competence_id: null, max_score, points }];
    }

    if (viewMode === 'sub_criterio') {
      // Show only the selected sub-criteria
      const selected = series.find(
        (s) => s.sub_competence_id === selectedSubId || s.label === selectedSubId,
      );
      return selected ? [selected] : series;
    }

    return series;
  }, [evolutionData, viewMode, selectedSubId]);

  // ── Chart max_score for Y axis ────────────────────────────────────────────
  const chartMaxScore = useMemo(() => {
    if (!evolutionData) return 100;
    if (viewMode === 'sub_criterio' && displaySeries.length > 0) {
      return displaySeries[0].max_score;
    }
    return evolutionData.max_score;
  }, [evolutionData, viewMode, displaySeries]);

  // ── Build chart data from displaySeries ───────────────────────────────────
  const chartData = useMemo(() => {
    if (!displaySeries.length) return [];
    const examMap = new Map<string, { examName: string; examDate: string }>();
    displaySeries.forEach((s) => {
      s.points.forEach((p) => {
        if (!examMap.has(p.exam_id)) {
          examMap.set(p.exam_id, { examName: p.exam_name, examDate: p.exam_date });
        }
      });
    });
    const sortedExams = Array.from(examMap.entries()).sort(
      ([, a], [, b]) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime(),
    );
    return sortedExams.map(([examId, { examName }]) => {
      const row: Record<string, any> = { name: examName };
      displaySeries.forEach((s) => {
        const point = s.points.find((p) => p.exam_id === examId);
        row[s.label] = point ? point.score : null;
      });
      return row;
    });
  }, [displaySeries]);

  // ── Stats per display series ──────────────────────────────────────────────
  const seriesStats = useMemo(() => {
    return displaySeries.map((s) => {
      const scores = s.points.map((p) => p.score);
      if (!scores.length) return { label: s.label, max_score: s.max_score, avg: null, best: null, last: null, count: 0 };
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      const best = Math.max(...scores);
      const last = scores[scores.length - 1];
      return { label: s.label, max_score: s.max_score, avg: +avg.toFixed(2), best, last, count: scores.length };
    });
  }, [displaySeries]);

  const totalExams = chartData.length;

  // ── Render ─────────────────────────────────────────────────────────────────
  if (isLoadingInit) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const VIEW_MODES: { value: ViewMode; label: string }[] = [
    { value: 'geral', label: 'Nota Geral' },
    { value: 'criterio', label: 'Por Critério' },
    { value: 'sub_criterio', label: 'Por Sub Critério' },
  ];

  // Label shown in the chart card header
  const chartTitle =
    evolutionData
      ? viewMode === 'geral'
        ? 'Nota Geral (todos os critérios)'
        : viewMode === 'sub_criterio' && displaySeries.length > 0
          ? displaySeries[0].label
          : evolutionData.competence_name
      : '—';

  const needsCompetence = viewMode === 'criterio' || viewMode === 'sub_criterio';
  const subCriteriaOptions = evolutionData?.has_sub_competences ? (evolutionData?.series ?? []) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Evolução por Critério</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Acompanhe a evolução das notas ao longo das avaliações.
          </p>
        </div>
        {evolutionData && (
          <Badge variant="info" className="self-start sm:self-auto">
            {totalExams} {totalExams === 1 ? 'avaliação' : 'avaliações'}
          </Badge>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardBody>
          {/* View mode segmented control */}
          <div className="mb-4">
            <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">
              Modo de visualização
            </label>
            <div className="inline-flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1 gap-0.5">
              {VIEW_MODES.map((m) => (
                <button
                  key={m.value}
                  onClick={() => setViewMode(m.value)}
                  className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${
                    viewMode === m.value
                      ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          {/* Filter selectors */}
          <div className={`grid grid-cols-1 gap-4 ${
            isEvaluatorOrAdmin
              ? needsCompetence
                ? viewMode === 'sub_criterio'
                  ? 'sm:grid-cols-2 lg:grid-cols-4'
                  : 'sm:grid-cols-2 lg:grid-cols-3'
                : 'sm:grid-cols-2'
              : needsCompetence
                ? viewMode === 'sub_criterio'
                  ? 'sm:grid-cols-2 lg:grid-cols-3'
                  : 'sm:grid-cols-2 lg:grid-cols-3'
                : 'sm:grid-cols-2'
          }`}>
            {/* Competitor (evaluator/admin only) */}
            {isEvaluatorOrAdmin && (
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-1.5">
                  Competidor
                </label>
                <select
                  value={selectedCompetitorId}
                  onChange={(e) => handleCompetitorChange(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Selecione um competidor...</option>
                  {competitors.map((c) => (
                    <option key={c.id} value={c.id}>{c.full_name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Modality */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-1.5">
                Modalidade
              </label>
              <div className="relative">
                <select
                  value={selectedModalityId}
                  onChange={(e) => setSelectedModalityId(e.target.value)}
                  disabled={isEvaluatorOrAdmin && (!selectedCompetitorId || isLoadingModalities)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="">
                    {isLoadingModalities ? 'Carregando...' : 'Todas as modalidades'}
                  </option>
                  {modalities.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Competence (criterio / sub_criterio modes) */}
            {needsCompetence && (
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-1.5">
                  Critério de Avaliação
                </label>
                <select
                  value={selectedCompetenceId}
                  onChange={(e) => setSelectedCompetenceId(e.target.value)}
                  disabled={competences.length === 0}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="">Selecione um critério...</option>
                  {competences.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} (0–{c.max_score})</option>
                  ))}
                </select>
              </div>
            )}

            {/* Sub-criteria selector (sub_criterio mode only) */}
            {viewMode === 'sub_criterio' && (
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-1.5">
                  Sub Critério
                </label>
                <select
                  value={selectedSubId}
                  onChange={(e) => setSelectedSubId(e.target.value)}
                  disabled={subCriteriaOptions.length === 0}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {subCriteriaOptions.length === 0 ? (
                    <option value="">
                      {!selectedCompetenceId
                        ? 'Selecione um critério primeiro'
                        : evolutionData && !evolutionData.has_sub_competences
                          ? 'Critério sem sub critérios'
                          : 'Carregando...'}
                    </option>
                  ) : (
                    subCriteriaOptions.map((s) => (
                      <option
                        key={s.sub_competence_id ?? s.label}
                        value={s.sub_competence_id ?? s.label}
                      >
                        {s.label} (0–{s.max_score})
                      </option>
                    ))
                  )}
                </select>
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {error && <Alert type="error">{error}</Alert>}

      {/* Loading */}
      {(isLoadingEvolution || isLoadingModalities) && (
        <div className="flex justify-center items-center h-48">
          <Spinner size="lg" />
        </div>
      )}

      {/* Empty state */}
      {!isLoadingEvolution && !isLoadingModalities && !evolutionData && !error && (
        <Card>
          <CardBody>
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-300 font-medium">
                {!selectedCompetitorId
                  ? 'Selecione um competidor para começar'
                  : needsCompetence && !selectedCompetenceId
                    ? 'Selecione um critério de avaliação'
                    : 'Nenhum dado encontrado para os filtros selecionados'}
              </p>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                {selectedCompetitorId && needsCompetence && !selectedCompetenceId &&
                  'Escolha uma modalidade e um critério no painel acima.'}
              </p>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Data loaded */}
      {!isLoadingEvolution && !isLoadingModalities && evolutionData && (
        <>
          {/* Chart card */}
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold text-gray-900 dark:text-white">
                    {chartTitle}
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {evolutionData.competitor_name}
                    {viewMode !== 'geral' && (
                      <> · Pontuação máxima: {chartMaxScore}</>
                    )}
                    {viewMode === 'geral' && (
                      <> · Pontuação máxima: {evolutionData.max_score}</>
                    )}
                    {viewMode === 'criterio' && evolutionData.has_sub_competences && (
                      <span className="ml-2 px-1.5 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-[10px] font-semibold rounded-full uppercase">
                        agregado
                      </span>
                    )}
                  </p>
                </div>

                {/* Series toggles (only shown when displaying multiple series) */}
                {displaySeries.length > 1 && (
                  <div className="flex flex-wrap gap-2">
                    {displaySeries.map((s, i) => {
                      const active = selectedSeriesIds.has(s.label);
                      const color = SERIES_COLORS[i % SERIES_COLORS.length];
                      return (
                        <button
                          key={s.label}
                          onClick={() => {
                            setSelectedSeriesIds((prev) => {
                              const next = new Set(prev);
                              if (next.has(s.label)) {
                                if (next.size > 1) next.delete(s.label);
                              } else {
                                next.add(s.label);
                              }
                              return next;
                            });
                          }}
                          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-all ${
                            active
                              ? 'border-transparent text-white shadow-sm'
                              : 'border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800'
                          }`}
                          style={active ? { backgroundColor: color } : {}}
                          title={`${s.label} (máx ${s.max_score})`}
                        >
                          <span
                            className="w-2 h-2 rounded-full flex-shrink-0"
                            style={{ backgroundColor: active ? 'rgba(255,255,255,0.7)' : color }}
                          />
                          {s.label}
                          <span className={`${active ? 'text-white/70' : 'text-gray-400'} text-[9px]`}>
                            /{s.max_score}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardBody>
              {totalExams === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <p className="text-gray-500 dark:text-gray-400">
                    Nenhuma nota registrada ainda.
                  </p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={360}>
                  <LineChart data={chartData} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="currentColor" className="text-gray-200 dark:text-gray-700" opacity={0.5} />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 11, fill: 'currentColor' }}
                      className="text-gray-500 dark:text-gray-400"
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      domain={[0, chartMaxScore]}
                      tick={{ fontSize: 11, fill: 'currentColor' }}
                      className="text-gray-500 dark:text-gray-400"
                      tickLine={false}
                      axisLine={false}
                      width={36}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend
                      wrapperStyle={{ fontSize: 12, paddingTop: 12 }}
                      formatter={(value) => <span className="text-gray-600 dark:text-gray-300">{value}</span>}
                    />
                    <ReferenceLine
                      y={chartMaxScore}
                      stroke="#E5E7EB"
                      strokeDasharray="4 4"
                      label={{ value: `máx ${chartMaxScore}`, position: 'right', fontSize: 10, fill: '#9CA3AF' }}
                    />
                    {displaySeries
                      .filter((s) => selectedSeriesIds.has(s.label))
                      .map((s, i) => {
                        const color = SERIES_COLORS[i % SERIES_COLORS.length];
                        return (
                          <Line
                            key={s.label}
                            type="monotone"
                            dataKey={s.label}
                            stroke={color}
                            strokeWidth={2.5}
                            dot={{ r: 5, fill: color, strokeWidth: 2, stroke: '#fff' }}
                            activeDot={{ r: 7 }}
                            connectNulls={false}
                          />
                        );
                      })}
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardBody>
          </Card>

          {/* Stats cards */}
          {(() => {
            const visibleStats = seriesStats.filter((s) => s.count > 0);
            if (!visibleStats.length) return null;

            // Card único → largura total, layout horizontal
            if (visibleStats.length === 1) {
              const s = visibleStats[0];
              const color = SERIES_COLORS[0];
              const pct = s.avg !== null ? Math.round((s.avg / s.max_score) * 100) : 0;
              const pctBest = s.best !== null ? Math.round((s.best / s.max_score) * 100) : 0;
              const pctLast = s.last !== null ? Math.round((s.last / s.max_score) * 100) : 0;
              return (
                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
                  {/* Barra de cor no topo */}
                  <div className="h-1" style={{ backgroundColor: color }} />
                  <div className="px-6 py-5">
                    {/* Título + badges */}
                    <div className="flex flex-wrap items-center gap-3 mb-5">
                      <span className="text-base font-semibold text-gray-800 dark:text-gray-100">{s.label}</span>
                      <span className="text-xs font-medium text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                        máx {s.max_score}
                      </span>
                      <span className="text-xs font-medium text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                        {s.count} {s.count === 1 ? 'avaliação' : 'avaliações'}
                      </span>
                    </div>

                    {/* Stats horizontais */}
                    <div className="grid grid-cols-3 gap-6 mb-5">
                      {/* Média */}
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                          <span className="font-medium uppercase tracking-wide">Média</span>
                          <span className="font-semibold text-gray-700 dark:text-gray-200">{pct}%</span>
                        </div>
                        <div className="flex items-end gap-3">
                          <span className="text-3xl font-bold text-gray-900 dark:text-white leading-none">{s.avg ?? '–'}</span>
                          <span className="text-sm text-gray-400 mb-0.5">/ {s.max_score}</span>
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                          <div className="h-2 rounded-full transition-all" style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }} />
                        </div>
                      </div>

                      {/* Melhor */}
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                          <span className="font-medium uppercase tracking-wide">Melhor</span>
                          <span className="font-semibold text-emerald-600 dark:text-emerald-400">{pctBest}%</span>
                        </div>
                        <div className="flex items-end gap-3">
                          <span className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 leading-none">{s.best ?? '–'}</span>
                          <span className="text-sm text-gray-400 mb-0.5">/ {s.max_score}</span>
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                          <div className="h-2 rounded-full transition-all bg-emerald-500" style={{ width: `${Math.min(pctBest, 100)}%` }} />
                        </div>
                      </div>

                      {/* Último */}
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                          <span className="font-medium uppercase tracking-wide">Último</span>
                          <span className="font-semibold text-blue-600 dark:text-blue-400">{pctLast}%</span>
                        </div>
                        <div className="flex items-end gap-3">
                          <span className="text-3xl font-bold text-blue-600 dark:text-blue-400 leading-none">{s.last ?? '–'}</span>
                          <span className="text-sm text-gray-400 mb-0.5">/ {s.max_score}</span>
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                          <div className="h-2 rounded-full transition-all bg-blue-500" style={{ width: `${Math.min(pctLast, 100)}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }

            // Múltiplos cards → grid
            return (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {visibleStats.map((s, i) => {
                  const color = SERIES_COLORS[i % SERIES_COLORS.length];
                  const pct = s.avg !== null ? Math.round((s.avg / s.max_score) * 100) : 0;
                  return (
                    <div
                      key={s.label}
                      className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden"
                    >
                      <div className="h-1.5" style={{ backgroundColor: color }} />
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">{s.label}</span>
                          <span className="text-[10px] font-medium text-gray-400 bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded-full ml-2 flex-shrink-0">
                            máx {s.max_score}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-center">
                          <div>
                            <p className="text-xs text-gray-400 dark:text-gray-500">Média</p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">{s.avg ?? '–'}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400 dark:text-gray-500">Melhor</p>
                            <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{s.best ?? '–'}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400 dark:text-gray-500">Último</p>
                            <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{s.last ?? '–'}</p>
                          </div>
                        </div>
                        <div className="mt-3">
                          <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                            <span>Aproveitamento médio</span>
                            <span>{pct}%</span>
                          </div>
                          <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full transition-all" style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }} />
                          </div>
                        </div>
                        <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-2 text-right">
                          {s.count} {s.count === 1 ? 'avaliação' : 'avaliações'}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </>
      )}
    </div>
  );
};

export default CompetitorEvolutionPage;

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Card, CardHeader, CardBody, Button, Badge, Select, Spinner, Alert, Input, Modal } from '../../components/ui';
import { EvolutionChart } from '../../components/charts/EvolutionChart';
import { CompetitorSelect } from '../../components/forms/CompetitorSelect';
import { examService, gradeService, competitorService, enrollmentService, examTimeService } from '../../services';
import type { Exam, Modality, Competitor, CompetitorTime } from '../../types';

interface SimuladoData {
  id: string;
  name: string;
  date: string;
  modality: string;
  modalityId: string;
  competitorsCount: number;
  averageScore: number;
  timeLimitMinutes: number | null;
}

interface CompetitorEvolution {
  competitorId: string;
  competitorName: string;
  data: Array<{
    examId: string;
    modalityId: string;
    simuladoName: string;
    date: string;
    score: number;
  }>;
}

interface CompetitorTimePoint {
  competitorId: string;
  competitorName: string;
  examId: string;
  simuladoName: string;
  date: string;
  modalityId: string;
  durationMinutes: number;
}

// Format minutes as "h:mm"
const fmtTime = (minutes: number) => {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}:${String(m).padStart(2, '0')}`;
};

// Parse "h:mm" to minutes
const parseTimeInput = (str: string): number | null => {
  const trimmed = str.trim();
  if (!trimmed) return null;
  const parts = trimmed.split(':');
  if (parts.length === 1) {
    const m = parseInt(parts[0], 10);
    return isNaN(m) || m <= 0 ? null : m;
  }
  const h = parseInt(parts[0], 10);
  const m = parseInt(parts[1], 10);
  if (isNaN(h) || isNaN(m) || m < 0 || m > 59 || h < 0) return null;
  return h * 60 + m;
};

type DashboardView = 'notas' | 'tempo';

const SimuladosDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState<DashboardView>('notas');
  const [simulados, setSimulados] = useState<SimuladoData[]>([]);
  const [evolutionData, setEvolutionData] = useState<CompetitorEvolution[]>([]);
  const [timePoints, setTimePoints] = useState<CompetitorTimePoint[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [selectedModality, setSelectedModality] = useState<string>('all');
  const [selectedCompetitors, setSelectedCompetitors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Time limit config modal
  const [isTimeLimitModalOpen, setIsTimeLimitModalOpen] = useState(false);
  const [timeLimitExam, setTimeLimitExam] = useState<SimuladoData | null>(null);
  const [timeLimitInput, setTimeLimitInput] = useState('');
  const [isSavingTimeLimit, setIsSavingTimeLimit] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (simulados.length > 0) buildEvolutionData();
  }, [selectedModality]);

  // Re-fetch time data when switching to tempo tab
  useEffect(() => {
    if (activeView === 'tempo' && simulados.length > 0) {
      const simuladoExams = simulados.map(s => ({ id: s.id, exam_date: s.date, modality_id: s.modalityId, name: s.name } as any));
      fetchTimesData(simuladoExams, []);
    }
  }, [activeView]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const modalitiesData = await enrollmentService.getMyModalities();
      setModalities(modalitiesData || []);
      const myModalityIds = new Set(modalitiesData.map((m: Modality) => m.id));

      const examResponse = await examService.getAll({ active_only: true, limit: 500 });
      const allExams = (examResponse.exams || []).filter(
        (exam: Exam) => myModalityIds.has(exam.modality_id)
      );
      const simuladoExams = allExams.filter((e: Exam) => e.assessment_type === 'simulation');
      simuladoExams.sort((a: Exam, b: Exam) => new Date(a.exam_date).getTime() - new Date(b.exam_date).getTime());

      const simuladoDataPromises = simuladoExams.map(async (exam: Exam) => {
        try {
          const stats = await examService.getStatistics(exam.id);
          const modality = modalitiesData?.find((m: Modality) => m.id === exam.modality_id);
          return {
            id: exam.id,
            name: exam.name,
            date: exam.exam_date,
            modality: modality?.name || 'N/A',
            modalityId: exam.modality_id,
            competitorsCount: stats.total_competitors || 0,
            averageScore: stats.overall_average || 0,
            timeLimitMinutes: exam.time_limit_minutes ?? null,
          };
        } catch {
          const modality = modalitiesData?.find((m: Modality) => m.id === exam.modality_id);
          return {
            id: exam.id,
            name: exam.name,
            date: exam.exam_date,
            modality: modality?.name || 'N/A',
            modalityId: exam.modality_id,
            competitorsCount: 0,
            averageScore: 0,
            timeLimitMinutes: exam.time_limit_minutes ?? null,
          };
        }
      });

      const simuladosData = await Promise.all(simuladoDataPromises);
      setSimulados(simuladosData);

      await Promise.all([
        fetchGradesAndBuildEvolution(simuladoExams, modalitiesData || []),
        fetchTimesData(simuladoExams, modalitiesData || []),
      ]);

    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao carregar dados dos simulados');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchGradesAndBuildEvolution = async (simuladoExams: Exam[], _modalitiesData: Modality[]) => {
    try {
      const competitorGradesMap = new Map<string, Array<{ examId: string; examName: string; examDate: string; modalityId: string; score: number }>>();
      const competitorIdsSet = new Set<string>();

      for (const exam of simuladoExams) {
        try {
          const gradesResponse = await gradeService.getAll({ exam_id: exam.id, limit: 1000 });
          const grades = gradesResponse.grades || [];
          const competitorScores = new Map<string, number[]>();

          for (const grade of grades) {
            competitorIdsSet.add(grade.competitor_id);
            if (!competitorScores.has(grade.competitor_id)) competitorScores.set(grade.competitor_id, []);
            competitorScores.get(grade.competitor_id)!.push(grade.score);
          }

          competitorScores.forEach((scores, competitorId) => {
            const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
            if (!competitorGradesMap.has(competitorId)) competitorGradesMap.set(competitorId, []);
            competitorGradesMap.get(competitorId)!.push({
              examId: exam.id, examName: exam.name, examDate: exam.exam_date,
              modalityId: exam.modality_id, score: avgScore,
            });
          });
        } catch { /* ignore */ }
      }

      const competitorIds = Array.from(competitorIdsSet);
      const competitorsMap = new Map<string, Competitor>();
      for (const compId of competitorIds) {
        try {
          const competitor = await competitorService.getById(compId);
          competitorsMap.set(compId, competitor);
        } catch { /* ignore */ }
      }

      const evolution: CompetitorEvolution[] = [];
      competitorGradesMap.forEach((examsData, competitorId) => {
        const competitor = competitorsMap.get(competitorId);
        if (!competitor) return;
        examsData.sort((a, b) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime());
        evolution.push({
          competitorId: competitor.id,
          competitorName: competitor.full_name,
          data: examsData.map(ed => ({
            examId: ed.examId, modalityId: ed.modalityId,
            simuladoName: ed.examName, date: ed.examDate,
            score: Math.round(ed.score * 10) / 10,
          })),
        });
      });

      setEvolutionData(evolution);
      setSelectedCompetitors(evolution.map(e => e.competitorId));
    } catch { /* ignore */ }
  };

  const fetchTimesData = async (simuladoExams: Exam[], _modalitiesData: Modality[]) => {
    try {
      const competitorIdsSet = new Set<string>();
      const allPoints: Array<Omit<CompetitorTimePoint, 'competitorName'> & { competitorId: string }> = [];

      for (const exam of simuladoExams) {
        try {
          const times: CompetitorTime[] = await examTimeService.getTimes(exam.id);
          for (const t of times) {
            competitorIdsSet.add(t.competitor_id);
            allPoints.push({
              competitorId: t.competitor_id,
              examId: exam.id,
              simuladoName: exam.name,
              date: exam.exam_date,
              modalityId: exam.modality_id,
              durationMinutes: t.duration_minutes,
            });
          }
        } catch { /* ignore */ }
      }

      const competitorsMap = new Map<string, Competitor>();
      for (const compId of Array.from(competitorIdsSet)) {
        try {
          const c = await competitorService.getById(compId);
          competitorsMap.set(compId, c);
        } catch { /* ignore */ }
      }

      setTimePoints(allPoints.map(p => ({
        ...p,
        competitorName: competitorsMap.get(p.competitorId)?.full_name || p.competitorId,
      })));
    } catch { /* ignore */ }
  };

  const buildEvolutionData = () => {
    const competitorsWithData = evolutionData
      .filter(c => selectedModality === 'all' ? true : c.data.some(d => d.modalityId === selectedModality))
      .map(c => c.competitorId);
    setSelectedCompetitors(competitorsWithData);
  };

  const handleOpenTimeLimitModal = (simulado: SimuladoData) => {
    setTimeLimitExam(simulado);
    setTimeLimitInput(simulado.timeLimitMinutes ? fmtTime(simulado.timeLimitMinutes) : '');
    setIsTimeLimitModalOpen(true);
  };

  const handleSaveTimeLimit = async () => {
    if (!timeLimitExam) return;
    const minutes = parseTimeInput(timeLimitInput);
    setIsSavingTimeLimit(true);
    try {
      await examService.update(timeLimitExam.id, { time_limit_minutes: minutes });
      setSimulados(prev => prev.map(s =>
        s.id === timeLimitExam.id ? { ...s, timeLimitMinutes: minutes } : s
      ));
      setIsTimeLimitModalOpen(false);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao salvar meta de tempo');
    } finally {
      setIsSavingTimeLimit(false);
    }
  };

  const filteredSimulados = selectedModality === 'all'
    ? simulados
    : simulados.filter(s => s.modalityId === selectedModality);

  const filteredEvolutionData = evolutionData
    .map(c => ({
      ...c,
      data: selectedModality === 'all' ? c.data : c.data.filter(d => d.modalityId === selectedModality),
    }))
    .filter(c => c.data.length > 0 && selectedCompetitors.includes(c.competitorId));

  // Time view: filter by modality + group by simulado
  const filteredTimePoints = timePoints.filter(p =>
    selectedModality === 'all' || p.modalityId === selectedModality
  );


  const totalSimulados = filteredSimulados.length;
  const averageScore = filteredSimulados.length > 0
    ? (filteredSimulados.reduce((sum, s) => sum + s.averageScore, 0) / filteredSimulados.length).toFixed(1)
    : '0.0';
  const lastSimulado = filteredSimulados[filteredSimulados.length - 1];
  const scoreImprovement = filteredSimulados.length >= 2
    ? (filteredSimulados[filteredSimulados.length - 1].averageScore - filteredSimulados[0].averageScore).toFixed(1)
    : '0.0';

  if (isLoading) {
    return <div className="flex justify-center items-center h-64"><Spinner size="lg" /></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Dashboard de Simulados</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Acompanhe a evolução dos competidores nos simulados
          </p>
        </div>
        <Button variant="primary" onClick={() => navigate('/exams')}>Gerenciar Avaliações</Button>
      </div>

      {error && <Alert type="error" onClose={() => setError(null)}>{error}</Alert>}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardBody>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center mb-2">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-xs text-blue-600 dark:text-blue-400 font-medium uppercase tracking-wide">Total de Simulados</p>
              <p className="text-3xl font-bold text-blue-700 dark:text-blue-300 mt-1">{totalSimulados}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardBody>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-full bg-green-100 dark:bg-green-800 flex items-center justify-center mb-2">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-xs text-green-600 dark:text-green-400 font-medium uppercase tracking-wide">Média Geral</p>
              <p className="text-3xl font-bold text-green-700 dark:text-green-300 mt-1">{averageScore}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardBody>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-full bg-purple-100 dark:bg-purple-800 flex items-center justify-center mb-2">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                </svg>
              </div>
              <p className="text-xs text-purple-600 dark:text-purple-400 font-medium uppercase tracking-wide">Último Simulado</p>
              <p className="text-3xl font-bold text-purple-700 dark:text-purple-300 mt-1">
                {lastSimulado?.averageScore.toFixed(1) || '-'}
              </p>
            </div>
          </CardBody>
        </Card>
        <Card className={`bg-gradient-to-br ${parseFloat(scoreImprovement) >= 0 ? 'from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 border-emerald-200 dark:border-emerald-700' : 'from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-700'}`}>
          <CardBody>
            <div className="text-center">
              <div className={`w-12 h-12 mx-auto rounded-full ${parseFloat(scoreImprovement) >= 0 ? 'bg-emerald-100 dark:bg-emerald-800' : 'bg-red-100 dark:bg-red-800'} flex items-center justify-center mb-2`}>
                <svg className={`w-6 h-6 ${parseFloat(scoreImprovement) >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={parseFloat(scoreImprovement) >= 0 ? "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" : "M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"} />
                </svg>
              </div>
              <p className={`text-xs font-medium uppercase tracking-wide ${parseFloat(scoreImprovement) >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>Evolução</p>
              <p className={`text-3xl font-bold mt-1 ${parseFloat(scoreImprovement) >= 0 ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'}`}>
                {parseFloat(scoreImprovement) >= 0 ? '+' : ''}{scoreImprovement}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardBody>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="w-48">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Modalidade</label>
              <Select
                value={selectedModality}
                onChange={(e) => setSelectedModality(e.target.value)}
                options={[
                  { value: 'all', label: 'Todas' },
                  ...modalities.map(m => ({ value: m.id, label: m.name })),
                ]}
              />
            </div>
            {filteredEvolutionData.length > 0 && activeView === 'notas' && (
              <CompetitorSelect
                competitors={evolutionData
                  .filter(c => selectedModality === 'all' ? true : c.data.some(d => d.modalityId === selectedModality))
                  .map(c => ({ id: c.competitorId, name: c.competitorName }))}
                selected={selectedCompetitors}
                onChange={setSelectedCompetitors}
              />
            )}
            {/* View tabs */}
            <div className="ml-auto flex gap-2">
              <button
                onClick={() => setActiveView('notas')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeView === 'notas' ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
              >
                Notas
              </button>
              <button
                onClick={() => setActiveView('tempo')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${activeView === 'tempo' ? 'bg-orange-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Tempo
              </button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* NOTAS view */}
      {activeView === 'notas' && (
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              Evolução dos Competidores
            </div>
          </CardHeader>
          <CardBody>
            {filteredEvolutionData.length > 0 ? (
              <EvolutionChart data={filteredEvolutionData} />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
                <svg className="w-16 h-16 mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                <p className="text-lg font-medium">Nenhum dado disponível</p>
                <p className="text-sm mt-1">Lance notas nos simulados para visualizar a evolução</p>
              </div>
            )}
          </CardBody>
        </Card>
      )}

      {/* TEMPO view */}
      {activeView === 'tempo' && (() => {
        // Build chart data: one row per simulado, columns per competitor
        // Only competitors that are selected AND have time data
        const competitorNameMap: Record<string, string> = {};
        filteredTimePoints.forEach(p => { competitorNameMap[p.competitorId] = p.competitorName; });
        const competitorIds = Array.from(new Set(filteredTimePoints.map(p => p.competitorId)))
          .filter(cid => selectedCompetitors.length === 0 || selectedCompetitors.includes(cid));

        // Only simulados that have at least one time entry (from selected competitors)
        const simuladosWithData = filteredSimulados.filter(s =>
          filteredTimePoints.some(p => p.examId === s.id && competitorIds.includes(p.competitorId))
        );

        const chartData = simuladosWithData.map(s => {
          const row: Record<string, string | number> = { name: s.name };
          competitorIds.forEach(cid => {
            const pt = filteredTimePoints.find(p => p.examId === s.id && p.competitorId === cid);
            if (pt) row[cid] = pt.durationMinutes;
          });
          return row;
        });

        const hasAnyData = competitorIds.length > 0 && simuladosWithData.length > 0;

        const metaSimulado = filteredSimulados.find(s => s.timeLimitMinutes !== null);
        const metaMinutes = metaSimulado?.timeLimitMinutes ?? null;

        // Y-axis: nice 30-min ticks
        const allMinutes = filteredTimePoints
          .filter(p => competitorIds.includes(p.competitorId))
          .map(p => p.durationMinutes);
        const maxMinutes = Math.max(...allMinutes, metaMinutes ?? 0, 60);
        const step = maxMinutes <= 90 ? 15 : maxMinutes <= 180 ? 30 : 60;
        const yTicks: number[] = [];
        for (let t = 0; t <= maxMinutes + step; t += step) yTicks.push(t);

        const COLORS = ['#6366f1','#22c55e','#f59e0b','#ef4444','#3b82f6','#ec4899','#14b8a6','#a855f7','#f97316','#84cc16'];

        return (
          <Card>
            <CardHeader action={
              metaSimulado ? (
                <button
                  onClick={() => handleOpenTimeLimitModal(metaSimulado)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-colors"
                  title="Configurar meta de tempo"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {metaMinutes ? `Meta: ${fmtTime(metaMinutes)}` : 'Definir Meta'}
                </button>
              ) : filteredSimulados.length > 0 ? (
                <button
                  onClick={() => handleOpenTimeLimitModal(filteredSimulados[0])}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-colors"
                  title="Configurar meta de tempo"
                >
                  Definir Meta
                </button>
              ) : null
            }>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-semibold text-gray-900 dark:text-gray-100">Evolução do Tempo por Competidor</span>
              </div>
            </CardHeader>
            <CardBody>
              {!hasAnyData ? (
                <div className="flex flex-col items-center justify-center h-48 text-gray-500 dark:text-gray-400">
                  <svg className="w-14 h-14 mb-3 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-lg font-medium">Nenhum tempo registrado</p>
                  <p className="text-sm mt-1">Lance as notas dos simulados e preencha a coluna Tempo</p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={380}>
                  <LineChart data={chartData} margin={{ top: 10, right: 80, left: 10, bottom: 70 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      angle={-40}
                      textAnchor="end"
                      interval={0}
                      tickFormatter={(name: string) => name.length > 22 ? name.slice(0, 20) + '…' : name}
                    />
                    <YAxis
                      ticks={yTicks}
                      tickFormatter={fmtTime}
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      width={52}
                      domain={[0, yTicks[yTicks.length - 1]]}
                    />
                    <Tooltip
                      formatter={(value: number, name: string) => [fmtTime(value), competitorNameMap[name] || name]}
                      labelStyle={{ fontWeight: 600 }}
                      contentStyle={{ fontSize: 12 }}
                    />
                    <Legend
                      layout="vertical"
                      align="left"
                      verticalAlign="middle"
                      width={140}
                      formatter={(value) => competitorNameMap[value] || value}
                      wrapperStyle={{ fontSize: 12, left: 0 }}
                    />
                    {metaMinutes !== null && (
                      <ReferenceLine
                        y={metaMinutes}
                        stroke="#f97316"
                        strokeDasharray="6 3"
                        strokeWidth={1.5}
                        label={{ value: `Meta: ${fmtTime(metaMinutes)}`, position: 'right', fontSize: 11, fill: '#f97316', offset: 8 }}
                      />
                    )}
                    {competitorIds.map((cid, idx) => (
                      <Line
                        key={cid}
                        type="monotone"
                        dataKey={cid}
                        name={cid}
                        stroke={COLORS[idx % COLORS.length]}
                        strokeWidth={2}
                        dot={{ r: 4, fill: COLORS[idx % COLORS.length] }}
                        activeDot={{ r: 6 }}
                        connectNulls={true}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardBody>
          </Card>
        );
      })()}

      {/* Simulados List */}
      <Card>
        <CardHeader action={<Button size="sm" onClick={() => navigate('/exams')}>+ Novo Simulado</Button>}>
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Simulados Realizados
          </div>
        </CardHeader>
        <CardBody>
          {filteredSimulados.length > 0 ? (
            <div className="space-y-4">
              {filteredSimulados.map((simulado) => (
                <div
                  key={simulado.id}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 flex-shrink-0 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">{simulado.name}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(simulado.date).toLocaleDateString('pt-BR')} • {simulado.modality} • {simulado.competitorsCount} competidor{simulado.competitorsCount !== 1 ? 'es' : ''}
                        {simulado.timeLimitMinutes && (
                          <span className="ml-2 text-orange-500 dark:text-orange-400">• Meta: {fmtTime(simulado.timeLimitMinutes)}</span>
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between sm:justify-end gap-3 flex-shrink-0">
                    <div className="text-right">
                      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase">Média</p>
                      <Badge variant={simulado.averageScore >= 70 ? 'success' : simulado.averageScore >= 50 ? 'warning' : 'danger'}>
                        {simulado.averageScore.toFixed(1)}
                      </Badge>
                    </div>
                    <Button size="sm" variant="secondary" onClick={() => navigate('/exams')}>Ver Detalhes</Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p className="text-gray-500 dark:text-gray-400 text-lg">Nenhum simulado encontrado</p>
              <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">
                Crie um novo simulado em Avaliações com o tipo "Simulado"
              </p>
              <Button className="mt-4" onClick={() => navigate('/exams')}>Ir para Avaliações</Button>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Modal: Configurar Meta de Tempo */}
      <Modal
        isOpen={isTimeLimitModalOpen}
        onClose={() => setIsTimeLimitModalOpen(false)}
        title={`Meta de Tempo — ${timeLimitExam?.name || ''}`}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Defina o tempo máximo desejado para este simulado. Competidores que ultrapassarem este tempo serão destacados em vermelho no gráfico.
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Meta de tempo (h:mm)
            </label>
            <Input
              type="text"
              value={timeLimitInput}
              onChange={(e) => {
                const digits = e.target.value.replace(/[^0-9]/g, '');
                setTimeLimitInput(digits.length <= 2 ? digits : digits.slice(0, 2) + ':' + digits.slice(2, 4));
              }}
              placeholder="ex: 1:30"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Formato: horas:minutos. Exemplo: 1:30 = 1 hora e 30 minutos.
              {timeLimitInput && parseTimeInput(timeLimitInput) !== null && (
                <span className="ml-1 text-orange-600 dark:text-orange-400 font-medium">
                  = {parseTimeInput(timeLimitInput)} minutos
                </span>
              )}
            </p>
          </div>
          {timeLimitExam?.timeLimitMinutes && (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Meta atual: <strong>{fmtTime(timeLimitExam.timeLimitMinutes)}</strong>
            </p>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setIsTimeLimitModalOpen(false)}>Cancelar</Button>
            {timeLimitExam?.timeLimitMinutes && (
              <Button
                variant="danger"
                onClick={async () => {
                  setIsSavingTimeLimit(true);
                  try {
                    await examService.update(timeLimitExam.id, { time_limit_minutes: null });
                    setSimulados(prev => prev.map(s =>
                      s.id === timeLimitExam.id ? { ...s, timeLimitMinutes: null } : s
                    ));
                    setIsTimeLimitModalOpen(false);
                  } catch (err: any) {
                    setError(err?.response?.data?.detail || 'Erro ao remover meta');
                  } finally {
                    setIsSavingTimeLimit(false);
                  }
                }}
                isLoading={isSavingTimeLimit}
              >
                Remover Meta
              </Button>
            )}
            <Button
              onClick={handleSaveTimeLimit}
              isLoading={isSavingTimeLimit}
              disabled={!timeLimitInput || parseTimeInput(timeLimitInput) === null}
            >
              Salvar Meta
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SimuladosDashboard;

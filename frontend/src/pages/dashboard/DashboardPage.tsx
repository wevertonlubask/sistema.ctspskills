import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores';
import { Card, CardHeader, CardBody, Badge, Button, Spinner, Alert } from '../../components/ui';
import { StatCard } from '../../components/charts/StatCard';
import { LineChartCard, ProgressChart, TrainingHoursChart } from '../../components/charts';
import { GoalConfigModal, MetaConfigModal, getStoredMeta, TrainingHoursConfigModal, getStoredTrainingHoursMeta, getDailyTrainingTarget } from '../../components/forms';
import { gradeService, trainingService, enrollmentService, competitorService, examService } from '../../services';
import type { Grade, TrainingStatistics, Modality, TrainingSession, Exam } from '../../types';
import type { ProgressData } from '../../components/charts/ProgressChart';
import type { TrainingHoursData } from '../../components/charts/TrainingHoursChart';

/**
 * Parse date string (YYYY-MM-DD) without timezone conversion issues
 * Returns { year, month, day } as numbers
 */
const parseDateString = (dateString: string): { year: number; month: number; day: number } => {
  const [year, month, day] = dateString.split('T')[0].split('-').map(Number);
  return { year, month, day };
};

interface CompetitorStats {
  competitorId: string;
  competitorName: string;
  average: number;
  trainingHours: number;
  evolutionData: Array<{ name: string; value: number }>;
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const isCompetitor = user?.role === 'competitor';
  const isEvaluator = user?.role === 'evaluator';
  const isSuperAdmin = user?.role === 'super_admin';

  // Shared state
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [metaGlobal, setMetaGlobal] = useState(getStoredMeta());

  // Competitor-specific state
  const [myGrades, setMyGrades] = useState<Grade[]>([]);
  const [myTrainingStats, setMyTrainingStats] = useState<TrainingStatistics | null>(null);
  const [myEvolutionData, setMyEvolutionData] = useState<Array<{ name: string; value: number }>>([]);
  const [myProgressData, setMyProgressData] = useState<ProgressData[]>([]);
  const [_myExams, setMyExams] = useState<Exam[]>([]);
  const [overallCompetitorAverage, setOverallCompetitorAverage] = useState(0);

  // Training hours per day (shared between all roles)
  const [trainingHoursPerDay, setTrainingHoursPerDay] = useState<TrainingHoursData[]>([]);

  // Evaluator/Admin-specific state
  const [competitorsStats, setCompetitorsStats] = useState<CompetitorStats[]>([]);
  const [overallAverage, setOverallAverage] = useState(0);
  const [progressData, setProgressData] = useState<ProgressData[]>([]);

  // Modal states
  const [goalModalOpen, setGoalModalOpen] = useState(false);
  const [metaModalOpen, setMetaModalOpen] = useState(false);
  const [trainingHoursModalOpen, setTrainingHoursModalOpen] = useState(false);

  // Training hours filter and target
  const [trainingHoursMeta, setTrainingHoursMeta] = useState(getStoredTrainingHoursMeta());
  const [allTrainings, setAllTrainings] = useState<TrainingSession[]>([]);
  const [selectedCompetitor, setSelectedCompetitor] = useState<{ id: string; full_name: string } | null>(null);
  const [trainingHoursFilterCompetitorId, setTrainingHoursFilterCompetitorId] = useState<string>('all');
  // Unified period filter: "day:YYYY-MM" for daily view of a month, "week" for weekly, "month" for monthly
  const [trainingPeriodFilter, setTrainingPeriodFilter] = useState<string>(() => {
    const now = new Date();
    return `day:${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const roleLabels: Record<string, string> = {
    super_admin: 'Super Administrador',
    evaluator: 'Avaliador',
    competitor: 'Competidor',
  };

  // Parse the unified filter
  const parseTrainingFilter = (filter: string): { period: 'day' | 'quarter' | 'semester' | 'year'; month?: string } => {
    if (filter.startsWith('day:')) {
      return { period: 'day', month: filter.substring(4) };
    }
    return { period: filter as 'quarter' | 'semester' | 'year' };
  };

  // Generate unified period options
  const getPeriodOptions = (): Array<{ value: string; label: string; group?: string }> => {
    const options: Array<{ value: string; label: string; group?: string }> = [];
    const now = new Date();

    // Daily options for each month
    for (let i = 0; i < 12; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const value = `day:${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleDateString('pt-BR', { month: 'short' }).replace('.', '');
      const label = `${monthName.charAt(0).toUpperCase() + monthName.slice(1)}/${date.getFullYear()} (diário)`;
      options.push({ value, label, group: 'Diário por mês' });
    }

    // Grouped options (quarter, semester, year)
    options.push({ value: 'quarter', label: 'Trimestral', group: 'Agrupado' });
    options.push({ value: 'semester', label: 'Semestral', group: 'Agrupado' });
    options.push({ value: 'year', label: 'Anual', group: 'Agrupado' });

    return options;
  };

  const periodOptions = getPeriodOptions();

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch modalities for all users
      const myModalities = await enrollmentService.getMyModalities();
      setModalities(myModalities);

      if (isCompetitor) {
        await fetchCompetitorData(myModalities);
      } else {
        await fetchEvaluatorData(myModalities);
      }
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar dados do dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCompetitorData = async (myModalities: Modality[]) => {
    // Fetch exams for all modalities
    const allExams: Exam[] = [];
    try {
      for (const modality of myModalities) {
        const examsResponse = await examService.getAll({ modality_id: modality.id, limit: 100 });
        allExams.push(...(examsResponse.exams || []));
      }
      setMyExams(allExams);
    } catch (err) {
      console.error('Error fetching exams:', err);
    }

    // Fetch grades
    try {
      const gradesResponse = await gradeService.getAll({ limit: 500 });
      const grades = gradesResponse.grades || [];
      setMyGrades(grades);

      // Calculate overall average
      const totalAvg = grades.length > 0
        ? grades.reduce((sum, g) => sum + g.score, 0) / grades.length
        : 0;
      setOverallCompetitorAverage(Math.round(totalAvg * 10) / 10);

      // Group grades by exam and calculate average per exam
      const examGradesMap = new Map<string, { scores: number[]; examName: string; examDate: string }>();

      for (const grade of grades) {
        const exam = allExams.find(e => e.id === grade.exam_id);
        if (!examGradesMap.has(grade.exam_id)) {
          examGradesMap.set(grade.exam_id, {
            scores: [],
            examName: exam?.name || 'Avaliação',
            examDate: exam?.exam_date || grade.created_at,
          });
        }
        examGradesMap.get(grade.exam_id)!.scores.push(grade.score);
      }

      // Sort exams by date and build progress data
      const examEntries = Array.from(examGradesMap.entries())
        .map(([examId, data]) => ({
          examId,
          ...data,
          average: data.scores.reduce((s, sc) => s + sc, 0) / data.scores.length,
        }))
        .sort((a, b) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime());

      // Build progress data showing exam averages vs overall average
      const progressItems: ProgressData[] = examEntries.map((exam, index) => {
        // Abbreviate exam name for display
        let displayName = exam.examName;
        if (displayName.length > 15) {
          displayName = displayName.substring(0, 12) + '...';
        }
        // Add index for uniqueness if names repeat
        return {
          name: examEntries.length > 1 ? `${index + 1}. ${displayName}` : displayName,
          atual: Math.round(exam.average * 10) / 10,
          meta: Math.round(totalAvg * 10) / 10, // Use overall average as comparison
        };
      });
      setMyProgressData(progressItems);

      // Build evolution data - show average per exam (sorted by date)
      const evolution = examEntries.map((exam, index) => ({
        name: `Sim. ${index + 1}`,
        value: Math.round(exam.average * 10) / 10,
      }));
      setMyEvolutionData(evolution);
    } catch (err) {
      console.error('Error fetching grades:', err);
    }

    // Fetch training stats and hours per day
    try {
      const trainingsResponse = await trainingService.getAll({ limit: 500 });
      const trainings = trainingsResponse.trainings || [];
      setAllTrainings(trainings);

      if (trainings.length > 0) {
        const competitorId = trainings[0].competitor_id;
        const stats = await trainingService.getStatistics(competitorId);
        setMyTrainingStats(stats);

        // Group trainings by date for the hours chart
        const { period, month } = parseTrainingFilter(trainingPeriodFilter);
        const hoursPerDay = buildTrainingHoursData(trainings, period, month);
        setTrainingHoursPerDay(hoursPerDay);
      }
    } catch (err) {
      console.error('Error fetching training stats:', err);
    }
  };

  // Helper function to group trainings by period
  const buildTrainingHoursData = (
    trainings: TrainingSession[],
    period: 'day' | 'quarter' | 'semester' | 'year',
    monthFilter?: string // Format: "YYYY-MM"
  ): TrainingHoursData[] => {
    // Get only approved trainings
    const approvedTrainings = trainings.filter(t => t.status === 'approved');

    if (period === 'day') {
      // Group by date
      const hoursMap = new Map<string, number>();
      for (const training of approvedTrainings) {
        const date = training.training_date.split('T')[0];
        const current = hoursMap.get(date) || 0;
        hoursMap.set(date, current + training.hours);
      }

      // If a month filter is provided, show all days of that month
      if (monthFilter) {
        const [year, month] = monthFilter.split('-').map(Number);
        const daysInMonth = new Date(year, month, 0).getDate();
        const result: TrainingHoursData[] = [];

        for (let day = 1; day <= daysInMonth; day++) {
          const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          const hours = hoursMap.get(dateStr) || 0;
          result.push({
            date: dateStr,
            hours: Math.round(hours * 10) / 10,
            label: String(day), // Just show the day number
          });
        }
        return result;
      }

      // Default: show last 14 days with data
      const sortedEntries = Array.from(hoursMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .slice(-14);
      return sortedEntries.map(([date, hours]) => ({
        date,
        hours: Math.round(hours * 10) / 10,
      }));
    } else if (period === 'quarter') {
      // Group by month for last 3 months (trimestral)
      const hoursMap = new Map<string, { hours: number; label: string }>();
      const now = new Date();
      const monthNames = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
      for (const training of approvedTrainings) {
        const { year, month } = parseDateString(training.training_date);
        // Only include last 3 months
        const monthsDiff = (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month);
        if (monthsDiff >= 0 && monthsDiff < 3) {
          const key = `${year}-${String(month).padStart(2, '0')}`;
          const label = `${monthNames[month - 1]}/${String(year).slice(-2)}`;
          const current = hoursMap.get(key) || { hours: 0, label };
          hoursMap.set(key, { hours: current.hours + training.hours, label: current.label });
        }
      }
      const sortedEntries = Array.from(hoursMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]));
      return sortedEntries.map(([date, data]) => ({
        date,
        hours: Math.round(data.hours * 10) / 10,
        label: data.label,
      }));
    } else if (period === 'semester') {
      // Group by month for last 6 months (semestral)
      const hoursMap = new Map<string, { hours: number; label: string }>();
      const now = new Date();
      const monthNames = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
      for (const training of approvedTrainings) {
        const { year, month } = parseDateString(training.training_date);
        // Only include last 6 months
        const monthsDiff = (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month);
        if (monthsDiff >= 0 && monthsDiff < 6) {
          const key = `${year}-${String(month).padStart(2, '0')}`;
          const label = `${monthNames[month - 1]}/${String(year).slice(-2)}`;
          const current = hoursMap.get(key) || { hours: 0, label };
          hoursMap.set(key, { hours: current.hours + training.hours, label: current.label });
        }
      }
      const sortedEntries = Array.from(hoursMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]));
      return sortedEntries.map(([date, data]) => ({
        date,
        hours: Math.round(data.hours * 10) / 10,
        label: data.label,
      }));
    } else {
      // Group by month for last 12 months (anual)
      const hoursMap = new Map<string, { hours: number; label: string }>();
      const now = new Date();
      const monthNames = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
      for (const training of approvedTrainings) {
        const { year, month } = parseDateString(training.training_date);
        // Only include last 12 months
        const monthsDiff = (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month);
        if (monthsDiff >= 0 && monthsDiff < 12) {
          const key = `${year}-${String(month).padStart(2, '0')}`;
          const label = `${monthNames[month - 1]}/${String(year).slice(-2)}`;
          const current = hoursMap.get(key) || { hours: 0, label };
          hoursMap.set(key, { hours: current.hours + training.hours, label: current.label });
        }
      }
      const sortedEntries = Array.from(hoursMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]));
      return sortedEntries.map(([date, data]) => ({
        date,
        hours: Math.round(data.hours * 10) / 10,
        label: data.label,
      }));
    }
  };

  // Update chart when period filter or competitor filter changes
  useEffect(() => {
    if (allTrainings.length > 0) {
      // Filter trainings by competitor if a specific one is selected
      const filteredTrainings = trainingHoursFilterCompetitorId === 'all'
        ? allTrainings
        : allTrainings.filter(t => t.competitor_id === trainingHoursFilterCompetitorId);
      // Parse the unified filter
      const { period, month } = parseTrainingFilter(trainingPeriodFilter);
      const hoursData = buildTrainingHoursData(filteredTrainings, period, month);
      setTrainingHoursPerDay(hoursData);
    }
  }, [trainingPeriodFilter, allTrainings, trainingHoursFilterCompetitorId]);

  // Get target for current view period
  const getTrainingTarget = (): number => {
    const dailyTarget = getDailyTrainingTarget();
    const { period } = parseTrainingFilter(trainingPeriodFilter);
    switch (period) {
      case 'day':
        return dailyTarget;
      case 'quarter':
      case 'semester':
      case 'year':
        return trainingHoursMeta; // Monthly target for grouped views
      default:
        return dailyTarget;
    }
  };

  // Get target label for current view period
  const getTrainingTargetLabel = (): string => {
    const target = getTrainingTarget();
    const { period } = parseTrainingFilter(trainingPeriodFilter);
    switch (period) {
      case 'day':
        return `Meta: ${target}h/dia`;
      case 'quarter':
      case 'semester':
      case 'year':
        return `Meta: ${target}h/mês`;
      default:
        return `Meta: ${target}h`;
    }
  };

  const handleTrainingHoursMetaSave = (newMeta: number) => {
    setTrainingHoursMeta(newMeta);
  };

  const fetchEvaluatorData = async (myModalities: Modality[]) => {
    // Fetch competitors and their stats
    const allGrades: Grade[] = [];
    const statsMap = new Map<string, CompetitorStats>();

    for (const modality of myModalities) {
      try {
        const competitorsResponse = await competitorService.getByModality(modality.id);
        const competitors = competitorsResponse.competitors || [];

        for (const competitor of competitors) {
          if (statsMap.has(competitor.id)) continue;

          // Get grades
          const gradesResponse = await gradeService.getAll({
            competitor_id: competitor.id,
            limit: 500,
          });
          const competitorGrades = gradesResponse.grades || [];
          allGrades.push(...competitorGrades);

          // Calculate average
          const avg = competitorGrades.length > 0
            ? competitorGrades.reduce((sum, g) => sum + g.score, 0) / competitorGrades.length
            : 0;

          // Get training hours
          let trainingHours = 0;
          try {
            const stats = await trainingService.getStatistics(competitor.id);
            trainingHours = stats.approved_hours;
          } catch {
            // Ignore
          }

          // Build evolution data
          const examGrades = new Map<string, number[]>();
          for (const grade of competitorGrades) {
            if (!examGrades.has(grade.exam_id)) {
              examGrades.set(grade.exam_id, []);
            }
            examGrades.get(grade.exam_id)!.push(grade.score);
          }

          const evolution = Array.from(examGrades.entries()).map(([_, scores], index) => ({
            name: `Av ${index + 1}`,
            value: Math.round((scores.reduce((s, sc) => s + sc, 0) / scores.length) * 10) / 10,
          }));

          statsMap.set(competitor.id, {
            competitorId: competitor.id,
            competitorName: competitor.full_name,
            average: Math.round(avg * 10) / 10,
            trainingHours,
            evolutionData: evolution,
          });
        }
      } catch (err) {
        console.error('Error fetching competitors for modality:', modality.id, err);
      }
    }

    const competitorsArray = Array.from(statsMap.values());
    setCompetitorsStats(competitorsArray);

    // Build progress data for bar chart - show each competitor's average vs meta
    const progressItems: ProgressData[] = competitorsArray.map(comp => ({
      name: comp.competitorName.split(' ')[0], // First name only for chart
      atual: comp.average,
      meta: metaGlobal,
    }));
    setProgressData(progressItems);

    // Calculate overall average
    const avgScore = allGrades.length > 0
      ? allGrades.reduce((sum, g) => sum + g.score, 0) / allGrades.length
      : 0;
    setOverallAverage(Math.round(avgScore * 10) / 10);

    // Fetch all trainings for hours chart (for all competitors in the evaluator's modalities)
    try {
      const fetchedTrainings: TrainingSession[] = [];
      for (const modality of myModalities) {
        try {
          const trainingsResponse = await trainingService.getAll({
            modality_id: modality.id,
            limit: 500,
          });
          fetchedTrainings.push(...(trainingsResponse.trainings || []));
        } catch {
          // Ignore
        }
      }

      setAllTrainings(fetchedTrainings);
      if (fetchedTrainings.length > 0) {
        const { period, month } = parseTrainingFilter(trainingPeriodFilter);
        const hoursData = buildTrainingHoursData(fetchedTrainings, period, month);
        setTrainingHoursPerDay(hoursData);
      }
    } catch (err) {
      console.error('Error fetching trainings for hours chart:', err);
    }
  };

  // Calculate competitor stats
  const competitorAverage = myGrades.length > 0
    ? (myGrades.reduce((sum, g) => sum + g.score, 0) / myGrades.length).toFixed(1)
    : '0.0';

  const handleMetaSave = (newMeta: number) => {
    setMetaGlobal(newMeta);
    // Update progress data with new meta
    setProgressData(prev => prev.map(item => ({ ...item, meta: newMeta })));
    setMyProgressData(prev => prev.map(item => ({ ...item, meta: newMeta })));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">
            Bem-vindo, {user?.full_name}!
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isCompetitor
              ? 'Acompanhe seu desempenho e evolução'
              : 'Painel de controle do sistema SPSkills'}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {(isEvaluator || isSuperAdmin) && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setMetaModalOpen(true)}
              title="Configurar Meta Global"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Meta: {metaGlobal}
            </Button>
          )}
          <Badge variant="primary" size="lg">
            {roleLabels[user?.role || ''] || user?.role}
          </Badge>
        </div>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Competitor View */}
      {isCompetitor && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Média Geral"
              value={competitorAverage}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
            />
            <StatCard
              title="Meta"
              value={metaGlobal.toString()}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            />
            <StatCard
              title="Total Avaliações"
              value={myGrades.length}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              }
            />
            <StatCard
              title="Horas Treinamento"
              value={`${myTrainingStats?.approved_hours || 0}h`}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
          </div>

          {/* Progress Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Progress Chart - Notas por Simulado vs Média */}
            <Card>
              <CardHeader>Notas por Simulado vs Média {overallCompetitorAverage > 0 ? `(${overallCompetitorAverage})` : ''}</CardHeader>
              <CardBody>
                {myProgressData.length > 0 ? (
                  <ProgressChart
                    data={myProgressData}
                    height={250}
                    metaGlobal={overallCompetitorAverage}
                    atualLabel="Nota do Simulado"
                    metaLabel="Média Geral"
                  />
                ) : (
                  <div className="flex items-center justify-center h-[250px] text-gray-500">
                    <div className="text-center">
                      <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <p>Nenhuma avaliação realizada ainda</p>
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>

            {/* Training Hours Per Day */}
            <Card>
              <CardHeader action={
                <select
                  value={trainingPeriodFilter}
                  onChange={(e) => setTrainingPeriodFilter(e.target.value)}
                  className="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                >
                  <optgroup label="Diário por mês">
                    {periodOptions.filter(opt => opt.group === 'Diário por mês').map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="Agrupado">
                    {periodOptions.filter(opt => opt.group === 'Agrupado').map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </optgroup>
                </select>
              }>
                Horas de Treinamento
              </CardHeader>
              <CardBody>
                {trainingHoursPerDay.length > 0 ? (
                  <TrainingHoursChart
                    data={trainingHoursPerDay}
                    height={250}
                    targetHoursPerDay={getTrainingTarget()}
                    showTarget={true}
                    targetLabel={getTrainingTargetLabel()}
                  />
                ) : (
                  <div className="flex items-center justify-center h-[250px] text-gray-500">
                    <div className="text-center">
                      <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p>Nenhum treinamento registrado</p>
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>Evolução por Simulado</CardHeader>
              <CardBody>
                {myEvolutionData.length > 0 ? (
                  <LineChartCard data={myEvolutionData} color="#3B82F6" height={250} />
                ) : (
                  <div className="flex items-center justify-center h-[250px] text-gray-500">
                    <p>Nenhuma avaliação realizada ainda</p>
                  </div>
                )}
              </CardBody>
            </Card>

            <Card>
              <CardHeader>Últimas Notas</CardHeader>
              <CardBody>
                {myGrades.length > 0 ? (
                  <div className="space-y-3">
                    {[...myGrades]
                      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                      .slice(0, 5)
                      .map((grade) => (
                        <div key={grade.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-gray-100">Avaliação</p>
                            <p className="text-sm text-gray-500">{new Date(grade.created_at).toLocaleDateString('pt-BR')}</p>
                          </div>
                          <Badge variant={grade.score >= metaGlobal ? 'success' : grade.score >= metaGlobal * 0.7 ? 'warning' : 'danger'}>
                            {grade.score.toFixed(1)}
                          </Badge>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-[200px] text-gray-500">
                    <p>Nenhuma nota lançada ainda</p>
                  </div>
                )}
              </CardBody>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>Acesso Rápido</CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button variant="secondary" onClick={() => navigate('/my-grades')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Ver Minhas Notas
                </Button>
                <Button variant="secondary" onClick={() => navigate('/trainings')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Ver Treinamentos
                </Button>
                <Button variant="secondary" onClick={() => navigate('/modalities')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  Ver Modalidades
                </Button>
              </div>
            </CardBody>
          </Card>
        </>
      )}

      {/* Evaluator/Admin View */}
      {(isEvaluator || isSuperAdmin) && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Modalidades"
              value={modalities.length}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              }
            />
            <StatCard
              title="Competidores"
              value={competitorsStats.length}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              }
            />
            <StatCard
              title="Média Geral"
              value={`${overallAverage}`}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
            />
            <StatCard
              title="Meta Global"
              value={metaGlobal.toString()}
              icon={
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            />
          </div>

          {/* Progress Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Progress Chart - Competitors vs Meta */}
            {progressData.length > 0 && (
              <Card>
                <CardHeader action={
                  <Button size="sm" variant="secondary" onClick={() => setMetaModalOpen(true)}>
                    Configurar Meta
                  </Button>
                }>
                  Média dos Competidores vs Meta
                </CardHeader>
                <CardBody>
                  <ProgressChart data={progressData} height={300} />
                </CardBody>
              </Card>
            )}

            {/* Training Hours Per Day */}
            <Card>
              <CardHeader action={
                <div className="flex items-center space-x-2 flex-wrap gap-y-2">
                  <select
                    value={trainingHoursFilterCompetitorId}
                    onChange={(e) => setTrainingHoursFilterCompetitorId(e.target.value)}
                    className="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 max-w-[140px]"
                  >
                    <option value="all">Todos</option>
                    {competitorsStats.map((comp) => (
                      <option key={comp.competitorId} value={comp.competitorId}>
                        {comp.competitorName.split(' ').slice(0, 2).join(' ')}
                      </option>
                    ))}
                  </select>
                  <select
                    value={trainingPeriodFilter}
                    onChange={(e) => setTrainingPeriodFilter(e.target.value)}
                    className="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  >
                    <optgroup label="Diário por mês">
                      {periodOptions.filter(opt => opt.group === 'Diário por mês').map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </optgroup>
                    <optgroup label="Agrupado">
                      {periodOptions.filter(opt => opt.group === 'Agrupado').map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </optgroup>
                  </select>
                  <Button size="sm" variant="secondary" onClick={() => setTrainingHoursModalOpen(true)}>
                    Meta: {trainingHoursMeta}h/mês
                  </Button>
                </div>
              }>
                Horas de Treinamento {trainingHoursFilterCompetitorId === 'all' ? '(Todos)' : ''}
              </CardHeader>
              <CardBody>
                {trainingHoursPerDay.length > 0 ? (
                  <TrainingHoursChart
                    data={trainingHoursPerDay}
                    height={300}
                    targetHoursPerDay={getTrainingTarget()}
                    showTarget={true}
                    targetLabel={getTrainingTargetLabel()}
                  />
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-gray-500">
                    <div className="text-center">
                      <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p>Nenhum treinamento registrado</p>
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>
          </div>

          {/* Competitors Overview */}
          <Card>
            <CardHeader action={
              <Button size="sm" onClick={() => navigate('/simulados')}>
                Ver Dashboard Completo
              </Button>
            }>
              Desempenho dos Competidores
            </CardHeader>
            <CardBody>
              {competitorsStats.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {competitorsStats.slice(0, 6).map((comp) => (
                    <div key={comp.competitorId} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100">{comp.competitorName}</p>
                          <p className="text-sm text-gray-500">{comp.trainingHours}h de treino</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={comp.average >= metaGlobal ? 'success' : comp.average >= metaGlobal * 0.7 ? 'warning' : 'danger'}>
                            {comp.average.toFixed(1)}
                          </Badge>
                          <button
                            onClick={() => {
                              setSelectedCompetitor({ id: comp.competitorId, full_name: comp.competitorName });
                              setGoalModalOpen(true);
                            }}
                            className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                            title="Configurar Metas"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      {/* Mini progress bar showing vs meta */}
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span>Média</span>
                          <span>Meta: {metaGlobal}</span>
                        </div>
                        <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${
                              comp.average >= metaGlobal ? 'bg-green-500' : comp.average >= metaGlobal * 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min((comp.average / metaGlobal) * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                      {comp.evolutionData.length > 0 && (
                        <div className="mt-3">
                          <LineChartCard data={comp.evolutionData} color="#10B981" height={60} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <p>Nenhum competidor encontrado</p>
                  <p className="text-sm mt-1">Inscreva competidores em suas modalidades</p>
                </div>
              )}
            </CardBody>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>Acesso Rápido</CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Button variant="secondary" onClick={() => navigate('/simulados')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                  Dashboard Simulados
                </Button>
                <Button variant="secondary" onClick={() => navigate('/exams')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Gerenciar Avaliações
                </Button>
                <Button variant="secondary" onClick={() => navigate('/grades')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Lançar Notas
                </Button>
                <Button variant="secondary" onClick={() => navigate('/trainings')} className="justify-start">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Validar Treinamentos
                </Button>
              </div>
            </CardBody>
          </Card>

          {/* Goal Configuration Modal */}
          <GoalConfigModal
            isOpen={goalModalOpen}
            onClose={() => {
              setGoalModalOpen(false);
              setSelectedCompetitor(null);
            }}
            competitor={selectedCompetitor as any}
            modality={null}
            onSaved={() => {
              // Optionally refresh data
            }}
          />

          {/* Meta Configuration Modal */}
          <MetaConfigModal
            isOpen={metaModalOpen}
            onClose={() => setMetaModalOpen(false)}
            currentMeta={metaGlobal}
            onSave={handleMetaSave}
          />
        </>
      )}

      {/* Training Hours Config Modal - available for all users */}
      <TrainingHoursConfigModal
        isOpen={trainingHoursModalOpen}
        onClose={() => setTrainingHoursModalOpen(false)}
        currentMeta={trainingHoursMeta}
        onSave={handleTrainingHoursMetaSave}
      />
    </div>
  );
};

export default DashboardPage;

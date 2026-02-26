import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Badge, Select, Spinner, Alert } from '../../components/ui';
import { EvolutionChart } from '../../components/charts/EvolutionChart';
import { CompetitorSelect } from '../../components/forms/CompetitorSelect';
import { examService, gradeService, competitorService, enrollmentService } from '../../services';
import type { Exam, Modality, Competitor } from '../../types';

interface SimuladoData {
  id: string;
  name: string;
  date: string;
  modality: string;
  modalityId: string;
  competitorsCount: number;
  averageScore: number;
}

interface CompetitorEvolution {
  competitorId: string;
  competitorName: string;
  data: Array<{
    simuladoName: string;
    date: string;
    score: number;
  }>;
}

const SimuladosDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [simulados, setSimulados] = useState<SimuladoData[]>([]);
  const [evolutionData, setEvolutionData] = useState<CompetitorEvolution[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [selectedModality, setSelectedModality] = useState<string>('all');
  const [selectedCompetitors, setSelectedCompetitors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial data
  useEffect(() => {
    fetchData();
  }, []);

  // Re-filter when modality changes
  useEffect(() => {
    if (simulados.length > 0) {
      buildEvolutionData();
    }
  }, [selectedModality]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch modalities assigned to the current user
      const modalitiesData = await enrollmentService.getMyModalities();
      setModalities(modalitiesData || []);

      // Get the IDs of modalities the user has access to
      const myModalityIds = new Set(modalitiesData.map((m: Modality) => m.id));

      // Fetch all exams and filter by user's modalities
      const examResponse = await examService.getAll({ active_only: true, limit: 500 });
      const allExams = (examResponse.exams || []).filter(
        (exam: Exam) => myModalityIds.has(exam.modality_id)
      );

      // Filter only simulados (simulation type)
      const simuladoExams = allExams.filter(e => e.assessment_type === 'simulation');

      // Sort by date
      simuladoExams.sort((a, b) => new Date(a.exam_date).getTime() - new Date(b.exam_date).getTime());

      // Fetch statistics and grades for each simulado
      const simuladoDataPromises = simuladoExams.map(async (exam) => {
        try {
          const stats = await examService.getStatistics(exam.id);
          const modality = modalitiesData?.find(m => m.id === exam.modality_id);

          return {
            id: exam.id,
            name: exam.name,
            date: exam.exam_date,
            modality: modality?.name || 'N/A',
            modalityId: exam.modality_id,
            competitorsCount: stats.total_competitors || 0,
            averageScore: stats.overall_average || 0,
          };
        } catch (err) {
          console.error(`Error fetching stats for exam ${exam.id}:`, err);
          return {
            id: exam.id,
            name: exam.name,
            date: exam.exam_date,
            modality: 'N/A',
            modalityId: exam.modality_id,
            competitorsCount: 0,
            averageScore: 0,
          };
        }
      });

      const simuladosData = await Promise.all(simuladoDataPromises);
      setSimulados(simuladosData);

      // Fetch all grades for simulados to build evolution data
      await fetchGradesAndBuildEvolution(simuladoExams, modalitiesData || []);

    } catch (err: any) {
      console.error('Error fetching simulados data:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar dados dos simulados');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchGradesAndBuildEvolution = async (simuladoExams: Exam[], _modalitiesData: Modality[]) => {
    try {
      // Collect all unique competitor IDs from grades
      const competitorGradesMap = new Map<string, Array<{ examId: string; examName: string; examDate: string; score: number }>>();
      const competitorIdsSet = new Set<string>();

      // Fetch grades for each simulado
      for (const exam of simuladoExams) {
        try {
          const gradesResponse = await gradeService.getAll({ exam_id: exam.id, limit: 1000 });
          const grades = gradesResponse.grades || [];

          // Group grades by competitor and calculate average per exam
          const competitorScores = new Map<string, number[]>();

          for (const grade of grades) {
            competitorIdsSet.add(grade.competitor_id);
            if (!competitorScores.has(grade.competitor_id)) {
              competitorScores.set(grade.competitor_id, []);
            }
            competitorScores.get(grade.competitor_id)!.push(grade.score);
          }

          // Calculate average score per competitor for this exam
          competitorScores.forEach((scores, competitorId) => {
            const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;

            if (!competitorGradesMap.has(competitorId)) {
              competitorGradesMap.set(competitorId, []);
            }
            competitorGradesMap.get(competitorId)!.push({
              examId: exam.id,
              examName: exam.name,
              examDate: exam.exam_date,
              score: avgScore,
            });
          });
        } catch (err) {
          console.error(`Error fetching grades for exam ${exam.id}:`, err);
        }
      }

      // Fetch competitor details
      const competitorIds = Array.from(competitorIdsSet);
      const competitorsMap = new Map<string, Competitor>();

      for (const compId of competitorIds) {
        try {
          const competitor = await competitorService.getById(compId);
          competitorsMap.set(compId, competitor);
        } catch (err) {
          console.error(`Error fetching competitor ${compId}:`, err);
        }
      }

      // Build evolution data
      const evolution: CompetitorEvolution[] = [];

      competitorGradesMap.forEach((examsData, competitorId) => {
        const competitor = competitorsMap.get(competitorId);
        if (!competitor) return;

        // Sort exams by date
        examsData.sort((a, b) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime());

        evolution.push({
          competitorId: competitor.id,
          competitorName: competitor.full_name,
          data: examsData.map(ed => ({
            simuladoName: ed.examName,
            date: ed.examDate,
            score: Math.round(ed.score * 10) / 10,
          })),
        });
      });

      setEvolutionData(evolution);
      setSelectedCompetitors(evolution.map(e => e.competitorId));

    } catch (err) {
      console.error('Error building evolution data:', err);
    }
  };

  const buildEvolutionData = () => {
    // Filter evolution data based on selected modality
    // This would require tracking which competitor belongs to which modality
    // For now, we'll show all competitors
  };

  // Filter simulados by modality
  const filteredSimulados = selectedModality === 'all'
    ? simulados
    : simulados.filter(s => s.modalityId === selectedModality);

  const filteredEvolutionData = evolutionData.filter(
    c => selectedCompetitors.includes(c.competitorId)
  );

  // Calculate statistics from filtered simulados
  const totalSimulados = filteredSimulados.length;
  const averageScore = filteredSimulados.length > 0
    ? (filteredSimulados.reduce((sum, s) => sum + s.averageScore, 0) / filteredSimulados.length).toFixed(1)
    : '0.0';
  const lastSimulado = filteredSimulados[filteredSimulados.length - 1];
  const scoreImprovement = filteredSimulados.length >= 2
    ? (filteredSimulados[filteredSimulados.length - 1].averageScore - filteredSimulados[0].averageScore).toFixed(1)
    : '0.0';

  const handleNavigateToExams = () => {
    navigate('/exams');
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
            Dashboard de Simulados
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Acompanhe a evolução dos competidores nos simulados
          </p>
        </div>
        <div className="flex-shrink-0">
          <Button variant="primary" onClick={handleNavigateToExams}>
            Gerenciar Avaliações
          </Button>
        </div>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
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
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Modalidade
              </label>
              <Select
                value={selectedModality}
                onChange={(e) => setSelectedModality(e.target.value)}
                options={[
                  { value: 'all', label: 'Todas' },
                  ...modalities.map(m => ({ value: m.id, label: m.name })),
                ]}
              />
            </div>
            {evolutionData.length > 0 && (
              <CompetitorSelect
                competitors={evolutionData.map(c => ({
                  id: c.competitorId,
                  name: c.competitorName,
                }))}
                selected={selectedCompetitors}
                onChange={setSelectedCompetitors}
              />
            )}
          </div>
        </CardBody>
      </Card>

      {/* Evolution Chart */}
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
              <p className="text-lg font-medium">Nenhum dado de evolução disponível</p>
              <p className="text-sm mt-1">Lance notas nos simulados para visualizar a evolução dos competidores</p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Simulados List */}
      <Card>
        <CardHeader action={
          <Button size="sm" onClick={handleNavigateToExams}>
            + Novo Simulado
          </Button>
        }>
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
                      <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                        {simulado.name}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(simulado.date).toLocaleDateString('pt-BR')} • {simulado.modality} • {simulado.competitorsCount} competidor{simulado.competitorsCount !== 1 ? 'es' : ''}
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
                    <Button size="sm" variant="secondary" onClick={handleNavigateToExams}>
                      Ver Detalhes
                    </Button>
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
              <Button className="mt-4" onClick={handleNavigateToExams}>
                Ir para Avaliações
              </Button>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};

export default SimuladosDashboard;

import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardBody, Badge, Spinner, Alert } from '../../components/ui';
import { LineChartCard } from '../../components/charts';
import { useAuthStore } from '../../stores/authStore';
import { gradeService, trainingService, enrollmentService, examService } from '../../services';
import type { Grade, TrainingStatistics, Exam, Modality } from '../../types';

interface EvolutionPoint {
  name: string;
  value: number;
}

const MyGradesPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  const [grades, setGrades] = useState<Grade[]>([]);
  const [exams, setExams] = useState<Map<string, Exam>>(new Map());
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [trainingStats, setTrainingStats] = useState<TrainingStatistics | null>(null);
  const [evolutionData, setEvolutionData] = useState<EvolutionPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.id) {
      fetchData();
    }
  }, [user?.id]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch competitor's modalities (through enrollments)
      const myModalities = await enrollmentService.getMyModalities();
      setModalities(myModalities);

      // Fetch all exams from competitor's modalities
      const modalityIds = new Set(myModalities.map(m => m.id));
      const examsResponse = await examService.getAll({ active_only: false, limit: 500 });
      const myExams = examsResponse.exams.filter(e => modalityIds.has(e.modality_id));

      const examMap = new Map<string, Exam>();
      myExams.forEach(e => examMap.set(e.id, e));
      setExams(examMap);

      // Fetch grades for the competitor (we need the competitor ID from the backend)
      // The grades API should filter by the current user when competitor_id is not provided
      // For now, we'll fetch all grades and they should be filtered by the backend
      try {
        const gradesResponse = await gradeService.getAll({ limit: 500 });
        const myGrades = gradesResponse.grades || [];
        setGrades(myGrades);

        // Build evolution data from grades
        buildEvolutionData(myGrades, examMap);
      } catch (err) {
        console.error('Error fetching grades:', err);
        setGrades([]);
      }

      // Fetch training statistics
      // For competitors, the backend should return stats for their own trainings
      try {
        // We need to pass the competitor_id, but for the logged-in competitor
        // we can try to get it from the modalities/enrollments
        const trainingsResponse = await trainingService.getAll({ limit: 1 });
        if (trainingsResponse.trainings.length > 0) {
          const competitorId = trainingsResponse.trainings[0].competitor_id;
          const stats = await trainingService.getStatistics(competitorId);
          setTrainingStats(stats);
        }
      } catch (err) {
        console.error('Error fetching training stats:', err);
      }

    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  const buildEvolutionData = (gradesList: Grade[], examMap: Map<string, Exam>) => {
    // Show each individual grade as a point in the evolution chart
    // Sort by exam date, then by created_at for grades in the same exam
    const gradesWithExamInfo = gradesList.map(grade => {
      const exam = examMap.get(grade.exam_id);
      return {
        ...grade,
        examName: exam?.name || 'Avaliação',
        examDate: exam?.exam_date || grade.created_at,
      };
    });

    // Sort by exam date
    gradesWithExamInfo.sort((a, b) => {
      const dateA = new Date(a.examDate).getTime();
      const dateB = new Date(b.examDate).getTime();
      if (dateA !== dateB) return dateA - dateB;
      // If same exam date, sort by created_at
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    });

    // Build evolution data - each grade is a point
    const evolution = gradesWithExamInfo.map((grade) => {
      // Truncate exam name if too long
      let displayName = grade.examName;
      if (displayName.length > 20) {
        displayName = displayName.substring(0, 17) + '...';
      }

      return {
        name: displayName,
        value: Math.round(grade.score * 10) / 10,
      };
    });

    setEvolutionData(evolution);
  };

  // Calculate statistics
  const averageScore = grades.length > 0
    ? (grades.reduce((sum, g) => sum + g.score, 0) / grades.length).toFixed(1)
    : '0.0';

  const bestScore = grades.length > 0 ? Math.max(...grades.map(g => g.score)).toFixed(1) : '0.0';

  const getScoreVariant = (score: number): 'success' | 'warning' | 'danger' => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  const getExamName = (examId: string) => {
    return exams.get(examId)?.name || `Avaliação`;
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Minhas Notas</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Acompanhe seu desempenho nas avaliações
        </p>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">Média Geral</p>
              <p className="text-4xl font-bold text-blue-700 dark:text-blue-300 mt-2">{averageScore}</p>
              <Badge variant={getScoreVariant(parseFloat(averageScore))} className="mt-2">
                {parseFloat(averageScore) >= 80 ? 'Excelente' : parseFloat(averageScore) >= 60 ? 'Bom' : 'Precisa Melhorar'}
              </Badge>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-green-600 dark:text-green-400 font-medium">Total de Avaliações</p>
              <p className="text-4xl font-bold text-green-700 dark:text-green-300 mt-2">{grades.length}</p>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-purple-600 dark:text-purple-400 font-medium">Melhor Nota</p>
              <p className="text-4xl font-bold text-purple-700 dark:text-purple-300 mt-2">{bestScore}</p>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 border-amber-200 dark:border-amber-700">
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-amber-600 dark:text-amber-400 font-medium">Horas de Treinamento</p>
              <p className="text-4xl font-bold text-amber-700 dark:text-amber-300 mt-2">
                {trainingStats?.approved_hours || 0}h
              </p>
              {trainingStats && trainingStats.pending_hours > 0 && (
                <p className="text-xs text-amber-500 mt-1">
                  +{trainingStats.pending_hours}h pendentes
                </p>
              )}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Training Hours Breakdown */}
      {trainingStats && (
        <Card>
          <CardHeader>Resumo de Treinamentos</CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-500 dark:text-gray-400">Total de Horas</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{trainingStats.total_hours}h</p>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-green-600 dark:text-green-400">Aprovadas</p>
                <p className="text-2xl font-bold text-green-700 dark:text-green-300">{trainingStats.approved_hours}h</p>
              </div>
              <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <p className="text-sm text-yellow-600 dark:text-yellow-400">Pendentes</p>
                <p className="text-2xl font-bold text-yellow-700 dark:text-yellow-300">{trainingStats.pending_hours}h</p>
              </div>
              <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">Rejeitadas</p>
                <p className="text-2xl font-bold text-red-700 dark:text-red-300">{trainingStats.rejected_hours}h</p>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Evolution Chart */}
        <Card>
          <CardHeader>Notas por Simulado</CardHeader>
          <CardBody>
            {evolutionData.length > 0 ? (
              <LineChartCard data={evolutionData} color="#3B82F6" height={250} />
            ) : (
              <div className="flex items-center justify-center h-[250px] text-gray-500 dark:text-gray-400">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p>Nenhuma nota lançada ainda</p>
                </div>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Recent Grades */}
        <Card>
          <CardHeader>Últimas Notas</CardHeader>
          <CardBody>
            {grades.length > 0 ? (
              <div className="space-y-4">
                {[...grades]
                  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .slice(0, 5)
                  .map((grade) => (
                    <div
                      key={grade.id}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          {getExamName(grade.exam_id)}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {new Date(grade.created_at).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      <Badge variant={getScoreVariant(grade.score)} size="lg">
                        {grade.score.toFixed(1)}
                      </Badge>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-[200px] text-gray-500 dark:text-gray-400">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <p>Nenhuma nota lançada ainda</p>
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Modalities */}
      {modalities.length > 0 && (
        <Card>
          <CardHeader>Minhas Modalidades</CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {modalities.map((modality) => (
                <div
                  key={modality.id}
                  className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">{modality.name}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{modality.code}</p>
                    </div>
                    <Badge variant={modality.is_active ? 'success' : 'default'}>
                      {modality.is_active ? 'Ativa' : 'Inativa'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

export default MyGradesPage;

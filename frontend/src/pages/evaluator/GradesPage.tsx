import React, { useEffect, useState } from 'react';
import { Card, CardBody, Button, Table, Badge, Spinner, Alert, Modal } from '../../components/ui';
import { gradeService, examService, modalityService, competitorService, enrollmentService } from '../../services';
import { useAuthStore } from '../../stores/authStore';
import type { Grade, Exam, Competence, Competitor, Modality } from '../../types';

const GradesPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const isCompetitor = user?.role === 'competitor';

  // Main data
  const [grades, setGrades] = useState<Grade[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);

  // Bulk grade modal state
  const [isBulkGradeModalOpen, setIsBulkGradeModalOpen] = useState(false);
  const [bulkGradeExam, setBulkGradeExam] = useState<Exam | null>(null);
  const [bulkCompetitors, setBulkCompetitors] = useState<Competitor[]>([]);
  const [bulkCompetences, setBulkCompetences] = useState<Competence[]>([]);
  const [bulkGrades, setBulkGrades] = useState<Map<string, string>>(new Map());
  const [existingGrades, setExistingGrades] = useState<Grade[]>([]);
  const [isLoadingBulkData, setIsLoadingBulkData] = useState(false);
  const [isSavingBulkGrades, setIsSavingBulkGrades] = useState(false);

  // Filter state
  const [filterExamId, setFilterExamId] = useState<string>('');

  // Loading/Error
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Maps for displaying names
  const [competitorMap, setCompetitorMap] = useState<Map<string, string>>(new Map());
  const [examMap, setExamMap] = useState<Map<string, Exam>>(new Map());
  const [competenceMap, setCompetenceMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (filterExamId) {
      fetchGradesByExam(filterExamId);
    }
  }, [filterExamId]);

  const fetchInitialData = async () => {
    try {
      setIsLoading(true);

      // Fetch modalities assigned to the current user (evaluator)
      const [examsResponse, myModalities] = await Promise.all([
        examService.getAll({ active_only: true, limit: 500 }),
        enrollmentService.getMyModalities(),
      ]);

      // Get the IDs of modalities the user has access to
      const myModalityIds = new Set(myModalities.map((m: Modality) => m.id));

      // Filter exams to only those from the user's modalities
      const examsList = (examsResponse.exams || []).filter(
        (exam: Exam) => myModalityIds.has(exam.modality_id)
      );

      setExams(examsList);

      // Build exam map
      const eMap = new Map<string, Exam>();
      examsList.forEach((e: Exam) => eMap.set(e.id, e));
      setExamMap(eMap);

      // Build competence map from the user's modalities
      const cMap = new Map<string, string>();
      for (const mod of myModalities || []) {
        const comps = (mod as any)?.competences || [];
        comps.forEach((c: Competence) => cMap.set(c.id, c.name));
      }
      setCompetenceMap(cMap);

      // If there are exams, select the first one and load its grades
      if (examsList.length > 0) {
        setFilterExamId(examsList[0].id);
      }

    } catch (err: any) {
      console.error('Error fetching initial data:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchGradesByExam = async (examId: string) => {
    try {
      const response = await gradeService.getAll({ exam_id: examId, limit: 1000 });
      setGrades(response.grades || []);

      // Fetch competitor names for the grades
      const compIds = new Set<string>();
      (response.grades || []).forEach(g => compIds.add(g.competitor_id));

      const cmpMap = new Map<string, string>(competitorMap);
      for (const compId of compIds) {
        if (!cmpMap.has(compId)) {
          try {
            const competitor = await competitorService.getById(compId);
            cmpMap.set(compId, competitor.full_name);
          } catch (err) {
            console.error(`Error fetching competitor ${compId}:`, err);
          }
        }
      }
      setCompetitorMap(cmpMap);

    } catch (err: any) {
      console.error('Error fetching grades:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar notas');
    }
  };

  // Open bulk grade modal
  const handleOpenBulkGradeModal = async () => {
    if (!filterExamId) {
      setError('Selecione uma avaliação primeiro');
      return;
    }

    const exam = examMap.get(filterExamId);
    if (!exam) return;

    setBulkGradeExam(exam);
    setIsBulkGradeModalOpen(true);
    setIsLoadingBulkData(true);

    try {
      // Fetch competitors for the exam's modality
      const competitorResponse = await competitorService.getByModality(exam.modality_id);
      setBulkCompetitors(competitorResponse.competitors || []);

      // Fetch modality with competences
      const modalityData = await modalityService.getById(exam.modality_id);
      const allCompetences = (modalityData as any)?.competences || [];

      // Filter competences to only those assigned to this exam
      if (exam.competence_ids && exam.competence_ids.length > 0) {
        const examCompetences = allCompetences.filter((c: Competence) =>
          exam.competence_ids.includes(c.id)
        );
        setBulkCompetences(examCompetences);
      } else {
        setBulkCompetences(allCompetences);
      }

      // Fetch existing grades for this exam
      const gradesResponse = await gradeService.getAll({ exam_id: exam.id });
      setExistingGrades(gradesResponse.grades || []);

      // Initialize bulk grades map with existing values
      const initialGrades = new Map<string, string>();
      (gradesResponse.grades || []).forEach((g: Grade) => {
        const key = `${g.competitor_id}|${g.competence_id}`;
        initialGrades.set(key, g.score.toString());
      });
      setBulkGrades(initialGrades);
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError('Erro ao carregar dados para lançamento de notas');
    } finally {
      setIsLoadingBulkData(false);
    }
  };

  const handleCloseBulkGradeModal = () => {
    setIsBulkGradeModalOpen(false);
    setBulkGradeExam(null);
    setBulkCompetitors([]);
    setBulkCompetences([]);
    setExistingGrades([]);
    setBulkGrades(new Map());
  };

  const handleBulkGradeChange = (competitorId: string, competenceId: string, value: string) => {
    const key = `${competitorId}|${competenceId}`;
    setBulkGrades(prev => {
      const newMap = new Map(prev);
      if (value === '' || value === null) {
        newMap.delete(key);
      } else {
        newMap.set(key, value);
      }
      return newMap;
    });
  };

  const getBulkGradeValue = (competitorId: string, competenceId: string): string => {
    const key = `${competitorId}|${competenceId}`;
    return bulkGrades.get(key) || '';
  };

  const getExistingGrade = (competitorId: string, competenceId: string): Grade | undefined => {
    return existingGrades.find(g => g.competitor_id === competitorId && g.competence_id === competenceId);
  };

  const handleSaveBulkGrades = async () => {
    if (!bulkGradeExam) return;

    setIsSavingBulkGrades(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const [key, scoreStr] of bulkGrades.entries()) {
        const [competitorId, competenceId] = key.split('|');
        const score = parseFloat(scoreStr);

        if (isNaN(score) || score < 0 || score > 100) {
          continue; // Skip invalid scores
        }

        const existingGrade = getExistingGrade(competitorId, competenceId);

        try {
          if (existingGrade) {
            // Update existing grade
            if (existingGrade.score !== score) {
              await gradeService.update(existingGrade.id, { score });
              successCount++;
            }
          } else {
            // Create new grade
            await gradeService.create({
              exam_id: bulkGradeExam.id,
              competitor_id: competitorId,
              competence_id: competenceId,
              score,
            });
            successCount++;
          }
        } catch (err) {
          console.error(`Erro ao salvar nota para ${competitorId}/${competenceId}:`, err);
          errorCount++;
        }
      }

      if (successCount > 0) {
        setSuccessMessage(`${successCount} nota(s) salva(s) com sucesso!${errorCount > 0 ? ` (${errorCount} erro(s))` : ''}`);
        setTimeout(() => setSuccessMessage(null), 3000);
      }

      if (errorCount > 0 && successCount === 0) {
        setError(`Erro ao salvar notas. ${errorCount} erro(s) encontrado(s).`);
      }

      handleCloseBulkGradeModal();

      // Refresh grades list
      if (filterExamId) {
        await fetchGradesByExam(filterExamId);
      }
    } catch (err) {
      setError('Erro ao salvar notas em lote');
    } finally {
      setIsSavingBulkGrades(false);
    }
  };

  const getScoreVariant = (score: number): 'success' | 'warning' | 'danger' => {
    if (score >= 70) return 'success';
    if (score >= 50) return 'warning';
    return 'danger';
  };

  const getCompetitorName = (competitorId: string) => {
    return competitorMap.get(competitorId) || competitorId.slice(0, 8) + '...';
  };

  const getCompetenceName = (competenceId: string) => {
    return competenceMap.get(competenceId) || competenceId.slice(0, 8) + '...';
  };

  // Calculate statistics
  const totalGrades = grades.length;
  const averageScore = grades.length > 0
    ? (grades.reduce((sum, g) => sum + g.score, 0) / grades.length)
    : 0;
  const uniqueCompetitors = new Set(grades.map(g => g.competitor_id)).size;

  const columns = [
    {
      key: 'competitor_id',
      header: 'Competidor',
      render: (item: Grade) => (
        <span className="font-medium">{getCompetitorName(item.competitor_id)}</span>
      ),
    },
    {
      key: 'competence_id',
      header: 'Competência',
      render: (item: Grade) => getCompetenceName(item.competence_id),
    },
    {
      key: 'score',
      header: 'Nota',
      render: (item: Grade) => (
        <Badge variant={getScoreVariant(item.score)}>
          {item.score.toFixed(1)}
        </Badge>
      ),
    },
    {
      key: 'notes',
      header: 'Observações',
      render: (item: Grade) => (
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {item.notes || '-'}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Data',
      render: (item: Grade) => new Date(item.created_at).toLocaleDateString('pt-BR'),
    },
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Notas</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            {isCompetitor ? 'Visualize suas notas' : 'Lançamento e gestão de notas'}
          </p>
        </div>
        {!isCompetitor && (
          <div className="flex-shrink-0">
            <Button onClick={handleOpenBulkGradeModal} disabled={!filterExamId}>
              Lançar Notas
            </Button>
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert type="success" onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-xs text-blue-600 dark:text-blue-400 font-medium uppercase tracking-wide">Média Geral</p>
              <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{averageScore.toFixed(1)}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-green-100 dark:bg-green-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-xs text-green-600 dark:text-green-400 font-medium uppercase tracking-wide">Total de Notas</p>
              <p className="text-3xl font-bold text-green-700 dark:text-green-300">{totalGrades}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-purple-100 dark:bg-purple-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <p className="text-xs text-purple-600 dark:text-purple-400 font-medium uppercase tracking-wide">Competidores Avaliados</p>
              <p className="text-3xl font-bold text-purple-700 dark:text-purple-300">{uniqueCompetitors}</p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Filter by Exam */}
      <Card>
        <CardBody>
          <div className="flex items-end gap-4">
            <div className="flex-1 max-w-md">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Filtrar por Avaliação
              </label>
              <select
                value={filterExamId}
                onChange={(e) => setFilterExamId(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
              >
                <option value="">Selecione uma avaliação</option>
                {exams.map(exam => (
                  <option key={exam.id} value={exam.id}>
                    {exam.name} - {new Date(exam.exam_date).toLocaleDateString('pt-BR')}
                  </option>
                ))}
              </select>
            </div>
            {filterExamId && (
              <Button
                variant="secondary"
                onClick={() => fetchGradesByExam(filterExamId)}
              >
                Atualizar
              </Button>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Grades Table */}
      <Card padding="none">
        {filterExamId ? (
          <Table
            data={grades}
            columns={columns}
            keyExtractor={(item) => item.id}
            emptyMessage="Nenhuma nota lançada para esta avaliação"
          />
        ) : (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-lg">Selecione uma avaliação para ver as notas</p>
          </div>
        )}
      </Card>

      {/* Bulk Grade Modal */}
      <Modal
        isOpen={isBulkGradeModalOpen}
        onClose={handleCloseBulkGradeModal}
        title={`Lançar Notas - ${bulkGradeExam?.name || ''}`}
        size="xl"
      >
        {isLoadingBulkData ? (
          <div className="flex justify-center items-center h-32">
            <Spinner size="lg" />
          </div>
        ) : (
          <div className="space-y-4">
            {/* Info about the exam */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  <p className="font-medium mb-1">Lançamento em Massa</p>
                  <p>Preencha as notas de todos os competidores de uma vez. Notas existentes serão atualizadas automaticamente.</p>
                </div>
              </div>
            </div>

            {bulkCompetitors.length === 0 ? (
              <Alert type="warning">
                Nenhum competidor encontrado para a modalidade desta avaliação.
              </Alert>
            ) : bulkCompetences.length === 0 ? (
              <Alert type="warning">
                Nenhuma competência cadastrada para esta modalidade. Cadastre as competências na modalidade primeiro.
              </Alert>
            ) : (
              <>
                {/* Grid de notas */}
                <div className="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-800">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider sticky left-0 bg-gray-50 dark:bg-gray-800 z-10 min-w-[180px]">
                          Competidor
                        </th>
                        {bulkCompetences.map((comp) => (
                          <th
                            key={comp.id}
                            className="px-3 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider min-w-[100px]"
                            title={comp.description || comp.name}
                          >
                            {comp.name.length > 15 ? comp.name.substring(0, 15) + '...' : comp.name}
                            <span className="block text-gray-400 font-normal normal-case">
                              (0-{comp.max_score})
                            </span>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                      {bulkCompetitors.map((competitor, idx) => (
                        <tr key={competitor.id} className={idx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800/50'}>
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 sticky left-0 bg-inherit z-10 border-r border-gray-200 dark:border-gray-700">
                            {competitor.full_name}
                          </td>
                          {bulkCompetences.map((comp) => {
                            const existingGrade = getExistingGrade(competitor.id, comp.id);
                            const currentValue = getBulkGradeValue(competitor.id, comp.id);
                            const hasChanged = existingGrade && currentValue !== '' && parseFloat(currentValue) !== existingGrade.score;

                            return (
                              <td key={comp.id} className="px-2 py-2 text-center">
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  step="0.1"
                                  value={currentValue}
                                  onChange={(e) => handleBulkGradeChange(competitor.id, comp.id, e.target.value)}
                                  placeholder="-"
                                  className={`w-20 text-center rounded-lg border px-2 py-1.5 text-sm transition-colors
                                    ${existingGrade && !hasChanged
                                      ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700'
                                      : hasChanged
                                        ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700'
                                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'
                                    }
                                    text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                                />
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Legenda */}
                <div className="flex items-center gap-6 text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded border border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-700"></div>
                    <span>Nota já lançada</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded border border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-700"></div>
                    <span>Nota alterada</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded border border-gray-300 bg-white dark:bg-gray-700 dark:border-gray-600"></div>
                    <span>Nova nota</span>
                  </div>
                </div>

                {/* Resumo */}
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{bulkCompetitors.length}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Competidores</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{bulkCompetences.length}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Competências</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{bulkGrades.size}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Notas preenchidas</p>
                    </div>
                  </div>
                </div>

                {/* Botões */}
                <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <Button type="button" variant="secondary" onClick={handleCloseBulkGradeModal}>
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleSaveBulkGrades}
                    isLoading={isSavingBulkGrades}
                    disabled={bulkGrades.size === 0}
                  >
                    Salvar Todas as Notas
                  </Button>
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default GradesPage;

import React, { useEffect, useState } from 'react';
import { Card, CardBody, Button, Table, Badge, Spinner, Alert, Modal } from '../../components/ui';
import { gradeService, examService, modalityService, competitorService, enrollmentService, subCompetenceService, examTimeService } from '../../services';
import { useAuthStore } from '../../stores/authStore';
import type { Grade, Exam, Competence, Competitor, Modality, SubCompetence } from '../../types';

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
  const [bulkSubCompetences, setBulkSubCompetences] = useState<Map<string, SubCompetence[]>>(new Map());
  const [bulkTimes, setBulkTimes] = useState<Map<string, string>>(new Map());

  const minutesToTimeStr = (minutes: number): string => {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return `${h}:${m.toString().padStart(2, '0')}`;
  };

  const parseTimeStr = (str: string): number | null => {
    const parts = str.split(':');
    if (parts.length !== 2) return null;
    const h = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10);
    if (isNaN(h) || isNaN(m) || m < 0 || m > 59) return null;
    return h * 60 + m;
  };

  // Filter state
  const [filterExamId, setFilterExamId] = useState<string>('');

  // Loading/Error
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Maps for displaying names
  const [competitorMap, setCompetitorMap] = useState<Map<string, string>>(new Map());
  const [examMap, setExamMap] = useState<Map<string, Exam>>(new Map());
  const [_competenceMap, setCompetenceMap] = useState<Map<string, string>>(new Map());

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
    setBulkSubCompetences(new Map());

    try {
      // Fetch competitors for the exam's modality
      const competitorResponse = await competitorService.getByModality(exam.modality_id);
      setBulkCompetitors(competitorResponse.competitors || []);

      // Fetch modality with competences
      const modalityData = await modalityService.getById(exam.modality_id);
      const allCompetences = (modalityData as any)?.competences || [];

      // Filter competences to only those assigned to this exam
      let examCompetences: Competence[];
      if (exam.competence_ids && exam.competence_ids.length > 0) {
        examCompetences = allCompetences.filter((c: Competence) =>
          exam.competence_ids.includes(c.id)
        );
      } else {
        examCompetences = allCompetences;
      }
      setBulkCompetences(examCompetences);

      // Fetch sub-criteria for each competence
      const subMap = new Map<string, SubCompetence[]>();
      await Promise.all(examCompetences.map(async (c: Competence) => {
        try {
          const subs = await subCompetenceService.list(c.id);
          if (subs.length > 0) subMap.set(c.id, subs);
        } catch { /* ignore */ }
      }));
      setBulkSubCompetences(subMap);

      // Fetch existing grades for this exam
      const gradesResponse = await gradeService.getAll({ exam_id: exam.id });
      setExistingGrades(gradesResponse.grades || []);

      // Initialize bulk grades map with existing values
      const initialGrades = new Map<string, string>();
      (gradesResponse.grades || []).forEach((g: Grade) => {
        const key = g.sub_competence_id
          ? `${g.competitor_id}|${g.competence_id}|${g.sub_competence_id}`
          : `${g.competitor_id}|${g.competence_id}`;
        initialGrades.set(key, g.score.toString());
      });
      setBulkGrades(initialGrades);

      // Load competitor times
      try {
        const times = await examTimeService.getTimes(exam.id);
        const initialTimes = new Map<string, string>();
        times.forEach(t => initialTimes.set(t.competitor_id, minutesToTimeStr(t.duration_minutes)));
        setBulkTimes(initialTimes);
      } catch { /* ignore */ }
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
    setBulkSubCompetences(new Map());
    setBulkTimes(new Map());
  };

  const handleBulkGradeChange = (competitorId: string, competenceId: string, value: string, subCompetenceId?: string) => {
    const key = subCompetenceId ? `${competitorId}|${competenceId}|${subCompetenceId}` : `${competitorId}|${competenceId}`;
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

  const getBulkGradeValue = (competitorId: string, competenceId: string, subCompetenceId?: string): string => {
    const key = subCompetenceId ? `${competitorId}|${competenceId}|${subCompetenceId}` : `${competitorId}|${competenceId}`;
    return bulkGrades.get(key) || '';
  };

  const getExistingGrade = (competitorId: string, competenceId: string, subCompetenceId?: string): Grade | undefined => {
    return existingGrades.find(g =>
      g.competitor_id === competitorId &&
      g.competence_id === competenceId &&
      (subCompetenceId ? g.sub_competence_id === subCompetenceId : !g.sub_competence_id)
    );
  };

  const handleGridKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const key = e.key;
    if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) return;

    const table = e.currentTarget.closest('table');
    if (!table) return;

    const rows = Array.from(table.querySelectorAll<HTMLTableRowElement>('tbody tr'));
    const currentRow = e.currentTarget.closest('tr') as HTMLTableRowElement | null;
    if (!currentRow) return;

    const rowIndex = rows.indexOf(currentRow);
    const rowInputs = Array.from(currentRow.querySelectorAll<HTMLInputElement>('input'));
    const colIndex = rowInputs.indexOf(e.currentTarget);

    e.preventDefault();

    if (key === 'ArrowUp' || key === 'ArrowDown') {
      const nextRow = rows[rowIndex + (key === 'ArrowDown' ? 1 : -1)];
      if (nextRow) {
        const nextInputs = Array.from(nextRow.querySelectorAll<HTMLInputElement>('input'));
        const target = nextInputs[Math.min(colIndex, nextInputs.length - 1)];
        if (target) { target.focus(); target.select(); }
      }
    } else {
      const target = rowInputs[colIndex + (key === 'ArrowRight' ? 1 : -1)];
      if (target) { target.focus(); target.select(); }
    }
  };

  const handleSaveBulkGrades = async () => {
    if (!bulkGradeExam) return;

    setIsSavingBulkGrades(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      // Process updated/new grades from the map
      for (const [key, scoreStr] of bulkGrades.entries()) {
        const parts = key.split('|');
        const competitorId = parts[0];
        const competenceId = parts[1];
        const subCompetenceId = parts[2];
        const existingGrade = getExistingGrade(competitorId, competenceId, subCompetenceId);

        // Empty field + existing grade → delete
        if (scoreStr === '' || scoreStr === null) {
          if (existingGrade) {
            try {
              await gradeService.delete(existingGrade.id);
              successCount++;
            } catch (err) {
              console.error(`Erro ao remover nota para ${competitorId}/${competenceId}:`, err);
              errorCount++;
            }
          }
          continue;
        }

        const score = parseFloat(scoreStr);
        if (isNaN(score) || score < 0) {
          continue; // Skip invalid scores
        }

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
              sub_competence_id: subCompetenceId,
              score,
            });
            successCount++;
          }
        } catch (err) {
          console.error(`Erro ao salvar nota para ${competitorId}/${competenceId}:`, err);
          errorCount++;
        }
      }

      // Delete grades that were cleared (existing but removed from the map)
      for (const existingGrade of existingGrades) {
        const key = existingGrade.sub_competence_id
          ? `${existingGrade.competitor_id}|${existingGrade.competence_id}|${existingGrade.sub_competence_id}`
          : `${existingGrade.competitor_id}|${existingGrade.competence_id}`;
        if (!bulkGrades.has(key)) {
          try {
            await gradeService.delete(existingGrade.id);
            successCount++;
          } catch (err) {
            console.error(`Erro ao remover nota ${existingGrade.id}:`, err);
            errorCount++;
          }
        }
      }

      // Save competitor times
      for (const [competitorId, timeStr] of bulkTimes.entries()) {
        const minutes = parseTimeStr(timeStr);
        if (minutes !== null && minutes > 0) {
          try {
            await examTimeService.setTime(bulkGradeExam.id, competitorId, minutes);
          } catch { /* ignore */ }
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


  // Calculate statistics
  const totalGrades = grades.length;
  const averageScore = grades.length > 0
    ? (grades.reduce((sum, g) => sum + g.score, 0) / grades.length)
    : 0;
  const uniqueCompetitors = new Set(grades.map(g => g.competitor_id)).size;

  // Group grades by competitor
  type GroupedGrade = {
    competitor_id: string;
    total_score: number;
    average_score: number;
    count: number;
    latest_date: string;
  };

  const groupedGradesMap = new Map<string, GroupedGrade>();
  grades.forEach((g) => {
    const existing = groupedGradesMap.get(g.competitor_id);
    if (existing) {
      existing.total_score += g.score;
      existing.count += 1;
      existing.average_score = existing.total_score / existing.count;
      if (g.created_at > existing.latest_date) existing.latest_date = g.created_at;
    } else {
      groupedGradesMap.set(g.competitor_id, {
        competitor_id: g.competitor_id,
        total_score: g.score,
        average_score: g.score,
        count: 1,
        latest_date: g.created_at,
      });
    }
  });
  const groupedGrades = Array.from(groupedGradesMap.values()).sort((a, b) =>
    getCompetitorName(a.competitor_id).localeCompare(getCompetitorName(b.competitor_id))
  );

  const columns = [
    {
      key: 'competitor_id',
      header: 'Competidor',
      render: (item: GroupedGrade) => (
        <span className="font-medium">{getCompetitorName(item.competitor_id)}</span>
      ),
    },
    {
      key: 'total_score',
      header: 'Total',
      render: (item: GroupedGrade) => (
        <Badge variant={getScoreVariant(item.total_score)}>
          {item.total_score.toFixed(1)}
        </Badge>
      ),
    },
    {
      key: 'count',
      header: 'Critérios de Avaliação',
      render: (item: GroupedGrade) => (
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {item.count}
        </span>
      ),
    },
    {
      key: 'latest_date',
      header: 'Data',
      render: (item: GroupedGrade) => new Date(item.latest_date).toLocaleDateString('pt-BR'),
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
            data={groupedGrades}
            columns={columns}
            keyExtractor={(item) => item.competitor_id}
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
            <div className="flex items-center gap-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
              <div className="flex-shrink-0 w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-800/60 flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-blue-800 dark:text-blue-200">Lançamento em Massa</p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-0.5">Preencha as notas de todos os competidores. Notas existentes serão atualizadas automaticamente.</p>
              </div>
            </div>

            {bulkCompetitors.length === 0 ? (
              <Alert type="warning">
                Nenhum competidor encontrado para a modalidade desta avaliação.
              </Alert>
            ) : bulkCompetences.length === 0 ? (
              <Alert type="warning">
                Nenhum critério de avaliação cadastrado para esta modalidade. Cadastre os critérios de avaliação na modalidade primeiro.
              </Alert>
            ) : (
              <>
                {/* Barra de progresso */}
                {(() => {
                  const hasAnySubs = bulkCompetences.some(comp => {
                    const subs = bulkSubCompetences.get(comp.id);
                    return subs && subs.length > 0;
                  });
                  const totalColumns = bulkCompetences.reduce((acc, comp) => {
                    const subs = bulkSubCompetences.get(comp.id);
                    return acc + (subs && subs.length > 0 ? subs.length : 1);
                  }, 0);
                  const totalCells = bulkCompetitors.length * totalColumns;
                  const fillPct = totalCells > 0 ? Math.round((bulkGrades.size / totalCells) * 100) : 0;
                  return (
                    <>
                      <div className="bg-gray-50 dark:bg-gray-800/60 rounded-xl border border-gray-200 dark:border-gray-700 px-4 py-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Progresso do preenchimento</span>
                          <span className="text-xs font-bold text-gray-800 dark:text-gray-200">{bulkGrades.size} / {totalCells} notas</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full transition-all duration-500 ${fillPct >= 100 ? 'bg-emerald-500' : fillPct > 0 ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'}`}
                            style={{ width: `${Math.min(fillPct, 100)}%` }}
                          />
                        </div>
                      </div>

                      {/* Tabela de notas */}
                      <div className="overflow-auto rounded-xl border border-gray-200 dark:border-gray-700 max-h-[440px]">
                        <table className="min-w-full border-collapse">
                          <thead>
                            <tr className="bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                              <th
                                rowSpan={hasAnySubs ? 2 : 1}
                                className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider sticky left-0 bg-gray-100 dark:bg-gray-800 z-20 min-w-[160px] border-r-2 border-gray-300 dark:border-gray-600"
                              >
                                Competidor
                              </th>
                              {true && (
                                <th
                                  rowSpan={hasAnySubs ? 2 : 1}
                                  className="px-2 py-2.5 text-center text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-wider border-l-2 border-orange-200 dark:border-orange-700 bg-orange-50 dark:bg-orange-900/20 min-w-[80px]"
                                  title="Tempo gasto no simulado (h:mm)"
                                >
                                  <div className="flex flex-col items-center gap-0.5">
                                    <span>Tempo</span>
                                    <span className="text-[9px] font-normal text-orange-500 dark:text-orange-400">(h:mm)</span>
                                  </div>
                                </th>
                              )}
                              {bulkCompetences.map((comp) => {
                                const subs = bulkSubCompetences.get(comp.id);
                                const hasSubs = subs && subs.length > 0;
                                const colSpan = hasSubs ? subs.length : 1;
                                const rowSpan = hasAnySubs && !hasSubs ? 2 : 1;
                                return (
                                  <th
                                    key={comp.id}
                                    colSpan={colSpan}
                                    rowSpan={rowSpan}
                                    className="px-3 py-2.5 text-center text-xs font-semibold text-gray-700 dark:text-gray-200 border-l border-gray-200 dark:border-gray-600"
                                    title={comp.description || comp.name}
                                  >
                                    <div className="flex flex-col items-center gap-1">
                                      <span className="leading-tight">{comp.name}</span>
                                      {!hasSubs && (
                                        <span className="text-[10px] font-normal text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-600/60 px-2 py-0.5 rounded-full">
                                          0 – {comp.max_score}
                                        </span>
                                      )}
                                    </div>
                                  </th>
                                );
                              })}
                            </tr>
                            {hasAnySubs && (
                              <tr className="bg-indigo-50/60 dark:bg-indigo-900/10 border-b-2 border-gray-300 dark:border-gray-600">
                                {bulkCompetences.map((comp) => {
                                  const subs = bulkSubCompetences.get(comp.id);
                                  if (!subs || subs.length === 0) return null;
                                  return subs.map((sub) => (
                                    <th
                                      key={sub.id}
                                      className="px-2 py-2 text-center border-l border-gray-200 dark:border-gray-600 min-w-[90px]"
                                      title={`${comp.name} › ${sub.name}`}
                                    >
                                      <div className="flex flex-col items-center gap-0.5">
                                        <span className="text-[10px] font-semibold text-indigo-700 dark:text-indigo-300">
                                          {sub.name.length > 12 ? sub.name.substring(0, 12) + '…' : sub.name}
                                        </span>
                                        <span className="text-[9px] font-normal text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-700/60 px-1.5 py-0.5 rounded-full">
                                          0 – {sub.max_score}
                                        </span>
                                      </div>
                                    </th>
                                  ));
                                })}
                              </tr>
                            )}
                          </thead>
                          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800">
                            {bulkCompetitors.map((competitor) => (
                              <tr key={competitor.id} className="group hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-colors">
                                <td className="px-3 py-2.5 whitespace-nowrap sticky left-0 bg-white dark:bg-gray-900 group-hover:bg-blue-50/50 dark:group-hover:bg-blue-900/10 z-10 border-r-2 border-gray-200 dark:border-gray-700 transition-colors">
                                  <div className="flex items-center gap-2.5">
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center flex-shrink-0">
                                      <span className="text-xs font-bold text-white">
                                        {competitor.full_name.split(' ').slice(0, 2).map((n: string) => n[0]).join('').toUpperCase()}
                                      </span>
                                    </div>
                                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate max-w-[110px]" title={competitor.full_name}>
                                      {competitor.full_name}
                                    </span>
                                  </div>
                                </td>
                                {true && (
                                  <td className="px-2 py-2 text-center border-l-2 border-orange-200 dark:border-orange-800 bg-orange-50/30 dark:bg-orange-900/10">
                                    <input
                                      type="text"
                                      inputMode="text"
                                      value={bulkTimes.get(competitor.id) || ''}
                                      onChange={(e) => {
                                        const digits = e.target.value.replace(/[^0-9]/g, '');
                                        const v = digits.length <= 2 ? digits : digits.slice(0, 2) + ':' + digits.slice(2, 4);
                                        setBulkTimes(prev => {
                                          const next = new Map(prev);
                                          if (v === '') next.delete(competitor.id);
                                          else next.set(competitor.id, v);
                                          return next;
                                        });
                                      }}
                                      onKeyDown={handleGridKeyDown}
                                      placeholder="0:00"
                                      title="Tempo gasto (horas:minutos, ex: 1:30)"
                                      className={`w-[62px] text-center rounded-lg border-2 px-1.5 py-1.5 text-sm font-semibold appearance-none outline-none focus:ring-2 focus:ring-orange-400 focus:ring-offset-0
                                        ${bulkTimes.get(competitor.id)
                                          ? 'bg-orange-50 dark:bg-orange-900/20 border-orange-400 dark:border-orange-600 text-orange-700 dark:text-orange-300'
                                          : 'border-orange-200 dark:border-orange-700 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:border-orange-300'
                                        }`}
                                    />
                                  </td>
                                )}
                                {bulkCompetences.map((comp) => {
                                  const subs = bulkSubCompetences.get(comp.id);
                                  if (subs && subs.length > 0) {
                                    return subs.map((sub) => {
                                      const existingGrade = getExistingGrade(competitor.id, comp.id, sub.id);
                                      const currentValue = getBulkGradeValue(competitor.id, comp.id, sub.id);
                                      const hasChanged = existingGrade && currentValue !== '' && parseFloat(currentValue) !== existingGrade.score;
                                      return (
                                        <td key={sub.id} className="px-2 py-2 text-center border-l border-gray-100 dark:border-gray-800">
                                          <input
                                            type="number"
                                            min="0"
                                            max={sub.max_score}
                                            step="0.1"
                                            value={currentValue}
                                            onChange={(e) => handleBulkGradeChange(competitor.id, comp.id, e.target.value, sub.id)}
                                            onKeyDown={handleGridKeyDown}
                                            placeholder="–"
                                            className={`w-[72px] text-center rounded-lg border-2 px-1.5 py-1.5 text-sm font-semibold transition-all
                                              [appearance:none] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none
                                              focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-1 dark:focus:ring-offset-gray-900
                                              ${existingGrade && !hasChanged
                                                ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-400 dark:border-emerald-600 text-emerald-700 dark:text-emerald-300'
                                                : hasChanged
                                                  ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-400 dark:border-amber-500 text-amber-700 dark:text-amber-300'
                                                  : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:border-blue-300 dark:hover:border-blue-500'
                                              }`}
                                          />
                                        </td>
                                      );
                                    });
                                  }
                                  const existingGrade = getExistingGrade(competitor.id, comp.id);
                                  const currentValue = getBulkGradeValue(competitor.id, comp.id);
                                  const hasChanged = existingGrade && currentValue !== '' && parseFloat(currentValue) !== existingGrade.score;
                                  return (
                                    <td key={comp.id} className="px-2 py-2 text-center border-l border-gray-100 dark:border-gray-800">
                                      <input
                                        type="number"
                                        min="0"
                                        max={comp.max_score}
                                        step="0.1"
                                        value={currentValue}
                                        onChange={(e) => handleBulkGradeChange(competitor.id, comp.id, e.target.value)}
                                        onKeyDown={handleGridKeyDown}
                                        placeholder="–"
                                        className={`w-[72px] text-center rounded-lg border-2 px-1.5 py-1.5 text-sm font-semibold transition-all
                                          [appearance:none] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none
                                          focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-1 dark:focus:ring-offset-gray-900
                                          ${existingGrade && !hasChanged
                                            ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-400 dark:border-emerald-600 text-emerald-700 dark:text-emerald-300'
                                            : hasChanged
                                              ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-400 dark:border-amber-500 text-amber-700 dark:text-amber-300'
                                              : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:border-blue-300 dark:hover:border-blue-500'
                                          }`}
                                      />
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  );
                })()}

                {/* Legenda e Resumo */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-1.5">
                      <div className="w-4 h-4 rounded border-2 border-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 dark:border-emerald-600"></div>
                      <span>Nota lançada</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-4 h-4 rounded border-2 border-amber-400 bg-amber-50 dark:bg-amber-900/30 dark:border-amber-500"></div>
                      <span>Nota alterada</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-4 h-4 rounded border-2 border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-600"></div>
                      <span>Não preenchida</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs flex-shrink-0">
                    <span className="px-2.5 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400 font-medium">
                      {bulkCompetitors.length} competidores
                    </span>
                    <span className="px-2.5 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400 font-medium">
                      {bulkCompetences.length} critérios
                    </span>
                    <span className={`px-2.5 py-1 rounded-full font-medium ${bulkGrades.size > 0 ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'}`}>
                      {bulkGrades.size} preenchidas
                    </span>
                  </div>
                </div>

                {/* Botões */}
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <Button type="button" variant="secondary" onClick={handleCloseBulkGradeModal}>
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleSaveBulkGrades}
                    isLoading={isSavingBulkGrades}
                    disabled={bulkGrades.size === 0 && existingGrades.length === 0}
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

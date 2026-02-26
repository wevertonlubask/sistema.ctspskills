import React, { useEffect, useState } from 'react';
import { Card, Button, Table, Badge, Spinner, Alert, Modal, Input, Select, RichTextEditor, RichTextDisplay } from '../../components/ui';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { examService, gradeService, modalityService, competitorService, enrollmentService } from '../../services';
import type { Exam, Modality, Competitor, Grade, Competence } from '../../types';

const examSchema = z.object({
  name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  description: z.string().optional(),
  modality_id: z.string().min(1, 'Selecione uma modalidade'),
  assessment_type: z.enum(['simulation', 'practical', 'theoretical', 'mixed']),
  exam_date: z.string().min(1, 'Data é obrigatória'),
});

type ExamFormData = z.infer<typeof examSchema>;

const competenceSchema = z.object({
  name: z.string().min(2, 'Nome deve ter no mínimo 2 caracteres'),
  description: z.string().optional(),
  max_score: z.coerce.number().min(1, 'Nota máxima deve ser pelo menos 1').max(1000, 'Nota máxima não pode exceder 1000'),
  weight: z.coerce.number().min(0.1, 'Peso mínimo é 0.1').max(10, 'Peso máximo é 10').optional(),
});

type CompetenceFormData = z.infer<typeof competenceSchema>;

const assessmentTypes = [
  { value: 'simulation', label: 'Simulado' },
  { value: 'theoretical', label: 'Prova Teórica' },
  { value: 'practical', label: 'Avaliação Prática' },
  { value: 'mixed', label: 'Avaliação Mista' },
];

// Função para formatar data sem conversão de timezone
const formatDateBR = (dateString: string): string => {
  if (!dateString) return '-';
  // Extrai apenas a parte da data (YYYY-MM-DD) antes do T
  const datePart = dateString.split('T')[0];
  const [year, month, day] = datePart.split('-');
  return `${day}/${month}/${year}`;
};

// Função para formatar data completa sem conversão de timezone
const formatDateFullBR = (dateString: string): string => {
  if (!dateString) return '-';
  const datePart = dateString.split('T')[0];
  const [year, month, day] = datePart.split('-');
  const months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                  'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
  const weekdays = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira',
                    'quinta-feira', 'sexta-feira', 'sábado'];
  // Criar data ao meio-dia para evitar problemas de timezone
  const date = new Date(`${datePart}T12:00:00`);
  const weekday = weekdays[date.getDay()];
  const monthName = months[parseInt(month) - 1];
  return `${weekday}, ${parseInt(day)} de ${monthName} de ${year}`;
};

interface ExamStatistics {
  exam_id: string;
  total_competitors: number;
  total_grades: number;
  overall_average: number;
  competence_stats: Array<{
    competence_id: string;
    average: number;
    median: number;
    std_deviation: number;
    min_score: number;
    max_score: number;
    count: number;
  }>;
}

const ExamsPage: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Create exam modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalCompetences, setModalCompetences] = useState<Competence[]>([]);
  const [selectedCompetenceIds, setSelectedCompetenceIds] = useState<string[]>([]);
  const [selectedModalityId, setSelectedModalityId] = useState<string>('');

  // Grade modal state
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [competences, setCompetences] = useState<Competence[]>([]);
  const [examGrades, setExamGrades] = useState<Grade[]>([]);
  const [isLoadingGrades, setIsLoadingGrades] = useState(false);

  // Bulk grade modal state
  const [isBulkGradeModalOpen, setIsBulkGradeModalOpen] = useState(false);
  const [bulkGrades, setBulkGrades] = useState<Map<string, string>>(new Map());
  const [isSavingBulkGrades, setIsSavingBulkGrades] = useState(false);

  // Statistics modal state
  const [isStatsModalOpen, setIsStatsModalOpen] = useState(false);
  const [examStats, setExamStats] = useState<ExamStatistics | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [statsCompetences, setStatsCompetences] = useState<Competence[]>([]);

  // Details modal state
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [detailsExam, setDetailsExam] = useState<Exam | null>(null);
  const [detailsCompetences, setDetailsCompetences] = useState<Competence[]>([]);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);

  // Edit modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingExam, setEditingExam] = useState<Exam | null>(null);
  const [editCompetences, setEditCompetences] = useState<Competence[]>([]);
  const [editSelectedCompetenceIds, setEditSelectedCompetenceIds] = useState<string[]>([]);
  const [isUpdating, setIsUpdating] = useState(false);

  // Delete confirmation modal state
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [examToDelete, setExamToDelete] = useState<Exam | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Competence creation modal state
  const [isCompetenceModalOpen, setIsCompetenceModalOpen] = useState(false);
  const [competenceModalityId, setCompetenceModalityId] = useState<string>('');
  const [isCreatingCompetence, setIsCreatingCompetence] = useState(false);

  // Competence management modal state
  const [isCompetenceManagementOpen, setIsCompetenceManagementOpen] = useState(false);
  const [managementModalityId, setManagementModalityId] = useState<string>('');
  const [managementCompetences, setManagementCompetences] = useState<Competence[]>([]);
  const [isLoadingManagementCompetences, setIsLoadingManagementCompetences] = useState(false);
  const [editingCompetence, setEditingCompetence] = useState<Competence | null>(null);
  const [isEditCompetenceModalOpen, setIsEditCompetenceModalOpen] = useState(false);
  const [isUpdatingCompetence, setIsUpdatingCompetence] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting },
  } = useForm<ExamFormData>({
    resolver: zodResolver(examSchema),
  });

  // Form for editing
  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    control: controlEdit,
    formState: { errors: errorsEdit },
  } = useForm<ExamFormData>({
    resolver: zodResolver(examSchema),
  });

  // Form for creating competences
  const {
    register: registerCompetence,
    handleSubmit: handleSubmitCompetence,
    reset: resetCompetence,
    formState: { errors: errorsCompetence, isSubmitting: isSubmittingCompetence },
  } = useForm<CompetenceFormData>({
    resolver: zodResolver(competenceSchema),
    defaultValues: {
      max_score: 100,
      weight: 1,
    },
  });

  // Form for editing competences
  const {
    register: registerEditCompetence,
    handleSubmit: handleSubmitEditCompetence,
    reset: resetEditCompetence,
    formState: { errors: errorsEditCompetence },
  } = useForm<CompetenceFormData>({
    resolver: zodResolver(competenceSchema),
  });

  const fetchExams = async () => {
    try {
      setIsLoading(true);

      // Fetch modalities assigned to the current user first
      const myModalities = await enrollmentService.getMyModalities();
      setModalities(myModalities || []);

      // Get the IDs of modalities the user has access to
      const myModalityIds = new Set(myModalities.map((m: Modality) => m.id));

      // Fetch all exams and filter by user's modalities
      const response = await examService.getAll();
      const filteredExams = (response.exams || []).filter(
        (exam: Exam) => myModalityIds.has(exam.modality_id)
      );
      setExams(filteredExams);
    } catch (err: any) {
      console.error('Erro ao carregar avaliações:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao carregar avaliações';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const getModalityName = (modalityId: string) => {
    const modality = modalities.find(m => m.id === modalityId);
    return modality?.name || 'N/A';
  };

  useEffect(() => {
    fetchExams();
  }, []);

  const handleModalityChange = async (modalityId: string) => {
    setSelectedModalityId(modalityId);
    if (!modalityId) {
      setModalCompetences([]);
      setSelectedCompetenceIds([]);
      return;
    }
    try {
      const modalityData = await modalityService.getById(modalityId);
      const comps = (modalityData as any)?.competences || [];
      setModalCompetences(comps);
      // Select all by default
      setSelectedCompetenceIds(comps.map((c: Competence) => c.id));
    } catch (err) {
      console.error('Erro ao carregar competências:', err);
    }
  };

  const toggleCompetence = (competenceId: string) => {
    setSelectedCompetenceIds(prev =>
      prev.includes(competenceId)
        ? prev.filter(id => id !== competenceId)
        : [...prev, competenceId]
    );
  };

  // Open competence creation modal
  const handleOpenCompetenceModal = (modalityId: string) => {
    setCompetenceModalityId(modalityId);
    resetCompetence({ name: '', description: '', max_score: 100, weight: 1 });
    setIsCompetenceModalOpen(true);
  };

  // Create new competence
  const onSubmitCompetence = async (data: CompetenceFormData) => {
    if (!competenceModalityId) return;

    setIsCreatingCompetence(true);
    try {
      const newCompetence = await modalityService.addCompetence(competenceModalityId, {
        name: data.name,
        description: data.description || '',
        max_score: data.max_score,
        weight: data.weight || 1,
      });

      // Update the competence list in the modal
      setModalCompetences(prev => [...prev, newCompetence]);
      // Auto-select the new competence
      setSelectedCompetenceIds(prev => [...prev, newCompetence.id]);

      // Also update management competences and reopen management modal
      if (managementModalityId === competenceModalityId) {
        setManagementCompetences(prev => [...prev, newCompetence]);
        // Reabrir o modal de gerenciamento após criar
        setTimeout(() => setIsCompetenceManagementOpen(true), 100);
      }

      // Also update edit modal competences if that modal is open
      if (editingExam && editingExam.modality_id === competenceModalityId) {
        setEditCompetences(prev => [...prev, newCompetence]);
        setEditSelectedCompetenceIds(prev => [...prev, newCompetence.id]);
      }

      setIsCompetenceModalOpen(false);
      resetCompetence();
      setSuccessMessage('Competência criada com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Erro ao criar competência:', err);
      setError(err?.response?.data?.detail || 'Erro ao criar competência');
    } finally {
      setIsCreatingCompetence(false);
    }
  };

  // Competence management handlers
  const handleOpenCompetenceManagement = () => {
    setIsCompetenceManagementOpen(true);
    setManagementModalityId('');
    setManagementCompetences([]);
  };

  const handleManagementModalityChange = async (modalityId: string) => {
    setManagementModalityId(modalityId);
    if (!modalityId) {
      setManagementCompetences([]);
      return;
    }

    setIsLoadingManagementCompetences(true);
    try {
      const modalityData = await modalityService.getById(modalityId);
      const comps = (modalityData as any)?.competences || [];
      setManagementCompetences(comps);
    } catch (err) {
      console.error('Erro ao carregar competências:', err);
      setManagementCompetences([]);
    } finally {
      setIsLoadingManagementCompetences(false);
    }
  };

  const handleOpenEditCompetence = (competence: Competence) => {
    // Fechar o modal de gerenciamento primeiro
    setIsCompetenceManagementOpen(false);
    setEditingCompetence(competence);
    resetEditCompetence({
      name: competence.name,
      description: competence.description || '',
      max_score: competence.max_score,
      weight: competence.weight || 1,
    });
    setIsEditCompetenceModalOpen(true);
  };

  const handleCloseEditCompetence = () => {
    setIsEditCompetenceModalOpen(false);
    setEditingCompetence(null);
    resetEditCompetence();
  };

  const onSubmitEditCompetence = async (data: CompetenceFormData) => {
    if (!editingCompetence || !managementModalityId) return;

    setIsUpdatingCompetence(true);
    try {
      const updatedCompetence = await modalityService.updateCompetence(
        managementModalityId,
        editingCompetence.id,
        {
          name: data.name,
          description: data.description || '',
          max_score: data.max_score,
          weight: data.weight || 1,
        }
      );

      // Update the competence list
      setManagementCompetences(prev =>
        prev.map(c => c.id === updatedCompetence.id ? updatedCompetence : c)
      );

      handleCloseEditCompetence();
      // Reabrir o modal de gerenciamento
      setTimeout(() => setIsCompetenceManagementOpen(true), 100);
      setSuccessMessage('Competência atualizada com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Erro ao atualizar competência:', err);
      setError(err?.response?.data?.detail || 'Erro ao atualizar competência');
    } finally {
      setIsUpdatingCompetence(false);
    }
  };

  const handleAddCompetenceFromManagement = () => {
    if (!managementModalityId) return;
    // Fechar o modal de gerenciamento primeiro
    setIsCompetenceManagementOpen(false);
    setCompetenceModalityId(managementModalityId);
    resetCompetence({ name: '', description: '', max_score: 100, weight: 1 });
    setIsCompetenceModalOpen(true);
  };

  const onSubmit = async (data: ExamFormData) => {
    try {
      await examService.create({
        ...data,
        // Enviar apenas a data no formato YYYY-MM-DD
        exam_date: data.exam_date,
        competence_ids: selectedCompetenceIds,
      });
      setIsModalOpen(false);
      reset();
      setModalCompetences([]);
      setSelectedCompetenceIds([]);
      setSelectedModalityId('');
      fetchExams();
      setSuccessMessage('Avaliação criada com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Erro ao criar avaliação');
    }
  };

  // Open bulk grade modal
  const handleOpenBulkGradeModal = async (exam: Exam) => {
    setSelectedExam(exam);
    setIsBulkGradeModalOpen(true);
    setIsLoadingGrades(true);

    try {
      // Fetch competitors for the exam's modality
      const competitorResponse = await competitorService.getByModality(exam.modality_id);
      setCompetitors(competitorResponse.competitors || []);

      // Fetch modality with competences
      const modalityData = await modalityService.getById(exam.modality_id);
      const allCompetences = (modalityData as any)?.competences || [];

      // Filter competences to only those assigned to this exam
      if (exam.competence_ids && exam.competence_ids.length > 0) {
        const examCompetences = allCompetences.filter((c: Competence) =>
          exam.competence_ids.includes(c.id)
        );
        setCompetences(examCompetences);
      } else {
        setCompetences(allCompetences);
      }

      // Fetch existing grades for this exam
      const gradesResponse = await gradeService.getAll({ exam_id: exam.id });
      setExamGrades(gradesResponse.grades || []);

      // Initialize bulk grades map with existing values
      // Using '|' as separator since UUIDs contain hyphens
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
      setIsLoadingGrades(false);
    }
  };

  const handleCloseBulkGradeModal = () => {
    setIsBulkGradeModalOpen(false);
    setSelectedExam(null);
    setCompetitors([]);
    setCompetences([]);
    setExamGrades([]);
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
    return examGrades.find(g => g.competitor_id === competitorId && g.competence_id === competenceId);
  };

  const handleSaveBulkGrades = async () => {
    if (!selectedExam) return;

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
              exam_id: selectedExam.id,
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
    } catch (err) {
      setError('Erro ao salvar notas em lote');
    } finally {
      setIsSavingBulkGrades(false);
    }
  };

  const handleOpenStatsModal = async (exam: Exam) => {
    setSelectedExam(exam);
    setIsStatsModalOpen(true);
    setIsLoadingStats(true);

    try {
      // Fetch competences from modality to display proper names
      const modalityData = await modalityService.getById(exam.modality_id);
      const allCompetences = (modalityData as any)?.competences || [];
      setStatsCompetences(allCompetences);

      const stats = await examService.getStatistics(exam.id);
      setExamStats(stats as unknown as ExamStatistics);
    } catch (err) {
      console.error('Erro ao carregar estatísticas:', err);
      setError('Erro ao carregar estatísticas');
      setExamStats(null);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleCloseStatsModal = () => {
    setIsStatsModalOpen(false);
    setSelectedExam(null);
    setExamStats(null);
    setStatsCompetences([]);
  };

  // Details modal handlers
  const handleOpenDetailsModal = async (exam: Exam) => {
    setDetailsExam(exam);
    setIsDetailsModalOpen(true);
    setIsLoadingDetails(true);

    try {
      // Fetch modality with competences
      const modalityData = await modalityService.getById(exam.modality_id);
      const allCompetences = (modalityData as any)?.competences || [];

      // Filter competences to only those assigned to this exam
      if (exam.competence_ids && exam.competence_ids.length > 0) {
        const examCompetences = allCompetences.filter((c: Competence) =>
          exam.competence_ids.includes(c.id)
        );
        setDetailsCompetences(examCompetences);
      } else {
        setDetailsCompetences(allCompetences);
      }
    } catch (err) {
      console.error('Erro ao carregar detalhes:', err);
      setDetailsCompetences([]);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleCloseDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setDetailsExam(null);
    setDetailsCompetences([]);
  };

  // Edit modal handlers
  const handleOpenEditModal = async (exam: Exam) => {
    setEditingExam(exam);
    setIsEditModalOpen(true);

    // Load competences for the modality
    try {
      const modalityData = await modalityService.getById(exam.modality_id);
      const allCompetences = (modalityData as any)?.competences || [];
      setEditCompetences(allCompetences);
      setEditSelectedCompetenceIds(exam.competence_ids || []);
    } catch (err) {
      console.error('Erro ao carregar competências:', err);
      setEditCompetences([]);
    }

    // Populate form with exam data
    resetEdit({
      name: exam.name,
      description: exam.description || '',
      modality_id: exam.modality_id,
      assessment_type: exam.assessment_type as 'simulation' | 'practical' | 'theoretical' | 'mixed',
      exam_date: exam.exam_date.split('T')[0], // Format for date input
    });
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingExam(null);
    setEditCompetences([]);
    setEditSelectedCompetenceIds([]);
    resetEdit();
  };

  const handleEditModalityChange = async (modalityId: string) => {
    if (!modalityId) {
      setEditCompetences([]);
      setEditSelectedCompetenceIds([]);
      return;
    }
    try {
      const modalityData = await modalityService.getById(modalityId);
      const comps = (modalityData as any)?.competences || [];
      setEditCompetences(comps);
      setEditSelectedCompetenceIds(comps.map((c: Competence) => c.id));
    } catch (err) {
      console.error('Erro ao carregar competências:', err);
    }
  };

  const toggleEditCompetence = (competenceId: string) => {
    setEditSelectedCompetenceIds(prev =>
      prev.includes(competenceId)
        ? prev.filter(id => id !== competenceId)
        : [...prev, competenceId]
    );
  };

  const onSubmitEdit = async (data: ExamFormData) => {
    if (!editingExam) return;

    setIsUpdating(true);
    try {
      await examService.update(editingExam.id, {
        ...data,
        // Enviar apenas a data no formato YYYY-MM-DD
        exam_date: data.exam_date,
        competence_ids: editSelectedCompetenceIds,
      });
      handleCloseEditModal();
      fetchExams();
      setSuccessMessage('Avaliação atualizada com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Erro ao atualizar avaliação:', err);
      setError(err?.response?.data?.detail || 'Erro ao atualizar avaliação');
    } finally {
      setIsUpdating(false);
    }
  };

  // Delete handlers
  const handleOpenDeleteModal = (exam: Exam) => {
    setExamToDelete(exam);
    setIsDeleteModalOpen(true);
  };

  const handleCloseDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setExamToDelete(null);
  };

  const handleDeleteExam = async () => {
    if (!examToDelete) return;

    setIsDeleting(true);
    try {
      await examService.delete(examToDelete.id);
      handleCloseDeleteModal();
      fetchExams();
      setSuccessMessage('Avaliação excluída com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Erro ao excluir avaliação:', err);
      setError(err?.response?.data?.detail || 'Erro ao excluir avaliação');
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatsCompetenceName = (competenceId: string) => {
    const competence = statsCompetences.find(c => c.id === competenceId);
    return competence?.name || `Competência ${competenceId.slice(0, 8)}...`;
  };

  const columns = [
    { key: 'name', header: 'Nome' },
    {
      key: 'description',
      header: 'Descrição',
      className: 'hidden md:table-cell',
      render: (item: Exam) => {
        if (!item.description) return <span className="text-gray-400">-</span>;
        // Converter quebras de linha HTML para \n e remover tags
        const withLineBreaks = item.description
          .replace(/<br\s*\/?>/gi, '\n')
          .replace(/<\/p>/gi, '\n')
          .replace(/<\/li>/gi, '\n')
          .replace(/<[^>]*>/g, '')
          .trim();
        // Pegar apenas a primeira linha
        const firstLine = withLineBreaks.split('\n')[0].trim();
        const maxLength = 60;
        const preview = firstLine.length > maxLength
          ? firstLine.substring(0, maxLength) + '...'
          : firstLine;
        return (
          <span className="text-gray-600 dark:text-gray-400" title={firstLine}>
            {preview}
          </span>
        );
      },
    },
    {
      key: 'modality_id',
      header: 'Modalidade',
      render: (item: Exam) => getModalityName(item.modality_id),
    },
    {
      key: 'assessment_type',
      header: 'Tipo',
      render: (item: Exam) => {
        const type = assessmentTypes.find(t => t.value === item.assessment_type);
        return <Badge variant="primary">{type?.label || item.assessment_type}</Badge>;
      },
    },
    {
      key: 'exam_date',
      header: 'Data',
      render: (item: Exam) => formatDateBR(item.exam_date),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (item: Exam) => (
        <Badge variant={item.is_active ? 'success' : 'danger'}>
          {item.is_active ? 'Ativo' : 'Inativo'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (item: Exam) => (
        <div className="flex items-center justify-end gap-2">
          {/* Grupo: Todos os ícones */}
          <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-0.5">
            <button
              onClick={() => handleOpenDetailsModal(item)}
              title="Ver detalhes"
              className="p-1.5 rounded-md text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-600 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
            <button
              onClick={() => handleOpenEditModal(item)}
              title="Editar"
              className="p-1.5 rounded-md text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-600 hover:text-amber-600 dark:hover:text-amber-400 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={() => handleOpenStatsModal(item)}
              title="Estatísticas"
              className="p-1.5 rounded-md text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-600 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </button>
            <button
              onClick={() => handleOpenDeleteModal(item)}
              title="Excluir"
              className="p-1.5 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          {/* Botão Principal: Notas (à direita) */}
          <button
            onClick={() => handleOpenBulkGradeModal(item)}
            title="Lançar notas"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg transition-colors shadow-sm"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Notas
          </button>
        </div>
      ),
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
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Avaliações</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Gerencie exames e avaliações
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="secondary" onClick={handleOpenCompetenceManagement}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Gerenciar Competências
          </Button>
          <Button onClick={() => setIsModalOpen(true)}>Nova Avaliação</Button>
        </div>
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

      <Card padding="none">
        <Table
          data={exams}
          columns={columns}
          keyExtractor={(item) => item.id}
          emptyMessage="Nenhuma avaliação cadastrada"
        />
      </Card>

      {/* Modal Nova Avaliação */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          reset();
          setModalCompetences([]);
          setSelectedCompetenceIds([]);
          setSelectedModalityId('');
        }}
        title="Nova Avaliação"
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nome"
            placeholder="Nome da avaliação"
            error={errors.name?.message}
            {...register('name')}
          />
          <Controller
            name="description"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <RichTextEditor
                label="Descrição"
                placeholder="Descrição da avaliação (suporta formatação: negrito, itálico, listas...)"
                value={field.value || ''}
                onChange={field.onChange}
                error={errors.description?.message}
                minHeight="120px"
              />
            )}
          />
          <Select
            label="Tipo de Avaliação"
            placeholder="Selecione o tipo"
            error={errors.assessment_type?.message}
            options={assessmentTypes}
            {...register('assessment_type')}
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Modalidade
            </label>
            <select
              {...register('modality_id')}
              onChange={(e) => {
                register('modality_id').onChange(e);
                handleModalityChange(e.target.value);
              }}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
            >
              <option value="">Selecione uma modalidade</option>
              {modalities.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
            {errors.modality_id && (
              <p className="text-sm text-red-600 mt-1">{errors.modality_id.message}</p>
            )}
          </div>

          {/* Competências da modalidade */}
          {selectedModalityId && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Competências a Avaliar
                </label>
                {modalCompetences.length > 0 && (
                  <button
                    type="button"
                    onClick={() => handleOpenCompetenceModal(selectedModalityId)}
                    className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 font-medium flex items-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Adicionar
                  </button>
                )}
              </div>

              {modalCompetences.length > 0 ? (
                <>
                  <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-3 max-h-40 overflow-y-auto space-y-2">
                    {modalCompetences.map(c => (
                      <label key={c.id} className="flex items-center justify-between cursor-pointer group">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={selectedCompetenceIds.includes(c.id)}
                            onChange={() => toggleCompetence(c.id)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">{c.name}</span>
                        </div>
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                          0-{c.max_score}
                        </span>
                      </label>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {selectedCompetenceIds.length} de {modalCompetences.length} competências selecionadas
                  </p>
                </>
              ) : (
                <div className="border border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 text-center">
                  <svg className="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    Nenhuma competência cadastrada nesta modalidade
                  </p>
                  <button
                    type="button"
                    onClick={() => handleOpenCompetenceModal(selectedModalityId)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Cadastrar Competência
                  </button>
                </div>
              )}
            </div>
          )}

          <Input
            label="Data da Avaliação"
            type="date"
            error={errors.exam_date?.message}
            {...register('exam_date')}
          />
          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Criar
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal Lançamento em Massa */}
      <Modal
        isOpen={isBulkGradeModalOpen}
        onClose={handleCloseBulkGradeModal}
        title={`Lançar Notas - ${selectedExam?.name || ''}`}
        size="xl"
      >
        {isLoadingGrades ? (
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

            {/* Descrição da avaliação */}
            {selectedExam?.description && (
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Descrição da Avaliação</h4>
                <RichTextDisplay content={selectedExam.description} />
              </div>
            )}

            {competitors.length === 0 ? (
              <Alert type="warning">
                Nenhum competidor encontrado para a modalidade desta avaliação.
              </Alert>
            ) : competences.length === 0 ? (
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
                        {competences.map((comp) => (
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
                      {competitors.map((competitor, idx) => (
                        <tr key={competitor.id} className={idx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800/50'}>
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 sticky left-0 bg-inherit z-10 border-r border-gray-200 dark:border-gray-700">
                            {competitor.full_name}
                          </td>
                          {competences.map((comp) => {
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
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{competitors.length}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Competidores</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{competences.length}</p>
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

      {/* Modal Estatísticas */}
      <Modal
        isOpen={isStatsModalOpen}
        onClose={handleCloseStatsModal}
        title={`Estatísticas - ${selectedExam?.name || ''}`}
        size="xl"
      >
        {isLoadingStats ? (
          <div className="flex justify-center items-center h-32">
            <Spinner size="lg" />
          </div>
        ) : examStats ? (
          <div className="space-y-6">
            {/* Descrição da avaliação */}
            {selectedExam?.description && (
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Descrição da Avaliação</h4>
                <RichTextDisplay content={selectedExam.description} />
              </div>
            )}

            {/* Resumo geral */}
            <div className="grid grid-cols-3 gap-4">
              <Card className="text-center bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center mb-2">
                    <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p className="text-xs text-blue-600 dark:text-blue-400 font-medium uppercase tracking-wide">Competidores</p>
                  <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">
                    {examStats.total_competitors}
                  </p>
                </div>
              </Card>
              <Card className="text-center bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-800 flex items-center justify-center mb-2">
                    <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-xs text-green-600 dark:text-green-400 font-medium uppercase tracking-wide">Notas Lançadas</p>
                  <p className="text-3xl font-bold text-green-700 dark:text-green-300">
                    {examStats.total_grades}
                  </p>
                </div>
              </Card>
              <Card className="text-center bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-800 flex items-center justify-center mb-2">
                    <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                    </svg>
                  </div>
                  <p className="text-xs text-purple-600 dark:text-purple-400 font-medium uppercase tracking-wide">Média Geral</p>
                  <p className="text-3xl font-bold text-purple-700 dark:text-purple-300">
                    {examStats.overall_average?.toFixed(1) || 'N/A'}
                  </p>
                </div>
              </Card>
            </div>

            {/* Estatísticas por competência */}
            {examStats.competence_stats && examStats.competence_stats.length > 0 ? (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Desempenho por Competência
                </h3>
                <div className="space-y-4">
                  {examStats.competence_stats.map((stat) => {
                    const avgPercent = Math.min((stat.average / 100) * 100, 100);
                    return (
                      <Card key={stat.competence_id} className="overflow-hidden">
                        <div className="p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-base">
                                {getStatsCompetenceName(stat.competence_id)}
                              </h4>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                {stat.count} {stat.count === 1 ? 'avaliação' : 'avaliações'}
                              </p>
                            </div>
                            <div className="text-right">
                              <span className={`text-2xl font-bold ${
                                stat.average >= 70 ? 'text-green-600 dark:text-green-400' :
                                stat.average >= 50 ? 'text-yellow-600 dark:text-yellow-400' :
                                'text-red-600 dark:text-red-400'
                              }`}>
                                {stat.average.toFixed(1)}
                              </span>
                              <p className="text-xs text-gray-500">média</p>
                            </div>
                          </div>

                          {/* Barra de progresso */}
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
                            <div
                              className={`h-2 rounded-full transition-all duration-300 ${
                                stat.average >= 70 ? 'bg-green-500' :
                                stat.average >= 50 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${avgPercent}%` }}
                            />
                          </div>

                          {/* Métricas detalhadas */}
                          <div className="grid grid-cols-4 gap-3 text-center">
                            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
                              <p className="text-xs text-gray-500 dark:text-gray-400">Mediana</p>
                              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">{stat.median.toFixed(1)}</p>
                            </div>
                            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
                              <p className="text-xs text-gray-500 dark:text-gray-400">Mínima</p>
                              <p className="text-sm font-semibold text-red-600 dark:text-red-400">{stat.min_score.toFixed(1)}</p>
                            </div>
                            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
                              <p className="text-xs text-gray-500 dark:text-gray-400">Máxima</p>
                              <p className="text-sm font-semibold text-green-600 dark:text-green-400">{stat.max_score.toFixed(1)}</p>
                            </div>
                            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
                              <p className="text-xs text-gray-500 dark:text-gray-400">Desvio</p>
                              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">{stat.std_deviation.toFixed(2)}</p>
                            </div>
                          </div>
                        </div>
                      </Card>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <svg className="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-gray-500 dark:text-gray-400">
                  Nenhuma nota por competência disponível
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              Não há estatísticas disponíveis para esta avaliação
            </p>
            <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">
              Lance algumas notas primeiro para ver as estatísticas
            </p>
          </div>
        )}
      </Modal>

      {/* Modal Detalhes da Avaliação */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={handleCloseDetailsModal}
        title={`Detalhes - ${detailsExam?.name || ''}`}
        size="lg"
      >
        {isLoadingDetails ? (
          <div className="flex justify-center items-center h-32">
            <Spinner size="lg" />
          </div>
        ) : detailsExam ? (
          <div className="space-y-6">
            {/* Informações básicas */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-1">Nome</p>
                <p className="text-gray-900 dark:text-gray-100 font-semibold">{detailsExam.name}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-1">Modalidade</p>
                <p className="text-gray-900 dark:text-gray-100 font-semibold">{getModalityName(detailsExam.modality_id)}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-1">Tipo de Avaliação</p>
                <Badge variant="primary">
                  {assessmentTypes.find(t => t.value === detailsExam.assessment_type)?.label || detailsExam.assessment_type}
                </Badge>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-1">Data da Avaliação</p>
                <p className="text-gray-900 dark:text-gray-100 font-semibold">
                  {formatDateFullBR(detailsExam.exam_date)}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-1">Status</p>
                <Badge variant={detailsExam.is_active ? 'success' : 'danger'}>
                  {detailsExam.is_active ? 'Ativo' : 'Inativo'}
                </Badge>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-1">Criado em</p>
                <p className="text-gray-900 dark:text-gray-100 font-semibold">
                  {formatDateBR(detailsExam.created_at)}
                </p>
              </div>
            </div>

            {/* Descrição completa */}
            {detailsExam.description ? (
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Descrição
                </h4>
                <RichTextDisplay content={detailsExam.description} />
              </div>
            ) : (
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center">
                <p className="text-gray-400 dark:text-gray-500 text-sm italic">Nenhuma descrição cadastrada</p>
              </div>
            )}

            {/* Competências avaliadas */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                Competências Avaliadas ({detailsCompetences.length})
              </h4>
              {detailsCompetences.length > 0 ? (
                <div className="space-y-2">
                  {detailsCompetences.map((comp) => (
                    <div
                      key={comp.id}
                      className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg p-3"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">{comp.name}</p>
                        {comp.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{comp.description}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                          0-{comp.max_score}
                        </span>
                        <p className="text-xs text-gray-500 dark:text-gray-400">pontos</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 dark:text-gray-500 text-sm italic text-center">
                  Nenhuma competência cadastrada
                </p>
              )}
            </div>

            {/* Botões de ação */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button variant="secondary" onClick={handleCloseDetailsModal}>
                Fechar
              </Button>
              <Button variant="ghost" onClick={() => { handleCloseDetailsModal(); handleOpenEditModal(detailsExam); }}>
                Editar
              </Button>
              <Button onClick={() => { handleCloseDetailsModal(); handleOpenBulkGradeModal(detailsExam); }}>
                Lançar Notas
              </Button>
            </div>
          </div>
        ) : null}
      </Modal>

      {/* Modal Editar Avaliação */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        title={`Editar - ${editingExam?.name || ''}`}
        size="lg"
      >
        <form onSubmit={handleSubmitEdit(onSubmitEdit)} className="space-y-4">
          <Input
            label="Nome"
            placeholder="Nome da avaliação"
            error={errorsEdit.name?.message}
            {...registerEdit('name')}
          />
          <Controller
            name="description"
            control={controlEdit}
            defaultValue=""
            render={({ field }) => (
              <RichTextEditor
                label="Descrição"
                placeholder="Descrição da avaliação (suporta formatação: negrito, itálico, listas...)"
                value={field.value || ''}
                onChange={field.onChange}
                error={errorsEdit.description?.message}
                minHeight="120px"
              />
            )}
          />
          <Select
            label="Tipo de Avaliação"
            placeholder="Selecione o tipo"
            error={errorsEdit.assessment_type?.message}
            options={assessmentTypes}
            {...registerEdit('assessment_type')}
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Modalidade
            </label>
            <select
              {...registerEdit('modality_id')}
              onChange={(e) => {
                registerEdit('modality_id').onChange(e);
                handleEditModalityChange(e.target.value);
              }}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
            >
              <option value="">Selecione uma modalidade</option>
              {modalities.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
            {errorsEdit.modality_id && (
              <p className="text-sm text-red-600 mt-1">{errorsEdit.modality_id.message}</p>
            )}
          </div>

          {/* Competências da modalidade */}
          {editingExam && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Competências a Avaliar
                </label>
                {editCompetences.length > 0 && (
                  <button
                    type="button"
                    onClick={() => handleOpenCompetenceModal(editingExam.modality_id)}
                    className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 font-medium flex items-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Adicionar
                  </button>
                )}
              </div>

              {editCompetences.length > 0 ? (
                <>
                  <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-3 max-h-40 overflow-y-auto space-y-2">
                    {editCompetences.map(c => (
                      <label key={c.id} className="flex items-center justify-between cursor-pointer group">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={editSelectedCompetenceIds.includes(c.id)}
                            onChange={() => toggleEditCompetence(c.id)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">{c.name}</span>
                        </div>
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                          0-{c.max_score}
                        </span>
                      </label>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {editSelectedCompetenceIds.length} de {editCompetences.length} competências selecionadas
                  </p>
                </>
              ) : (
                <div className="border border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 text-center">
                  <svg className="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    Nenhuma competência cadastrada nesta modalidade
                  </p>
                  <button
                    type="button"
                    onClick={() => handleOpenCompetenceModal(editingExam.modality_id)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Cadastrar Competência
                  </button>
                </div>
              )}
            </div>
          )}

          <Input
            label="Data da Avaliação"
            type="date"
            error={errorsEdit.exam_date?.message}
            {...registerEdit('exam_date')}
          />
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="secondary" onClick={handleCloseEditModal}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isUpdating}>
              Salvar Alterações
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal Confirmação de Exclusão */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={handleCloseDeleteModal}
        title="Confirmar Exclusão"
        size="sm"
      >
        <div className="space-y-4">
          <div className="flex items-center space-x-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <svg className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-800 dark:text-red-200">
                Tem certeza que deseja excluir esta avaliação?
              </p>
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                <strong>{examToDelete?.name}</strong>
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Esta ação é irreversível. Todas as notas lançadas para esta avaliação também serão excluídas.
          </p>
          <div className="flex justify-end space-x-3 pt-2 border-t border-gray-200 dark:border-gray-700">
            <Button variant="secondary" onClick={handleCloseDeleteModal}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={handleDeleteExam}
              isLoading={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-500"
            >
              Excluir
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal Criar Competência */}
      <Modal
        isOpen={isCompetenceModalOpen}
        onClose={() => {
          setIsCompetenceModalOpen(false);
          resetCompetence();
        }}
        title="Nova Competência"
        size="md"
      >
        <form onSubmit={handleSubmitCompetence(onSubmitCompetence)} className="space-y-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              Cadastre as competências que serão avaliadas nesta modalidade.
            </p>
          </div>

          <Input
            label="Nome da Competência"
            placeholder="Ex: Programação Web, Design de Interface..."
            error={errorsCompetence.name?.message}
            {...registerCompetence('name')}
          />

          <Input
            label="Descrição (opcional)"
            placeholder="Descreva o que será avaliado nesta competência"
            error={errorsCompetence.description?.message}
            {...registerCompetence('description')}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Nota Máxima"
              type="number"
              placeholder="100"
              error={errorsCompetence.max_score?.message}
              {...registerCompetence('max_score')}
            />

            <Input
              label="Peso (opcional)"
              type="number"
              step="0.1"
              placeholder="1.0"
              error={errorsCompetence.weight?.message}
              {...registerCompetence('weight')}
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsCompetenceModalOpen(false);
                resetCompetence();
              }}
            >
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmittingCompetence || isCreatingCompetence}>
              Criar Competência
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal Gerenciar Competências */}
      <Modal
        isOpen={isCompetenceManagementOpen}
        onClose={() => {
          setIsCompetenceManagementOpen(false);
          setManagementModalityId('');
          setManagementCompetences([]);
        }}
        title="Gerenciar Competências"
        size="lg"
      >
        <div className="space-y-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                Selecione uma modalidade para visualizar, adicionar ou editar suas competências.
              </p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Modalidade
            </label>
            <select
              value={managementModalityId}
              onChange={(e) => handleManagementModalityChange(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
            >
              <option value="">Selecione uma modalidade</option>
              {modalities.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>

          {managementModalityId && (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  Competências ({managementCompetences.length})
                </h3>
                <button
                  type="button"
                  onClick={handleAddCompetenceFromManagement}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Nova Competência
                </button>
              </div>

              {isLoadingManagementCompetences ? (
                <div className="flex justify-center items-center h-32">
                  <Spinner size="md" />
                </div>
              ) : managementCompetences.length > 0 ? (
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {managementCompetences.map(comp => (
                    <div
                      key={comp.id}
                      className="px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900 dark:text-gray-100">{comp.name}</span>
                          <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full">
                            0-{comp.max_score}
                          </span>
                          {comp.weight && comp.weight !== 1 && (
                            <span className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-full">
                              Peso: {comp.weight}
                            </span>
                          )}
                        </div>
                        {comp.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">
                            {comp.description}
                          </p>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleOpenEditCompetence(comp)}
                        className="ml-3 p-2 text-gray-500 hover:text-amber-600 dark:text-gray-400 dark:hover:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors"
                        title="Editar competência"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="px-4 py-8 text-center">
                  <svg className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                  <p className="text-gray-500 dark:text-gray-400 text-sm mb-3">
                    Nenhuma competência cadastrada nesta modalidade
                  </p>
                  <button
                    type="button"
                    onClick={handleAddCompetenceFromManagement}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Cadastrar Competência
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="secondary"
              onClick={() => {
                setIsCompetenceManagementOpen(false);
                setManagementModalityId('');
                setManagementCompetences([]);
              }}
            >
              Fechar
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal Editar Competência */}
      <Modal
        isOpen={isEditCompetenceModalOpen}
        onClose={handleCloseEditCompetence}
        title={`Editar - ${editingCompetence?.name || ''}`}
        size="md"
      >
        <form onSubmit={handleSubmitEditCompetence(onSubmitEditCompetence)} className="space-y-4">
          <Input
            label="Nome da Competência"
            placeholder="Ex: Programação Web, Design de Interface..."
            error={errorsEditCompetence.name?.message}
            {...registerEditCompetence('name')}
          />

          <Input
            label="Descrição (opcional)"
            placeholder="Descreva o que será avaliado nesta competência"
            error={errorsEditCompetence.description?.message}
            {...registerEditCompetence('description')}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Nota Máxima"
              type="number"
              placeholder="100"
              error={errorsEditCompetence.max_score?.message}
              {...registerEditCompetence('max_score')}
            />

            <Input
              label="Peso (opcional)"
              type="number"
              step="0.1"
              placeholder="1.0"
              error={errorsEditCompetence.weight?.message}
              {...registerEditCompetence('weight')}
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="secondary" onClick={handleCloseEditCompetence}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isUpdatingCompetence}>
              Salvar Alterações
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ExamsPage;

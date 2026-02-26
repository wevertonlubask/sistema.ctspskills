import React, { useEffect, useState } from 'react';
import { Card, Button, Table, Badge, Modal, Input, Alert, Spinner } from '../../components/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { modalityService, enrollmentService, competitorService } from '../../services';
import { useAuthStore } from '../../stores/authStore';
import type { Modality, EnrollmentDetail, User, Competence, Competitor } from '../../types';

const modalitySchema = z.object({
  name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  description: z.string().optional(),
  code: z
    .string()
    .min(2, 'Código deve ter no mínimo 2 caracteres')
    .max(7, 'Código deve ter no máximo 7 caracteres')
    .regex(
      /^[A-Za-z]{2,4}(\d{2,3})?$/,
      'Código: 2-4 letras, opcionalmente seguidas de 2-3 números (ex: WS17, SOLD, IT)'
    )
    .transform(val => val.toUpperCase()),
});

type ModalityFormData = z.infer<typeof modalitySchema>;

const competenceSchema = z.object({
  name: z.string().min(2, 'Nome deve ter no mínimo 2 caracteres'),
  description: z.string().optional(),
  max_score: z.coerce.number().min(1, 'Nota máxima deve ser pelo menos 1').max(1000, 'Nota máxima deve ser no máximo 1000'),
  weight: z.coerce.number().min(0.1, 'Peso deve ser pelo menos 0.1').max(10, 'Peso máximo é 10').optional(),
});

type CompetenceFormData = z.infer<typeof competenceSchema>;

const ModalitiesPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const isSuperAdmin = user?.role === 'super_admin';
  const isCompetitor = user?.role === 'competitor';

  const [modalities, setModalities] = useState<Modality[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingModality, setEditingModality] = useState<Modality | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingModality, setDeletingModality] = useState<Modality | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Details modal state
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedModality, setSelectedModality] = useState<Modality | null>(null);
  const [modalityEnrollments, setModalityEnrollments] = useState<EnrollmentDetail[]>([]);
  const [loadingEnrollments, setLoadingEnrollments] = useState(false);
  const [evaluators, setEvaluators] = useState<User[]>([]);
  const [editingEnrollmentId, setEditingEnrollmentId] = useState<string | null>(null);
  const [selectedEvaluatorId, setSelectedEvaluatorId] = useState<string>('');

  // Competence state
  const [competences, setCompetences] = useState<Competence[]>([]);
  const [loadingCompetences, setLoadingCompetences] = useState(false);
  const [isCompetenceModalOpen, setIsCompetenceModalOpen] = useState(false);
  const [isDeletingCompetence, setIsDeletingCompetence] = useState(false);
  const [deletingCompetenceId, setDeletingCompetenceId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ModalityFormData>({
    resolver: zodResolver(modalitySchema),
  });

  const {
    register: registerCompetence,
    handleSubmit: handleSubmitCompetence,
    reset: resetCompetence,
    formState: { errors: competenceErrors, isSubmitting: isSubmittingCompetence },
  } = useForm<CompetenceFormData>({
    resolver: zodResolver(competenceSchema),
    defaultValues: {
      max_score: 100,
      weight: 1,
    },
  });

  const fetchModalities = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Super admins see all modalities, evaluators see only their assigned ones
      let data: Modality[];
      if (isSuperAdmin) {
        data = await modalityService.getAll();
      } else {
        data = await enrollmentService.getMyModalities();
      }
      setModalities(data || []);
    } catch (err: any) {
      console.error('Erro ao carregar modalidades:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao carregar modalidades';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModalities();
  }, []);

  const handleOpenModal = (modality?: Modality) => {
    if (modality) {
      setEditingModality(modality);
      reset({
        name: modality.name,
        description: modality.description || '',
        code: modality.code,
      });
    } else {
      setEditingModality(null);
      reset({ name: '', description: '', code: '' });
    }
    setIsModalOpen(true);
  };

  const onSubmit = async (data: ModalityFormData) => {
    try {
      if (editingModality) {
        await modalityService.update(editingModality.id, data);
      } else {
        await modalityService.create(data);
      }
      setIsModalOpen(false);
      fetchModalities();
    } catch (err: any) {
      console.error('Erro ao salvar modalidade:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao salvar modalidade';
      setError(message);
    }
  };

  const handleDeleteClick = (modality: Modality) => {
    setDeletingModality(modality);
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingModality) return;

    try {
      setIsDeleting(true);
      setError(null);
      await modalityService.delete(deletingModality.id);
      setDeleteModalOpen(false);
      setDeletingModality(null);
      await fetchModalities();
    } catch (err: any) {
      console.error('Erro ao excluir modalidade:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao excluir modalidade';
      setError(message);
      // Fecha o modal para mostrar o erro
      setDeleteModalOpen(false);
      setDeletingModality(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewDetails = async (modality: Modality) => {
    setSelectedModality(modality);
    setIsDetailsModalOpen(true);
    setLoadingEnrollments(true);
    setLoadingCompetences(true);
    setError(null);

    // Buscar dados separadamente para que erros em uma chamada não afetem as outras
    let enrollments: EnrollmentDetail[] = [];
    let competitors: Competitor[] = [];

    // Buscar enrollments
    try {
      const enrollmentsResponse = await enrollmentService.getByModality(modality.id);
      enrollments = enrollmentsResponse.enrollments || [];
    } catch (err: any) {
      console.error('Error fetching enrollments:', err);
      // Não bloquear se enrollments falhar
    }

    // Buscar competidores (fallback se enrollments estiver vazio)
    try {
      const competitorsResponse = await competitorService.getByModality(modality.id);
      competitors = competitorsResponse.competitors || [];
    } catch (err: any) {
      console.error('Error fetching competitors:', err);
      // Não bloquear se competitors falhar
    }

    // Se não houver enrollments mas houver competidores, criar enrollments virtuais
    if (enrollments.length === 0 && competitors.length > 0) {
      const now = new Date().toISOString();
      enrollments = competitors.map((c: Competitor) => ({
        id: c.id,
        competitor_id: c.id,
        competitor_name: c.full_name,
        modality_id: modality.id,
        modality_name: modality.name,
        modality_code: modality.code,
        evaluator_id: undefined,
        evaluator_name: undefined,
        enrolled_at: c.created_at || now,
        status: 'active' as const,
        notes: undefined,
        created_at: c.created_at || now,
        updated_at: c.updated_at || now,
      }));
    }

    setModalityEnrollments(enrollments);
    setLoadingEnrollments(false);

    // Buscar avaliadores (apenas para super admins, ignorar erro 403)
    try {
      const evaluatorsResponse = await enrollmentService.getEvaluators();
      setEvaluators(evaluatorsResponse.users || []);
    } catch (err: any) {
      console.error('Error fetching evaluators:', err);
      // Ignorar erro - usuário pode não ter permissão
      setEvaluators([]);
    }

    // Fetch competences
    try {
      const competencesData = await modalityService.getCompetences(modality.id);
      setCompetences(competencesData || []);
    } catch (err: any) {
      console.error('Error fetching competences:', err);
      setCompetences([]);
    } finally {
      setLoadingCompetences(false);
    }
  };

  const handleCloseDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setSelectedModality(null);
    setModalityEnrollments([]);
    setEditingEnrollmentId(null);
    setSelectedEvaluatorId('');
    setCompetences([]);
    setIsCompetenceModalOpen(false);
  };

  const handleEditEvaluator = (enrollment: EnrollmentDetail) => {
    setEditingEnrollmentId(enrollment.id);
    setSelectedEvaluatorId(enrollment.evaluator_id || '');
  };

  const handleSaveEvaluator = async (enrollment: EnrollmentDetail) => {
    if (!selectedModality) return;

    try {
      await enrollmentService.update(selectedModality.id, enrollment.id, {
        evaluator_id: selectedEvaluatorId || undefined,
      });

      // Refresh enrollments
      const response = await enrollmentService.getByModality(selectedModality.id);
      setModalityEnrollments(response.enrollments || []);

      setEditingEnrollmentId(null);
      setSelectedEvaluatorId('');
      setSuccessMessage('Avaliador atribuído com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error updating evaluator:', err);
      setError(err?.response?.data?.detail || 'Erro ao atribuir avaliador');
    }
  };

  const handleCancelEditEvaluator = () => {
    setEditingEnrollmentId(null);
    setSelectedEvaluatorId('');
  };

  // Competence functions
  const fetchCompetences = async (modalityId: string) => {
    setLoadingCompetences(true);
    try {
      const data = await modalityService.getCompetences(modalityId);
      setCompetences(data || []);
    } catch (err) {
      console.error('Erro ao carregar competências:', err);
      setCompetences([]);
    } finally {
      setLoadingCompetences(false);
    }
  };

  const handleOpenCompetenceModal = () => {
    resetCompetence({
      name: '',
      description: '',
      max_score: 100,
      weight: 1,
    });
    setIsCompetenceModalOpen(true);
  };

  const handleAddCompetence = async (data: CompetenceFormData) => {
    if (!selectedModality) return;

    try {
      await modalityService.addCompetence(selectedModality.id, {
        name: data.name,
        description: data.description,
        max_score: data.max_score,
        weight: data.weight,
      });

      setIsCompetenceModalOpen(false);
      await fetchCompetences(selectedModality.id);
      setSuccessMessage('Competência adicionada com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Erro ao adicionar competência:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao adicionar competência';
      setError(message);
    }
  };

  const handleDeleteCompetence = async (competenceId: string) => {
    if (!selectedModality) return;

    try {
      setIsDeletingCompetence(true);
      setDeletingCompetenceId(competenceId);
      await modalityService.deleteCompetence(selectedModality.id, competenceId);
      await fetchCompetences(selectedModality.id);
      setSuccessMessage('Competência removida com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Erro ao remover competência:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao remover competência';
      setError(message);
    } finally {
      setIsDeletingCompetence(false);
      setDeletingCompetenceId(null);
    }
  };

  const columns = [
    { key: 'code', header: 'Código' },
    { key: 'name', header: 'Nome' },
    {
      key: 'description',
      header: 'Descrição',
      render: (item: Modality) => (
        <span className="truncate max-w-xs block">
          {item.description || '-'}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (item: Modality) => (
        <Badge variant={item.is_active ? 'success' : 'danger'}>
          {item.is_active ? 'Ativo' : 'Inativo'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (item: Modality) => (
        <div className="flex space-x-2">
          {!isCompetitor && (
            <Button size="sm" variant="ghost" onClick={() => handleViewDetails(item)}>
              Ver Detalhes
            </Button>
          )}
          {isSuperAdmin && (
            <>
              <Button size="sm" variant="ghost" onClick={() => handleOpenModal(item)}>
                Editar
              </Button>
              <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700" onClick={() => handleDeleteClick(item)}>
                Excluir
              </Button>
            </>
          )}
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
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Modalidades</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            {isSuperAdmin
              ? 'Gerencie as modalidades de competição'
              : isCompetitor
              ? 'Suas modalidades de competição'
              : 'Visualize suas modalidades atribuídas'}
          </p>
        </div>
        {isSuperAdmin && (
          <div className="flex-shrink-0">
            <Button onClick={() => handleOpenModal()}>Nova Modalidade</Button>
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

      <Card padding="none">
        <Table
          data={modalities}
          columns={columns}
          keyExtractor={(item) => item.id}
          emptyMessage={isCompetitor ? "Você ainda não está inscrito em nenhuma modalidade" : "Nenhuma modalidade cadastrada"}
        />
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingModality ? 'Editar Modalidade' : 'Nova Modalidade'}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Código"
            placeholder="Ex: SOLD, WS17, IT"
            error={errors.code?.message}
            {...register('code')}
            helperText="2-4 letras maiúsculas, opcionalmente seguidas de 2-3 números"
          />
          <Input
            label="Nome"
            placeholder="Ex: Soldagem"
            error={errors.name?.message}
            {...register('name')}
          />
          <Input
            label="Descrição"
            placeholder="Descrição da modalidade"
            error={errors.description?.message}
            {...register('description')}
          />
          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              {editingModality ? 'Salvar' : 'Criar'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal de confirmação de exclusão */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setDeletingModality(null);
        }}
        title="Confirmar Exclusão"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Tem certeza que deseja excluir a modalidade{' '}
            <strong className="text-gray-900 dark:text-gray-100">
              {deletingModality?.name}
            </strong>
            ?
          </p>
          <p className="text-sm text-red-600 dark:text-red-400">
            Esta ação não pode ser desfeita.
          </p>
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setDeleteModalOpen(false);
                setDeletingModality(null);
              }}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="danger"
              isLoading={isDeleting}
              onClick={handleConfirmDelete}
            >
              Excluir
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal de detalhes da modalidade */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={handleCloseDetailsModal}
        title={`Detalhes: ${selectedModality?.name || ''}`}
        size="xl"
      >
        {selectedModality && (
          <div className="space-y-6">
            {/* Modality Info - Header Card */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl p-5 text-white shadow-lg">
              <div className="flex items-start gap-4">
                <div className="w-20 h-20 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center text-2xl font-bold border border-white/30">
                  {selectedModality.code}
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-1">
                    {selectedModality.name}
                  </h3>
                  <p className="text-blue-100 text-sm leading-relaxed">
                    {selectedModality.description || 'Sem descrição disponível'}
                  </p>
                  <div className="flex items-center gap-4 mt-3">
                    <div className="flex items-center gap-1.5 text-blue-100 text-xs">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <span>{competences.length} competências</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-blue-100 text-xs">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span>{modalityEnrollments.length} competidores</span>
                    </div>
                    <Badge variant={selectedModality.is_active ? 'success' : 'danger'} className="text-xs">
                      {selectedModality.is_active ? 'Ativa' : 'Inativa'}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>

            {/* Competences Section */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Competências ({competences.length})
                </h4>
                {isSuperAdmin && (
                  <Button size="sm" onClick={handleOpenCompetenceModal}>
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Adicionar
                  </Button>
                )}
              </div>

              {loadingCompetences ? (
                <div className="flex justify-center py-8">
                  <Spinner size="md" />
                </div>
              ) : competences.length === 0 ? (
                <div className="py-8 text-center">
                  <svg className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">Nenhuma competência cadastrada</p>
                  {isSuperAdmin && (
                    <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">
                      Clique em "Adicionar" para cadastrar
                    </p>
                  )}
                </div>
              ) : (
                <div className="divide-y divide-gray-100 dark:divide-gray-700 max-h-64 overflow-y-auto">
                  {competences.map((competence, index) => (
                    <div
                      key={competence.id}
                      className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <span className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
                            {index + 1}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                              {competence.name}
                            </p>
                            {competence.description && (
                              <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                                {competence.description}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <div className="flex items-center gap-1.5">
                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded text-xs font-medium">
                            Máx: {competence.max_score}
                          </span>
                          <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded text-xs font-medium">
                            Peso: {competence.weight}
                          </span>
                        </div>
                        {isSuperAdmin && (
                          <button
                            onClick={() => handleDeleteCompetence(competence.id)}
                            disabled={isDeletingCompetence && deletingCompetenceId === competence.id}
                            className="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                            title="Remover competência"
                          >
                            {isDeletingCompetence && deletingCompetenceId === competence.id ? (
                              <Spinner size="sm" />
                            ) : (
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Enrolled Competitors and Evaluator Assignment */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  Competidores Vinculados ({modalityEnrollments.length})
                </h4>
              </div>

              {loadingEnrollments ? (
                <div className="flex justify-center py-8">
                  <Spinner size="md" />
                </div>
              ) : modalityEnrollments.length === 0 ? (
                <div className="py-8 text-center">
                  <svg className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">Nenhum competidor vinculado a esta modalidade</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100 dark:divide-gray-700 max-h-64 overflow-y-auto">
                  {modalityEnrollments.map((enrollment) => (
                    <div
                      key={enrollment.id}
                      className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white text-sm font-bold shadow-sm">
                          {enrollment.competitor_name?.charAt(0).toUpperCase() || '?'}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100">
                            {enrollment.competitor_name}
                          </p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <Badge variant={enrollment.status === 'active' ? 'success' : 'warning'} className="text-xs">
                              {enrollment.status === 'active' ? 'Ativo' : enrollment.status}
                            </Badge>
                            {enrollment.evaluator_name ? (
                              <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                                {enrollment.evaluator_name}
                              </span>
                            ) : (
                              <span className="text-xs text-yellow-600 dark:text-yellow-400 flex items-center gap-1">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                Sem avaliador
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {isSuperAdmin && (
                        <div className="flex items-center gap-2">
                          {editingEnrollmentId === enrollment.id ? (
                            <>
                              <select
                                value={selectedEvaluatorId}
                                onChange={(e) => setSelectedEvaluatorId(e.target.value)}
                                className="text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5 text-gray-900 dark:text-gray-100"
                              >
                                <option value="">Sem avaliador</option>
                                {evaluators.map((evaluator) => (
                                  <option key={evaluator.id} value={evaluator.id}>
                                    {evaluator.full_name}
                                  </option>
                                ))}
                              </select>
                              <Button size="sm" onClick={() => handleSaveEvaluator(enrollment)}>
                                Salvar
                              </Button>
                              <Button size="sm" variant="ghost" onClick={handleCancelEditEvaluator}>
                                Cancelar
                              </Button>
                            </>
                          ) : (
                            <button
                              onClick={() => handleEditEvaluator(enrollment)}
                              className="px-3 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                            >
                              {enrollment.evaluator_id ? 'Alterar avaliador' : 'Atribuir avaliador'}
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-4 text-center border border-blue-200 dark:border-blue-800">
                <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {modalityEnrollments.length}
                </p>
                <p className="text-xs text-blue-600/70 dark:text-blue-400/70 font-medium uppercase tracking-wide mt-1">
                  Competidores
                </p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl p-4 text-center border border-green-200 dark:border-green-800">
                <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-green-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {modalityEnrollments.filter(e => e.evaluator_id).length}
                </p>
                <p className="text-xs text-green-600/70 dark:text-green-400/70 font-medium uppercase tracking-wide mt-1">
                  Com Avaliador
                </p>
              </div>
              <div className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 rounded-xl p-4 text-center border border-amber-200 dark:border-amber-800">
                <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-amber-500/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">
                  {modalityEnrollments.filter(e => !e.evaluator_id).length}
                </p>
                <p className="text-xs text-amber-600/70 dark:text-amber-400/70 font-medium uppercase tracking-wide mt-1">
                  Sem Avaliador
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button variant="secondary" onClick={handleCloseDetailsModal}>
                Fechar
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Modal para adicionar competência */}
      <Modal
        isOpen={isCompetenceModalOpen}
        onClose={() => setIsCompetenceModalOpen(false)}
        title="Adicionar Competência"
      >
        <form onSubmit={handleSubmitCompetence(handleAddCompetence)} className="space-y-4">
          <Input
            label="Nome da Competência"
            placeholder="Ex: Leitura de Projetos"
            error={competenceErrors.name?.message}
            {...registerCompetence('name')}
          />

          <Input
            label="Descrição (opcional)"
            placeholder="Descreva a competência"
            error={competenceErrors.description?.message}
            {...registerCompetence('description')}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Nota Máxima"
              type="number"
              step="1"
              min="1"
              max="1000"
              error={competenceErrors.max_score?.message}
              {...registerCompetence('max_score')}
              helperText="Valor máximo que pode ser atribuído"
            />

            <Input
              label="Peso"
              type="number"
              step="0.1"
              min="0.1"
              max="10"
              error={competenceErrors.weight?.message}
              {...registerCompetence('weight')}
              helperText="Peso para cálculo de média"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsCompetenceModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmittingCompetence}>
              Adicionar
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ModalitiesPage;

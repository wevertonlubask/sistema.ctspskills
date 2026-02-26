import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardBody, Button, Badge, Spinner, Alert, Modal, Input, RichTextEditor, RichTextDisplay } from '../../components/ui';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { trainingService, trainingTypeService, enrollmentService } from '../../services';
import { useAuthStore } from '../../stores/authStore';
import type { TrainingSession, Modality, TrainingStatus, TrainingType, TrainingTypeConfig } from '../../types';

/**
 * Format date string (YYYY-MM-DD) to Brazilian format (DD/MM/YYYY)
 * without timezone conversion issues
 */
const formatDateBR = (dateString: string): string => {
  const [year, month, day] = dateString.split('T')[0].split('-');
  return `${day}/${month}/${year}`;
};

const statusLabels: Record<TrainingStatus, { label: string; variant: 'success' | 'warning' | 'info' | 'danger' }> = {
  pending: { label: 'Pendente', variant: 'warning' },
  approved: { label: 'Aprovado', variant: 'success' },
  rejected: { label: 'Rejeitado', variant: 'danger' },
  validated: { label: 'Validado', variant: 'success' },
};

const trainingTypeLabels: Record<TrainingType, string> = {
  senai: 'SENAI',
  external: 'FORA',
  empresa: 'FORA',
  autonomo: 'FORA',
};

const createTrainingSchema = z.object({
  modality_id: z.string().min(1, 'Selecione uma modalidade'),
  training_date: z.string().min(1, 'Data é obrigatória'),
  hours: z.coerce.number().min(0.5, 'Mínimo 0.5 horas').max(12, 'Máximo 12 horas'),
  training_type: z.string().min(1, 'Selecione um tipo de treinamento'),
  location: z.string().optional(),
  description: z.string().optional(),
});

type CreateTrainingFormData = z.infer<typeof createTrainingSchema>;

const editTrainingSchema = z.object({
  training_date: z.string().min(1, 'Data é obrigatória'),
  hours: z.coerce.number().min(0.5, 'Mínimo 0.5 horas').max(12, 'Máximo 12 horas'),
  training_type: z.string().min(1, 'Selecione um tipo de treinamento'),
  location: z.string().optional(),
  description: z.string().optional(),
});

type EditTrainingFormData = z.infer<typeof editTrainingSchema>;

const validateSchema = z.object({
  approved: z.boolean(),
  rejection_reason: z.string().optional(),
}).refine(
  (data) => data.approved || (data.rejection_reason && data.rejection_reason.trim().length > 0),
  {
    message: 'Motivo da rejeição é obrigatório',
    path: ['rejection_reason'],
  }
);

type ValidateFormData = z.infer<typeof validateSchema>;

const TrainingsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [trainings, setTrainings] = useState<TrainingSession[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [trainingTypes, setTrainingTypes] = useState<TrainingTypeConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterModality, setFilterModality] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterMonth, setFilterMonth] = useState<string>('all');

  // Create modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Details modal state
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedTraining, setSelectedTraining] = useState<TrainingSession | null>(null);

  // Validate modal state
  const [isValidateModalOpen, setIsValidateModalOpen] = useState(false);
  const [validatingTraining, setValidatingTraining] = useState<TrainingSession | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  // Edit modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingTraining, setEditingTraining] = useState<TrainingSession | null>(null);

  // Delete modal state
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletingTraining, setDeletingTraining] = useState<TrainingSession | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Batch validation state
  const [selectedTrainingIds, setSelectedTrainingIds] = useState<Set<string>>(new Set());
  const [isBatchValidateModalOpen, setIsBatchValidateModalOpen] = useState(false);
  const [batchApproved, setBatchApproved] = useState(true);
  const [batchRejectionReason, setBatchRejectionReason] = useState('');
  const [isBatchValidating, setIsBatchValidating] = useState(false);

  const {
    register: registerCreate,
    handleSubmit: handleSubmitCreate,
    reset: resetCreate,
    control: controlCreate,
    formState: { errors: createErrors, isSubmitting: isCreating },
  } = useForm<CreateTrainingFormData>({
    resolver: zodResolver(createTrainingSchema),
    defaultValues: {
      training_type: 'senai',
    },
  });

  const {
    register: registerValidate,
    handleSubmit: handleSubmitValidate,
    reset: resetValidate,
    watch: watchValidate,
    setValue: setValidateValue,
    formState: { errors: validateErrors },
  } = useForm<ValidateFormData>({
    resolver: zodResolver(validateSchema),
    defaultValues: {
      approved: true,
    },
  });

  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    control: controlEdit,
    formState: { errors: editErrors, isSubmitting: isEditing },
  } = useForm<EditTrainingFormData>({
    resolver: zodResolver(editTrainingSchema),
  });

  const approvedValue = watchValidate('approved');

  const fetchTrainings = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch modalities assigned to the current user
      const myModalities = await enrollmentService.getMyModalities();
      setModalities(myModalities || []);

      // Get the IDs of modalities the user has access to
      const myModalityIds = new Set(myModalities.map((m: Modality) => m.id));

      // Fetch all trainings and filter by user's modalities
      const response = await trainingService.getAll();
      const filteredTrainings = (response.trainings || [])
        .filter((training: TrainingSession) => myModalityIds.has(training.modality_id))
        .sort((a: TrainingSession, b: TrainingSession) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      setTrainings(filteredTrainings);
    } catch (err: any) {
      console.error('Erro ao carregar treinamentos:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao carregar treinamentos';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTrainingTypes = async () => {
    try {
      const data = await trainingTypeService.getAll({ active_only: true });
      setTrainingTypes(data || []);
    } catch (err) {
      console.error('Erro ao carregar tipos de treinamento:', err);
    }
  };

  useEffect(() => {
    fetchTrainings();
    fetchTrainingTypes();
  }, []);

  const handleOpenCreateModal = () => {
    resetCreate({
      modality_id: '',
      training_date: new Date().toISOString().split('T')[0],
      hours: 1,
      training_type: 'senai',
      location: '',
      description: '',
    });
    setIsCreateModalOpen(true);
  };

  const handleCreateSubmit = async (data: CreateTrainingFormData) => {
    try {
      setError(null);
      await trainingService.create({
        ...data,
        training_type: data.training_type as TrainingType,
      });
      // First fetch the updated list, then close the modal
      await fetchTrainings();
      setIsCreateModalOpen(false);
    } catch (err: any) {
      console.error('Erro ao criar treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao criar treinamento';
      setError(message);
    }
  };

  const handleViewDetails = (training: TrainingSession) => {
    setSelectedTraining(training);
    setIsDetailsModalOpen(true);
  };

  const handleOpenValidateModal = (training: TrainingSession) => {
    setValidatingTraining(training);
    resetValidate({ approved: true, rejection_reason: '' });
    setIsValidateModalOpen(true);
  };

  const handleValidateSubmit = async (data: ValidateFormData) => {
    if (!validatingTraining) return;

    try {
      setIsValidating(true);
      setError(null);
      await trainingService.validate(validatingTraining.id, {
        approved: data.approved,
        rejection_reason: data.approved ? undefined : data.rejection_reason,
      });
      setIsValidateModalOpen(false);
      setValidatingTraining(null);
      await fetchTrainings();
    } catch (err: any) {
      console.error('Erro ao validar treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao validar treinamento';
      setError(message);
    } finally {
      setIsValidating(false);
    }
  };

  // Edit training handlers
  const handleOpenEditModal = (training: TrainingSession) => {
    setEditingTraining(training);
    resetEdit({
      training_date: training.training_date.split('T')[0],
      hours: training.hours,
      training_type: training.training_type,
      location: training.location || '',
      description: training.description || '',
    });
    setIsEditModalOpen(true);
  };

  const handleEditSubmit = async (data: EditTrainingFormData) => {
    if (!editingTraining) return;
    try {
      setError(null);
      await trainingService.update(editingTraining.id, {
        training_date: data.training_date,
        hours: data.hours,
        training_type: data.training_type as TrainingType,
        location: data.location,
        description: data.description,
      });
      await fetchTrainings();
      setIsEditModalOpen(false);
      setEditingTraining(null);
    } catch (err: any) {
      console.error('Erro ao editar treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao editar treinamento';
      setError(message);
    }
  };

  // Delete training handlers
  const handleOpenDeleteModal = (training: TrainingSession) => {
    setDeletingTraining(training);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteTraining = async () => {
    if (!deletingTraining) return;
    setIsDeleting(true);
    try {
      setError(null);
      await trainingService.delete(deletingTraining.id);
      setIsDeleteModalOpen(false);
      setDeletingTraining(null);
      await fetchTrainings();
    } catch (err: any) {
      console.error('Erro ao excluir treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao excluir treinamento';
      setError(message);
    } finally {
      setIsDeleting(false);
    }
  };

  const getModalityName = (modalityId: string) => {
    const modality = modalities.find(m => m.id === modalityId);
    return modality?.name || 'N/A';
  };

  const getTrainingTypeName = (typeCode: string) => {
    const type = trainingTypes.find(t => t.code === typeCode);
    if (type) return type.name;
    // Fallback to hardcoded labels
    return trainingTypeLabels[typeCode as TrainingType] || typeCode;
  };

  // Generate month options for filter
  const getMonthOptions = (): Array<{ value: string; label: string }> => {
    const options: Array<{ value: string; label: string }> = [];
    const now = new Date();
    for (let i = 0; i < 12; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleDateString('pt-BR', { month: 'long' });
      const label = `${monthName.charAt(0).toUpperCase() + monthName.slice(1)}/${date.getFullYear()}`;
      options.push({ value, label });
    }
    return options;
  };

  const monthOptions = getMonthOptions();

  // Apply filters to trainings
  const filteredTrainings = trainings.filter((training) => {
    // Search by competitor name
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      const competitorName = (training.competitor_name || '').toLowerCase();
      const modalityName = (training.modality_name || getModalityName(training.modality_id)).toLowerCase();
      if (!competitorName.includes(search) && !modalityName.includes(search)) {
        return false;
      }
    }

    // Filter by status
    if (filterStatus !== 'all' && training.status !== filterStatus) {
      return false;
    }

    // Filter by modality
    if (filterModality !== 'all' && training.modality_id !== filterModality) {
      return false;
    }

    // Filter by training type
    if (filterType !== 'all' && training.training_type !== filterType) {
      return false;
    }

    // Filter by month
    if (filterMonth !== 'all') {
      const trainingDate = training.training_date.split('T')[0];
      const trainingMonth = trainingDate.substring(0, 7); // YYYY-MM
      if (trainingMonth !== filterMonth) {
        return false;
      }
    }

    return true;
  });

  // Clear all filters
  const clearFilters = () => {
    setSearchTerm('');
    setFilterStatus('all');
    setFilterModality('all');
    setFilterType('all');
    setFilterMonth('all');
  };

  const hasActiveFilters = searchTerm || filterStatus !== 'all' || filterModality !== 'all' || filterType !== 'all' || filterMonth !== 'all';

  // Get pending trainings from filtered list
  const pendingTrainings = filteredTrainings.filter(t => t.status === 'pending');

  // Toggle selection of a single training
  const toggleTrainingSelection = (trainingId: string) => {
    const newSelection = new Set(selectedTrainingIds);
    if (newSelection.has(trainingId)) {
      newSelection.delete(trainingId);
    } else {
      newSelection.add(trainingId);
    }
    setSelectedTrainingIds(newSelection);
  };

  // Select all pending trainings
  const selectAllPending = () => {
    const allPendingIds = new Set(pendingTrainings.map(t => t.id));
    setSelectedTrainingIds(allPendingIds);
  };

  // Clear selection
  const clearSelection = () => {
    setSelectedTrainingIds(new Set());
  };

  // Open batch validation modal
  const handleOpenBatchValidateModal = () => {
    setBatchApproved(true);
    setBatchRejectionReason('');
    setIsBatchValidateModalOpen(true);
  };

  // Handle batch validation
  const handleBatchValidate = async () => {
    if (selectedTrainingIds.size === 0) return;

    try {
      setIsBatchValidating(true);
      setError(null);

      // Validate each selected training
      const promises = Array.from(selectedTrainingIds).map(id =>
        trainingService.validate(id, {
          approved: batchApproved,
          rejection_reason: batchApproved ? undefined : batchRejectionReason,
        })
      );

      await Promise.all(promises);

      setIsBatchValidateModalOpen(false);
      setSelectedTrainingIds(new Set());
      setBatchRejectionReason('');
      await fetchTrainings();
    } catch (err: any) {
      console.error('Erro ao validar treinamentos em lote:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao validar treinamentos';
      setError(message);
    } finally {
      setIsBatchValidating(false);
    }
  };

  const isEvaluator = user?.role === 'evaluator' || user?.role === 'super_admin';
  const isCompetitor = user?.role === 'competitor';

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
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Treinamentos</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            {isEvaluator ? 'Gerencie e valide os treinamentos' : 'Registre e acompanhe seus treinamentos'}
          </p>
        </div>
        {isCompetitor && (
          <div className="flex-shrink-0">
            <Button onClick={handleOpenCreateModal}>Novo Treinamento</Button>
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters Section */}
      <Card>
        <CardBody>
          <div className="space-y-4">
            {/* Search and quick filters row */}
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search input */}
              <div className="flex-1">
                <Input
                  placeholder="Buscar por competidor ou modalidade..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              {/* Status filter */}
              <div className="w-full md:w-40">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="all">Todos os Status</option>
                  <option value="pending">Pendente</option>
                  <option value="approved">Aprovado</option>
                  <option value="rejected">Rejeitado</option>
                </select>
              </div>
            </div>

            {/* Additional filters row */}
            <div className="flex flex-col md:flex-row gap-4">
              {/* Modality filter */}
              <div className="w-full md:w-48">
                <select
                  value={filterModality}
                  onChange={(e) => setFilterModality(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="all">Todas Modalidades</option>
                  {modalities.map((modality) => (
                    <option key={modality.id} value={modality.id}>
                      {modality.code} - {modality.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Type filter */}
              <div className="w-full md:w-40">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="all">Todos os Tipos</option>
                  {trainingTypes.length > 0 ? (
                    trainingTypes.map((type) => (
                      <option key={type.id} value={type.code}>
                        {type.name}
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="senai">SENAI</option>
                      <option value="external">FORA</option>
                    </>
                  )}
                </select>
              </div>

              {/* Month filter */}
              <div className="w-full md:w-48">
                <select
                  value={filterMonth}
                  onChange={(e) => setFilterMonth(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="all">Todos os Meses</option>
                  {monthOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Clear filters button */}
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  Limpar Filtros
                </Button>
              )}
            </div>

            {/* Results count and batch actions */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {filteredTrainings.length} de {trainings.length} treinamento(s)
                {hasActiveFilters && ' (filtrado)'}
                {pendingTrainings.length > 0 && ` • ${pendingTrainings.length} pendente(s)`}
              </div>

              {/* Batch validation actions for evaluators */}
              {isEvaluator && pendingTrainings.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                  {selectedTrainingIds.size > 0 ? (
                    <>
                      <span className="text-sm text-primary-600 dark:text-primary-400 font-medium">
                        {selectedTrainingIds.size} selecionado(s)
                      </span>
                      <Button size="sm" variant="ghost" onClick={clearSelection}>
                        Limpar Seleção
                      </Button>
                      <Button size="sm" variant="primary" onClick={handleOpenBatchValidateModal}>
                        Validar Selecionados
                      </Button>
                    </>
                  ) : (
                    <Button size="sm" variant="secondary" onClick={selectAllPending}>
                      Selecionar Todos Pendentes ({pendingTrainings.length})
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {filteredTrainings.length === 0 ? (
        <Card>
          <CardBody>
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              {hasActiveFilters
                ? 'Nenhum treinamento encontrado com os filtros aplicados'
                : 'Nenhum treinamento encontrado'
              }
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTrainings.map((training) => (
            <Card key={training.id} hover className={selectedTrainingIds.has(training.id) ? 'ring-2 ring-primary-500' : ''}>
              <CardHeader action={
                <div className="flex items-center gap-2">
                  {isEvaluator && training.status === 'pending' && (
                    <input
                      type="checkbox"
                      checked={selectedTrainingIds.has(training.id)}
                      onChange={() => toggleTrainingSelection(training.id)}
                      className="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 cursor-pointer"
                      onClick={(e) => e.stopPropagation()}
                    />
                  )}
                  <Badge variant={statusLabels[training.status]?.variant || 'info'}>
                    {statusLabels[training.status]?.label || training.status}
                  </Badge>
                </div>
              }>
                <div className="flex flex-col min-w-0">
                  <span className="truncate font-semibold">
                    {training.competitor_name || 'Competidor'}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400 truncate">
                    {training.modality_name || getModalityName(training.modality_id)}
                  </span>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Modalidade:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {training.modality_name || getModalityName(training.modality_id)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Data:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {formatDateBR(training.training_date)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Horas:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">{training.hours}h</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Tipo:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {getTrainingTypeName(training.training_type)}
                    </span>
                  </div>
                  {training.description && (
                    <div className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                      <RichTextDisplay content={training.description} />
                    </div>
                  )}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-2">
                  <Button size="sm" variant="ghost" onClick={() => handleViewDetails(training)}>
                    Ver Detalhes
                  </Button>
                  {isEvaluator && (
                    <>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleOpenEditModal(training)}
                        title="Editar"
                        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/20"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleOpenDeleteModal(training)}
                        title="Excluir"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </Button>
                    </>
                  )}
                  {isEvaluator && training.status === 'pending' && (
                    <Button size="sm" variant="primary" onClick={() => handleOpenValidateModal(training)}>
                      Validar
                    </Button>
                  )}
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Modal de Criar Treinamento */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Novo Treinamento"
      >
        <form onSubmit={handleSubmitCreate(handleCreateSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Modalidade
            </label>
            <select
              {...registerCreate('modality_id')}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Selecione uma modalidade</option>
              {modalities.map((modality) => (
                <option key={modality.id} value={modality.id}>
                  {modality.code} - {modality.name}
                </option>
              ))}
            </select>
            {createErrors.modality_id && (
              <p className="mt-1 text-sm text-red-600">{createErrors.modality_id.message}</p>
            )}
          </div>

          <Input
            label="Data do Treinamento"
            type="date"
            error={createErrors.training_date?.message}
            {...registerCreate('training_date')}
          />

          <Input
            label="Horas"
            type="number"
            step="0.5"
            min="0.5"
            max="12"
            error={createErrors.hours?.message}
            {...registerCreate('hours')}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tipo
            </label>
            <select
              {...registerCreate('training_type')}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {trainingTypes.length > 0 ? (
                trainingTypes.map((type) => (
                  <option key={type.id} value={type.code}>
                    {type.name}
                  </option>
                ))
              ) : (
                <>
                  <option value="senai">SENAI</option>
                  <option value="external">FORA</option>
                </>
              )}
            </select>
          </div>

          <Input
            label="Local (opcional)"
            placeholder="Ex: SENAI Curitiba - Lab 3"
            error={createErrors.location?.message}
            {...registerCreate('location')}
          />

          <Controller
            name="description"
            control={controlCreate}
            defaultValue=""
            render={({ field }) => (
              <RichTextEditor
                label="Descrição (opcional)"
                placeholder="Descreva as atividades realizadas (suporta formatação: negrito, itálico, listas...)"
                value={field.value || ''}
                onChange={field.onChange}
                error={createErrors.description?.message}
                minHeight="100px"
              />
            )}
          />

          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isCreating}>
              Criar
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal de Detalhes */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedTraining(null);
        }}
        title="Detalhes do Treinamento"
      >
        {selectedTraining && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Competidor</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {selectedTraining.competitor_name || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Modalidade</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {selectedTraining.modality_name || getModalityName(selectedTraining.modality_id)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
                <Badge variant={statusLabels[selectedTraining.status]?.variant || 'info'}>
                  {statusLabels[selectedTraining.status]?.label || selectedTraining.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Data</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {formatDateBR(selectedTraining.training_date)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Horas</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">{selectedTraining.hours}h</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Tipo</p>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {getTrainingTypeName(selectedTraining.training_type)}
                </p>
              </div>
              {selectedTraining.location && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Local</p>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{selectedTraining.location}</p>
                </div>
              )}
            </div>

            {selectedTraining.description && (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Descrição</p>
                <div className="mt-1 text-gray-900 dark:text-gray-100">
                  <RichTextDisplay content={selectedTraining.description} />
                </div>
              </div>
            )}

            {selectedTraining.status === 'rejected' && selectedTraining.rejection_reason && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-sm font-medium text-red-800 dark:text-red-200">Motivo da Rejeição</p>
                <p className="mt-1 text-red-700 dark:text-red-300">{selectedTraining.rejection_reason}</p>
              </div>
            )}

            {selectedTraining.validated_at && (
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Validado em: {new Date(selectedTraining.validated_at).toLocaleString('pt-BR')}
              </div>
            )}

            {selectedTraining.evidences && selectedTraining.evidences.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Evidências ({selectedTraining.evidences.length})</p>
                <div className="space-y-2">
                  {selectedTraining.evidences.map((evidence) => (
                    <div key={evidence.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
                      <span className="text-sm text-gray-900 dark:text-gray-100">{evidence.file_name}</span>
                      <Badge variant="info">{evidence.evidence_type}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-4">
              <Button variant="secondary" onClick={() => {
                setIsDetailsModalOpen(false);
                setSelectedTraining(null);
              }}>
                Fechar
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Modal de Validação */}
      <Modal
        isOpen={isValidateModalOpen}
        onClose={() => {
          setIsValidateModalOpen(false);
          setValidatingTraining(null);
        }}
        title="Validar Treinamento"
      >
        {validatingTraining && (
          <form onSubmit={handleSubmitValidate(handleValidateSubmit)} className="space-y-4">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-500 dark:text-gray-400">Competidor</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {validatingTraining.competitor_name || 'N/A'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Treinamento</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {validatingTraining.modality_name || getModalityName(validatingTraining.modality_id)} - {validatingTraining.hours}h
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {formatDateBR(validatingTraining.training_date)}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Decisão
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="approved"
                    checked={approvedValue === true}
                    onChange={() => setValidateValue('approved', true)}
                    className="mr-2"
                  />
                  <span className="text-green-600 dark:text-green-400">Aprovar</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="approved"
                    checked={approvedValue === false}
                    onChange={() => setValidateValue('approved', false)}
                    className="mr-2"
                  />
                  <span className="text-red-600 dark:text-red-400">Rejeitar</span>
                </label>
              </div>
            </div>

            {!approvedValue && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Motivo da Rejeição
                </label>
                <textarea
                  {...registerValidate('rejection_reason')}
                  rows={3}
                  placeholder="Explique o motivo da rejeição"
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {validateErrors.rejection_reason && (
                  <p className="mt-1 text-sm text-red-600">{validateErrors.rejection_reason.message}</p>
                )}
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setIsValidateModalOpen(false);
                  setValidatingTraining(null);
                }}
              >
                Cancelar
              </Button>
              <Button type="submit" isLoading={isValidating}>
                Confirmar
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {/* Modal de Validação em Lote */}
      <Modal
        isOpen={isBatchValidateModalOpen}
        onClose={() => {
          setIsBatchValidateModalOpen(false);
          setBatchRejectionReason('');
        }}
        title="Validar em Lote"
      >
        <div className="space-y-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>{selectedTrainingIds.size}</strong> treinamento(s) selecionado(s) para validação
            </p>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              A ação será aplicada a todos os treinamentos selecionados.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Decisão
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="batchApproved"
                  checked={batchApproved === true}
                  onChange={() => setBatchApproved(true)}
                  className="mr-2"
                />
                <span className="text-green-600 dark:text-green-400">Aprovar Todos</span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="batchApproved"
                  checked={batchApproved === false}
                  onChange={() => setBatchApproved(false)}
                  className="mr-2"
                />
                <span className="text-red-600 dark:text-red-400">Rejeitar Todos</span>
              </label>
            </div>
          </div>

          {!batchApproved && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Motivo da Rejeição (aplicado a todos)
              </label>
              <textarea
                value={batchRejectionReason}
                onChange={(e) => setBatchRejectionReason(e.target.value)}
                rows={3}
                placeholder="Explique o motivo da rejeição"
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              {!batchApproved && !batchRejectionReason.trim() && (
                <p className="mt-1 text-sm text-red-600">Motivo da rejeição é obrigatório</p>
              )}
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => {
                setIsBatchValidateModalOpen(false);
                setBatchRejectionReason('');
              }}
            >
              Cancelar
            </Button>
            <Button
              variant={batchApproved ? 'primary' : 'danger'}
              onClick={handleBatchValidate}
              isLoading={isBatchValidating}
              disabled={!batchApproved && !batchRejectionReason.trim()}
            >
              {batchApproved ? 'Aprovar Todos' : 'Rejeitar Todos'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal de Edição de Treinamento */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => { setIsEditModalOpen(false); setEditingTraining(null); }}
        title="Editar Treinamento"
      >
        {editingTraining && (
          <form onSubmit={handleSubmitEdit(handleEditSubmit)} className="space-y-4">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
              <p className="text-sm text-gray-500 dark:text-gray-400">Competidor</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {editingTraining.competitor_name || 'N/A'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Modalidade</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {editingTraining.modality_name || getModalityName(editingTraining.modality_id)}
              </p>
            </div>

            <Input
              label="Data do Treinamento"
              type="date"
              error={editErrors.training_date?.message}
              {...registerEdit('training_date')}
            />

            <Input
              label="Horas"
              type="number"
              step="0.5"
              min="0.5"
              max="12"
              error={editErrors.hours?.message}
              {...registerEdit('hours')}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tipo
              </label>
              <select
                {...registerEdit('training_type')}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {trainingTypes.length > 0 ? (
                  trainingTypes.map((type) => (
                    <option key={type.id} value={type.code}>
                      {type.name}
                    </option>
                  ))
                ) : (
                  <>
                    <option value="senai">SENAI</option>
                    <option value="external">FORA</option>
                  </>
                )}
              </select>
            </div>

            <Input
              label="Local (opcional)"
              placeholder="Ex: SENAI Curitiba - Lab 3"
              error={editErrors.location?.message}
              {...registerEdit('location')}
            />

            <Controller
              name="description"
              control={controlEdit}
              defaultValue=""
              render={({ field }) => (
                <RichTextEditor
                  label="Descrição (opcional)"
                  placeholder="Descreva as atividades realizadas"
                  value={field.value || ''}
                  onChange={field.onChange}
                  error={editErrors.description?.message}
                  minHeight="100px"
                />
              )}
            />

            <div className="flex justify-end space-x-3 pt-4">
              <Button type="button" variant="secondary" onClick={() => { setIsEditModalOpen(false); setEditingTraining(null); }}>
                Cancelar
              </Button>
              <Button type="submit" isLoading={isEditing}>
                Salvar
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {/* Modal de Confirmação de Exclusão */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => { setIsDeleteModalOpen(false); setDeletingTraining(null); }}
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
                Tem certeza que deseja excluir este treinamento?
              </p>
              {deletingTraining && (
                <div className="text-sm text-red-600 dark:text-red-400 mt-1">
                  <p><strong>{deletingTraining.competitor_name}</strong></p>
                  <p>{formatDateBR(deletingTraining.training_date)} - {deletingTraining.hours}h</p>
                </div>
              )}
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Esta ação é irreversível. O registro de treinamento será removido permanentemente.
          </p>
          <div className="flex justify-end space-x-3 pt-2 border-t border-gray-200 dark:border-gray-700">
            <Button variant="secondary" onClick={() => { setIsDeleteModalOpen(false); setDeletingTraining(null); }}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={handleDeleteTraining}
              isLoading={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-500"
            >
              Excluir
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TrainingsPage;

import React, { useEffect, useState } from 'react';
import { Card, CardBody, Button, Table, Badge, Spinner, Alert, Modal, Input } from '../../components/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { competitorService, authService, modalityService, enrollmentService } from '../../services';
import { useAuthStore } from '../../stores/authStore';
import type { Competitor, Modality, EnrollmentDetail, User } from '../../types';

// Senha padrão para novos competidores - será exigida troca no primeiro login
const DEFAULT_PASSWORD = 'Mudar@123';

const competitorSchema = z.object({
  // User fields
  email: z.string().email('Email inválido'),
  // Competitor fields
  full_name: z.string().min(2, 'Nome deve ter no mínimo 2 caracteres'),
  birth_date: z.string().optional(),
  document_number: z.string().optional(),
  phone: z.string().optional(),
  emergency_contact: z.string().optional(),
  emergency_phone: z.string().optional(),
  notes: z.string().optional(),
});

type CompetitorFormData = z.infer<typeof competitorSchema>;

const CompetitorsPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const isSuperAdmin = user?.role === 'super_admin';

  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Details modal state
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null);

  // Enrollment management state
  const [competitorEnrollments, setCompetitorEnrollments] = useState<EnrollmentDetail[]>([]);
  const [loadingEnrollments, setLoadingEnrollments] = useState(false);
  const [isEnrollModalOpen, setIsEnrollModalOpen] = useState(false);
  const [selectedModalityForEnroll, setSelectedModalityForEnroll] = useState<string>('');
  const [selectedEvaluator, setSelectedEvaluator] = useState<string>('');
  const [evaluators, setEvaluators] = useState<User[]>([]);
  const [enrollingCompetitor, setEnrollingCompetitor] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CompetitorFormData>({
    resolver: zodResolver(competitorSchema),
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);

      // Super admins see all modalities, evaluators see only their assigned ones
      let modalitiesData: Modality[];
      if (isSuperAdmin) {
        modalitiesData = await modalityService.getAll({ active_only: true });
      } else {
        modalitiesData = await enrollmentService.getMyModalities();
      }
      setModalities(modalitiesData || []);

      // Fetch competitors
      const competitorsResponse = await competitorService.getAll({ limit: 500 });
      let allCompetitors = competitorsResponse.competitors || [];

      // For evaluators, filter to show only competitors enrolled in their modalities
      if (!isSuperAdmin && modalitiesData.length > 0) {
        // Get all enrollments for the evaluator's modalities to filter competitors
        const enrollmentPromises = modalitiesData.map(m =>
          enrollmentService.getByModality(m.id).catch(() => ({ enrollments: [] }))
        );
        const enrollmentResponses = await Promise.all(enrollmentPromises);

        // Collect all competitor IDs from the enrollments
        const myCompetitorIds = new Set<string>();
        enrollmentResponses.forEach(response => {
          (response.enrollments || []).forEach((enrollment: EnrollmentDetail) => {
            myCompetitorIds.add(enrollment.competitor_id);
          });
        });

        // Filter competitors to only those enrolled in the evaluator's modalities
        allCompetitors = allCompetitors.filter(c => myCompetitorIds.has(c.id));
      }

      setCompetitors(allCompetitors);
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = async (data: CompetitorFormData) => {
    try {
      // Step 1: Create user with role 'competitor' using default password
      const newUser = await authService.register({
        email: data.email,
        password: DEFAULT_PASSWORD,
        full_name: data.full_name,
        role: 'competitor',
        must_change_password: true,
      });

      // Step 2: Create competitor profile linked to the user
      await competitorService.create({
        user_id: newUser.id,
        full_name: data.full_name,
        birth_date: data.birth_date || undefined,
        document_number: data.document_number || undefined,
        phone: data.phone || undefined,
        emergency_contact: data.emergency_contact || undefined,
        emergency_phone: data.emergency_phone || undefined,
        notes: data.notes || undefined,
      });

      setIsModalOpen(false);
      reset();
      fetchData();
      setSuccessMessage('Competidor cadastrado com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error creating competitor:', err);
      const message = err?.response?.data?.detail || 'Erro ao cadastrar competidor';
      setError(message);
    }
  };

  const handleOpenModal = () => {
    reset();
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    reset();
  };

  const handleViewDetails = async (competitor: Competitor) => {
    setSelectedCompetitor(competitor);
    setIsDetailsModalOpen(true);

    // Fetch enrollments for this competitor
    setLoadingEnrollments(true);
    try {
      console.log('[ViewDetails] Fetching enrollments for competitor:', competitor.id);
      const response = await enrollmentService.getByCompetitor(competitor.id);
      console.log('[ViewDetails] Enrollments response:', response);
      setCompetitorEnrollments(response.enrollments || []);
    } catch (err) {
      console.error('[ViewDetails] Error fetching enrollments:', err);
      setCompetitorEnrollments([]);
    } finally {
      setLoadingEnrollments(false);
    }
  };

  const handleCloseDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setSelectedCompetitor(null);
    setCompetitorEnrollments([]);
  };

  const handleOpenEnrollModal = async () => {
    setSelectedModalityForEnroll('');
    setSelectedEvaluator('');
    setIsEnrollModalOpen(true);

    // Fetch evaluators only for super admins
    // Evaluators will auto-assign themselves
    if (isSuperAdmin) {
      try {
        const response = await enrollmentService.getEvaluators();
        setEvaluators(response.users || []);
      } catch (err) {
        console.error('Error fetching evaluators:', err);
      }
    } else {
      // For evaluators, pre-select themselves as the evaluator
      setSelectedEvaluator(user?.id || '');
    }
  };

  const handleCloseEnrollModal = () => {
    setIsEnrollModalOpen(false);
    setSelectedModalityForEnroll('');
    setSelectedEvaluator('');
  };

  const handleEnrollCompetitor = async () => {
    if (!selectedCompetitor || !selectedModalityForEnroll) return;

    setEnrollingCompetitor(true);
    try {
      console.log('[Enrollment] Creating enrollment:', {
        modalityId: selectedModalityForEnroll,
        competitorId: selectedCompetitor.id,
        evaluatorId: selectedEvaluator || undefined,
      });

      const enrollmentResult = await enrollmentService.enrollCompetitor(selectedModalityForEnroll, {
        competitor_id: selectedCompetitor.id,
        evaluator_id: selectedEvaluator || undefined,
      });
      console.log('[Enrollment] Created successfully:', enrollmentResult);

      // Refresh enrollments
      console.log('[Enrollment] Fetching enrollments for competitor:', selectedCompetitor.id);
      const response = await enrollmentService.getByCompetitor(selectedCompetitor.id);
      console.log('[Enrollment] Fetched enrollments:', response);
      setCompetitorEnrollments(response.enrollments || []);

      handleCloseEnrollModal();
      setSuccessMessage('Competidor vinculado à modalidade com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('[Enrollment] Error:', err);
      console.error('[Enrollment] Error response:', err?.response?.data);
      setError(err?.response?.data?.detail || 'Erro ao vincular competidor');
    } finally {
      setEnrollingCompetitor(false);
    }
  };

  const handleRemoveEnrollment = async (enrollment: EnrollmentDetail) => {
    if (!window.confirm('Deseja realmente remover este vínculo?')) return;

    try {
      await enrollmentService.delete(enrollment.modality_id, enrollment.id);

      // Refresh enrollments
      if (selectedCompetitor) {
        const response = await enrollmentService.getByCompetitor(selectedCompetitor.id);
        setCompetitorEnrollments(response.enrollments || []);
      }

      setSuccessMessage('Vínculo removido com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error removing enrollment:', err);
      setError(err?.response?.data?.detail || 'Erro ao remover vínculo');
    }
  };

  // Get modalities the competitor is NOT enrolled in (for enrollment dropdown)
  const availableModalities = modalities.filter(
    m => !competitorEnrollments.some(e => e.modality_id === m.id)
  );

  // Filter competitors by search term
  const filteredCompetitors = competitors.filter(comp =>
    comp.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    comp.document_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Statistics
  const totalCompetitors = competitors.length;
  const activeCompetitors = competitors.filter(c => c.is_active).length;

  const columns = [
    {
      key: 'full_name',
      header: 'Nome',
      render: (item: Competitor) => (
        <span className="font-medium text-gray-900 dark:text-gray-100">
          {item.full_name}
        </span>
      ),
    },
    {
      key: 'document_number',
      header: 'Documento',
      render: (item: Competitor) => item.document_number || '-',
    },
    {
      key: 'phone',
      header: 'Telefone',
      render: (item: Competitor) => item.phone || '-',
    },
    {
      key: 'birth_date',
      header: 'Nascimento',
      render: (item: Competitor) =>
        item.birth_date ? new Date(item.birth_date).toLocaleDateString('pt-BR') : '-',
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (item: Competitor) => (
        <Badge variant={item.is_active ? 'success' : 'danger'}>
          {item.is_active ? 'Ativo' : 'Inativo'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Cadastro',
      render: (item: Competitor) =>
        item.created_at ? new Date(item.created_at).toLocaleDateString('pt-BR') : '-',
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (item: Competitor) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => handleViewDetails(item)}>
            Ver Detalhes
          </Button>
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
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Competidores</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Gerencie os competidores cadastrados no sistema
          </p>
        </div>
        <div className="flex-shrink-0">
          <Button onClick={handleOpenModal}>Novo Competidor</Button>
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

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <p className="text-xs text-blue-600 dark:text-blue-400 font-medium uppercase tracking-wide">Total</p>
              <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{totalCompetitors}</p>
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
              <p className="text-xs text-green-600 dark:text-green-400 font-medium uppercase tracking-wide">Ativos</p>
              <p className="text-3xl font-bold text-green-700 dark:text-green-300">{activeCompetitors}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-purple-100 dark:bg-purple-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-xs text-purple-600 dark:text-purple-400 font-medium uppercase tracking-wide">Modalidades</p>
              <p className="text-3xl font-bold text-purple-700 dark:text-purple-300">{modalities.length}</p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Search */}
      <Card>
        <CardBody>
          <div className="flex items-center gap-4">
            <div className="flex-1 max-w-md">
              <Input
                placeholder="Buscar por nome ou documento..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            {searchTerm && (
              <Button variant="secondary" onClick={() => setSearchTerm('')}>
                Limpar
              </Button>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Table */}
      <Card padding="none">
        <Table
          data={filteredCompetitors}
          columns={columns}
          keyExtractor={(item) => item.id}
          emptyMessage="Nenhum competidor encontrado"
        />
      </Card>

      {/* Modal for creating new competitor */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title="Novo Competidor"
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* User Account Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
              <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Conta de Acesso
            </h3>
            <div className="space-y-4">
              <Input
                label="Email *"
                type="email"
                placeholder="email@exemplo.com"
                error={errors.email?.message}
                {...register('email')}
              />
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  <strong>Senha padrão:</strong> {DEFAULT_PASSWORD}
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  O competidor será solicitado a alterar a senha no primeiro acesso.
                </p>
              </div>
            </div>
          </div>

          {/* Personal Info Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
              <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
              </svg>
              Dados Pessoais
            </h3>
            <div className="space-y-4">
              <Input
                label="Nome Completo *"
                placeholder="Nome do competidor"
                error={errors.full_name?.message}
                {...register('full_name')}
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Data de Nascimento"
                  type="date"
                  error={errors.birth_date?.message}
                  {...register('birth_date')}
                />
                <Input
                  label="Documento (CPF/RG)"
                  placeholder="000.000.000-00"
                  error={errors.document_number?.message}
                  {...register('document_number')}
                />
              </div>
              <Input
                label="Telefone"
                placeholder="(00) 00000-0000"
                error={errors.phone?.message}
                {...register('phone')}
              />
            </div>
          </div>

          {/* Emergency Contact Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
              <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Contato de Emergência
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome do Contato"
                placeholder="Nome do responsável"
                error={errors.emergency_contact?.message}
                {...register('emergency_contact')}
              />
              <Input
                label="Telefone de Emergência"
                placeholder="(00) 00000-0000"
                error={errors.emergency_phone?.message}
                {...register('emergency_phone')}
              />
            </div>
          </div>

          {/* Notes Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Observações
            </label>
            <textarea
              {...register('notes')}
              rows={3}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
              placeholder="Informações adicionais sobre o competidor..."
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="secondary" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Cadastrar Competidor
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal for viewing competitor details */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={handleCloseDetailsModal}
        title="Detalhes do Competidor"
        size="lg"
      >
        {selectedCompetitor && (
          <div className="space-y-6">
            {/* Header with name and status */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                  {selectedCompetitor.full_name?.charAt(0).toUpperCase() || '?'}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.full_name}
                  </h3>
                  <Badge variant={selectedCompetitor.is_active ? 'success' : 'danger'}>
                    {selectedCompetitor.is_active ? 'Ativo' : 'Inativo'}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Account Info */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
                Conta de Acesso
              </h4>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
                <div>
                  <p className="text-xs text-blue-600 dark:text-blue-400 uppercase tracking-wide">Email de Login</p>
                  <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    {selectedCompetitor.email || selectedCompetitor.user?.email || 'Não informado'}
                  </p>
                </div>
              </div>
            </div>

            {/* Personal Info */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Dados Pessoais
              </h4>
              <div className="grid grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Data de Nascimento</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.birth_date
                      ? new Date(selectedCompetitor.birth_date).toLocaleDateString('pt-BR')
                      : 'Não informado'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Idade</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.age ? `${selectedCompetitor.age} anos` : 'Não informado'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Documento</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.document_number || 'Não informado'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Telefone</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.phone || 'Não informado'}
                  </p>
                </div>
              </div>
            </div>

            {/* Emergency Contact */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                Contato de Emergência
              </h4>
              <div className="grid grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Nome</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.emergency_contact || 'Não informado'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Telefone</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedCompetitor.emergency_phone || 'Não informado'}
                  </p>
                </div>
              </div>
            </div>

            {/* Modality Enrollments */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 flex items-center">
                  <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  Modalidades Vinculadas
                </h4>
                <Button size="sm" onClick={handleOpenEnrollModal}>
                  Vincular Modalidade
                </Button>
              </div>

              {loadingEnrollments ? (
                <div className="flex justify-center py-4">
                  <Spinner size="sm" />
                </div>
              ) : competitorEnrollments.length === 0 ? (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  Nenhuma modalidade vinculada
                </div>
              ) : (
                <div className="space-y-2">
                  {competitorEnrollments.map((enrollment) => (
                    <div
                      key={enrollment.id}
                      className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg p-3"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                          <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
                            {enrollment.modality_code}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {enrollment.modality_name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {enrollment.evaluator_name ? (
                              <>Avaliador: {enrollment.evaluator_name}</>
                            ) : (
                              <span className="text-yellow-600 dark:text-yellow-400">Sem avaliador atribuído</span>
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={enrollment.status === 'active' ? 'success' : 'warning'}>
                          {enrollment.status === 'active' ? 'Ativo' : enrollment.status}
                        </Badge>
                        {isSuperAdmin && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-600 hover:text-red-800"
                            onClick={() => handleRemoveEnrollment(enrollment)}
                          >
                            Remover
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Notes */}
            {selectedCompetitor.notes && (
              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                  <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Observações
                </h4>
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {selectedCompetitor.notes}
                  </p>
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-xs text-gray-500 dark:text-gray-400">
                <div>
                  <span className="uppercase tracking-wide">Cadastrado em:</span>{' '}
                  <span className="text-gray-700 dark:text-gray-300">
                    {selectedCompetitor.created_at
                      ? new Date(selectedCompetitor.created_at).toLocaleString('pt-BR')
                      : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="uppercase tracking-wide">Atualizado em:</span>{' '}
                  <span className="text-gray-700 dark:text-gray-300">
                    {selectedCompetitor.updated_at
                      ? new Date(selectedCompetitor.updated_at).toLocaleString('pt-BR')
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <Button variant="secondary" onClick={handleCloseDetailsModal}>
                Fechar
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Modal for enrolling competitor in modality */}
      <Modal
        isOpen={isEnrollModalOpen}
        onClose={handleCloseEnrollModal}
        title="Vincular à Modalidade"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Vincule o competidor <strong>{selectedCompetitor?.full_name}</strong> a uma modalidade.
          </p>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Modalidade *
            </label>
            <select
              value={selectedModalityForEnroll}
              onChange={(e) => setSelectedModalityForEnroll(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
            >
              <option value="">Selecione uma modalidade</option>
              {availableModalities.map((modality) => (
                <option key={modality.id} value={modality.id}>
                  [{modality.code}] {modality.name}
                </option>
              ))}
            </select>
            {availableModalities.length === 0 && (
              <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                O competidor já está vinculado a todas as modalidades disponíveis.
              </p>
            )}
          </div>

          {isSuperAdmin ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Avaliador Responsável
              </label>
              <select
                value={selectedEvaluator}
                onChange={(e) => setSelectedEvaluator(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
              >
                <option value="">Selecione um avaliador (opcional)</option>
                {evaluators.map((evaluator) => (
                  <option key={evaluator.id} value={evaluator.id}>
                    {evaluator.full_name} ({evaluator.email})
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                O avaliador será responsável por este competidor na modalidade selecionada.
              </p>
            </div>
          ) : (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                Você será automaticamente atribuído como avaliador responsável por este competidor.
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="secondary" onClick={handleCloseEnrollModal}>
              Cancelar
            </Button>
            <Button
              onClick={handleEnrollCompetitor}
              isLoading={enrollingCompetitor}
              disabled={!selectedModalityForEnroll}
            >
              Vincular
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CompetitorsPage;

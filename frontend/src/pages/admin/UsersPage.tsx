import React, { useEffect, useState } from 'react';
import { Card, CardBody, Button, Table, Badge, Spinner, Alert, Modal, Input } from '../../components/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authService, modalityService, enrollmentService } from '../../services';
import type { User, Modality } from '../../types';
import api from '../../services/api';

interface EvaluatorModality {
  id: string;
  evaluator_id: string;
  modality_id: string;
  modality_code: string;
  modality_name: string;
  assigned_at: string;
  assigned_by: string;
  is_active: boolean;
}

// Senha padrão para novos usuários - será exigida troca no primeiro login
const DEFAULT_PASSWORD = 'Mudar@123';

const userSchema = z.object({
  full_name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
  role: z.enum(['super_admin', 'evaluator']),
});

type UserFormData = z.infer<typeof userSchema>;

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedModalities, setSelectedModalities] = useState<string[]>([]);

  // User details modal state
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userModalities, setUserModalities] = useState<EvaluatorModality[]>([]);
  const [loadingUserModalities, setLoadingUserModalities] = useState(false);
  const [isAssigningModality, setIsAssigningModality] = useState(false);
  const [modalityToAssign, setModalityToAssign] = useState<string>('');
  const [removingModalityId, setRemovingModalityId] = useState<string | null>(null);

  // Delete confirmation modal state
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [togglingUserId, setTogglingUserId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      role: 'evaluator',
    },
  });

  const watchedRole = watch('role');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      // Fetch all users and modalities
      const [usersResponse, modalitiesData] = await Promise.all([
        api.get<{ users: User[]; total: number }>('/users', { params: { limit: 500 } }),
        modalityService.getAll({ active_only: true }),
      ]);
      // Filter to show only evaluators and admins (not competitors)
      const filteredUsers = (usersResponse.data.users || []).filter(
        (user) => user.role === 'super_admin' || user.role === 'evaluator'
      );
      setUsers(filteredUsers);
      setModalities(modalitiesData || []);
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError(err?.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = () => {
    reset({
      full_name: '',
      email: '',
      role: 'evaluator',
    });
    setSelectedModalities([]);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedModalities([]);
    reset();
  };

  const toggleModality = (modalityId: string) => {
    setSelectedModalities(prev =>
      prev.includes(modalityId)
        ? prev.filter(id => id !== modalityId)
        : [...prev, modalityId]
    );
  };

  const onSubmit = async (data: UserFormData) => {
    try {
      // Step 1: Create the user with default password
      const newUser = await authService.register({
        email: data.email,
        password: DEFAULT_PASSWORD,
        full_name: data.full_name,
        role: data.role,
        must_change_password: true,
      });

      // Step 2: If evaluator and modalities were selected, assign them directly
      if (data.role === 'evaluator' && selectedModalities.length > 0) {
        for (const modalityId of selectedModalities) {
          try {
            await enrollmentService.assignModalityToEvaluator(newUser.id, modalityId);
          } catch (err) {
            console.error(`Error assigning modality ${modalityId}:`, err);
          }
        }
      }

      setIsModalOpen(false);
      setSelectedModalities([]);
      reset();
      fetchData();
      setSuccessMessage('Usuário cadastrado com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error creating user:', err);
      const message = err?.response?.data?.detail || 'Erro ao cadastrar usuário';
      setError(message);
    }
  };

  // User details modal handlers
  const handleViewUserDetails = async (user: User) => {
    setSelectedUser(user);
    setIsDetailsModalOpen(true);
    setModalityToAssign('');

    if (user.role === 'evaluator') {
      setLoadingUserModalities(true);
      try {
        // Get modalities directly assigned to this evaluator
        const assignments = await enrollmentService.getEvaluatorModalities(user.id);
        setUserModalities(assignments || []);
      } catch (err) {
        console.error('Error fetching user modalities:', err);
        setUserModalities([]);
      } finally {
        setLoadingUserModalities(false);
      }
    }
  };

  const handleCloseDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setSelectedUser(null);
    setUserModalities([]);
    setModalityToAssign('');
  };

  const handleAssignModalityToEvaluator = async () => {
    if (!selectedUser || !modalityToAssign) return;

    setIsAssigningModality(true);
    try {
      // Assign modality directly to evaluator
      await enrollmentService.assignModalityToEvaluator(selectedUser.id, modalityToAssign);

      // Refresh user modalities
      const assignments = await enrollmentService.getEvaluatorModalities(selectedUser.id);
      setUserModalities(assignments || []);
      setModalityToAssign('');

      setSuccessMessage('Modalidade atribuída com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error assigning modality:', err);
      setError(err?.response?.data?.detail || 'Erro ao atribuir modalidade');
    } finally {
      setIsAssigningModality(false);
    }
  };

  const handleRemoveModalityFromEvaluator = async (modalityId: string) => {
    if (!selectedUser) return;

    setRemovingModalityId(modalityId);
    try {
      await enrollmentService.removeModalityFromEvaluator(selectedUser.id, modalityId);

      // Refresh user modalities
      const assignments = await enrollmentService.getEvaluatorModalities(selectedUser.id);
      setUserModalities(assignments || []);

      setSuccessMessage('Modalidade removida com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error removing modality:', err);
      setError(err?.response?.data?.detail || 'Erro ao remover modalidade');
    } finally {
      setRemovingModalityId(null);
    }
  };

  // Get modalities this evaluator is NOT assigned to yet
  const getAvailableModalitiesForUser = () => {
    const assignedModalityIds = new Set(userModalities.map(m => m.modality_id));
    return modalities.filter(m => !assignedModalityIds.has(m.id));
  };

  // User status toggle (activate/deactivate)
  const handleToggleUserStatus = async (user: User) => {
    const isActive = user.status === 'active';
    const endpoint = isActive ? 'deactivate' : 'activate';
    setTogglingUserId(user.id);
    try {
      await api.patch(`/users/${user.id}/${endpoint}`);
      fetchData();
      setSuccessMessage(`Usuário ${isActive ? 'desativado' : 'ativado'} com sucesso!`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error toggling user status:', err);
      setError(err?.response?.data?.detail || 'Erro ao alterar status do usuário');
    } finally {
      setTogglingUserId(null);
    }
  };

  // Delete user
  const handleDeleteUser = async () => {
    if (!userToDelete) return;
    setIsDeleting(true);
    try {
      await api.delete(`/users/${userToDelete.id}`);
      setIsDeleteModalOpen(false);
      setUserToDelete(null);
      fetchData();
      setSuccessMessage('Usuário excluído com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error deleting user:', err);
      setError(err?.response?.data?.detail || 'Erro ao excluir usuário');
    } finally {
      setIsDeleting(false);
    }
  };

  const openDeleteModal = (user: User) => {
    setUserToDelete(user);
    setIsDeleteModalOpen(true);
  };

  const roleLabels: Record<string, string> = {
    super_admin: 'Super Admin',
    evaluator: 'Avaliador',
  };

  const roleColors: Record<string, 'danger' | 'warning' | 'info' | 'success'> = {
    super_admin: 'danger',
    evaluator: 'warning',
  };

  // Statistics
  const totalUsers = users.length;
  const totalAdmins = users.filter(u => u.role === 'super_admin').length;
  const totalEvaluators = users.filter(u => u.role === 'evaluator').length;

  const columns = [
    {
      key: 'full_name',
      header: 'Nome',
      render: (item: User) => (
        <span className="font-medium text-gray-900 dark:text-gray-100">
          {item.full_name || item.name || '-'}
        </span>
      ),
    },
    { key: 'email', header: 'Email' },
    {
      key: 'role',
      header: 'Perfil',
      render: (item: User) => (
        <Badge variant={roleColors[item.role] || 'info'}>
          {roleLabels[item.role] || item.role}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item: User) => (
        <Badge variant={item.status === 'active' ? 'success' : 'danger'}>
          {item.status === 'active' ? 'Ativo' : 'Inativo'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Cadastro',
      render: (item: User) =>
        item.created_at ? new Date(item.created_at).toLocaleDateString('pt-BR') : '-',
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (item: User) => (
        <div className="flex space-x-1">
          {item.role === 'evaluator' && (
            <Button size="sm" variant="ghost" onClick={() => handleViewUserDetails(item)} title="Modalidades">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleToggleUserStatus(item)}
            disabled={togglingUserId === item.id}
            title={item.status === 'active' ? 'Desativar' : 'Ativar'}
            className={item.status === 'active'
              ? 'text-yellow-600 hover:text-yellow-700 hover:bg-yellow-50 dark:text-yellow-400 dark:hover:bg-yellow-900/20'
              : 'text-green-600 hover:text-green-700 hover:bg-green-50 dark:text-green-400 dark:hover:bg-green-900/20'
            }
          >
            {togglingUserId === item.id ? (
              <Spinner size="sm" />
            ) : item.status === 'active' ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => openDeleteModal(item)}
            title="Excluir"
            className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
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
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Usuários</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Gerencie avaliadores e administradores do sistema
          </p>
        </div>
        <div className="flex-shrink-0">
          <Button onClick={handleOpenModal}>Novo Usuário</Button>
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <p className="text-xs text-blue-600 dark:text-blue-400 font-medium uppercase tracking-wide">Total</p>
              <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{totalUsers}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-red-100 dark:bg-red-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <p className="text-xs text-red-600 dark:text-red-400 font-medium uppercase tracking-wide">Administradores</p>
              <p className="text-3xl font-bold text-red-700 dark:text-red-300">{totalAdmins}</p>
            </div>
          </CardBody>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-700">
          <CardBody>
            <div className="text-center">
              <div className="w-10 h-10 mx-auto rounded-full bg-yellow-100 dark:bg-yellow-800 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <p className="text-xs text-yellow-600 dark:text-yellow-400 font-medium uppercase tracking-wide">Avaliadores</p>
              <p className="text-3xl font-bold text-yellow-700 dark:text-yellow-300">{totalEvaluators}</p>
            </div>
          </CardBody>
        </Card>
      </div>

      <Card padding="none">
        <Table
          data={users}
          columns={columns}
          keyExtractor={(item) => item.id}
          emptyMessage="Nenhum usuário cadastrado"
        />
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title="Novo Usuário"
        size="md"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nome Completo *"
            placeholder="Nome do usuário"
            error={errors.full_name?.message}
            {...register('full_name')}
          />
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
              O usuário será solicitado a alterar a senha no primeiro acesso.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Perfil *
            </label>
            <select
              {...register('role')}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
            >
              <option value="evaluator">Avaliador</option>
              <option value="super_admin">Super Admin</option>
            </select>
            {errors.role && (
              <p className="text-sm text-red-600 mt-1">{errors.role.message}</p>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Avaliadores podem gerenciar competidores e lançar notas. Super Admins têm acesso total ao sistema.
            </p>
          </div>

          {/* Modality selection - only for evaluators */}
          {watchedRole === 'evaluator' && modalities.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Modalidades do Avaliador
              </label>
              <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-3 max-h-40 overflow-y-auto space-y-2">
                {modalities.map(modality => (
                  <label key={modality.id} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedModalities.includes(modality.id)}
                      onChange={() => toggleModality(modality.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      <span className="font-medium">[{modality.code}]</span> {modality.name}
                    </span>
                  </label>
                ))}
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {selectedModalities.length > 0
                  ? `${selectedModalities.length} modalidade(s) selecionada(s). O avaliador poderá gerenciar competidores, exames e notas destas modalidades.`
                  : 'Selecione as modalidades que este avaliador irá gerenciar (opcional).'}
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="secondary" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Cadastrar
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => { setIsDeleteModalOpen(false); setUserToDelete(null); }}
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
                Tem certeza que deseja excluir este usuário?
              </p>
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                <strong>{userToDelete?.full_name}</strong> ({userToDelete?.email})
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Esta ação é irreversível. Todos os dados associados a este usuário serão removidos.
          </p>
          <div className="flex justify-end space-x-3 pt-2 border-t border-gray-200 dark:border-gray-700">
            <Button variant="secondary" onClick={() => { setIsDeleteModalOpen(false); setUserToDelete(null); }}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={handleDeleteUser}
              isLoading={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-500"
            >
              Excluir
            </Button>
          </div>
        </div>
      </Modal>

      {/* User Details Modal - For managing evaluator modalities */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={handleCloseDetailsModal}
        title={`Modalidades: ${selectedUser?.full_name || ''}`}
        size="lg"
      >
        {selectedUser && selectedUser.role === 'evaluator' && (
          <div className="space-y-6">
            {/* User Info */}
            <div className="flex items-center space-x-4 pb-4 border-b border-gray-200 dark:border-gray-700">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center text-white text-lg font-bold">
                {selectedUser.full_name?.charAt(0).toUpperCase() || '?'}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {selectedUser.full_name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {selectedUser.email}
                </p>
              </div>
            </div>

            {/* Assign new modality */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Atribuir Nova Modalidade
              </h4>
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <select
                    value={modalityToAssign}
                    onChange={(e) => setModalityToAssign(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
                  >
                    <option value="">Selecione uma modalidade</option>
                    {getAvailableModalitiesForUser().map(modality => (
                      <option key={modality.id} value={modality.id}>
                        [{modality.code}] {modality.name}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={handleAssignModalityToEvaluator}
                  isLoading={isAssigningModality}
                  disabled={!modalityToAssign}
                >
                  Atribuir
                </Button>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                O avaliador poderá visualizar e gerenciar competidores, exames e notas desta modalidade.
              </p>
            </div>

            {/* Current modalities */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Modalidades Atribuídas ({userModalities.length})
              </h4>

              {loadingUserModalities ? (
                <div className="flex justify-center py-4">
                  <Spinner size="sm" />
                </div>
              ) : userModalities.length === 0 ? (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  Nenhuma modalidade atribuída a este avaliador
                </div>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {userModalities.map(assignment => (
                    <div
                      key={assignment.id}
                      className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                            <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
                              {assignment.modality_code}
                            </span>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                              {assignment.modality_name}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Atribuída em {new Date(assignment.assigned_at).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleRemoveModalityFromEvaluator(assignment.modality_id)}
                          isLoading={removingModalityId === assignment.modality_id}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button variant="secondary" onClick={handleCloseDetailsModal}>
                Fechar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default UsersPage;

import React, { useEffect, useState } from 'react';
import { Card, Button, Table, Badge, Modal, Input, Alert, Spinner } from '../../components/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { trainingTypeService } from '../../services';
import type { TrainingTypeConfig } from '../../types';

const trainingTypeSchema = z.object({
  code: z
    .string()
    .min(2, 'Código deve ter no mínimo 2 caracteres')
    .max(50, 'Código deve ter no máximo 50 caracteres')
    .regex(/^[a-z0-9_]+$/, 'Código deve conter apenas letras minúsculas, números e underscores')
    .transform((val) => val.toLowerCase()),
  name: z.string().min(2, 'Nome deve ter no mínimo 2 caracteres').max(100, 'Nome deve ter no máximo 100 caracteres'),
  description: z.string().max(500, 'Descrição deve ter no máximo 500 caracteres').optional().or(z.literal('')),
  display_order: z.coerce.number().min(0, 'Ordem deve ser maior ou igual a 0').default(0),
});

type TrainingTypeFormData = z.infer<typeof trainingTypeSchema>;

const TrainingTypesPage: React.FC = () => {
  const [trainingTypes, setTrainingTypes] = useState<TrainingTypeConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingType, setEditingType] = useState<TrainingTypeConfig | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingType, setDeletingType] = useState<TrainingTypeConfig | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TrainingTypeFormData>({
    resolver: zodResolver(trainingTypeSchema),
    defaultValues: {
      display_order: 0,
    },
  });

  const fetchTrainingTypes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await trainingTypeService.getAll();
      setTrainingTypes(data || []);
    } catch (err: any) {
      console.error('Erro ao carregar tipos de treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao carregar tipos de treinamento';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrainingTypes();
  }, []);

  const handleOpenModal = (type?: TrainingTypeConfig) => {
    if (type) {
      setEditingType(type);
      reset({
        code: type.code,
        name: type.name,
        description: type.description || '',
        display_order: type.display_order,
      });
    } else {
      setEditingType(null);
      reset({ code: '', name: '', description: '', display_order: 0 });
    }
    setIsModalOpen(true);
  };

  const onSubmit = async (data: TrainingTypeFormData) => {
    try {
      setError(null);
      if (editingType) {
        await trainingTypeService.update(editingType.id, {
          name: data.name,
          description: data.description || undefined,
          display_order: data.display_order,
        });
      } else {
        await trainingTypeService.create({
          code: data.code,
          name: data.name,
          description: data.description || undefined,
          display_order: data.display_order,
        });
      }
      setIsModalOpen(false);
      fetchTrainingTypes();
    } catch (err: any) {
      console.error('Erro ao salvar tipo de treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao salvar tipo de treinamento';
      setError(message);
    }
  };

  const handleDeleteClick = (type: TrainingTypeConfig) => {
    setDeletingType(type);
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingType) return;

    try {
      setIsDeleting(true);
      setError(null);
      await trainingTypeService.delete(deletingType.id);
      setDeleteModalOpen(false);
      setDeletingType(null);
      await fetchTrainingTypes();
    } catch (err: any) {
      console.error('Erro ao excluir tipo de treinamento:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao excluir tipo de treinamento';
      setError(message);
      setDeleteModalOpen(false);
      setDeletingType(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggleActive = async (type: TrainingTypeConfig) => {
    try {
      setError(null);
      await trainingTypeService.update(type.id, { is_active: !type.is_active });
      await fetchTrainingTypes();
    } catch (err: any) {
      console.error('Erro ao atualizar status:', err);
      const message = err?.response?.data?.detail || err?.message || 'Erro ao atualizar status';
      setError(message);
    }
  };

  const columns = [
    { key: 'display_order', header: 'Ordem' },
    { key: 'code', header: 'Código' },
    { key: 'name', header: 'Nome' },
    { key: 'description', header: 'Descrição' },
    {
      key: 'is_active',
      header: 'Status',
      render: (item: TrainingTypeConfig) => (
        <Badge variant={item.is_active ? 'success' : 'danger'}>{item.is_active ? 'Ativo' : 'Inativo'}</Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (item: TrainingTypeConfig) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => handleOpenModal(item)}>
            Editar
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleToggleActive(item)}
            className={item.is_active ? 'text-yellow-600 hover:text-yellow-700' : 'text-green-600 hover:text-green-700'}
          >
            {item.is_active ? 'Desativar' : 'Ativar'}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-red-600 hover:text-red-700"
            onClick={() => handleDeleteClick(item)}
          >
            Excluir
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
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Tipos de Treinamento</h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Gerencie os tipos de treinamento disponíveis no sistema
          </p>
        </div>
        <div className="flex-shrink-0">
          <Button onClick={() => handleOpenModal()}>Novo Tipo</Button>
        </div>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card padding="none">
        <Table
          data={trainingTypes}
          columns={columns}
          keyExtractor={(item) => item.id}
          emptyMessage="Nenhum tipo de treinamento cadastrado"
        />
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingType ? 'Editar Tipo de Treinamento' : 'Novo Tipo de Treinamento'}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Código"
            placeholder="Ex: senai, external, empresa"
            error={errors.code?.message}
            disabled={!!editingType}
            {...register('code')}
            helperText={editingType ? 'O código não pode ser alterado' : 'Letras minúsculas, números e underscores'}
          />
          <Input
            label="Nome"
            placeholder="Ex: SENAI, FORA, Empresa"
            error={errors.name?.message}
            {...register('name')}
          />
          <Input
            label="Descrição"
            placeholder="Descrição do tipo de treinamento"
            error={errors.description?.message}
            {...register('description')}
          />
          <Input
            label="Ordem de Exibição"
            type="number"
            min="0"
            error={errors.display_order?.message}
            {...register('display_order')}
            helperText="Menor número aparece primeiro na lista"
          />
          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              {editingType ? 'Salvar' : 'Criar'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal de confirmação de exclusão */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setDeletingType(null);
        }}
        title="Confirmar Exclusão"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Tem certeza que deseja excluir o tipo de treinamento{' '}
            <strong className="text-gray-900 dark:text-gray-100">{deletingType?.name}</strong>?
          </p>
          <p className="text-sm text-red-600 dark:text-red-400">Esta ação não pode ser desfeita.</p>
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setDeleteModalOpen(false);
                setDeletingType(null);
              }}
            >
              Cancelar
            </Button>
            <Button type="button" variant="danger" isLoading={isDeleting} onClick={handleConfirmDelete}>
              Excluir
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TrainingTypesPage;

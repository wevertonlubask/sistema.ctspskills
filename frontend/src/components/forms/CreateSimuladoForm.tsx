import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input, Select } from '../ui';

const simuladoSchema = z.object({
  name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  description: z.string().optional(),
  modality_id: z.string().min(1, 'Selecione uma modalidade'),
  exam_date: z.string().min(1, 'Data é obrigatória'),
});

type SimuladoFormData = z.infer<typeof simuladoSchema>;

interface CreateSimuladoFormProps {
  onSubmit: (data: SimuladoFormData) => void;
  onCancel: () => void;
}

const modalities = [
  { value: 'sold', label: 'Soldagem' },
  { value: 'usin', label: 'Tornearia CNC' },
  { value: 'cad', label: 'Desenho Mecânico CAD' },
  { value: 'elet', label: 'Instalações Elétricas' },
  { value: 'meca', label: 'Mecatrônica' },
];

export const CreateSimuladoForm: React.FC<CreateSimuladoFormProps> = ({
  onSubmit,
  onCancel,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SimuladoFormData>({
    resolver: zodResolver(simuladoSchema),
    defaultValues: {
      exam_date: new Date().toISOString().split('T')[0],
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input
        label="Nome do Simulado"
        placeholder="Ex: Simulado Regional 2024"
        error={errors.name?.message}
        {...register('name')}
      />

      <Input
        label="Descrição"
        placeholder="Descrição opcional do simulado"
        error={errors.description?.message}
        {...register('description')}
      />

      <Select
        label="Modalidade"
        placeholder="Selecione a modalidade"
        error={errors.modality_id?.message}
        options={modalities}
        {...register('modality_id')}
      />

      <Input
        label="Data do Simulado"
        type="date"
        error={errors.exam_date?.message}
        {...register('exam_date')}
      />

      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          Criar Simulado
        </Button>
      </div>
    </form>
  );
};

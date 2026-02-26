import React, { useState, useEffect } from 'react';
import { Modal, Button, Input, Alert, Spinner } from '../ui';
import { goalService } from '../../services';
import type { Goal, Competitor, Modality } from '../../types';

interface GoalConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  competitor: Competitor | null;
  modality: Modality | null;
  onSaved?: () => void;
}

interface GoalForm {
  trainingHoursTarget: number;
  trainingHoursDeadline: string;
  averageScoreTarget: number;
  averageScoreDeadline: string;
}

export const GoalConfigModal: React.FC<GoalConfigModalProps> = ({
  isOpen,
  onClose,
  competitor,
  modality,
  onSaved,
}) => {
  const [form, setForm] = useState<GoalForm>({
    trainingHoursTarget: 120,
    trainingHoursDeadline: '',
    averageScoreTarget: 80,
    averageScoreDeadline: '',
  });
  const [existingGoals, setExistingGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && competitor) {
      fetchExistingGoals();
    }
  }, [isOpen, competitor]);

  const fetchExistingGoals = async () => {
    if (!competitor) return;

    setIsLoading(true);
    try {
      const response = await goalService.getAll({
        competitor_id: competitor.id,
        modality_id: modality?.id,
      });
      setExistingGoals(response.goals || []);

      // Pre-fill form with existing goals
      const trainingGoal = response.goals?.find(g => g.title.toLowerCase().includes('treinamento') || g.unit === 'hours');
      const averageGoal = response.goals?.find(g => g.title.toLowerCase().includes('média') || g.unit === 'percent');

      if (trainingGoal) {
        setForm(prev => ({
          ...prev,
          trainingHoursTarget: trainingGoal.target_value,
          trainingHoursDeadline: trainingGoal.due_date || '',
        }));
      }
      if (averageGoal) {
        setForm(prev => ({
          ...prev,
          averageScoreTarget: averageGoal.target_value,
          averageScoreDeadline: averageGoal.due_date || '',
        }));
      }
    } catch (err: any) {
      console.error('Error fetching goals:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!competitor) return;

    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // Create or update training hours goal
      if (form.trainingHoursTarget > 0) {
        await goalService.create({
          title: `Meta de Horas de Treinamento${modality ? ` - ${modality.name}` : ''}`,
          description: `Meta de ${form.trainingHoursTarget} horas de treinamento por mês`,
          competitor_id: competitor.id,
          target_value: form.trainingHoursTarget,
          unit: 'hours',
          priority: 'high',
          due_date: form.trainingHoursDeadline || undefined,
          modality_id: modality?.id,
        });
      }

      // Create or update average score goal
      if (form.averageScoreTarget > 0) {
        await goalService.create({
          title: `Meta de Média${modality ? ` - ${modality.name}` : ''}`,
          description: `Meta de média ${form.averageScoreTarget} nos simulados`,
          competitor_id: competitor.id,
          target_value: form.averageScoreTarget,
          unit: 'percent',
          priority: 'high',
          due_date: form.averageScoreDeadline || undefined,
          modality_id: modality?.id,
        });
      }

      setSuccess('Metas configuradas com sucesso!');
      onSaved?.();

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      console.error('Error saving goals:', err);
      setError(err?.response?.data?.detail || 'Erro ao salvar metas');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Configurar Metas${competitor ? ` - ${competitor.full_name}` : ''}`}
      size="lg"
    >
      {isLoading ? (
        <div className="flex justify-center items-center py-8">
          <Spinner size="lg" />
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert type="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert type="success" onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          )}

          {modality && (
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                <span className="font-medium">Modalidade:</span> {modality.name} ({modality.code})
              </p>
            </div>
          )}

          {/* Training Hours Target */}
          <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Meta de Horas de Treinamento (Mensal)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Horas por Mês
                </label>
                <Input
                  type="number"
                  value={form.trainingHoursTarget}
                  onChange={(e) => setForm({ ...form, trainingHoursTarget: parseInt(e.target.value) || 0 })}
                  min={0}
                  max={500}
                  placeholder="Ex: 120"
                />
                <p className="text-xs text-gray-500 mt-1">Recomendado: 80-160 horas/mês</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Prazo (opcional)
                </label>
                <Input
                  type="date"
                  value={form.trainingHoursDeadline}
                  onChange={(e) => setForm({ ...form, trainingHoursDeadline: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Average Score Target */}
          <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Meta de Média nos Simulados
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Média Alvo (0-100)
                </label>
                <Input
                  type="number"
                  value={form.averageScoreTarget}
                  onChange={(e) => setForm({ ...form, averageScoreTarget: parseInt(e.target.value) || 0 })}
                  min={0}
                  max={100}
                  placeholder="Ex: 80"
                />
                <p className="text-xs text-gray-500 mt-1">Recomendado: 70-90</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Prazo (opcional)
                </label>
                <Input
                  type="date"
                  value={form.averageScoreDeadline}
                  onChange={(e) => setForm({ ...form, averageScoreDeadline: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Existing Goals Info */}
          {existingGoals.length > 0 && (
            <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                <span className="font-medium">Atenção:</span> Este competidor já possui {existingGoals.length} meta(s) definida(s).
                Ao salvar, novas metas serão criadas.
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-600">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSaving}>
              Salvar Metas
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
};

export default GoalConfigModal;

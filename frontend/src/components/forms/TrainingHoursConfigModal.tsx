import React, { useState, useEffect } from 'react';
import { Modal, Button, Input, Alert } from '../ui';
import { setStoredTrainingHoursMeta } from './MetaConfigModal';

interface TrainingHoursConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentMeta: number;
  onSave: (meta: number) => void;
}

export const TrainingHoursConfigModal: React.FC<TrainingHoursConfigModalProps> = ({
  isOpen,
  onClose,
  currentMeta,
  onSave,
}) => {
  const [meta, setMeta] = useState(currentMeta);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    setMeta(currentMeta);
  }, [currentMeta]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStoredTrainingHoursMeta(meta);
    onSave(meta);
    setSuccess(true);
    setTimeout(() => {
      setSuccess(false);
      onClose();
    }, 1000);
  };

  const dailyTarget = Math.round((meta / 22) * 10) / 10;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Meta de Horas de Treinamento"
      size="sm"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {success && (
          <Alert type="success">
            Meta salva com sucesso!
          </Alert>
        )}

        <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
          <p className="text-sm text-amber-700 dark:text-amber-300">
            Defina a meta mensal de horas de treinamento. O ideal para competidores
            WorldSkills é de 120 horas por mês (~5.5h/dia útil).
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Meta Mensal (horas)
          </label>
          <Input
            type="number"
            value={meta}
            onChange={(e) => setMeta(parseFloat(e.target.value) || 0)}
            min={0}
            max={300}
            step={5}
            placeholder="Ex: 120"
          />
          <p className="text-xs text-gray-500 mt-1">
            Recomendado: 100-160 horas/mês
          </p>
        </div>

        {/* Visual preview */}
        <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Equivalente a:</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">{meta}h</p>
              <p className="text-xs text-gray-500">por mês</p>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">{dailyTarget}h</p>
              <p className="text-xs text-gray-500">por dia útil</p>
            </div>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>0h</span>
              <span>160h</span>
            </div>
            <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((meta / 160) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit">
            Salvar Meta
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default TrainingHoursConfigModal;

import React, { useState, useEffect } from 'react';
import { Modal, Button, Input, Alert } from '../ui';

interface MetaConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentMeta: number;
  onSave: (meta: number) => void;
}

const META_STORAGE_KEY = 'spskills_meta_global';
const TRAINING_HOURS_META_KEY = 'spskills_training_hours_meta';

// Helper functions to persist meta
export const getStoredMeta = (): number => {
  const stored = localStorage.getItem(META_STORAGE_KEY);
  return stored ? parseFloat(stored) : 80; // Default meta is 80
};

export const setStoredMeta = (meta: number): void => {
  localStorage.setItem(META_STORAGE_KEY, meta.toString());
};

// Helper functions for training hours meta (monthly target)
export const getStoredTrainingHoursMeta = (): number => {
  const stored = localStorage.getItem(TRAINING_HOURS_META_KEY);
  return stored ? parseFloat(stored) : 120; // Default is 120h/month
};

export const setStoredTrainingHoursMeta = (hours: number): void => {
  localStorage.setItem(TRAINING_HOURS_META_KEY, hours.toString());
};

// Calculate daily target from monthly
export const getDailyTrainingTarget = (): number => {
  const monthlyTarget = getStoredTrainingHoursMeta();
  return Math.round((monthlyTarget / 22) * 10) / 10; // ~22 working days per month
};

export const MetaConfigModal: React.FC<MetaConfigModalProps> = ({
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
    setStoredMeta(meta);
    onSave(meta);
    setSuccess(true);
    setTimeout(() => {
      setSuccess(false);
      onClose();
    }, 1000);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Configurar Meta Global"
      size="sm"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {success && (
          <Alert type="success">
            Meta salva com sucesso!
          </Alert>
        )}

        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Defina a meta global de nota média que será exibida no dashboard.
            Essa meta serve como referência para todos os competidores.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Meta de Nota Média (0-100)
          </label>
          <Input
            type="number"
            value={meta}
            onChange={(e) => setMeta(parseFloat(e.target.value) || 0)}
            min={0}
            max={100}
            step={0.1}
            placeholder="Ex: 80"
          />
          <p className="text-xs text-gray-500 mt-1">
            Recomendado: 70-90 pontos
          </p>
        </div>

        {/* Visual preview */}
        <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Visualização:</p>
          <div className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Meta:</span>
            <span className="text-2xl font-bold text-green-600 dark:text-green-400">{meta}</span>
          </div>
          <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all duration-300"
              style={{ width: `${meta}%` }}
            />
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

export default MetaConfigModal;

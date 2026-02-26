export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  EVALUATOR: 'evaluator',
  COMPETITOR: 'competitor',
} as const;

export const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Administrador',
  evaluator: 'Avaliador',
  competitor: 'Competidor',
};

export const ASSESSMENT_TYPES = [
  { value: 'simulado', label: 'Simulado' },
  { value: 'prova', label: 'Prova Teórica' },
  { value: 'pratica', label: 'Avaliação Prática' },
  { value: 'modulo', label: 'Avaliação de Módulo' },
] as const;

export const STATUS_COLORS = {
  active: 'success',
  inactive: 'danger',
  pending: 'warning',
  completed: 'success',
  in_progress: 'warning',
  scheduled: 'info',
  cancelled: 'danger',
} as const;

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
} as const;

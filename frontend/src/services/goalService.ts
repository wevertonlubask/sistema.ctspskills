import api from './api';
import type { Goal, GoalStatus, GoalPriority } from '@/types';

export interface CreateGoalRequest {
  title: string;
  competitor_id: string;
  description?: string;
  target_value?: number;
  unit?: string;
  priority?: GoalPriority;
  start_date?: string;
  due_date?: string;
  modality_id?: string;
  competence_id?: string;
  milestones?: Array<{
    title: string;
    target_value: number;
    due_date?: string;
  }>;
}

export interface UpdateGoalProgressRequest {
  current_value?: number;
  milestone_id?: string;
  milestone_value?: number;
}

export interface GoalListResponse {
  goals: Goal[];
  total: number;
  overdue_count: number;
}

export const goalService = {
  async getAll(params?: {
    competitor_id: string;
    status?: GoalStatus;
    modality_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<GoalListResponse> {
    const response = await api.get<GoalListResponse>('/extras/goals', { params });
    return response.data;
  },

  async create(data: CreateGoalRequest): Promise<Goal> {
    const response = await api.post<Goal>('/extras/goals', data);
    return response.data;
  },

  async updateProgress(goalId: string, data: UpdateGoalProgressRequest): Promise<Goal> {
    const response = await api.put<Goal>(`/extras/goals/${goalId}/progress`, data);
    return response.data;
  },

  async getAlerts(daysThreshold?: number): Promise<Goal[]> {
    const response = await api.get<Goal[]>('/extras/goals/alerts', {
      params: { days_threshold: daysThreshold },
    });
    return response.data;
  },
};

import api from './api';
import type { TrainingSession, TrainingStatistics, TrainingStatus, TrainingType } from '@/types';

export interface CreateTrainingRequest {
  modality_id: string;
  training_date: string;
  hours: number;
  training_type: TrainingType;
  location?: string;
  description?: string;
}

export interface UpdateTrainingRequest {
  training_date?: string;
  hours?: number;
  training_type?: TrainingType;
  location?: string;
  description?: string;
}

export interface TrainingListParams {
  competitor_id?: string;
  modality_id?: string;
  status?: TrainingStatus;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}

export interface ValidateTrainingRequest {
  approved: boolean;
  rejection_reason?: string;
}

export interface TrainingListResponse {
  trainings: TrainingSession[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export const trainingService = {
  async getAll(params?: TrainingListParams): Promise<TrainingListResponse> {
    const response = await api.get<TrainingListResponse>('/trainings', { params });
    return response.data;
  },

  async getById(id: string): Promise<TrainingSession> {
    const response = await api.get<TrainingSession>(`/trainings/${id}`);
    return response.data;
  },

  async create(data: CreateTrainingRequest): Promise<TrainingSession> {
    const response = await api.post<TrainingSession>('/trainings', data);
    return response.data;
  },

  async update(id: string, data: UpdateTrainingRequest): Promise<TrainingSession> {
    const response = await api.put<TrainingSession>(`/trainings/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/trainings/${id}`);
  },

  async validate(id: string, data: ValidateTrainingRequest): Promise<TrainingSession> {
    const response = await api.put<TrainingSession>(`/trainings/${id}/validate`, data);
    return response.data;
  },

  async getStatistics(competitorId: string, modalityId?: string): Promise<TrainingStatistics> {
    const response = await api.get<TrainingStatistics>(`/trainings/statistics`, {
      params: { competitor_id: competitorId, modality_id: modalityId },
    });
    return response.data;
  },

  async getPendingCount(modalityId?: string): Promise<number> {
    const response = await api.get<{ count: number }>('/trainings/pending/count', {
      params: { modality_id: modalityId },
    });
    return response.data.count;
  },
};

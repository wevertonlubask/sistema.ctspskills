import api from './api';
import type { TrainingTypeConfig } from '@/types';

export interface CreateTrainingTypeRequest {
  code: string;
  name: string;
  description?: string;
  display_order?: number;
}

export interface UpdateTrainingTypeRequest {
  name?: string;
  description?: string;
  display_order?: number;
  is_active?: boolean;
}

export interface TrainingTypeListResponse {
  items: TrainingTypeConfig[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export const trainingTypeService = {
  async getAll(params?: { skip?: number; limit?: number; active_only?: boolean }): Promise<TrainingTypeConfig[]> {
    const response = await api.get<TrainingTypeListResponse>('/training-types', { params });
    return response.data.items;
  },

  async getById(id: string): Promise<TrainingTypeConfig> {
    const response = await api.get<TrainingTypeConfig>(`/training-types/${id}`);
    return response.data;
  },

  async create(data: CreateTrainingTypeRequest): Promise<TrainingTypeConfig> {
    const response = await api.post<TrainingTypeConfig>('/training-types', data);
    return response.data;
  },

  async update(id: string, data: UpdateTrainingTypeRequest): Promise<TrainingTypeConfig> {
    const response = await api.put<TrainingTypeConfig>(`/training-types/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/training-types/${id}`);
  },
};

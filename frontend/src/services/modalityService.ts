import api from './api';
import type { Modality, Competence } from '@/types';

export interface CreateModalityRequest {
  code: string;
  name: string;
  description?: string;
  skill_number?: string;
}

export interface UpdateModalityRequest {
  code?: string;
  name?: string;
  description?: string;
  skill_number?: string;
  is_active?: boolean;
}

export interface CreateCompetenceRequest {
  name: string;
  description?: string;
  max_score: number;
  weight?: number;
}

export interface UpdateCompetenceRequest {
  name?: string;
  description?: string;
  max_score?: number;
  weight?: number;
  is_active?: boolean;
}

export const modalityService = {
  async getAll(params?: { skip?: number; limit?: number; active_only?: boolean }): Promise<Modality[]> {
    const response = await api.get<{ modalities: Modality[]; total: number }>('/modalities', { params });
    return response.data.modalities;
  },

  async getById(id: string): Promise<Modality> {
    const response = await api.get<Modality>(`/modalities/${id}`);
    return response.data;
  },

  async create(data: CreateModalityRequest): Promise<Modality> {
    const response = await api.post<Modality>('/modalities', data);
    return response.data;
  },

  async update(id: string, data: UpdateModalityRequest): Promise<Modality> {
    const response = await api.put<Modality>(`/modalities/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/modalities/${id}`);
  },

  async search(query: string): Promise<Modality[]> {
    const response = await api.get<{ modalities: Modality[]; total: number }>('/modalities/search', {
      params: { query },
    });
    return response.data.modalities;
  },

  // Competence methods
  async getCompetences(modalityId: string): Promise<Competence[]> {
    const response = await api.get<Competence[]>(`/modalities/${modalityId}/competences`);
    return response.data;
  },

  async addCompetence(modalityId: string, data: CreateCompetenceRequest): Promise<Competence> {
    const response = await api.post<Competence>(`/modalities/${modalityId}/competences`, data);
    return response.data;
  },

  async updateCompetence(modalityId: string, competenceId: string, data: UpdateCompetenceRequest): Promise<Competence> {
    const response = await api.put<Competence>(`/modalities/${modalityId}/competences/${competenceId}`, data);
    return response.data;
  },

  async deleteCompetence(modalityId: string, competenceId: string): Promise<void> {
    await api.delete(`/modalities/${modalityId}/competences/${competenceId}`);
  },
};

import api from './api';
import type { Competitor } from '@/types';

export interface CompetitorListResponse {
  competitors: Competitor[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface CreateCompetitorRequest {
  user_id: string;
  full_name: string;
  birth_date?: string;
  document_number?: string;
  phone?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  notes?: string;
}

export interface UpdateCompetitorRequest {
  full_name?: string;
  birth_date?: string;
  document_number?: string;
  phone?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  notes?: string;
  is_active?: boolean;
}

export const competitorService = {
  async getAll(params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
    modality_id?: string;
    search?: string;
  }): Promise<CompetitorListResponse> {
    const response = await api.get<CompetitorListResponse>('/competitors', { params });
    return response.data;
  },

  async getById(id: string): Promise<Competitor> {
    const response = await api.get<Competitor>(`/competitors/${id}`);
    return response.data;
  },

  async getByModality(modalityId: string): Promise<CompetitorListResponse> {
    const response = await api.get<CompetitorListResponse>('/competitors', {
      params: { modality_id: modalityId, limit: 1000 },
    });
    return response.data;
  },

  async create(data: CreateCompetitorRequest): Promise<Competitor> {
    const response = await api.post<Competitor>('/competitors', data);
    return response.data;
  },

  async update(id: string, data: UpdateCompetitorRequest): Promise<Competitor> {
    const response = await api.put<Competitor>(`/competitors/${id}`, data);
    return response.data;
  },
};

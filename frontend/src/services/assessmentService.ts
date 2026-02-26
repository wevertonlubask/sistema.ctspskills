import api from './api';
import type { Exam, Grade, GradeStatistics, AssessmentType } from '@/types';

export interface CreateExamRequest {
  name: string;
  description?: string;
  modality_id: string;
  assessment_type: AssessmentType;
  exam_date: string;
  competence_ids?: string[];
}

export interface UpdateExamRequest {
  name?: string;
  description?: string;
  modality_id?: string;
  assessment_type?: AssessmentType;
  exam_date?: string;
  competence_ids?: string[];
  is_active?: boolean;
}

export interface CreateGradeRequest {
  exam_id: string;
  competitor_id: string;
  competence_id: string;
  score: number;
  notes?: string;
}

export interface UpdateGradeRequest {
  score?: number;
  notes?: string;
}

export interface GradeAuditLog {
  id: string;
  grade_id: string;
  action: string;
  old_score?: number;
  new_score?: number;
  changed_by: string;
  changed_at: string;
}

export const examService = {
  async getAll(params?: { modality_id?: string; active_only?: boolean; skip?: number; limit?: number }): Promise<{
    exams: Exam[];
    total: number;
  }> {
    const response = await api.get<{ exams: Exam[]; total: number }>('/exams', { params });
    return response.data;
  },

  async getById(id: string): Promise<Exam> {
    const response = await api.get<Exam>(`/exams/${id}`);
    return response.data;
  },

  async create(data: CreateExamRequest): Promise<Exam> {
    const response = await api.post<Exam>('/exams', data);
    return response.data;
  },

  async update(id: string, data: UpdateExamRequest): Promise<Exam> {
    const response = await api.put<Exam>(`/exams/${id}`, data);
    return response.data;
  },

  async deactivate(id: string): Promise<void> {
    await api.patch(`/exams/${id}/deactivate`);
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/exams/${id}`);
  },

  async getStatistics(id: string): Promise<GradeStatistics> {
    const response = await api.get<GradeStatistics>(`/exams/${id}/statistics`);
    return response.data;
  },
};

export const gradeService = {
  async getAll(params?: {
    exam_id?: string;
    competitor_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ grades: Grade[]; total: number }> {
    const response = await api.get<{ grades: Grade[]; total: number }>('/grades', { params });
    return response.data;
  },

  async getById(id: string): Promise<Grade> {
    const response = await api.get<Grade>(`/grades/${id}`);
    return response.data;
  },

  async create(data: CreateGradeRequest): Promise<Grade> {
    const response = await api.post<Grade>('/grades', data);
    return response.data;
  },

  async update(id: string, data: UpdateGradeRequest): Promise<Grade> {
    const response = await api.put<Grade>(`/grades/${id}`, data);
    return response.data;
  },

  async getHistory(id: string): Promise<GradeAuditLog[]> {
    const response = await api.get<{ history: GradeAuditLog[] }>(`/grades/${id}/history`);
    return response.data.history;
  },

  async getCompetitorAverage(competitorId: string, modalityId?: string): Promise<number> {
    const response = await api.get<{ average: number }>(`/competitors/${competitorId}/average`, {
      params: { modality_id: modalityId },
    });
    return response.data.average;
  },
};

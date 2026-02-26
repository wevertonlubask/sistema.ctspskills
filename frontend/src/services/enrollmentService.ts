import api from './api';
import type { Enrollment, EnrollmentDetail, EnrollmentStatus } from '@/types';

export interface EnrollmentListResponse {
  enrollments: EnrollmentDetail[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface EnrollCompetitorRequest {
  competitor_id: string;
  evaluator_id?: string;
  notes?: string;
}

export interface UpdateEnrollmentRequest {
  evaluator_id?: string;
  status?: EnrollmentStatus;
  notes?: string;
}

export const enrollmentService = {
  /**
   * Get enrollments for a specific modality
   */
  async getByModality(
    modalityId: string,
    params?: { skip?: number; limit?: number; status?: EnrollmentStatus }
  ): Promise<EnrollmentListResponse> {
    const response = await api.get<EnrollmentListResponse>(
      `/modalities/${modalityId}/enrollments`,
      { params }
    );
    return response.data;
  },

  /**
   * Get enrollments for a specific competitor
   */
  async getByCompetitor(competitorId: string): Promise<EnrollmentListResponse> {
    const response = await api.get<EnrollmentListResponse>(
      `/competitors/${competitorId}/enrollments`
    );
    return response.data;
  },

  /**
   * Enroll a competitor in a modality
   */
  async enrollCompetitor(
    modalityId: string,
    data: EnrollCompetitorRequest
  ): Promise<Enrollment> {
    const response = await api.post<Enrollment>(
      `/modalities/${modalityId}/competitors`,
      data
    );
    return response.data;
  },

  /**
   * Update an enrollment (assign evaluator, change status)
   */
  async update(
    modalityId: string,
    enrollmentId: string,
    data: UpdateEnrollmentRequest
  ): Promise<Enrollment> {
    const response = await api.put<Enrollment>(
      `/modalities/${modalityId}/enrollments/${enrollmentId}`,
      data
    );
    return response.data;
  },

  /**
   * Remove an enrollment (unenroll competitor from modality)
   */
  async delete(modalityId: string, enrollmentId: string): Promise<void> {
    await api.delete(`/modalities/${modalityId}/enrollments/${enrollmentId}`);
  },

  /**
   * Get modalities assigned to the current evaluator
   */
  async getMyModalities(): Promise<any[]> {
    const response = await api.get<any[]>('/users/me/modalities');
    return response.data;
  },

  /**
   * Get all evaluators (for assignment dropdown)
   */
  async getEvaluators(): Promise<any> {
    const response = await api.get<any>('/users/evaluators');
    return response.data;
  },

  /**
   * Get modalities assigned to an evaluator
   */
  async getEvaluatorModalities(evaluatorId: string): Promise<any[]> {
    const response = await api.get<any[]>(`/users/${evaluatorId}/modalities`);
    return response.data;
  },

  /**
   * Assign a modality to an evaluator
   */
  async assignModalityToEvaluator(
    evaluatorId: string,
    modalityId: string
  ): Promise<any> {
    const response = await api.post<any>(`/users/${evaluatorId}/modalities`, {
      modality_id: modalityId,
    });
    return response.data;
  },

  /**
   * Remove a modality from an evaluator
   */
  async removeModalityFromEvaluator(
    evaluatorId: string,
    modalityId: string
  ): Promise<void> {
    await api.delete(`/users/${evaluatorId}/modalities/${modalityId}`);
  },
};

import api from './api';
import type { CompetenceEvolutionData } from '@/types';

export interface RankingEntry {
  position: number;
  competitor_id: string;
  competitor_name: string;
  score: number;
  position_change: number | null;
}

export interface RankingResponse {
  modality_id: string;
  modality_name: string;
  entries: RankingEntry[];
  generated_at: string;
  total_competitors: number;
}

export const analyticsService = {
  async getRanking(modalityId: string): Promise<RankingResponse> {
    const response = await api.get(`/analytics/ranking/${modalityId}`);
    return response.data;
  },

  async getCompetenceEvolution(
    competitorId: string,
    competenceId: string,
    modalityId?: string,
  ): Promise<CompetenceEvolutionData> {
    const params = modalityId ? { modality_id: modalityId } : {};
    const response = await api.get(
      `/analytics/competence-evolution/${competitorId}/${competenceId}`,
      { params },
    );
    return response.data;
  },

  async getTotalEvolution(
    competitorId: string,
    modalityId?: string,
  ): Promise<CompetenceEvolutionData> {
    const params = modalityId ? { modality_id: modalityId } : {};
    const response = await api.get(
      `/analytics/total-evolution/${competitorId}`,
      { params },
    );
    return response.data;
  },
};

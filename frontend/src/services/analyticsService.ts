import api from './api';
import type { CompetenceEvolutionData } from '@/types';

export const analyticsService = {
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

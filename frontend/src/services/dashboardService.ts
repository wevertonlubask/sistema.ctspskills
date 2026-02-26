import type { CompetitorDashboardStats, EvaluatorDashboardStats, Grade, TrainingStatistics } from '@/types';
import { gradeService } from './assessmentService';
import { trainingService } from './trainingService';
import { examService } from './assessmentService';
import { enrollmentService } from './enrollmentService';
import { competitorService } from './competitorService';

export const dashboardService = {
  /**
   * Get dashboard statistics for a competitor
   */
  async getCompetitorStats(competitorId: string, modalityId?: string): Promise<CompetitorDashboardStats> {
    // Fetch grades for the competitor
    const gradesResponse = await gradeService.getAll({
      competitor_id: competitorId,
      limit: 1000,
    });

    const grades = gradesResponse.grades || [];

    // Fetch training statistics
    let trainingStats: TrainingStatistics = {
      total_hours: 0,
      senai_hours: 0,
      external_hours: 0,
      approved_hours: 0,
      pending_hours: 0,
      rejected_hours: 0,
    };

    try {
      trainingStats = await trainingService.getStatistics(competitorId, modalityId);
    } catch (err) {
      console.error('Error fetching training stats:', err);
    }

    // Calculate statistics
    const scores = grades.map(g => g.score);
    const averageScore = scores.length > 0
      ? scores.reduce((sum, s) => sum + s, 0) / scores.length
      : 0;
    const bestScore = scores.length > 0 ? Math.max(...scores) : 0;
    const worstScore = scores.length > 0 ? Math.min(...scores) : 0;

    // Build evolution data (group by exam date)
    const examGrades = new Map<string, { scores: number[]; date: string }>();

    // We need to get exam info to build the evolution chart
    for (const grade of grades) {
      if (!examGrades.has(grade.exam_id)) {
        examGrades.set(grade.exam_id, { scores: [], date: grade.created_at });
      }
      examGrades.get(grade.exam_id)!.scores.push(grade.score);
    }

    // Calculate average per exam and sort by date
    const evolutionData = Array.from(examGrades.entries())
      .map(([examId, data]) => ({
        examId,
        date: data.date,
        average: data.scores.reduce((sum, s) => sum + s, 0) / data.scores.length,
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .map((item, index) => ({
        name: `Avaliação ${index + 1}`,
        value: Math.round(item.average * 10) / 10,
        date: item.date,
      }));

    // Get recent grades (last 5)
    const recentGrades = [...grades]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);

    return {
      average_score: Math.round(averageScore * 10) / 10,
      total_grades: grades.length,
      best_score: bestScore,
      worst_score: worstScore,
      total_training_hours: trainingStats.total_hours,
      approved_training_hours: trainingStats.approved_hours,
      pending_training_hours: trainingStats.pending_hours,
      target_training_hours: undefined, // TODO: Get from goals
      target_average: undefined, // TODO: Get from goals
      evolution_data: evolutionData,
      recent_grades: recentGrades,
    };
  },

  /**
   * Get dashboard statistics for an evaluator
   */
  async getEvaluatorStats(): Promise<EvaluatorDashboardStats> {
    // Get modalities assigned to the evaluator
    const modalities = await enrollmentService.getMyModalities();

    // Get exams from these modalities
    const examsResponse = await examService.getAll({ active_only: true, limit: 500 });
    const myModalityIds = new Set(modalities.map(m => m.id));
    const myExams = examsResponse.exams.filter(e => myModalityIds.has(e.modality_id));

    // Get competitors from enrollments
    const competitorsData: EvaluatorDashboardStats['competitors_data'] = [];
    const allGrades: Grade[] = [];

    for (const modality of modalities) {
      try {
        const competitorsResponse = await competitorService.getByModality(modality.id);
        const competitors = competitorsResponse.competitors || [];

        for (const competitor of competitors) {
          // Get grades for this competitor
          const gradesResponse = await gradeService.getAll({
            competitor_id: competitor.id,
            limit: 500,
          });
          const competitorGrades = gradesResponse.grades || [];
          allGrades.push(...competitorGrades);

          // Calculate average
          const avg = competitorGrades.length > 0
            ? competitorGrades.reduce((sum, g) => sum + g.score, 0) / competitorGrades.length
            : 0;

          // Get training hours
          let trainingHours = 0;
          try {
            const stats = await trainingService.getStatistics(competitor.id);
            trainingHours = stats.approved_hours;
          } catch {
            // Ignore
          }

          // Build evolution data
          const examGrades = new Map<string, number[]>();
          for (const grade of competitorGrades) {
            if (!examGrades.has(grade.exam_id)) {
              examGrades.set(grade.exam_id, []);
            }
            examGrades.get(grade.exam_id)!.push(grade.score);
          }

          const evolution = Array.from(examGrades.entries()).map(([_examId, scores], index) => ({
            name: `Av ${index + 1}`,
            value: Math.round((scores.reduce((s, sc) => s + sc, 0) / scores.length) * 10) / 10,
          }));

          // Check if competitor already added
          if (!competitorsData.find(c => c.competitor_id === competitor.id)) {
            competitorsData.push({
              competitor_id: competitor.id,
              competitor_name: competitor.full_name,
              average: Math.round(avg * 10) / 10,
              training_hours: trainingHours,
              evolution,
            });
          }
        }
      } catch (err) {
        console.error('Error fetching competitors for modality:', modality.id, err);
      }
    }

    // Calculate overall average
    const overallAverage = allGrades.length > 0
      ? allGrades.reduce((sum, g) => sum + g.score, 0) / allGrades.length
      : 0;

    return {
      total_competitors: competitorsData.length,
      total_modalities: modalities.length,
      total_exams: myExams.length,
      overall_average: Math.round(overallAverage * 10) / 10,
      competitors_data: competitorsData,
    };
  },
};

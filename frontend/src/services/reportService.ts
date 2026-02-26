/**
 * Report service - fetches data from existing APIs and generates PDF reports.
 */
import { trainingService } from './trainingService';
import { competitorService } from './competitorService';
import { modalityService } from './modalityService';
import { examService, gradeService } from './assessmentService';
import type { TrainingSession, Competitor, Exam, Grade } from '@/types';
import {
  generateCompetitorReport,
  generateModalityReport,
  generateAttendanceReport,
  generateRankingReport,
  generateTrainingHoursReport,
  generateGeneralReport,
  type PDFHeaderOptions,
  type CompetitorReportData,
  type ModalityReportData,
  type AttendanceReportData,
  type RankingReportData,
  type TrainingHoursReportData,
  type GeneralReportData,
} from '@/utils/pdfGenerator';

interface ReportFilters {
  competitorId?: string;
  modalityId?: string;
  startDate?: string;
  endDate?: string;
  trainingType?: 'senai' | 'external' | 'all';
}

/**
 * Fetch all trainings with optional filters.
 */
async function fetchTrainings(filters: ReportFilters): Promise<TrainingSession[]> {
  const allTrainings: TrainingSession[] = [];
  let skip = 0;
  const limit = 500;
  let hasMore = true;

  while (hasMore) {
    const response = await trainingService.getAll({
      competitor_id: filters.competitorId,
      modality_id: filters.modalityId,
      start_date: filters.startDate,
      end_date: filters.endDate,
      skip,
      limit,
    });
    allTrainings.push(...response.trainings);
    hasMore = response.has_more;
    skip += limit;
  }

  // Filter by training type if needed
  if (filters.trainingType && filters.trainingType !== 'all') {
    return allTrainings.filter((t) => t.training_type === filters.trainingType);
  }

  return allTrainings;
}

/**
 * Fetch all grades for a competitor.
 */
async function fetchGradesForCompetitor(
  competitorId: string
): Promise<{ grades: Grade[]; exams: Map<string, Exam> }> {
  const gradesResponse = await gradeService.getAll({
    competitor_id: competitorId,
    limit: 1000,
  });
  const grades = gradesResponse.grades || [];

  // Fetch exam details for grade context
  const examIds = [...new Set(grades.map((g) => g.exam_id))];
  const exams = new Map<string, Exam>();
  for (const examId of examIds) {
    try {
      const exam = await examService.getById(examId);
      exams.set(examId, exam);
    } catch {
      // Skip if exam not found
    }
  }

  return { grades, exams };
}

/**
 * Fetch competences for a modality (for grade context).
 */
async function fetchCompetenceMap(modalityId: string): Promise<Map<string, string>> {
  const map = new Map<string, string>();
  try {
    const competences = await modalityService.getCompetences(modalityId);
    for (const c of competences) {
      map.set(c.id, c.name);
    }
  } catch {
    // Skip
  }
  return map;
}

/**
 * Calculate training hours stats from a list of training sessions.
 */
function calcTrainingStats(trainings: TrainingSession[]) {
  const senaiHours = trainings
    .filter((t) => t.training_type === 'senai')
    .reduce((sum, t) => sum + t.hours, 0);
  const externalHours = trainings
    .filter((t) => t.training_type !== 'senai')
    .reduce((sum, t) => sum + t.hours, 0);
  const approvedHours = trainings
    .filter((t) => t.status === 'approved' || t.status === 'validated')
    .reduce((sum, t) => sum + t.hours, 0);
  const pendingHours = trainings
    .filter((t) => t.status === 'pending')
    .reduce((sum, t) => sum + t.hours, 0);
  return {
    totalHours: senaiHours + externalHours,
    senaiHours,
    externalHours,
    approvedHours,
    pendingHours,
    sessions: trainings.length,
  };
}

export const reportService = {
  /**
   * Generate a report for a specific competitor.
   */
  async generateCompetitor(
    competitorId: string,
    modalityId: string | undefined,
    headerOptions: PDFHeaderOptions
  ): Promise<void> {
    // Fetch competitor info
    const competitor = await competitorService.getById(competitorId);

    let modalityName: string | undefined;
    if (modalityId) {
      const modality = await modalityService.getById(modalityId);
      modalityName = modality.name;
    }

    // Fetch trainings
    const trainings = await fetchTrainings({
      competitorId,
      modalityId,
    });

    // Fetch grades
    const { grades, exams } = await fetchGradesForCompetitor(competitorId);

    // Fetch competence names
    const competenceNames = new Map<string, string>();
    if (modalityId) {
      const map = await fetchCompetenceMap(modalityId);
      map.forEach((v, k) => competenceNames.set(k, v));
    } else {
      // Get competences from all modalities of the exams
      const modalityIds = [...new Set([...exams.values()].map((e) => e.modality_id))];
      for (const mid of modalityIds) {
        const map = await fetchCompetenceMap(mid);
        map.forEach((v, k) => competenceNames.set(k, v));
      }
    }

    // Calculate stats
    const tStats = calcTrainingStats(trainings);

    const scores = grades.map((g) => g.score);
    const averageGrade =
      scores.length > 0 ? scores.reduce((s, v) => s + v, 0) / scores.length : 0;

    const data: CompetitorReportData = {
      competitor_name: competitor.full_name,
      modality_name: modalityName,
      trainings: trainings.map((t) => ({
        date: t.training_date,
        hours: t.hours,
        type: t.training_type,
        location: t.location,
        status: t.status,
        description: t.description,
      })),
      totalHours: tStats.totalHours,
      senaiHours: tStats.senaiHours,
      externalHours: tStats.externalHours,
      approvedHours: tStats.approvedHours,
      pendingHours: tStats.pendingHours,
      grades: grades.map((g) => ({
        exam_name: exams.get(g.exam_id)?.name || 'N/A',
        competence_name: competenceNames.get(g.competence_id) || 'N/A',
        score: g.score,
        date: g.created_at.split('T')[0],
      })),
      averageGrade,
    };

    await generateCompetitorReport(data, headerOptions);
  },

  /**
   * Generate a report for a specific modality.
   */
  async generateModality(
    modalityId: string,
    headerOptions: PDFHeaderOptions
  ): Promise<void> {
    const modality = await modalityService.getById(modalityId);

    // Get competitors in this modality
    const competitorsResponse = await competitorService.getByModality(modalityId);
    const competitors = competitorsResponse.competitors || [];

    // Get exams for this modality
    const examsResponse = await examService.getAll({ modality_id: modalityId, limit: 500 });
    const modalityExams = examsResponse.exams || [];

    // Fetch all trainings for this modality at once
    const allTrainings = await fetchTrainings({ modalityId });

    // Group trainings by competitor
    const trainingsByCompetitor = new Map<string, TrainingSession[]>();
    for (const t of allTrainings) {
      const list = trainingsByCompetitor.get(t.competitor_id) || [];
      list.push(t);
      trainingsByCompetitor.set(t.competitor_id, list);
    }

    // Get stats for each competitor
    const competitorStats: ModalityReportData['competitors'] = [];
    let totalTrainingHours = 0;
    const allGrades: number[] = [];

    for (const comp of competitors) {
      // Training stats from actual data
      const compTrainings = trainingsByCompetitor.get(comp.id) || [];
      const tStats = calcTrainingStats(compTrainings);
      totalTrainingHours += tStats.totalHours;

      // Grades
      let avgGrade = 0;
      try {
        const gradesResponse = await gradeService.getAll({
          competitor_id: comp.id,
          limit: 500,
        });
        const scores = (gradesResponse.grades || []).map((g) => g.score);
        if (scores.length > 0) {
          avgGrade = scores.reduce((s, v) => s + v, 0) / scores.length;
          allGrades.push(...scores);
        }
      } catch {
        // Skip
      }

      competitorStats.push({
        name: comp.full_name,
        trainingHours: tStats.totalHours,
        averageGrade: avgGrade,
        status: comp.is_active !== false ? 'active' : 'inactive',
      });
    }

    const overallAvg =
      allGrades.length > 0 ? allGrades.reduce((s, v) => s + v, 0) / allGrades.length : 0;

    const data: ModalityReportData = {
      modality_name: modality.name,
      modality_code: modality.code,
      totalCompetitors: competitors.length,
      totalExams: modalityExams.length,
      averageGrade: overallAvg,
      totalTrainingHours,
      competitors: competitorStats,
    };

    await generateModalityReport(data, headerOptions);
  },

  /**
   * Generate an attendance (presence) report.
   */
  async generateAttendance(
    filters: ReportFilters,
    headerOptions: PDFHeaderOptions
  ): Promise<void> {
    let modalityName: string | undefined;
    if (filters.modalityId) {
      const modality = await modalityService.getById(filters.modalityId);
      modalityName = modality.name;
    }

    // Fetch trainings
    const trainings = await fetchTrainings(filters);

    // Group by competitor
    const byCompetitor = new Map<string, { name: string; sessions: number; hours: number }>();
    for (const t of trainings) {
      const name = t.competitor_name || t.competitor_id;
      const existing = byCompetitor.get(name) || { name, sessions: 0, hours: 0 };
      existing.sessions++;
      existing.hours += t.hours;
      byCompetitor.set(name, existing);
    }

    const data: AttendanceReportData = {
      modality_name: modalityName,
      filterType: filters.trainingType || 'all',
      startDate: filters.startDate,
      endDate: filters.endDate,
      trainings: trainings.map((t) => ({
        competitor_name: t.competitor_name || t.competitor_id,
        date: t.training_date,
        hours: t.hours,
        type: t.training_type,
        location: t.location,
        status: t.status,
      })),
      totalHours: trainings.reduce((sum, t) => sum + t.hours, 0),
      totalSessions: trainings.length,
      byCompetitor: [...byCompetitor.values()],
    };

    await generateAttendanceReport(data, headerOptions);
  },

  /**
   * Generate a ranking report for a modality.
   */
  async generateRanking(
    modalityId: string,
    headerOptions: PDFHeaderOptions
  ): Promise<void> {
    const modality = await modalityService.getById(modalityId);

    // Get competitors
    const competitorsResponse = await competitorService.getByModality(modalityId);
    const competitors = competitorsResponse.competitors || [];

    // Fetch all trainings for this modality at once
    const allTrainings = await fetchTrainings({ modalityId });
    const trainingsByCompetitor = new Map<string, TrainingSession[]>();
    for (const t of allTrainings) {
      const list = trainingsByCompetitor.get(t.competitor_id) || [];
      list.push(t);
      trainingsByCompetitor.set(t.competitor_id, list);
    }

    // Get stats
    const entries: RankingReportData['entries'] = [];

    for (const comp of competitors) {
      let avgGrade = 0;

      try {
        const gradesResponse = await gradeService.getAll({
          competitor_id: comp.id,
          limit: 500,
        });
        const scores = (gradesResponse.grades || []).map((g) => g.score);
        if (scores.length > 0) {
          avgGrade = scores.reduce((s, v) => s + v, 0) / scores.length;
        }
      } catch {
        // Skip
      }

      const compTrainings = trainingsByCompetitor.get(comp.id) || [];
      const tStats = calcTrainingStats(compTrainings);

      entries.push({
        position: 0,
        competitor_name: comp.full_name,
        averageGrade: avgGrade,
        trainingHours: tStats.totalHours,
      });
    }

    // Sort by grade (descending) and assign positions
    entries.sort((a, b) => b.averageGrade - a.averageGrade);
    entries.forEach((e, i) => (e.position = i + 1));

    const data: RankingReportData = {
      modality_name: modality.name,
      modality_code: modality.code,
      entries,
    };

    await generateRankingReport(data, headerOptions);
  },

  /**
   * Generate training hours report.
   */
  async generateTrainingHours(
    filters: ReportFilters,
    headerOptions: PDFHeaderOptions
  ): Promise<void> {
    let modalityName: string | undefined;
    if (filters.modalityId) {
      const modality = await modalityService.getById(filters.modalityId);
      modalityName = modality.name;
    }

    // Get competitors for the modality (or all)
    let competitors: Competitor[] = [];
    if (filters.modalityId) {
      const response = await competitorService.getByModality(filters.modalityId);
      competitors = response.competitors || [];
    } else {
      const response = await competitorService.getAll({ limit: 1000 });
      competitors = response.competitors || [];
    }

    const competitorData: TrainingHoursReportData['competitors'] = [];
    let totalSenai = 0;
    let totalExternal = 0;

    for (const comp of competitors) {
      const trainings = await fetchTrainings({
        competitorId: comp.id,
        modalityId: filters.modalityId,
        startDate: filters.startDate,
        endDate: filters.endDate,
      });

      const senai = trainings
        .filter((t) => t.training_type === 'senai')
        .reduce((s, t) => s + t.hours, 0);
      const ext = trainings
        .filter((t) => t.training_type !== 'senai')
        .reduce((s, t) => s + t.hours, 0);
      const approved = trainings
        .filter((t) => t.status === 'approved' || t.status === 'validated')
        .reduce((s, t) => s + t.hours, 0);
      const pending = trainings
        .filter((t) => t.status === 'pending')
        .reduce((s, t) => s + t.hours, 0);

      totalSenai += senai;
      totalExternal += ext;

      competitorData.push({
        name: comp.full_name,
        senaiHours: senai,
        externalHours: ext,
        totalHours: senai + ext,
        approvedHours: approved,
        pendingHours: pending,
        sessions: trainings.length,
      });
    }

    const data: TrainingHoursReportData = {
      modality_name: modalityName,
      startDate: filters.startDate,
      endDate: filters.endDate,
      competitors: competitorData,
      totalSenai,
      totalExternal,
      totalHours: totalSenai + totalExternal,
    };

    await generateTrainingHoursReport(data, headerOptions);
  },

  /**
   * Generate a general overview report.
   */
  async generateGeneral(headerOptions: PDFHeaderOptions): Promise<void> {
    const modalities = await modalityService.getAll({ active_only: true });
    const examsResponse = await examService.getAll({ active_only: true, limit: 1000 });

    let totalCompetitors = 0;
    const modalityData: GeneralReportData['modalities'] = [];

    for (const mod of modalities) {
      const competitorsResponse = await competitorService.getByModality(mod.id);
      const competitors = competitorsResponse.competitors || [];
      const modalityExams = (examsResponse.exams || []).filter(
        (e) => e.modality_id === mod.id
      );

      // Fetch all trainings for this modality at once
      const modTrainings = await fetchTrainings({ modalityId: mod.id });
      const tStats = calcTrainingStats(modTrainings);

      const modGrades: number[] = [];

      for (const comp of competitors) {
        try {
          const gradesResponse = await gradeService.getAll({
            competitor_id: comp.id,
            limit: 500,
          });
          modGrades.push(...(gradesResponse.grades || []).map((g) => g.score));
        } catch {
          // Skip
        }
      }

      const avgGrade =
        modGrades.length > 0 ? modGrades.reduce((s, v) => s + v, 0) / modGrades.length : 0;

      totalCompetitors += competitors.length;
      modalityData.push({
        name: mod.name,
        code: mod.code,
        competitorCount: competitors.length,
        examCount: modalityExams.length,
        averageGrade: avgGrade,
        totalTrainingHours: tStats.totalHours,
      });
    }

    const avgGrades = modalityData
      .filter((m) => m.averageGrade > 0)
      .map((m) => m.averageGrade);
    const overallAvg =
      avgGrades.length > 0 ? avgGrades.reduce((s, v) => s + v, 0) / avgGrades.length : 0;

    const data: GeneralReportData = {
      modalities: modalityData,
      totalCompetitors,
      totalModalities: modalities.length,
      totalExams: examsResponse.exams?.length || 0,
      overallAverage: overallAvg,
    };

    await generateGeneralReport(data, headerOptions);
  },
};

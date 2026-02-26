// User and Authentication Types
export type UserRole = 'super_admin' | 'evaluator' | 'competitor';
export type UserStatus = 'active' | 'inactive' | 'suspended';

export interface User {
  id: string;
  email: string;
  full_name: string;
  name?: string; // Alias for full_name
  role: UserRole;
  status: UserStatus;
  is_active?: boolean;
  must_change_password?: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
  expires_at?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_at?: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  name?: string; // Alias for full_name
  cpf?: string;
  role?: UserRole;
  must_change_password?: boolean;
}

// Modality Types
export interface Modality {
  id: string;
  code: string;
  name: string;
  description?: string;
  skill_number?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Competence {
  id: string;
  modality_id: string;
  name: string;
  description?: string;
  max_score: number;
  weight: number;
  is_active: boolean;
}

// Competitor Types
export interface Competitor {
  id: string;
  user_id: string;
  full_name: string;
  email?: string;
  birth_date?: string;
  age?: number;
  document_number?: string;
  phone?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  modality_id?: string;
  registration_number?: string;
  status?: string;
  is_active?: boolean;
  notes?: string;
  modalities?: Modality[];
  modality?: Modality;
  created_at?: string;
  updated_at?: string;
  user?: {
    id: string;
    full_name: string;
    email: string;
    role: string;
    is_active: boolean;
  };
}

// Enrollment Types
export type EnrollmentStatus = 'active' | 'inactive' | 'suspended' | 'completed';

export interface Enrollment {
  id: string;
  competitor_id: string;
  modality_id: string;
  evaluator_id?: string;
  enrolled_at: string;
  status: EnrollmentStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EnrollmentDetail {
  id: string;
  competitor_id: string;
  competitor_name: string;
  modality_id: string;
  modality_name: string;
  modality_code: string;
  evaluator_id?: string;
  evaluator_name?: string;
  enrolled_at: string;
  status: EnrollmentStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Training Types
export type TrainingType = 'senai' | 'external' | 'empresa' | 'autonomo';
export type TrainingStatus = 'pending' | 'approved' | 'rejected' | 'validated';

// Training Type Configuration (admin-managed)
export interface TrainingTypeConfig {
  id: string;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: string;
  training_session_id: string;
  file_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  evidence_type: string;
  description?: string;
  uploaded_by?: string;
  created_at: string;
  updated_at: string;
}

export interface TrainingSession {
  id: string;
  competitor_id: string;
  competitor_name?: string;
  modality_id: string;
  modality_name?: string;
  enrollment_id: string;
  training_date: string;
  hours: number;
  training_type: TrainingType;
  location?: string;
  description?: string;
  status: TrainingStatus;
  validated_by?: string;
  validated_at?: string;
  rejection_reason?: string;
  evidences: Evidence[];
  created_at: string;
  updated_at: string;
}

export interface TrainingStatistics {
  total_hours: number;
  senai_hours: number;
  external_hours: number;
  approved_hours: number;
  pending_hours: number;
  rejected_hours: number;
}

// Assessment Types
export type AssessmentType = 'simulation' | 'practical' | 'theoretical' | 'mixed';

export interface Exam {
  id: string;
  name: string;
  description?: string;
  modality_id: string;
  assessment_type: AssessmentType;
  exam_date: string;
  is_active: boolean;
  competence_ids: string[];
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Grade {
  id: string;
  exam_id: string;
  competitor_id: string;
  competence_id: string;
  score: number;
  notes?: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

export interface GradeStatistics {
  average: number;
  median: number;
  min_score: number;
  max_score: number;
  std_deviation: number;
  count: number;
  total_competitors?: number;
  overall_average?: number;
}

// Analytics Types
export interface TimeSeriesPoint {
  date: string;
  value: number;
  label?: string;
}

export interface CompetenceScore {
  competence_id: string;
  competence_name: string;
  score: number;
  max_score: number;
}

export interface RankingEntry {
  position: number;
  competitor_id: string;
  competitor_name: string;
  score: number;
  previous_position?: number;
}

// Pagination Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// Goal Types
export type GoalStatus = 'not_started' | 'in_progress' | 'completed' | 'overdue' | 'cancelled';
export type GoalPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Milestone {
  id: string;
  goal_id: string;
  title: string;
  target_value: number;
  current_value: number;
  due_date?: string;
  is_completed: boolean;
  completed_at?: string;
  progress_percentage: number;
  is_overdue: boolean;
}

export interface Goal {
  id: string;
  title: string;
  description?: string;
  competitor_id: string;
  target_value: number;
  current_value: number;
  unit: string;
  priority: GoalPriority;
  status: GoalStatus;
  start_date: string;
  due_date?: string;
  modality_id?: string;
  competence_id?: string;
  progress_percentage: number;
  is_overdue: boolean;
  days_remaining?: number;
  needs_alert: boolean;
  milestones: Milestone[];
  completed_milestones: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// Dashboard Statistics Types
export interface CompetitorDashboardStats {
  average_score: number;
  total_grades: number;
  best_score: number;
  worst_score: number;
  total_training_hours: number;
  approved_training_hours: number;
  pending_training_hours: number;
  target_training_hours?: number;
  target_average?: number;
  evolution_data: Array<{ name: string; value: number; date: string }>;
  recent_grades: Grade[];
}

export interface EvaluatorDashboardStats {
  total_competitors: number;
  total_modalities: number;
  total_exams: number;
  overall_average: number;
  competitors_data: Array<{
    competitor_id: string;
    competitor_name: string;
    average: number;
    training_hours: number;
    evolution: Array<{ name: string; value: number }>;
  }>;
}

// Platform Settings Types
export interface PlatformSettings {
  id: string;
  platform_name: string;
  platform_subtitle: string | null;
  browser_title: string;
  logo_url: string | null;
  logo_collapsed_url: string | null;
  favicon_url: string | null;
  primary_color: string | null;
  created_at: string;
  updated_at: string;
}

export interface UpdatePlatformSettingsRequest {
  platform_name?: string;
  platform_subtitle?: string;
  browser_title?: string;
  primary_color?: string;
}

// API Response Types
export interface ApiError {
  detail: string;
  code?: string;
  errors?: Array<{ field: string; message: string }>;
}

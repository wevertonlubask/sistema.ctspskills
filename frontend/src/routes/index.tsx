import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '../components/layout';
import { ProtectedRoute } from './ProtectedRoute';
import { Spinner } from '../components/ui';

// Lazy load pages
const LoginPage = lazy(() => import('../pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage'));
const ChangePasswordPage = lazy(() => import('../pages/auth/ChangePasswordPage'));
const DashboardPage = lazy(() => import('../pages/dashboard/DashboardPage'));
const ModalitiesPage = lazy(() => import('../pages/admin/ModalitiesPage'));
const TrainingsPage = lazy(() => import('../pages/evaluator/TrainingsPage'));
const ExamsPage = lazy(() => import('../pages/evaluator/ExamsPage'));
const GradesPage = lazy(() => import('../pages/evaluator/GradesPage'));
const CompetitorsPage = lazy(() => import('../pages/admin/CompetitorsPage'));
const UsersPage = lazy(() => import('../pages/admin/UsersPage'));
const TrainingTypesPage = lazy(() => import('../pages/admin/TrainingTypesPage'));
const SettingsPage = lazy(() => import('../pages/admin/SettingsPage'));
const MyGradesPage = lazy(() => import('../pages/competitor/MyGradesPage'));
const ProfilePage = lazy(() => import('../pages/competitor/ProfilePage'));
const SimuladosDashboard = lazy(() => import('../pages/evaluator/SimuladosDashboard'));
const ReportsPage = lazy(() => import('../pages/evaluator/ReportsPage'));
const UnauthorizedPage = lazy(() => import('../pages/UnauthorizedPage'));

const LoadingFallback = () => (
  <div className="flex items-center justify-center h-screen">
    <Spinner size="lg" />
  </div>
);

export const AppRoutes: React.FC = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* Protected routes */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Accessible by all authenticated users */}
          <Route path="/modalities" element={<ModalitiesPage />} />
          <Route path="/trainings" element={<TrainingsPage />} />
          <Route path="/grades" element={<GradesPage />} />
          <Route path="/profile" element={<ProfilePage />} />

          {/* Evaluator and Admin only */}
          <Route
            path="/exams"
            element={
              <ProtectedRoute allowedRoles={['super_admin', 'evaluator']}>
                <ExamsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/simulados"
            element={
              <ProtectedRoute allowedRoles={['super_admin', 'evaluator']}>
                <SimuladosDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute allowedRoles={['super_admin', 'evaluator']}>
                <ReportsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/competitors"
            element={
              <ProtectedRoute allowedRoles={['super_admin', 'evaluator']}>
                <CompetitorsPage />
              </ProtectedRoute>
            }
          />

          {/* Admin only */}
          <Route
            path="/users"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <UsersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/training-types"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <TrainingTypesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <SettingsPage />
              </ProtectedRoute>
            }
          />

          {/* Competitor only */}
          <Route
            path="/my-grades"
            element={
              <ProtectedRoute allowedRoles={['competitor']}>
                <MyGradesPage />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
};

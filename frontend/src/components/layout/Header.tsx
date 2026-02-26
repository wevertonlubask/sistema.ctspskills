import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useAuthStore,
  usePlatformSettingsStore,
  selectPlatformName,
  selectPlatformSubtitle,
  selectLogoUrl,
} from '../../stores';
import { Button } from '../ui';

interface HeaderProps {
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const platformName = usePlatformSettingsStore(selectPlatformName);
  const platformSubtitle = usePlatformSettingsStore(selectPlatformSubtitle);
  const logoUrl = usePlatformSettingsStore(selectLogoUrl);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleLabels: Record<string, string> = {
    super_admin: 'Super Admin',
    evaluator: 'Avaliador',
    competitor: 'Competidor',
  };

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-50">
      <div className="h-full px-4 flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="ml-3 flex items-center min-w-0">
            {logoUrl ? (
              <img src={logoUrl} alt={platformName} className="h-10 object-contain flex-shrink-0" />
            ) : (
              <span className="text-lg font-bold text-blue-600 dark:text-blue-400 truncate">{platformName}</span>
            )}
            {platformSubtitle && (
              <span className="ml-3 text-sm text-gray-500 dark:text-gray-400 hidden md:block truncate">
                {platformSubtitle}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 md:space-x-4 flex-shrink-0">
          {user && (
            <div className="flex items-center space-x-2 md:space-x-3">
              {/* Name + role: hidden on mobile */}
              <div className="text-right hidden md:block">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{user.full_name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {roleLabels[user.role] || user.role}
                </p>
              </div>
              {/* Avatar: always visible */}
              <div className="w-9 h-9 md:w-10 md:h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-sm flex-shrink-0">
                {user.full_name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Sair
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

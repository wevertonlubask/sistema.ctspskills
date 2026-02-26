import axios from 'axios';
import api from './api';
import type { PlatformSettings, UpdatePlatformSettingsRequest } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || '/ctspskills/api/v1';
const BASE_PATH = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');

function addBasePath(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('http') || url.startsWith(BASE_PATH + '/')) return url;
  return `${BASE_PATH}${url}`;
}

function withBaseUrls(settings: PlatformSettings): PlatformSettings {
  return {
    ...settings,
    logo_url: addBasePath(settings.logo_url),
    logo_collapsed_url: addBasePath(settings.logo_collapsed_url),
    favicon_url: addBasePath(settings.favicon_url),
  };
}

export const platformSettingsService = {
  /**
   * Get platform settings (public endpoint, no auth required)
   */
  async getSettings(): Promise<PlatformSettings> {
    // Use axios directly without auth interceptor for public endpoint
    const response = await axios.get<PlatformSettings>(`${API_URL}/platform`);
    return withBaseUrls(response.data);
  },

  /**
   * Update platform settings (requires super_admin)
   */
  async updateSettings(data: UpdatePlatformSettingsRequest): Promise<PlatformSettings> {
    const response = await api.put<PlatformSettings>('/platform', data);
    return withBaseUrls(response.data);
  },

  /**
   * Upload main logo (requires super_admin)
   */
  async uploadLogo(file: File): Promise<PlatformSettings> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<PlatformSettings>('/platform/logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return withBaseUrls(response.data);
  },

  /**
   * Upload collapsed sidebar logo (requires super_admin)
   */
  async uploadLogoCollapsed(file: File): Promise<PlatformSettings> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<PlatformSettings>('/platform/logo-collapsed', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return withBaseUrls(response.data);
  },

  /**
   * Upload favicon (requires super_admin)
   */
  async uploadFavicon(file: File): Promise<PlatformSettings> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<PlatformSettings>('/platform/favicon', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return withBaseUrls(response.data);
  },
};

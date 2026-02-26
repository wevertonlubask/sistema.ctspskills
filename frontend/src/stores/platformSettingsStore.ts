import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { PlatformSettings } from '../types';
import { platformSettingsService } from '../services';

interface PlatformSettingsState {
  settings: PlatformSettings | null;
  isLoading: boolean;
  error: string | null;
  lastFetched: number | null;

  // Actions
  fetchSettings: () => Promise<void>;
  updateSettings: (data: Partial<PlatformSettings>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// Default settings for fallback
const DEFAULT_SETTINGS = {
  platform_name: 'SPSkills',
  platform_subtitle: 'Sistema de Treinamento',
  browser_title: 'SPSkills',
  logo_url: null,
  logo_collapsed_url: null,
  favicon_url: null,
  primary_color: '#3B82F6',
};

export const usePlatformSettingsStore = create<PlatformSettingsState>()(
  persist(
    (set, get) => ({
      settings: null,
      isLoading: false,
      error: null,
      lastFetched: null,

      fetchSettings: async () => {
        // Skip if recently fetched (within 5 minutes)
        const now = Date.now();
        const lastFetched = get().lastFetched;
        if (lastFetched && now - lastFetched < 5 * 60 * 1000 && get().settings) {
          return;
        }

        set({ isLoading: true, error: null });
        try {
          const settings = await platformSettingsService.getSettings();
          set({ settings, isLoading: false, lastFetched: now });
        } catch (err) {
          console.error('Failed to fetch platform settings:', err);
          set({ isLoading: false, error: 'Failed to load settings' });
        }
      },

      updateSettings: (data) => {
        set((state) => ({
          settings: state.settings ? { ...state.settings, ...data } : null,
          lastFetched: Date.now(),
        }));
      },

      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
    }),
    {
      name: 'platform-settings-storage',
      partialize: (state) => ({
        settings: state.settings,
        lastFetched: state.lastFetched,
      }),
    }
  )
);

// Selectors
export const selectPlatformName = (state: PlatformSettingsState) =>
  state.settings?.platform_name || DEFAULT_SETTINGS.platform_name;

export const selectPlatformSubtitle = (state: PlatformSettingsState) =>
  state.settings?.platform_subtitle || DEFAULT_SETTINGS.platform_subtitle;

export const selectBrowserTitle = (state: PlatformSettingsState) =>
  state.settings?.browser_title || DEFAULT_SETTINGS.browser_title;

export const selectLogoUrl = (state: PlatformSettingsState) =>
  state.settings?.logo_url || null;

export const selectLogoCollapsedUrl = (state: PlatformSettingsState) =>
  state.settings?.logo_collapsed_url || null;

export const selectFaviconUrl = (state: PlatformSettingsState) =>
  state.settings?.favicon_url || null;

export const selectPrimaryColor = (state: PlatformSettingsState) =>
  state.settings?.primary_color || DEFAULT_SETTINGS.primary_color;

export const selectSettings = (state: PlatformSettingsState) => state.settings;

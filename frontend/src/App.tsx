import React, { useEffect } from 'react';
import { AppRoutes } from './routes';
import {
  usePlatformSettingsStore,
  selectBrowserTitle,
  selectFaviconUrl,
} from './stores';

const App: React.FC = () => {
  const fetchSettings = usePlatformSettingsStore((state) => state.fetchSettings);
  const browserTitle = usePlatformSettingsStore(selectBrowserTitle);
  const faviconUrl = usePlatformSettingsStore(selectFaviconUrl);

  // Fetch platform settings on mount
  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  // Update document title
  useEffect(() => {
    document.title = browserTitle;
  }, [browserTitle]);

  // Update favicon
  useEffect(() => {
    if (faviconUrl) {
      let link = document.querySelector("link[rel*='icon']") as HTMLLinkElement;
      if (!link) {
        link = document.createElement('link');
        link.rel = 'shortcut icon';
        document.getElementsByTagName('head')[0].appendChild(link);
      }
      link.href = faviconUrl;
    }
  }, [faviconUrl]);

  return <AppRoutes />;
};

export default App;

import React, { useEffect, useState, useRef } from 'react';
import { Card, CardHeader, CardBody, Button, Input, Alert, Spinner } from '../../components/ui';
import { platformSettingsService } from '../../services';
import { usePlatformSettingsStore } from '../../stores';
import type { PlatformSettings, UpdatePlatformSettingsRequest } from '../../types';

const SettingsPage: React.FC = () => {
  const settings = usePlatformSettingsStore((state) => state.settings);
  const fetchSettings = usePlatformSettingsStore((state) => state.fetchSettings);
  const updateStoreSettings = usePlatformSettingsStore((state) => state.updateSettings);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<UpdatePlatformSettingsRequest>({
    platform_name: '',
    platform_subtitle: '',
    browser_title: '',
    primary_color: '#3B82F6',
  });

  // File refs
  const logoInputRef = useRef<HTMLInputElement>(null);
  const logoCollapsedInputRef = useRef<HTMLInputElement>(null);
  const faviconInputRef = useRef<HTMLInputElement>(null);

  // Upload states
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const [uploadingLogoCollapsed, setUploadingLogoCollapsed] = useState(false);
  const [uploadingFavicon, setUploadingFavicon] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      await fetchSettings();
    } catch (err) {
      setError('Erro ao carregar configurações');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (settings) {
      setFormData({
        platform_name: settings.platform_name || '',
        platform_subtitle: settings.platform_subtitle || '',
        browser_title: settings.browser_title || '',
        primary_color: settings.primary_color || '#3B82F6',
      });
    }
  }, [settings]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    setError(null);
    try {
      const updated = await platformSettingsService.updateSettings(formData);
      updateStoreSettings(updated);
      setSuccessMessage('Configurações salvas com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao salvar configurações');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFileUpload = async (
    file: File,
    uploadFn: (file: File) => Promise<PlatformSettings>,
    setUploading: (v: boolean) => void
  ) => {
    setUploading(true);
    setError(null);
    try {
      const updated = await uploadFn(file);
      updateStoreSettings(updated);
      setSuccessMessage('Arquivo enviado com sucesso!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao enviar arquivo');
    } finally {
      setUploading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Configurações da Plataforma
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Personalize o nome, logos e cores da plataforma
        </p>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert type="success" onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Branding Settings */}
      <Card>
        <CardHeader>Informações da Plataforma</CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Nome da Plataforma"
              name="platform_name"
              value={formData.platform_name}
              onChange={handleInputChange}
              placeholder="SPSkills"
            />
            <Input
              label="Subtítulo"
              name="platform_subtitle"
              value={formData.platform_subtitle}
              onChange={handleInputChange}
              placeholder="Sistema de Treinamento"
            />
            <Input
              label="Título do Navegador"
              name="browser_title"
              value={formData.browser_title}
              onChange={handleInputChange}
              placeholder="SPSkills - Treinamento"
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Cor Primária
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  name="primary_color"
                  value={formData.primary_color}
                  onChange={handleInputChange}
                  className="h-10 w-20 rounded border border-gray-300 dark:border-gray-600 cursor-pointer"
                />
                <Input
                  name="primary_color"
                  value={formData.primary_color}
                  onChange={handleInputChange}
                  placeholder="#3B82F6"
                  className="flex-1"
                />
              </div>
            </div>
          </div>
          <div className="mt-6 flex justify-end">
            <Button onClick={handleSaveSettings} isLoading={isSaving}>
              Salvar Alterações
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Logo Upload */}
      <Card>
        <CardHeader>Logos e Favicon</CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Main Logo */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Logo Principal
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Exibido no header e tela de login
              </p>
              <div className="h-32 w-full border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex items-center justify-center bg-gray-50 dark:bg-gray-800">
                {settings?.logo_url ? (
                  <img
                    src={settings.logo_url}
                    alt="Logo"
                    className="max-h-28 max-w-full object-contain"
                  />
                ) : (
                  <span className="text-gray-400">Nenhum logo</span>
                )}
              </div>
              <input
                ref={logoInputRef}
                type="file"
                accept="image/jpeg,image/png,image/svg+xml,image/webp"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleFileUpload(file, platformSettingsService.uploadLogo, setUploadingLogo);
                  }
                  e.target.value = '';
                }}
                className="hidden"
              />
              <Button
                variant="secondary"
                size="sm"
                onClick={() => logoInputRef.current?.click()}
                isLoading={uploadingLogo}
                className="w-full"
              >
                {uploadingLogo ? 'Enviando...' : 'Alterar Logo'}
              </Button>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                JPG, PNG, SVG ou WebP. Máx 2MB.
              </p>
            </div>

            {/* Collapsed Logo */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Logo Recolhido
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Exibido quando o menu lateral está recolhido
              </p>
              <div className="h-32 w-full border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex items-center justify-center bg-gray-50 dark:bg-gray-800">
                {settings?.logo_collapsed_url ? (
                  <img
                    src={settings.logo_collapsed_url}
                    alt="Logo Collapsed"
                    className="max-h-20 max-w-20 object-contain"
                  />
                ) : (
                  <span className="text-gray-400">Nenhum logo</span>
                )}
              </div>
              <input
                ref={logoCollapsedInputRef}
                type="file"
                accept="image/jpeg,image/png,image/svg+xml,image/webp"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleFileUpload(
                      file,
                      platformSettingsService.uploadLogoCollapsed,
                      setUploadingLogoCollapsed
                    );
                  }
                  e.target.value = '';
                }}
                className="hidden"
              />
              <Button
                variant="secondary"
                size="sm"
                onClick={() => logoCollapsedInputRef.current?.click()}
                isLoading={uploadingLogoCollapsed}
                className="w-full"
              >
                {uploadingLogoCollapsed ? 'Enviando...' : 'Alterar Logo'}
              </Button>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Ideal: quadrado, 64x64px
              </p>
            </div>

            {/* Favicon */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Favicon
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Ícone exibido na aba do navegador
              </p>
              <div className="h-32 w-full border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex items-center justify-center bg-gray-50 dark:bg-gray-800">
                {settings?.favicon_url ? (
                  <img
                    src={settings.favicon_url}
                    alt="Favicon"
                    className="max-h-16 max-w-16 object-contain"
                  />
                ) : (
                  <span className="text-gray-400">Nenhum favicon</span>
                )}
              </div>
              <input
                ref={faviconInputRef}
                type="file"
                accept="image/x-icon,image/png,image/svg+xml,image/vnd.microsoft.icon"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleFileUpload(
                      file,
                      platformSettingsService.uploadFavicon,
                      setUploadingFavicon
                    );
                  }
                  e.target.value = '';
                }}
                className="hidden"
              />
              <Button
                variant="secondary"
                size="sm"
                onClick={() => faviconInputRef.current?.click()}
                isLoading={uploadingFavicon}
                className="w-full"
              >
                {uploadingFavicon ? 'Enviando...' : 'Alterar Favicon'}
              </Button>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                ICO, PNG ou SVG. Ideal: 32x32px
              </p>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default SettingsPage;

import api from './api';
import type { AuthTokens, LoginRequest, LoginResponse, RegisterRequest, User } from '@/types';

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', data);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  async changePassword(data: ChangePasswordRequest): Promise<User> {
    const response = await api.post<User>('/auth/change-password', data);
    return response.data;
  },
};

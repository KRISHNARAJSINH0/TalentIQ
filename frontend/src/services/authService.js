/**
 * Auth Service – API calls for authentication.
 */

import axiosInstance from '../api/axiosInstance';

const authService = {
  register: (data) =>
    axiosInstance.post('/auth/register/', data),

  login: (data) =>
    axiosInstance.post('/auth/login/', data),

  logout: (refreshToken) =>
    axiosInstance.post('/auth/logout/', { refresh: refreshToken }),

  getCurrentUser: () =>
    axiosInstance.get('/auth/me/'),

  updateProfile: (data) => {
    const isFormData = data instanceof FormData;
    return axiosInstance.put('/auth/profile/', data, {
      headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {},
    });
  },

  changePassword: (data) =>
    axiosInstance.post('/auth/change-password/', data),

  refreshToken: (refresh) =>
    axiosInstance.post('/auth/token/refresh/', { refresh }),
};

export default authService;

import axiosInstance from './axiosInstance';

export const portfolioAPI = {
  getPortfolio: () => axiosInstance.get('/portfolio/'),
  generatePortfolio: () => axiosInstance.post('/portfolio/generate/'),
  updateTheme: (data) => axiosInstance.patch('/portfolio/theme/', data),
  updatePrivacy: (data) => axiosInstance.patch('/portfolio/privacy/', data),
  getAnalytics: () => axiosInstance.get('/portfolio/analytics/'),
  logActivity: (data) => axiosInstance.post('/portfolio/analytics/log/', data),
  getPublicPortfolio: (slug) => axiosInstance.get(`/portfolio/${slug}/`),
};

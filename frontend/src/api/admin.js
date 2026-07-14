import axiosInstance from './axiosInstance';

export const adminAPI = {
  /**
   * Get main dashboard metrics summary and recent logs
   */
  getDashboardSummary: () => {
    return axiosInstance.get('/admin/dashboard/');
  },

  /**
   * Get users with pagination, search, role and status filters
   */
  getUsers: (params = {}) => {
    return axiosInstance.get('/admin/users/', { params });
  },

  /**
   * Suspend a user account
   */
  suspendUser: (userId) => {
    return axiosInstance.post(`/admin/users/${userId}/suspend/`);
  },

  /**
   * Activate a suspended user account
   */
  activateUser: (userId) => {
    return axiosInstance.post(`/admin/users/${userId}/activate/`);
  },

  /**
   * Reset a user's profile and delete their resumes
   */
  resetProfile: (userId) => {
    return axiosInstance.post(`/admin/users/${userId}/reset-profile/`);
  },

  /**
   * Permanently delete a user account
   */
  deleteUser: (userId) => {
    return axiosInstance.delete(`/admin/users/${userId}/`);
  },

  /**
   * Export all system/profile data for a single user
   */
  exportUserData: (userId) => {
    return axiosInstance.get(`/admin/users/${userId}/export-data/`);
  },

  /**
   * Get timeseries growth, distributions, and skills insights
   */
  getAnalytics: () => {
    return axiosInstance.get('/admin/analytics/');
  },

  /**
   * Get raw system health statistics (CPU, memory, storage)
   */
  getSystemHealth: () => {
    return axiosInstance.get('/admin/system/');
  },

  /**
   * Get tables list for the reports tab (recent resumes, scores)
   */
  getReports: () => {
    return axiosInstance.get('/admin/reports/');
  },

  /**
   * Trigger report generation and CSV download
   */
  exportReport: (reportType) => {
    return axiosInstance.post('/admin/export/', { report_type: reportType }, { responseType: 'blob' });
  },
};

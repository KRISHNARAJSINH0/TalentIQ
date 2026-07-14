import axiosInstance from './axiosInstance';

export const notificationsAPI = {
  /**
   * Get user notifications with paging and status/type filter options
   */
  getNotifications: (params = {}) => {
    return axiosInstance.get('/notifications/', { params });
  },

  /**
   * Mark single ID, array of IDs, or all notifications as read
   */
  markRead: (data = {}) => {
    return axiosInstance.post('/notifications/read/', data);
  },

  /**
   * Delete single notification ID, array of IDs, or all notifications
   */
  deleteNotification: (idOrData) => {
    if (typeof idOrData === 'object' && idOrData !== null) {
      return axiosInstance.post('/notifications/delete/', idOrData);
    }
    if (idOrData) {
      return axiosInstance.delete(`/notifications/${idOrData}/`);
    }
    return axiosInstance.delete('/notifications/delete/');
  },

  /**
   * Get user notification delivery preferences
   */
  getPreferences: () => {
    return axiosInstance.get('/notifications/preferences/');
  },

  /**
   * Update notification channel/topic preferences
   */
  updatePreferences: (data) => {
    return axiosInstance.post('/notifications/preferences/', data);
  },

  /**
   * Get history of delivered notifications log
   */
  getHistory: (params = {}) => {
    return axiosInstance.get('/notifications/history/', { params });
  },

  /**
   * Get count of current unread notifications
   */
  getUnreadCount: () => {
    return axiosInstance.get('/notifications/unread/');
  },

  /**
   * Get active system announcements
   */
  getAnnouncements: () => {
    return axiosInstance.get('/notifications/announcements/');
  },
};

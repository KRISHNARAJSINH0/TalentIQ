import axiosInstance from './axiosInstance';

export const timelineAPI = {
  /**
   * Get paginated timeline events with optional filter parameters (event_type, search, page)
   */
  getTimelineEvents: (params = {}) => {
    return axiosInstance.get('/timeline/', { params });
  },

  /**
   * Manually log a timeline event
   */
  createTimelineEvent: (data) => {
    return axiosInstance.post('/timeline/event/', data);
  },

  /**
   * Fetch time-series growth and completion analytics
   */
  getTimelineHistory: () => {
    return axiosInstance.get('/timeline/history/');
  },

  /**
   * Fetch all resume version snapshots
   */
  getTimelineVersions: () => {
    return axiosInstance.get('/timeline/versions/');
  },

  /**
   * Diffs two or three selected version snapshots
   */
  compareTimelineVersions: (v1, v2, v3 = null) => {
    const params = { v1, v2 };
    if (v3) {
      params.v3 = v3;
    }
    return axiosInstance.get('/timeline/compare/', { params });
  },
};

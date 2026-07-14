import axiosInstance from './axiosInstance';

export const jdAPI = {
  uploadJD: (content, sourceType = 'text') =>
    axiosInstance.post('/jd/upload/', { content, source_type: sourceType }),

  analyzeJD: (content, jdId = null) => {
    const payload = {};
    if (content) payload.content = content;
    if (jdId) payload.jd_id = jdId;
    return axiosInstance.post('/jd/analyze/', payload);
  },

  getHistory: () => axiosInstance.get('/jd/history/'),

  getReport: (id) => axiosInstance.get(`/jd/report/${id}/`),

  getGaps: (id) => axiosInstance.get(`/jd/gaps/${id}/`),

  getATS: (id) => axiosInstance.get(`/jd/ats/${id}/`),
};

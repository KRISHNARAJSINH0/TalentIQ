import axiosInstance from './axiosInstance';

export const reputationAPI = {
  calculateReputation: (resumeId) => axiosInstance.post('/ai/reputation/', { resume_id: resumeId }),
  getReputation: (resumeId) => axiosInstance.get('/ai/reputation/', { params: { resume_id: resumeId } }),
  getHistory: () => axiosInstance.get('/ai/reputation/history/'),
  getBadges: (resumeId) => axiosInstance.get('/ai/reputation/badges/', { params: { resume_id: resumeId } }),
  getBenchmark: (resumeId) => axiosInstance.get('/ai/reputation/benchmark/', { params: { resume_id: resumeId } }),
};

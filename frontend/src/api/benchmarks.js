import axiosInstance from './axiosInstance';

export const benchmarksAPI = {
  triggerBenchmark: (resumeId) => axiosInstance.post('/benchmark/', { resume_id: resumeId }),
  getLatestReport: (resumeId) => axiosInstance.get('/benchmark/report/', { params: { resume_id: resumeId } }),
  getHistory: (resumeId) => axiosInstance.get('/benchmark/history/', { params: { resume_id: resumeId } }),
  getLeaderboard: (resumeId) => axiosInstance.get('/rank/', { params: { resume_id: resumeId } }),
};

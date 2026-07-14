import axiosInstance from './axiosInstance';

export const careerAPI = {
  analyzeProfile: () => axiosInstance.post('/career/analyze/'),
  getCareerDetails: () => axiosInstance.get('/career/'),
  getRoadmap: () => axiosInstance.get('/career/roadmap/'),
  getSkills: () => axiosInstance.get('/career/skills/'),
  generateCoverLetter: (data) => axiosInstance.post('/career/cover-letter/', data),
  getCoverLetterHistory: () => axiosInstance.get('/career/history/'),
  updateProgress: (data) => axiosInstance.patch('/career/progress/', data),
};

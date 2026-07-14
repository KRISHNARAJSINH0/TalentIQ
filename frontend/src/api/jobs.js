import axiosInstance from './axiosInstance';

export const jobsAPI = {
  matchProfile: () => axiosInstance.post('/jobs/match/'),
  predictCustom: (payload) => axiosInstance.post('/jobs/predict/', { payload }),
  getRecommendations: () => axiosInstance.get('/jobs/recommendations/'),
  getMarket: () => axiosInstance.get('/jobs/market/'),
  getSalary: () => axiosInstance.get('/jobs/salary/'),
  getCompanies: () => axiosInstance.get('/jobs/companies/'),
  getSkillsGap: () => axiosInstance.get('/jobs/skills-gap/'),
};

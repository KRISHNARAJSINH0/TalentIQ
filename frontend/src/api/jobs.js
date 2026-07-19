import axiosInstance from './axiosInstance';

export const jobsAPI = {
  matchProfile: () => axiosInstance.post('/jobs/match/'),
  predictCustom: (payload) => axiosInstance.post('/jobs/predict/', { payload }),
  getRecommendations: () => axiosInstance.get('/jobs/recommendations/'),
  getMarket: () => axiosInstance.get('/jobs/market/'),
  getSalary: () => axiosInstance.get('/jobs/salary/'),
  getCompanies: () => axiosInstance.get('/jobs/companies/'),
  getSkillsGap: () => axiosInstance.get('/jobs/skills-gap/'),
  
  // Phase E: Job ATS APIs
  evaluateJobATS: (jobDescription, companyName, jobTitle) => 
    axiosInstance.post('/job-ats/', { job_description: jobDescription, company_name: companyName, job_title: jobTitle }),
  getJobATSReport: (reportId) => 
    axiosInstance.post('/job-ats/report/', { report_id: reportId }),
  getJobATSHistory: () => 
    axiosInstance.get('/job-ats/history/'),
};


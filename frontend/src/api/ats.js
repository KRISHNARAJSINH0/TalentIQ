import axiosInstance from './axiosInstance';

export const atsAPI = {
  /**
   * Run ATS Analysis on a resume's verified profile data
   */
  analyzeResume: (resumeId) => {
    return axiosInstance.post('/ats/analyze/', { resume_id: resumeId });
  },

  /**
   * Get the latest ATS score and evaluation for a resume
   */
  getLatestATS: (resumeId) => {
    return axiosInstance.get(`/ats/${resumeId}/`);
  },

  /**
   * Get the history of all ATS analysis runs for the authenticated user
   */
  getATSHistory: () => {
    return axiosInstance.get('/ats/history/');
  },
};

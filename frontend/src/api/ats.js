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

  /**
   * Get specific ATS report by ID
   */
  getReportDetails: (reportId) => {
    return axiosInstance.get(`/ats/report/${reportId}/`);
  },

  /**
   * Run job description matching
   */
  matchJob: (resumeId, jobDescription) => {
    return axiosInstance.post('/ats/job-match/', {
      resume_id: resumeId,
      job_description: jobDescription
    });
  },

  /**
   * Get all ATS rules
   */
  getRules: () => {
    return axiosInstance.get('/ats/rules/');
  },

  /**
   * Update specific ATS rule configuration (points/enabled state)
   */
  updateRule: (ruleId, data) => {
    return axiosInstance.put(`/ats/rules/${ruleId}/`, data);
  },

  /**
   * Get rule execution logs for a resume
   */
  getRuleExecutions: (resumeId) => {
    return axiosInstance.get('/ats/execution/', { params: { resume_id: resumeId } });
  }
};


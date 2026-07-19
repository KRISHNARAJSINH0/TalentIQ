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
  },

  /**
   * Get Penalty & Bonus score adjustments
   */
  getAdjustments: (resumeId) => {
    return axiosInstance.post('/ats/adjustments/', { resume_id: resumeId });
  },

  /**
   * Get Penalty details breakdown
   */
  getPenalties: (resumeId) => {
    return axiosInstance.get('/ats/penalties/', { params: { resume_id: resumeId } });
  },

  /**
   * Get Bonus details breakdown
   */
  getBonuses: (resumeId) => {
    return axiosInstance.get('/ats/bonuses/', { params: { resume_id: resumeId } });
  },

  /**
   * Trigger explanation report generation
   */
  explainScore: (resumeId) => {
    return axiosInstance.post('/ats/explain/', { resume_id: resumeId });
  },

  /**
   * Retrieve explanation report details
   */
  getExplanation: (resumeId) => {
    return axiosInstance.get('/ats/explanation/', { params: { resume_id: resumeId } });
  },

  /**
   * Run score simulations
   */
  simulateScore: (resumeId, actions) => {
    return axiosInstance.post('/ats/simulate/', { resume_id: resumeId, actions });
  },

  /**
   * Get prioritized action plan / roadmap
   */
  getActionPlan: (resumeId) => {
    return axiosInstance.get('/ats/action-plan/', { params: { resume_id: resumeId } });
  },

  /**
   * Trigger ATS Calibration Sweep
   */
  runCalibration: () => {
    return axiosInstance.post('/ats/calibrate/');
  },

  /**
   * Trigger ATS Validation Sweep
   */
  runValidation: () => {
    return axiosInstance.post('/ats/validate/');
  },

  /**
   * Get latest ATS Engine health metrics and validation results
   */
  getEngineHealth: () => {
    return axiosInstance.get('/ats/health/');
  },

  /**
   * Get latest ATS score distribution metrics
   */
  getScoreDistribution: () => {
    return axiosInstance.get('/ats/distribution/');
  },

  /**
   * Get latest consolidated Engine Quality Report
   */
  getQualityReport: () => {
    return axiosInstance.get('/ats/quality/');
  }
};




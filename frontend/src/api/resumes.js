import axiosInstance from './axiosInstance';

export const resumesAPI = {
  /**
   * Upload a resume file with progress monitoring
   */
  uploadResume: (file, resumeTitle = '', onProgress = null) => {
    const formData = new FormData();
    formData.append('original_file', file);
    if (resumeTitle) {
      formData.append('resume_title', resumeTitle);
    }
    return axiosInstance.post('/resumes/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },

  /**
   * List all resumes
   */
  getResumes: () => {
    return axiosInstance.get('/resumes/');
  },

  /**
   * Get resume details by ID
   */
  getResumeDetails: (id) => {
    return axiosInstance.get(`/resumes/${id}/`);
  },

  /**
   * Download a resume by ID (resolves as file Blob)
   */
  downloadResume: (id) => {
    return axiosInstance.get(`/resumes/${id}/download/`, {
      responseType: 'blob',
    });
  },

  /**
   * Soft-delete a resume by ID
   */
  deleteResume: (id) => {
    return axiosInstance.delete(`/resumes/${id}/`);
  },

  /**
   * Set a specific resume version as active
   */
  activateResume: (id) => {
    return axiosInstance.patch(`/resumes/${id}/activate/`);
  },

  /**
   * Retrieve version history (paginated list of user's resumes)
   */
  getResumeHistory: () => {
    return axiosInstance.get('/resumes/history/');
  },

  /**
   * Trigger text extraction for a resume
   */
  extractResume: (id) => {
    return axiosInstance.post(`/resumes/${id}/extract/`);
  },

  /**
   * Retrieve the raw extracted text of a resume
   */
  getResumeText: (id) => {
    return axiosInstance.get(`/resumes/${id}/text/`);
  },

  /**
   * Retrieve the extraction status and metadata for a resume
   */
  getResumeStatus: (id) => {
    return axiosInstance.get(`/resumes/${id}/status/`);
  },

  /**
   * Trigger regex analysis for a resume
   */
  runRegexAnalysis: (id) => {
    return axiosInstance.post(`/resumes/${id}/regex/`);
  },

  /**
   * Retrieve the extracted regex JSON data for a resume
   */
  getRegexData: (id) => {
    return axiosInstance.get(`/resumes/${id}/regex/`);
  },

  /**
   * Retrieve the regex extraction status and metadata for a resume
   */
  getRegexStatus: (id) => {
    return axiosInstance.get(`/resumes/${id}/regex/status/`);
  },

  /**
   * Trigger spaCy NLP analysis for a resume
   * Uses extended timeout because first spaCy model load can take 60+ seconds
   */
  runSpacyAnalysis: (id) => {
    return axiosInstance.post(`/resumes/${id}/spacy/`, {}, {
      timeout: 120000,
    });
  },

  /**
   * Retrieve the extracted spaCy JSON data for a resume
   */
  getSpacyData: (id) => {
    return axiosInstance.get(`/resumes/${id}/spacy/`);
  },

  /**
   * Retrieve the spaCy extraction status and metadata for a resume
   */
  getSpacyStatus: (id) => {
    return axiosInstance.get(`/resumes/${id}/spacy/status/`);
  },

  /**
   * Trigger Gemini AI parsing for a resume
   */
  runAIParsing: (id) => {
    return axiosInstance.post(`/resumes/${id}/ai/`);
  },

  /**
   * Retrieve the extracted AI JSON data for a resume
   */
  getAIData: (id) => {
    return axiosInstance.get(`/resumes/${id}/ai/`);
  },

  /**
   * Retrieve the Gemini AI extraction status and metadata for a resume
   */
  getAIStatus: (id) => {
    return axiosInstance.get(`/resumes/${id}/ai/status/`);
  },

  /**
   * Trigger master profile merge and validation
   */
  mergeProfile: (id) => {
    return axiosInstance.post(`/resumes/${id}/merge/`);
  },

  /**
   * Retrieve the master resume profile JSON data
   */
  getMasterProfile: (id) => {
    return axiosInstance.get(`/resumes/${id}/master/`);
  },

  /**
   * Retrieve the completion status and overall percentage
   */
  getCompletionDetails: (id) => {
    return axiosInstance.get(`/resumes/${id}/completion/`);
  },
};

export default resumesAPI;

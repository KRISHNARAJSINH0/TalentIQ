import axiosInstance from './axiosInstance';

export const profilesAPI = {
  /**
   * Get the master profile (optionally initializing from a specific resume_id)
   */
  getMasterProfile: (resumeId = null) => {
    const params = resumeId ? { resume_id: resumeId } : {};
    return axiosInstance.get('/profile/master/', { params });
  },

  /**
   * Update the entire master profile
   */
  updateMasterProfile: (data) => {
    return axiosInstance.put('/profile/master/', data);
  },

  /**
   * Update a specific section of the profile
   */
  updateSection: (section, data) => {
    return axiosInstance.patch('/profile/section/', { section, data });
  },

  /**
   * Mark a section or the entire profile as verified
   */
  verifySection: (section = null, isVerified = true) => {
    return axiosInstance.post('/profile/verify/', { section, is_verified: isVerified });
  },
};

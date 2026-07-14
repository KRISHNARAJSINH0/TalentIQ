import axiosInstance from '../api/axiosInstance';

/**
 * Exports the verified profile JSON and opens the Resume Builder (internal or external).
 * Saves profile data to localStorage under 'master_resume_json' and opens a new tab or redirects.
 * 
 * @param {Function} navigate - React Router navigate hook function
 * @param {Function} setLoading - State setter for loading spinner
 */
export const handleOpenResumeBuilder = async (navigate, setLoading) => {
  if (setLoading) setLoading(true);
  try {
    // 1. Fetch verified profile JSON
    const response = await axiosInstance.get('/profile/export/');
    const profileJson = response.data;

    // 2. Save master_resume_json to localStorage so the builder can access it
    localStorage.setItem('master_resume_json', JSON.stringify(profileJson));

    // 3. Check if builder exists inside React
    // If the path '/resume-builder' is configured or hasInternalBuilder is toggled, navigate internally
    const hasInternalBuilder = false; // Set to true if an internal builder is developed/active

    if (hasInternalBuilder) {
      navigate('/resume-builder', { state: { master_resume_json: profileJson } });
    } else {
      // 4. Open external builder in a new tab
      const externalUrl = import.meta.env.VITE_RESUME_BUILDER_URL || 'https://rxresume.me';
      const serializedData = encodeURIComponent(JSON.stringify(profileJson));
      window.open(`${externalUrl}?data=${serializedData}`, '_blank');
    }
  } catch (error) {
    console.error('Error opening resume builder:', error);
    alert('Failed to open Resume Builder: Please verify that you have initialized your master profile.');
  } finally {
    if (setLoading) setLoading(false);
  }
};

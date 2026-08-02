import axiosInstance from '../api/axiosInstance';

const RESUME_BUILDER_TARGET_URL = 'https://resume-builder-from-talent-iq.vercel.app';

/**
 * Exports the verified profile JSON and opens the Resume Builder external Vercel app.
 * Target URL: https://resume-builder-from-talent-iq.vercel.app
 * 
 * @param {Function} navigate - React Router navigate hook function (optional)
 * @param {Function} setLoading - State setter for loading spinner (optional)
 */
export const handleOpenResumeBuilder = async (navigate, setLoading) => {
  if (setLoading) setLoading(true);

  // Determine external URL (defaulting to the specified vercel app)
  const envUrl = import.meta.env.VITE_RESUME_BUILDER_URL;
  const baseUrl = envUrl || RESUME_BUILDER_TARGET_URL;
  const formattedUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;

  try {
    // 1. Fetch verified profile JSON from backend API
    const response = await axiosInstance.get('/profile/export/');
    const profileJson = response.data;

    // 2. Save master_resume_json to localStorage
    if (profileJson) {
      localStorage.setItem('master_resume_json', JSON.stringify(profileJson));
    }

    // 3. Open target URL in a new tab
    window.open(formattedUrl, '_blank', 'noopener,noreferrer');
  } catch (error) {
    console.warn('Error fetching profile export, opening Resume Builder directly:', error);
    // Fallback: Open builder directly even if API export hits a warning
    window.open(formattedUrl, '_blank', 'noopener,noreferrer');
  } finally {
    if (setLoading) setLoading(false);
  }
};

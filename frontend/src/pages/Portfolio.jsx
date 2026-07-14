import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineSparkles, HiOutlineGlobeAlt, HiOutlineArrowTopRightOnSquare } from 'react-icons/hi2';
import { profilesAPI } from '../api/profiles';
import { handleOpenResumeBuilder } from '../utils/resumeBuilder';
import '../styles/Profile.css';

const Portfolio = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [builderLoading, setBuilderLoading] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const res = await profilesAPI.getMasterProfile();
        setProfile(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load profile details.');
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  const handleBuildResume = () => {
    handleOpenResumeBuilder(navigate, setBuilderLoading);
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container" style={{ textAlign: 'center', paddingTop: 100 }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading Portfolio...</span>
          </div>
          <p style={{ marginTop: 16, color: 'var(--gray-300)' }}>Loading your portfolio settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-container" style={{ maxWidth: '1000px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header Card */}
          <div className="profile-card" style={{ padding: '32px', marginBottom: '32px', border: '1px solid rgba(139, 92, 246, 0.15)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
            <div>
              <h1 className="profile-name" style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ color: '#8B5CF6' }}><HiOutlineSparkles /></span>
                Portfolio Builder (Phase 12)
              </h1>
              <p className="profile-headline" style={{ fontSize: '1rem', color: 'var(--gray-400)', marginTop: '4px' }}>
                Create a stunning online presence directly from your verified master profile.
              </p>
            </div>
            
            <button
              onClick={handleBuildResume}
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
                border: 'none',
                padding: '12px 24px',
                fontSize: '0.95rem'
              }}
              disabled={builderLoading}
            >
              {builderLoading ? 'Exporting...' : '📝 Open Resume Builder'}
            </button>
          </div>

          {/* Portfolio status section */}
          <div className="profile-card" style={{ padding: '32px', border: '1px solid var(--glass-border)' }}>
            <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
              <HiOutlineGlobeAlt /> Portfolio Deployment Status
            </h3>

            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '24px', borderRadius: '12px', border: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Deployment URL</span>
                <a 
                  href={profile?.portfolio_url || '#'} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  style={{ color: '#22D3EE', fontWeight: 600, fontSize: '1.1rem', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}
                >
                  {profile?.portfolio_url || `https://resume-ai.com/portfolio/${profile?.first_name?.toLowerCase() || 'user'}`}
                  <HiOutlineArrowTopRightOnSquare style={{ fontSize: '0.9rem' }} />
                </a>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.9rem', color: '#10B981', fontWeight: 600, marginTop: '4px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }}></span>
                  Active & Published
                </span>
              </div>
            </div>

            <div style={{ marginTop: '32px' }}>
              <h4 style={{ color: 'var(--white)', marginBottom: '16px' }}>Portfolio Details</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
                <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.01)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}>
                  <span style={{ color: 'var(--gray-400)', fontSize: '0.8rem' }}>Name</span>
                  <p style={{ color: 'var(--white)', margin: '4px 0 0', fontWeight: 500 }}>{profile?.first_name} {profile?.last_name}</p>
                </div>
                <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.01)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}>
                  <span style={{ color: 'var(--gray-400)', fontSize: '0.8rem' }}>Headline</span>
                  <p style={{ color: 'var(--white)', margin: '4px 0 0', fontWeight: 500 }}>{profile?.headline || 'Not set'}</p>
                </div>
                <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.01)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}>
                  <span style={{ color: 'var(--gray-400)', fontSize: '0.8rem' }}>Theme</span>
                  <p style={{ color: '#8B5CF6', margin: '4px 0 0', fontWeight: 600 }}>Glassmorphism Dark</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Portfolio;

import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  HiOutlineGlobeAlt, 
  HiOutlinePaintBrush, 
  HiOutlineEye, 
  HiOutlineSparkles, 
  HiOutlineLockClosed, 
  HiOutlineLockOpen,
  HiOutlineChartBar,
  HiOutlineCheck,
  HiOutlineLink,
  HiOutlineArrowTopRightOnSquare
} from 'react-icons/hi2';
import { portfolioAPI } from '../api/portfolio';
import GlassCard from '../components/GlassCard';
import GlassInput from '../components/GlassInput';
import SkeletonLoader from '../components/SkeletonLoader';

const THEMES = [
  { id: 'modern', name: 'Modern', desc: 'Sleek, multi-layered layout with clean typography.' },
  { id: 'minimal', name: 'Minimal', desc: 'Ultra clean, minimal whitespace-focused style.' },
  { id: 'developer', name: 'Developer', desc: 'Terminal style cues, syntax highlighting colors.' },
  { id: 'corporate', name: 'Corporate', desc: 'Professional, structured, business-ready.' },
  { id: 'creative', name: 'Creative', desc: 'Playful shapes, bold gradients, active shadows.' },
  { id: 'dark', name: 'Dark Mode', desc: 'Sophisticated charcoal-black aesthetic.' },
  { id: 'light', name: 'Light Mode', desc: 'Bright, paper-clean interface.' },
  { id: 'glassmorphism', name: 'Glassmorphism', desc: 'Intense frosted glass cards, glow effects.' },
  { id: 'professional', name: 'Professional', desc: 'Traditional resume styling with modern touches.' },
  { id: 'student', name: 'Student', desc: 'Compact, highlight-oriented modern presentation.' },
  { id: 'researcher', name: 'Researcher', desc: 'Publication-first clean academic theme.' }
];

const PortfolioDashboard = () => {
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [savingTheme, setSavingTheme] = useState(false);
  const [savingSlug, setSavingSlug] = useState(false);
  const [savingPrivacy, setSavingPrivacy] = useState(false);
  const [selectedTheme, setSelectedTheme] = useState('modern');
  const [customSlug, setCustomSlug] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      const res = await portfolioAPI.getPortfolio();
      setPortfolio(res.data);
      setSelectedTheme(res.data.theme);
      setCustomSlug(res.data.slug);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch portfolio data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      setError('');
      setSuccess('');
      const res = await portfolioAPI.generatePortfolio();
      setPortfolio(res.data);
      setSuccess('Portfolio website successfully generated from Master Profile!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error(err);
      setError('Failed to generate portfolio. Make sure you have initialized your master profile.');
    } finally {
      setGenerating(false);
    }
  };

  const handleThemeChange = async (themeId) => {
    if (!portfolio) return;
    try {
      setSavingTheme(true);
      setSelectedTheme(themeId);
      const res = await portfolioAPI.updateTheme({ theme: themeId });
      setPortfolio(res.data);
      setSuccess('Theme updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError('Failed to save theme choice.');
    } finally {
      setSavingTheme(false);
    }
  };

  const handleSlugUpdate = async (e) => {
    e.preventDefault();
    if (!portfolio || !customSlug) return;
    try {
      setSavingSlug(true);
      setError('');
      setSuccess('');
      const res = await portfolioAPI.updateTheme({ slug: customSlug });
      setPortfolio(res.data);
      setSuccess('Portfolio slug updated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.slug?.[0] || 'Failed to update custom slug. Choose a unique alphanumeric value.');
    } finally {
      setSavingSlug(false);
    }
  };

  const handlePrivacyToggle = async () => {
    if (!portfolio) return;
    try {
      setSavingPrivacy(true);
      setError('');
      setSuccess('');
      const nextPublic = !portfolio.is_public;
      const res = await portfolioAPI.updatePrivacy({ is_public: nextPublic });
      setPortfolio(res.data);
      setSuccess(`Portfolio visibility updated to ${nextPublic ? 'Public' : 'Private'}!`);
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error(err);
      setError('Failed to update privacy settings.');
    } finally {
      setSavingPrivacy(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <SkeletonLoader type="card" />
      </div>
    );
  }

  const publicUrl = `${window.location.origin}/portfolio/${portfolio?.slug}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Top Header Card */}
      <GlassCard hoverEffect={false} style={{ padding: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: 'var(--primary)' }}><HiOutlineGlobeAlt size={28} /></span>
            Portfolio Dashboard
          </h1>
          <p style={{ fontSize: '0.95rem', color: 'var(--subtext-color)', marginTop: '4px', marginBottom: 0 }}>
            Host a public resume website generated automatically from your verified profile data.
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <Link to="/portfolio/analytics" className="glass-panel" style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: '12px',
            color: 'var(--text-color)',
            textDecoration: 'none',
            fontSize: '0.9rem',
            fontWeight: 600
          }}>
            <HiOutlineChartBar size={18} /> Analytics
          </Link>
          
          <button
            onClick={handleGenerate}
            className="btn btn-primary"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              border: 'none',
              padding: '10px 18px',
              fontSize: '0.9rem',
              fontWeight: 600,
              borderRadius: '12px'
            }}
            disabled={generating}
          >
            <HiOutlineSparkles size={18} />
            {generating ? 'Rebuilding...' : 'Regenerate Site'}
          </button>
        </div>
      </GlassCard>

      {error && (
        <div className="glass-panel" style={{ padding: '14px 20px', backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '16px', color: 'var(--danger)', fontWeight: 500, fontSize: '0.9rem' }}>
          {error}
        </div>
      )}
      
      {success && (
        <div className="glass-panel" style={{ padding: '14px 20px', backgroundColor: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.25)', borderRadius: '16px', color: 'var(--success)', fontWeight: 500, fontSize: '0.9rem' }}>
          {success}
        </div>
      )}

      {/* 2 Column Settings Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }} className="profile-columns-grid">
        
        {/* Left Column: Theme Selector */}
        <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HiOutlinePaintBrush size={20} style={{ color: 'var(--primary)' }} /> Select Website Theme
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }} className="themes-grid-mobile">
            {THEMES.map((theme) => {
              const isActive = selectedTheme === theme.id;
              return (
                <div
                  key={theme.id}
                  onClick={() => handleThemeChange(theme.id)}
                  style={{
                    padding: '16px',
                    borderRadius: '12px',
                    background: isActive ? 'rgba(37, 99, 235, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                    border: isActive ? '2px solid var(--primary)' : '1px solid var(--glass-border)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)'
                  }}
                  className="theme-card-hover"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: isActive ? 'var(--primary)' : 'var(--text-color)' }}>
                      {theme.name}
                    </span>
                    {isActive && <HiOutlineCheck size={16} style={{ color: 'var(--primary)' }} />}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)', lineHeight: '1.4', display: 'block' }}>
                    {theme.desc}
                  </span>
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Right Column: Visibility & Slug */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Live Status & Quick Preview */}
          <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineEye size={20} style={{ color: 'var(--primary)' }} /> Live Portfolio URL
            </h3>
            
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              padding: '16px',
              borderRadius: '12px',
              border: '1px solid var(--glass-border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <a
                href={publicUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: 'var(--primary)',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  textDecoration: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  wordBreak: 'break-all'
                }}
              >
                {portfolio?.slug ? `/portfolio/${portfolio.slug}` : 'No URL generated'}
                <HiOutlineArrowTopRightOnSquare size={16} />
              </a>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <a
                href={publicUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="glass-panel"
                style={{
                  flex: 1,
                  textAlign: 'center',
                  display: 'inline-flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '10px',
                  borderRadius: '10px',
                  color: 'var(--text-color)',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600
                }}
              >
                👁️ Live Preview
              </a>
              
              <button
                onClick={handlePrivacyToggle}
                className="glass-panel"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '10px 16px',
                  borderRadius: '10px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-color)'
                }}
                disabled={savingPrivacy}
              >
                {savingPrivacy ? (
                  <span>Updating...</span>
                ) : portfolio?.is_public ? (
                  <>
                    <HiOutlineLockOpen size={16} style={{ color: 'var(--success)' }} />
                    Public Access
                  </>
                ) : (
                  <>
                    <HiOutlineLockClosed size={16} style={{ color: 'var(--danger)' }} />
                    Private Draft
                  </>
                )}
              </button>
            </div>
          </GlassCard>

          {/* Custom URL Slug Update */}
          <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineLink size={20} style={{ color: 'var(--primary)' }} /> Custom URL Slug
            </h3>
            
            <form onSubmit={handleSlugUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                  <span style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--subtext-color)', fontSize: '0.85rem' }}>
                    /portfolio/
                  </span>
                  <input
                    type="text"
                    className="edit-input"
                    value={customSlug}
                    onChange={(e) => setCustomSlug(e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, ''))}
                    style={{ paddingLeft: '88px', height: '44px', fontSize: '0.9rem', width: '100%' }}
                    placeholder="john-doe"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ height: '44px', padding: '0 20px', borderRadius: '12px', fontSize: '0.85rem', fontWeight: 600 }}
                  disabled={savingSlug}
                >
                  {savingSlug ? 'Saving...' : 'Update'}
                </button>
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>
                Alphanumeric characters, hyphens, and underscores only.
              </span>
            </form>
          </GlassCard>

          {/* Analytics Stats Overview */}
          <GlassCard hoverEffect={false} style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h4 style={{ color: 'var(--text-color)', fontSize: '0.95rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
              📊 Analytics Summary
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', textAlign: 'center' }}>
              <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.01)', border: '1px solid var(--glass-border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Total Views</span>
                <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--primary)', margin: '4px 0 0' }}>{portfolio?.views}</p>
              </div>
              <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.01)', border: '1px solid var(--glass-border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Downloads</span>
                <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--success)', margin: '4px 0 0' }}>{portfolio?.downloads}</p>
              </div>
              <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.01)', border: '1px solid var(--glass-border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Shares</span>
                <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--warning)', margin: '4px 0 0' }}>{portfolio?.shares}</p>
              </div>
            </div>
          </GlassCard>

        </div>
      </div>
      
      <style>{`
        .theme-card-hover:hover {
          background-color: rgba(37, 99, 235, 0.04) !important;
          border-color: var(--primary) !important;
        }
        @media (max-width: 576px) {
          .themes-grid-mobile {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};

export default PortfolioDashboard;

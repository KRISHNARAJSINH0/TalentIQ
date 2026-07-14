import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  HiOutlineSparkles, 
  HiOutlineChartBar, 
  HiOutlineAcademicCap, 
  HiOutlineDocumentText, 
  HiOutlineCheckBadge,
  HiOutlineArrowTrendingUp,
  HiOutlineCheckCircle,
  HiOutlineExclamationTriangle
} from 'react-icons/hi2';
import { careerAPI } from '../api/career';
import GlassCard from '../components/GlassCard';
import SkeletonLoader from '../components/SkeletonLoader';

const CareerDashboard = () => {
  const navigate = useNavigate();
  const [career, setCareer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchCareerData = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await careerAPI.getCareerDetails();
      setCareer(res.data);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setCareer(null);
      } else {
        setError('Failed to fetch career analysis data.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCareerData();
  }, []);

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      setError('');
      setSuccess('');
      const res = await careerAPI.analyzeProfile();
      setCareer(res.data);
      setSuccess('AI Career Analysis generated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to analyze profile. Make sure you have uploaded and verified your resume.');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <SkeletonLoader type="card" />
      </div>
    );
  }

  // Not generated yet view
  if (!career) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div style={{ maxWidth: '600px', width: '100%' }}>
          <GlassCard hoverEffect={true} style={{ padding: '40px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
            <span style={{ fontSize: '3.5rem' }}>🚀</span>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: 'var(--text-color)' }}>Initialize AI Career Assistant</h2>
            <p style={{ color: 'var(--subtext-color)', fontSize: '0.95rem', lineHeight: '1.6', margin: 0 }}>
              Unlock career insights, skill gap analysis, personalized learning roadmaps, and custom cover letters based on your Verified Master Profile.
            </p>
            {error && (
              <div className="glass-panel" style={{ padding: '12px 18px', backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '12px', color: 'var(--danger)', width: '100%' }}>
                {error}
              </div>
            )}
            <button
              onClick={handleAnalyze}
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 28px',
                fontSize: '1rem',
                fontWeight: 600,
                borderRadius: '12px',
                border: 'none'
              }}
              disabled={analyzing}
            >
              <HiOutlineSparkles size={20} />
              {analyzing ? 'Analyzing Profile...' : 'Generate Career Analysis'}
            </button>
          </GlassCard>
        </div>
      </div>
    );
  }

  const scores = [
    { label: 'Readiness', val: career.career_readiness, color: 'var(--primary)' },
    { label: 'Growth', val: career.growth_score, color: '#8B5CF6' },
    { label: 'Learning', val: career.learning_score, color: 'var(--success)' },
    { label: 'Alignment', val: career.industry_alignment, color: '#EC4899' },
    { label: 'Skill Strength', val: career.skill_strength, color: 'var(--warning)' },
    { label: 'Market Demand', val: career.market_demand, color: 'var(--danger)' }
  ];

  const details = career.career_json.career_details || {};
  const skillGap = career.career_json.skill_gap || {};
  const suggestions = career.career_json.suggestions || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Top Header Card */}
      <GlassCard hoverEffect={false} style={{ padding: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: 'var(--primary)' }}><HiOutlineSparkles size={28} /></span>
            AI Career Assistant
          </h1>
          <p style={{ fontSize: '0.95rem', color: 'var(--subtext-color)', marginTop: '4px', marginBottom: 0 }}>
            Strategic guidance, roadmap sequencing, and cover letter builder tailored to your profile.
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <Link to="/career/roadmap" className="glass-panel" style={{
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
            <HiOutlineAcademicCap size={18} /> Roadmap
          </Link>
          <Link to="/career/cover-letter" className="glass-panel" style={{
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
            <HiOutlineDocumentText size={18} /> Cover Letters
          </Link>
          <button
            onClick={handleAnalyze}
            className="btn btn-primary"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 18px',
              fontSize: '0.9rem',
              fontWeight: 600,
              borderRadius: '12px',
              border: 'none'
            }}
            disabled={analyzing}
          >
            <HiOutlineSparkles size={18} />
            {analyzing ? 'Refreshing...' : 'Re-Analyze'}
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

      {/* Scores Metric Row */}
      <GlassCard hoverEffect={false} style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <HiOutlineChartBar size={20} style={{ color: 'var(--primary)' }} /> Career Score Dashboard
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '20px' }}>
          {scores.map((s, idx) => (
            <div key={idx} style={{ textAlign: 'center', padding: '16px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--glass-border)', borderRadius: '12px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)', display: 'block', marginBottom: '8px' }}>{s.label}</span>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: s.color }}>
                {s.val}%
              </div>
              <div style={{ width: '100%', height: '4px', background: 'var(--glass-border)', borderRadius: '2px', marginTop: '10px', overflow: 'hidden' }}>
                <div style={{ width: `${s.val}%`, height: '100%', background: s.color }}></div>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* 2 Column Details */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }} className="profile-columns-grid">
        
        {/* Left Column: Stage, Strengths & Weaknesses */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Career Details */}
          <GlassCard hoverEffect={false} style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 20px 0' }}>📋 Career Assessment</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }} className="themes-grid-mobile">
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Current Role</span>
                <p style={{ color: 'var(--text-color)', fontWeight: 600, margin: '4px 0 0' }}>{details.current_role || 'Not Stated'}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Career Stage</span>
                <p style={{ color: 'var(--text-color)', fontWeight: 600, margin: '4px 0 0' }}>{details.career_stage || 'Not Stated'}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Experience</span>
                <p style={{ color: 'var(--text-color)', fontWeight: 600, margin: '4px 0 0' }}>{details.years_experience || 'Not Stated'}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Target Industry</span>
                <p style={{ color: 'var(--text-color)', fontWeight: 600, margin: '4px 0 0' }}>{details.industry || 'Not Stated'}</p>
              </div>
            </div>

            <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '16px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Strategic Direction</span>
              <p style={{ color: 'var(--text-color)', fontSize: '0.9rem', lineHeight: '1.6', marginTop: '6px', marginBottom: 0 }}>
                {details.career_direction}
              </p>
            </div>
          </GlassCard>

          {/* Strengths & Weaknesses */}
          <GlassCard hoverEffect={false} style={{ padding: '24px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }} className="themes-grid-mobile">
              <div>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '16px', fontWeight: 700 }}>
                  <HiOutlineCheckCircle size={18} /> Professional Strengths
                </h4>
                <ul style={{ paddingLeft: '18px', margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {details.strengths?.map((str, idx) => (
                    <li key={idx} style={{ fontSize: '0.85rem', color: 'var(--text-color)', lineHeight: '1.4' }}>{str}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '16px', fontWeight: 700 }}>
                  <HiOutlineExclamationTriangle size={18} /> Development Areas
                </h4>
                <ul style={{ paddingLeft: '18px', margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {details.weaknesses?.map((wk, idx) => (
                    <li key={idx} style={{ fontSize: '0.85rem', color: 'var(--text-color)', lineHeight: '1.4' }}>{wk}</li>
                  ))}
                </ul>
              </div>
            </div>
          </GlassCard>

        </div>

        {/* Right Column: Skill Gaps & Career Suggestions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Skill Gaps */}
          <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <HiOutlineCheckBadge size={20} style={{ color: 'var(--primary)' }} /> Skill Gap Tracker
            </h3>
            
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--success)', fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                Current Verified Skills
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {skillGap.current_skills?.map((sk, idx) => (
                  <span key={idx} style={{ fontSize: '0.75rem', padding: '4px 8px', borderRadius: '6px', background: 'rgba(34, 197, 94, 0.05)', border: '1px solid rgba(34, 197, 94, 0.15)', color: 'var(--success)', fontWeight: 600 }}>
                    {sk}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--warning)', fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                Recommended High-Demand Skills
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {skillGap.missing_skills?.map((sk, idx) => (
                  <span key={idx} style={{ fontSize: '0.75rem', padding: '4px 8px', borderRadius: '6px', background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.15)', color: 'var(--warning)', fontWeight: 600 }}>
                    + {sk}
                  </span>
                ))}
              </div>
            </div>
          </GlassCard>

          {/* Career Suggestions */}
          <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <HiOutlineArrowTrendingUp size={20} style={{ color: 'var(--primary)' }} /> Target Opportunities
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Recommended Roles</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                  {suggestions.roles?.map((r, idx) => (
                    <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '6px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)', color: 'var(--text-color)', fontWeight: 500 }}>
                      {r}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Emerging Tech to Watch</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                  {suggestions.emerging_technologies?.map((t, idx) => (
                    <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '6px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)', color: 'var(--primary)', fontWeight: 600 }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              
              <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '12px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Career Transition Path</span>
                <p style={{ color: 'var(--text-color)', fontSize: '0.85rem', margin: '4px 0 0', lineHeight: '1.4' }}>
                  {suggestions.career_transitions}
                </p>
              </div>
            </div>
          </GlassCard>

        </div>
      </div>
    </div>
  );
};

export default CareerDashboard;

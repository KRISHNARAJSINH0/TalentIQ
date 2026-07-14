import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiOutlineSparkles, 
  HiOutlineChartBar, 
  HiOutlineArrowTrendingUp,
  HiOutlineBriefcase,
  HiOutlineShieldCheck,
  HiOutlineBuildingOffice2,
  HiOutlineGlobeAlt,
  HiOutlineScale,
  HiOutlineLightBulb,
  HiOutlineBookOpen,
  HiOutlineAcademicCap,
  HiOutlineChevronRight,
  HiOutlineArrowPath
} from 'react-icons/hi2';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { jobsAPI } from '../api/jobs';
import GlassCard from '../components/GlassCard';
import SkeletonLoader from '../components/SkeletonLoader';
import '../styles/JobDashboard.css';

const JobDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Interactive Predictor state
  const [customTitle, setCustomTitle] = useState('');
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  const fetchJobIntelligence = async () => {
    try {
      setLoading(true);
      setError('');
      // Match recommendations triggers matching calculations if none exist
      const recsRes = await jobsAPI.getRecommendations();
      
      // Fetch details from other endpoints to compile state
      const marketRes = await jobsAPI.getMarket();
      const salaryRes = await jobsAPI.getSalary();
      const companiesRes = await jobsAPI.getCompanies();
      const gapsRes = await jobsAPI.getSkillsGap();

      setData({
        recommended_jobs: recsRes.data,
        market: marketRes.data,
        salary_forecast: salaryRes.data,
        companies: companiesRes.data.companies,
        countries: companiesRes.data.countries,
        skill_gaps: gapsRes.data.gaps,
        recommendations: gapsRes.data.recommendations
      });
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setData(null);
      } else {
        setError('Failed to load Job Intelligence data. Make sure you have uploaded and verified your resume.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobIntelligence();
  }, []);

  const handleMatch = async () => {
    try {
      setMatching(true);
      setError('');
      setSuccess('');
      const res = await jobsAPI.matchProfile();
      
      // Re-fetch everything to align database
      const marketRes = await jobsAPI.getMarket();
      const salaryRes = await jobsAPI.getSalary();
      const companiesRes = await jobsAPI.getCompanies();
      const gapsRes = await jobsAPI.getSkillsGap();

      setData({
        recommended_jobs: res.data.recommended_jobs,
        market: marketRes.data,
        salary_forecast: salaryRes.data,
        companies: companiesRes.data.companies,
        countries: companiesRes.data.countries,
        skill_gaps: gapsRes.data.gaps,
        recommendations: gapsRes.data.recommendations
      });
      setSuccess('Job Intelligence matching calculations re-generated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to match profile. Please review master profile.');
    } finally {
      setMatching(false);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!customTitle.trim()) return;

    try {
      setPredicting(true);
      const payload = {
        headline: customTitle,
        skills: data?.skill_gaps ? data.skill_gaps.map(g => ({ skill_name: g.skill })) : [],
        experiences: []
      };
      const res = await jobsAPI.predictCustom(payload);
      setPredictionResult(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to compute role prediction.');
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '20px' }}>
        <SkeletonLoader type="card" />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
          <SkeletonLoader type="card" />
          <SkeletonLoader type="card" />
        </div>
      </div>
    );
  }

  // Fallback if no matching records found
  if (!data) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', padding: '20px' }}>
        <div style={{ maxWidth: '600px', width: '100%' }}>
          <GlassCard hoverEffect={true} style={{ padding: '40px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
            <span style={{ fontSize: '3.5rem' }}>💼</span>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: 'var(--text-color)' }}>Activate Job Intelligence Engine</h2>
            <p style={{ color: 'var(--subtext-color)', fontSize: '0.95rem', lineHeight: '1.6', margin: 0 }}>
              Analyze salary curves, market growth curves, remote compatibility metrics, and matching positions tailored directly to your professional profile.
            </p>
            {error && (
              <div className="glass-panel" style={{ padding: '12px 18px', backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '12px', color: 'var(--danger)', width: '100%' }}>
                {error}
              </div>
            )}
            <button
              onClick={handleMatch}
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 28px',
                fontSize: '1rem',
                fontWeight: 600,
                borderRadius: '12px',
                border: 'none',
                cursor: 'pointer'
              }}
              disabled={matching}
            >
              <HiOutlineSparkles size={20} />
              {matching ? 'Running Matching Calculations...' : 'Evaluate Job Matches'}
            </button>
          </GlassCard>
        </div>
      </div>
    );
  }

  // Format Recharts data
  const forecast = data.salary_forecast || {};
  const forecastValues = forecast.values || {};
  
  const chartData = [
    { name: 'Current', Min: forecastValues.current_low || 10, Max: forecastValues.current_high || 20 },
    { name: '6 Months', Min: forecastValues.months_6_low || 11, Max: forecastValues.months_6_high || 21 },
    { name: '12 Months', Min: forecastValues.months_12_low || 12, Max: forecastValues.months_12_high || 22 },
    { name: '24 Months', Min: forecastValues.months_24_low || 14, Max: forecastValues.months_24_high || 25 }
  ];

  const primaryRole = data.recommended_jobs?.[0]?.title || 'Consultant';

  return (
    <div className="job-dashboard-page">
      
      {/* Top Header Panel */}
      <GlassCard hoverEffect={false} className="job-dashboard-header">
        <div className="job-dashboard-header-text">
          <h1>
            <span style={{ color: 'var(--primary)' }}><HiOutlineBriefcase size={28} /></span>
            Job Intelligence Dashboard
          </h1>
          <p>
            Compare matching jobs, missing skills, remote factors, and growth trends based on your Master Profile.
          </p>
        </div>
        
        <div className="job-dashboard-header-actions">
          <button
            onClick={handleMatch}
            className="btn-recalc"
            disabled={matching}
          >
            <HiOutlineArrowPath size={16} className={matching ? 'spin' : ''} />
            {matching ? 'Re-calculating...' : 'Re-calculate Matches'}
          </button>
        </div>
      </GlassCard>

      {success && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          style={{ padding: '12px 18px', backgroundColor: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '12px', color: 'var(--success)' }}
        >
          {success}
        </motion.div>
      )}

      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          style={{ padding: '12px 18px', backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '12px', color: 'var(--danger)' }}
        >
          {error}
        </motion.div>
      )}

      {/* Numerical Metrics Cards */}
      <div className="job-metrics-grid">
        <GlassCard hoverEffect={true} style={{ padding: '24px' }}>
          <div className="metric-card-inner">
            <div className="metric-card-icon-wrapper" style={{ backgroundColor: 'rgba(139, 92, 246, 0.1)', color: '#8B5CF6' }}>
              <HiOutlineSparkles size={24} />
            </div>
            <div>
              <div className="metric-card-label">Primary Role Fit</div>
              <div className="metric-card-value">{primaryRole}</div>
            </div>
          </div>
        </GlassCard>

        <GlassCard hoverEffect={true} style={{ padding: '24px' }}>
          <div className="metric-card-inner">
            <div className="metric-card-icon-wrapper" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
              <HiOutlineArrowTrendingUp size={24} />
            </div>
            <div>
              <div className="metric-card-label">Market Demand</div>
              <div className="metric-card-value">{data.market?.market_demand || 'High'} ({data.market?.market_score || 85}%)</div>
            </div>
          </div>
        </GlassCard>

        <GlassCard hoverEffect={true} style={{ padding: '24px' }}>
          <div className="metric-card-inner">
            <div className="metric-card-icon-wrapper" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>
              <HiOutlineShieldCheck size={24} />
            </div>
            <div>
              <div className="metric-card-label">Remote Score</div>
              <div className="metric-card-value">{data.market?.remote_eligibility?.score || 80}%</div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Main Grid: Jobs Table & Salary Trend */}
      <div className="job-main-grid">
        
        {/* Recommended Jobs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <GlassCard className="job-card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineBriefcase size={20} style={{ color: 'var(--primary)' }} />
              Recommended Positions
            </h2>
            <div className="job-table-container">
              <table className="job-table">
                <thead>
                  <tr>
                    <th>Job Title</th>
                    <th>Industry</th>
                    <th>Match Score</th>
                    <th>Est. Salary</th>
                    <th>Remote</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recommended_jobs?.map((job, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600, color: 'var(--text-color)' }}>{job.title}</td>
                      <td style={{ color: 'var(--subtext-color)' }}>{job.industry}</td>
                      <td>
                        <span 
                          className="job-table-score-badge"
                          style={{
                            backgroundColor: job.score >= 85 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                            color: job.score >= 85 ? 'var(--success)' : 'var(--warning)',
                            border: job.score >= 85 ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid rgba(245, 158, 11, 0.2)'
                          }}
                        >
                          {job.score}% Match
                        </span>
                      </td>
                      <td style={{ fontWeight: 500 }}>{job.salary}</td>
                      <td>
                        {job.remote ? (
                          <span style={{ color: 'var(--success)', fontSize: '0.8rem', fontWeight: 600 }}>Yes</span>
                        ) : (
                          <span style={{ color: 'var(--subtext-color)', fontSize: '0.8rem' }}>No</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>

          {/* Predictor Simulator Form */}
          <GlassCard className="job-card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineSparkles size={20} style={{ color: '#8B5CF6' }} />
              Target Position Compatibility Simulator
            </h2>
            <p style={{ fontSize: '0.9rem', color: 'var(--subtext-color)', margin: '0 0 20px 0' }}>
              Enter any role title below to calculate matching metrics and identify skill requirements.
            </p>
            <form onSubmit={handlePredict} className="job-simulator-form">
              <input
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="e.g. Senior Principal AI Architect"
                className="job-simulator-input"
              />
              <button
                type="submit"
                className="btn-simulate"
                disabled={predicting}
              >
                {predicting ? 'Calculating...' : 'Simulate'}
              </button>
            </form>

            <AnimatePresence>
              {predictionResult && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ overflow: 'hidden' }}
                >
                  <div className="glass-panel" style={{ padding: '20px', borderRadius: '12px', backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
                      <div>
                        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>{predictionResult.predicted_role}</h4>
                        <span style={{ fontSize: '0.85rem', color: 'var(--subtext-color)' }}>Forecasted salary: {predictionResult.salary_forecast?.current}</span>
                      </div>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        color: '#8B5CF6'
                      }}>
                        {predictionResult.recommended_jobs?.[0]?.score || 75}% Fit Score
                      </span>
                    </div>

                    <div>
                      <h5 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--subtext-color)' }}>Emerging Trending Skills</h5>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {predictionResult.trending_skills?.map((skill, sIdx) => (
                          <span key={sIdx} style={{ padding: '4px 10px', borderRadius: '8px', backgroundColor: 'rgba(255,255,255,0.05)', fontSize: '0.75rem' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </GlassCard>
        </div>

        {/* Salary Curve area chart */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <GlassCard className="job-card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineChartBar size={20} style={{ color: 'var(--success)' }} />
              Salary Progression Curve
            </h2>
            <span style={{ fontSize: '0.85rem', color: 'var(--subtext-color)' }}>Forecast values in target currency ({forecastValues.currency_symbol || '$'} in {forecastValues.currency_suffix || 'k/yr'})</span>
            
            <div style={{ width: '100%', height: '240px', marginTop: '20px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorMin" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorMax" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--success)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--success)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="var(--subtext-color)" fontSize={11} />
                  <YAxis stroke="var(--subtext-color)" fontSize={11} />
                  <Tooltip contentStyle={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
                  <Area type="monotone" dataKey="Min" stroke="var(--primary)" fillOpacity={1} fill="url(#colorMin)" />
                  <Area type="monotone" dataKey="Max" stroke="var(--success)" fillOpacity={1} fill="url(#colorMax)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* Target Locations & Companies */}
          <GlassCard className="job-card">
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineBuildingOffice2 size={20} style={{ color: '#8B5CF6' }} />
              High-Reputation Employers
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {data.companies?.map((company, idx) => (
                <div key={idx} className="employer-item">
                  <span style={{ fontWeight: 500, color: 'var(--text-color)' }}>{company}</span>
                  <span style={{ color: 'var(--subtext-color)', fontSize: '0.8rem' }}>Tier 1 Target</span>
                </div>
              ))}
            </div>

            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '24px 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineGlobeAlt size={20} style={{ color: 'var(--primary)' }} />
              Global Corridors
            </h2>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {data.countries?.map((country, idx) => (
                <span key={idx} style={{ padding: '6px 12px', borderRadius: '20px', backgroundColor: 'rgba(255,255,255,0.05)', fontSize: '0.8rem', border: '1px solid var(--border-color)' }}>
                  {country}
                </span>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Bottom Grid: Gaps & Learning path */}
      <div className="job-bottom-grid">
        
        {/* Skill Gaps List */}
        <GlassCard className="job-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HiOutlineScale size={20} style={{ color: 'var(--warning)' }} />
            Identified Skill Gaps
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {data.skill_gaps?.map((gap, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', borderRadius: '8px', backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontWeight: 600 }}>{gap.skill}</span>
                <span style={{
                  padding: '3px 8px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  backgroundColor: gap.importance === 'High' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                  color: gap.importance === 'High' ? 'var(--danger)' : 'var(--warning)'
                }}>
                  {gap.importance} Priority
                </span>
              </div>
            ))}
            {(!data.skill_gaps || data.skill_gaps.length === 0) && (
              <p style={{ color: 'var(--subtext-color)', fontSize: '0.9rem' }}>No significant skill gaps identified. You match all core skills!</p>
            )}
          </div>
        </GlassCard>

        {/* Actionable Learning Path */}
        <GlassCard className="job-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HiOutlineLightBulb size={20} style={{ color: 'var(--success)' }} />
            Learning Recommendations
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--subtext-color)', margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <HiOutlineAcademicCap size={16} /> Certifications
              </h4>
              <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {data.recommendations?.certifications?.map((c, idx) => (
                  <li key={idx} style={{ color: 'var(--text-color)' }}>{c}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--subtext-color)', margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <HiOutlineBookOpen size={16} /> Portfolio Project Ideas
              </h4>
              <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {data.recommendations?.projects?.map((p, idx) => (
                  <li key={idx} style={{ color: 'var(--text-color)' }}>{p}</li>
                ))}
              </ul>
            </div>
          </div>
        </GlassCard>
      </div>

    </div>
  );
};

export default JobDashboard;

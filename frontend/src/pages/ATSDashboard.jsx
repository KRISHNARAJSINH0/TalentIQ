/**
 * ATSDashboard – Real-time ATS scoring, industry matching, keyword evaluation,
 * custom SVG charts, and actionable improvement recommendations.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  HiOutlineArrowLeft, 
  HiOutlineSparkles, 
  HiOutlineExclamationCircle, 
  HiOutlineCheckCircle, 
  HiOutlineChartBar, 
  HiOutlineShieldCheck,
  HiOutlinePlusCircle,
  HiOutlineChevronRight,
  HiOutlineRefresh
} from 'react-icons/hi';
import { atsAPI } from '../api/ats';
import { handleOpenResumeBuilder } from '../utils/resumeBuilder';
import '../styles/ATSDashboard.css';

const ATSDashboard = () => {
  const { id: resumeId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [atsData, setAtsData] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [builderLoading, setBuilderLoading] = useState(false);

  // Fetch data
  const fetchData = async (isRecalculate = false) => {
    try {
      if (isRecalculate) {
        setAnalyzing(true);
        setError('');
      } else {
        setLoading(true);
      }
      
      let res;
      if (isRecalculate) {
        res = await atsAPI.analyzeResume(resumeId);
        setSuccess('ATS analysis updated successfully!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        // Try getting existing latest, if none found, analyze first
        try {
          res = await atsAPI.getLatestATS(resumeId);
        } catch (err) {
          if (err.response && err.response.status === 404) {
            res = await atsAPI.analyzeResume(resumeId);
          } else {
            throw err;
          }
        }
      }

      setAtsData(res.data);

      // Fetch history
      const historyRes = await atsAPI.getATSHistory();
      // Filter history for this specific resume to show progress trend
      const resumeHistory = historyRes.data.filter(h => h.resume === resumeId || h.resume_title === res.data.resume_title);
      setHistory(resumeHistory);

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to load ATS analysis. Make sure you have created and verified a profile first.');
    } finally {
      setLoading(false);
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchData();
    }
  }, [resumeId]);

  if (loading) {
    return (
      <div className="ats-dashboard-page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="skeleton-row" style={{ width: '80px', height: '80px', borderRadius: '50%', margin: '0 auto 20px', background: 'linear-gradient(90deg, rgba(139,92,246,0.1), rgba(139,92,246,0.3), rgba(139,92,246,0.1))' }}></div>
          <p style={{ color: 'var(--gray-400)', fontSize: '0.9375rem' }}>Analyzing profile data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ats-dashboard-page">
        <div className="ats-container" style={{ maxWidth: '600px', margin: '80px auto 0' }}>
          <div className="ats-card" style={{ textAlign: 'center', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
            <div style={{ fontSize: '3rem', color: '#EF4444', marginBottom: '16px' }}>⚠️</div>
            <h3 className="profile-name" style={{ marginBottom: '12px' }}>ATS Analysis Error</h3>
            <p style={{ color: 'var(--gray-400)', fontSize: '0.875rem', marginBottom: '24px', lineHeight: '1.6' }}>{error}</p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={() => navigate(`/resumes/${resumeId}`)} className="btn btn-outline-dark btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <HiOutlineArrowLeft /> Back to Resume
              </button>
              <button onClick={() => navigate(`/profile/review?resume_id=${resumeId}`)} className="btn btn-primary btn-sm">
                📝 Verify Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const {
    ats_score: overallScore,
    ats_json: details,
    missing_skills: missingSkills = [],
    suggestions = [],
    industry_match: industryMatches = {}
  } = atsData;

  const metadata = details?.metadata || {};
  const primaryIndustry = metadata.primary_industry || 'Software Engineering';

  // Group suggestions by priority
  const sortedSuggestions = [...suggestions].sort((a, b) => {
    const priorities = { critical: 3, important: 2, optional: 1 };
    return (priorities[b.priority] || 0) - (priorities[a.priority] || 0);
  });

  const getScoreColor = (score) => {
    if (score >= 80) return '#10B981'; // Green
    if (score >= 60) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  // Helper for Circular progress math
  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (overallScore / 100) * circumference;

  // Custom SVG Radar Chart math
  const radarCategories = [
    { key: 'keyword_score', label: 'Keywords' },
    { key: 'skills_score', label: 'Skills' },
    { key: 'formatting_score', label: 'Formatting' },
    { key: 'experience_score', label: 'Experience' },
    { key: 'education_score', label: 'Education' },
    { key: 'grammar_score', label: 'Grammar' }
  ];

  const center = 160;
  const maxRadarRadius = 100;

  const getRadarPoints = () => {
    return radarCategories.map((cat, idx) => {
      const value = details?.[cat.key] || 50;
      const angle = (idx * 2 * Math.PI) / radarCategories.length - Math.PI / 2;
      const x = center + (value / 100) * maxRadarRadius * Math.cos(angle);
      const y = center + (value / 100) * maxRadarRadius * Math.sin(angle);
      return { x, y, label: cat.label, angle, val: value };
    });
  };

  const radarPoints = getRadarPoints();
  const radarPath = radarPoints.map(p => `${p.x},${p.y}`).join(' ');

  // Bar Chart calculations
  const barChartCategories = [
    { key: 'keyword_score', label: 'Keywords' },
    { key: 'skills_score', label: 'Skills' },
    { key: 'experience_score', label: 'Exp' },
    { key: 'education_score', label: 'Edu' },
    { key: 'grammar_score', label: 'Grammar' },
    { key: 'formatting_score', label: 'Format' },
    { key: 'industry_score', label: 'Industry' },
    { key: 'completion_score', label: 'Complete' }
  ];

  return (
    <div className="ats-dashboard-page">
      <div className="ats-container">
        
        {/* Header Action Row */}
        <div className="ats-header">
          <div>
            <button onClick={() => navigate(`/resumes/${resumeId}`)} className="btn btn-outline-dark btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '12px', padding: '6px 12px' }}>
              <HiOutlineArrowLeft /> Back to Resume Details
            </button>
            <h1 className="ats-header-title">ATS Analysis Dashboard</h1>
            <div className="ats-header-subtitle">
              Analyzed Resume: <strong style={{ color: 'var(--white)' }}>{atsData.resume_title}</strong>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={() => handleOpenResumeBuilder(navigate, setBuilderLoading)}
              className="btn btn-primary btn-sm"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                borderColor: '#10B981'
              }}
              disabled={builderLoading}
            >
              📝 {builderLoading ? 'Opening...' : 'Open Resume Builder'}
            </button>
            
            <button 
              onClick={() => fetchData(true)} 
              disabled={analyzing} 
              className="btn btn-primary btn-sm"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)', borderColor: '#8B5CF6' }}
            >
              <HiOutlineRefresh className={analyzing ? 'spin-animation' : ''} />
              {analyzing ? 'Re-analyzing...' : 'Recalculate ATS Score'}
            </button>
          </div>
        </div>

        {success && <div className="edit-success" style={{ marginBottom: '24px' }}>{success}</div>}

        {/* Hero Section with Score Circle and Cards */}
        <div className="ats-score-hero-grid">
          
          {/* Circular overall progress */}
          <div className="ats-overall-score-card">
            <div className="circular-progress-container">
              <svg height={radius * 2} width={radius * 2} style={{ transform: 'rotate(-90deg)' }}>
                {/* Background circle */}
                <circle
                  stroke="rgba(255, 255, 255, 0.05)"
                  fill="transparent"
                  strokeWidth={stroke}
                  r={normalizedRadius}
                  cx={radius}
                  cy={radius}
                />
                {/* Fill circle */}
                <circle
                  stroke={getScoreColor(overallScore)}
                  fill="transparent"
                  strokeWidth={stroke}
                  strokeDasharray={circumference + ' ' + circumference}
                  style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.8s ease' }}
                  r={normalizedRadius}
                  cx={radius}
                  cy={radius}
                />
              </svg>
              <div className="circular-progress-text">
                <span className="circular-progress-number">{Math.round(overallScore)}</span>
                <div className="circular-progress-label">ATS Score</div>
              </div>
            </div>
            <div style={{ marginTop: '8px' }}>
              <span className="indicator-badge" style={{ 
                background: `${getScoreColor(overallScore)}18`, 
                borderColor: getScoreColor(overallScore),
                color: getScoreColor(overallScore),
                fontSize: '0.8125rem',
                fontWeight: '700'
              }}>
                {overallScore >= 80 ? 'Excellent Match' : overallScore >= 60 ? 'Average Match' : 'Needs Optimization'}
              </span>
            </div>
            <div style={{ marginTop: '16px', fontSize: '0.75rem', color: 'var(--gray-400)' }}>
              Completed: {new Date(atsData.ats_completed_at).toLocaleString()}
            </div>
          </div>

          {/* Sub-scores grid */}
          <div className="ats-scores-sub-grid">
            
            <div className="ats-sub-score-card">
              <span className="ats-sub-score-title">Primary Industry</span>
              <span className="ats-sub-score-value" style={{ fontSize: '1.2rem', margin: '12px 0' }}>{primaryIndustry}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Match Percentage: {details?.industry_score}%</span>
            </div>

            <div className="ats-sub-score-card">
              <span className="ats-sub-score-title">Keyword Score</span>
              <span className="ats-sub-score-value" style={{ color: getScoreColor(details?.keyword_score) }}>{Math.round(details?.keyword_score)}<span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>/100</span></span>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>{details?.metadata?.keyword_details?.strong_keywords?.length || 0} industry keywords found</span>
            </div>

            <div className="ats-sub-score-card">
              <span className="ats-sub-score-title">Skills Score</span>
              <span className="ats-sub-score-value" style={{ color: getScoreColor(details?.skills_score) }}>{Math.round(details?.skills_score)}<span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>/100</span></span>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Total Skills Listed: {details?.skills_score >= 100 ? '10+' : 'Needs Addition'}</span>
            </div>

            <div className="ats-sub-score-card">
              <span className="ats-sub-score-title">Formatting Score</span>
              <span className="ats-sub-score-value" style={{ color: getScoreColor(details?.formatting_score) }}>{Math.round(details?.formatting_score)}<span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>/100</span></span>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Completeness check: {Math.round(details?.formatting_score / 12.5)}/8 sections</span>
            </div>

            <div className="ats-sub-score-card">
              <span className="ats-sub-score-title">Grammar Score</span>
              <span className="ats-sub-score-value" style={{ color: getScoreColor(details?.grammar_score) }}>{Math.round(details?.grammar_score)}<span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>/100</span></span>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>{details?.metadata?.grammar_details?.passive_voice_count || 0} passive phrases found</span>
            </div>

            <div className="ats-sub-score-card">
              <span className="ats-sub-score-title">Completeness</span>
              <span className="ats-sub-score-value" style={{ color: getScoreColor(details?.completion_score) }}>{details?.completion_score}<span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>%</span></span>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Filled Master Fields</span>
            </div>

          </div>

        </div>

        {/* Charts & Visualization layout */}
        <div className="ats-charts-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px', marginBottom: '24px' }}>
          
          {/* Radar Chart */}
          <div className="ats-card" style={{ marginBottom: 0 }}>
            <h3 className="ats-card-title"><HiOutlineChartBar /> Scoring Dimension Radar</h3>
            <div className="svg-chart-container">
              <svg width="320" height="320" viewBox="0 0 320 320">
                {/* Outer concentric shapes */}
                {[0.2, 0.4, 0.6, 0.8, 1.0].map((scale, sIdx) => {
                  const points = radarCategories.map((cat, idx) => {
                    const angle = (idx * 2 * Math.PI) / radarCategories.length - Math.PI / 2;
                    const x = center + scale * maxRadarRadius * Math.cos(angle);
                    const y = center + scale * maxRadarRadius * Math.sin(angle);
                    return `${x},${y}`;
                  }).join(' ');
                  return (
                    <polygon
                      key={sIdx}
                      points={points}
                      className="svg-radar-grid"
                    />
                  );
                })}

                {/* Radar Grid Axes */}
                {radarPoints.map((p, idx) => (
                  <line
                    key={idx}
                    x1={center}
                    y1={center}
                    x2={center + maxRadarRadius * Math.cos(p.angle)}
                    y2={center + maxRadarRadius * Math.sin(p.angle)}
                    className="svg-radar-axis"
                  />
                ))}

                {/* Radar Value Polygon */}
                <polygon points={radarPath} className="svg-radar-polygon" />

                {/* Axis Value Points */}
                {radarPoints.map((p, idx) => (
                  <circle
                    key={idx}
                    cx={p.x}
                    cy={p.y}
                    r="4"
                    fill="var(--white)"
                    stroke="rgba(139, 92, 246, 1)"
                    strokeWidth="1.5"
                  />
                ))}

                {/* Labels */}
                {radarPoints.map((p, idx) => {
                  const textAnchor = Math.cos(p.angle) > 0.1 ? 'start' : Math.cos(p.angle) < -0.1 ? 'end' : 'middle';
                  const labelRadius = maxRadarRadius + 15;
                  const lx = center + labelRadius * Math.cos(p.angle);
                  const ly = center + labelRadius * Math.sin(p.angle) + 4;
                  return (
                    <text
                      key={idx}
                      x={lx}
                      y={ly}
                      fill="var(--gray-300)"
                      fontSize="10"
                      fontWeight="600"
                      textAnchor={textAnchor}
                    >
                      {p.label} ({p.val})
                    </text>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="ats-card" style={{ marginBottom: 0 }}>
            <h3 className="ats-card-title"><HiOutlineChartBar /> Category Sub-scores</h3>
            <div className="svg-chart-container">
              <svg width="420" height="288" viewBox="0 0 420 288">
                <defs>
                  <linearGradient id="bar-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3B82F6" />
                    <stop offset="100%" stopColor="#8B5CF6" />
                  </linearGradient>
                  <linearGradient id="bar-grad-hover" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#60A5FA" />
                    <stop offset="100%" stopColor="#A78BFA" />
                  </linearGradient>
                </defs>

                {/* Grid lines */}
                {[0, 25, 50, 75, 100].map((gridVal) => {
                  const y = 240 - (gridVal / 100) * 200;
                  return (
                    <g key={gridVal}>
                      <line x1="40" y1={y} x2="400" y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                      <text x="15" y={y + 4} fill="var(--gray-500)" fontSize="10" fontWeight="bold">{gridVal}</text>
                    </g>
                  );
                })}

                {/* Bars */}
                {barChartCategories.map((bar, idx) => {
                  const val = details?.[bar.key] || 50;
                  const x = 50 + idx * 43;
                  const barHeight = (val / 100) * 200;
                  const y = 240 - barHeight;

                  return (
                    <g key={bar.key}>
                      {/* Bar fill */}
                      <rect
                        x={x}
                        y={y}
                        width="24"
                        height={barHeight}
                        rx="3"
                        className="svg-bar-rect"
                      />
                      {/* Score label on top */}
                      <text
                        x={x + 12}
                        y={y - 8}
                        fill="var(--white)"
                        fontSize="10"
                        fontWeight="700"
                        textAnchor="middle"
                      >
                        {Math.round(val)}
                      </text>
                      {/* X Axis Label */}
                      <text
                        x={x + 12}
                        y="256"
                        fill="var(--gray-400)"
                        fontSize="9"
                        fontWeight="600"
                        textAnchor="middle"
                        transform={`rotate(-15, ${x + 12}, 256)`}
                      >
                        {bar.label}
                      </text>
                    </g>
                  );
                })}
                {/* Baseline */}
                <line x1="40" y1="240" x2="400" y2="240" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" />
              </svg>
            </div>
          </div>

        </div>

        {/* Main Sections (Suggestions & Details) */}
        <div className="ats-sections-layout">
          
          {/* Left Panel: Suggestions & Strengths */}
          <div>
            
            {/* Prioritized Suggestions */}
            <div className="ats-card">
              <h3 className="ats-card-title" style={{ color: '#F59E0B' }}><HiOutlineSparkles /> Actionable Improvement Checklist</h3>
              <div className="suggestions-list">
                {sortedSuggestions.length > 0 ? (
                  sortedSuggestions.map((item, idx) => (
                    <div key={idx} className={`suggestion-item ${item.priority}`}>
                      <span className={`suggestion-badge ${item.priority}`}>{item.priority}</span>
                      <div className="suggestion-content">
                        <span className="suggestion-category">{item.category}</span>
                        <div className="suggestion-text">{item.suggestion}</div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ padding: '20px 0', textAlign: 'center', color: '#10B981' }}>
                    <HiOutlineShieldCheck style={{ fontSize: '3rem', marginBottom: '8px' }} />
                    <p style={{ fontWeight: 'bold' }}>All set! No improvements needed.</p>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>Your profile matches excellent ATS structural and styling guidelines.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Strengths & Weaknesses Grid */}
            <div className="ats-card">
              <h3 className="ats-card-title"><HiOutlineShieldCheck /> Resume Strength & Weakness Analysis</h3>
              <div className="strengths-weaknesses-grid">
                
                {/* Strengths */}
                <div>
                  <h4 style={{ fontSize: '0.875rem', color: '#10B981', fontWeight: 'bold', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Strengths</h4>
                  {details?.strengths?.map((str, idx) => (
                    <div key={idx} className="strength-item">
                      <HiOutlineCheckCircle /> <span>{str}</span>
                    </div>
                  ))}
                </div>

                {/* Weaknesses */}
                <div>
                  <h4 style={{ fontSize: '0.875rem', color: '#F59E0B', fontWeight: 'bold', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Weaknesses</h4>
                  {details?.weaknesses?.map((weak, idx) => (
                    <div key={idx} className="weakness-item">
                      <HiOutlineExclamationCircle /> <span>{weak}</span>
                    </div>
                  ))}
                </div>

              </div>
            </div>

            {/* Score History Trends */}
            {history.length > 1 && (
              <div className="ats-card">
                <h3 className="ats-card-title"><HiOutlineChartBar /> Score Progress Over Time</h3>
                <div className="svg-chart-container" style={{ padding: '20px' }}>
                  <svg width="600" height="150" viewBox="0 0 600 150">
                    {/* Grid lines */}
                    {[50, 75, 100].map((gridY, gIdx) => {
                      const y = 130 - (gridY / 100) * 100;
                      return (
                        <g key={gIdx}>
                          <line x1="40" y1={y} x2="560" y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                          <text x="15" y={y + 4} fill="var(--gray-500)" fontSize="9" fontWeight="bold">{gridY}</text>
                        </g>
                      );
                    })}

                    {/* Plot history line */}
                    {(() => {
                      const widthInterval = 500 / (history.length - 1);
                      const points = history.map((run, hIdx) => {
                        const x = 50 + hIdx * widthInterval;
                        const y = 130 - (parseFloat(run.ats_score) / 100) * 100;
                        return { x, y, score: run.ats_score, date: new Date(run.ats_completed_at).toLocaleDateString() };
                      });

                      const pathD = `M ${points.map(p => `${p.x} ${p.y}`).join(' L ')}`;

                      return (
                        <g>
                          {/* Smooth Line */}
                          <path d={pathD} fill="none" stroke="rgba(139, 92, 246, 0.7)" strokeWidth="3" />
                          
                          {/* Point Dots */}
                          {points.map((p, dotIdx) => (
                            <g key={dotIdx}>
                              <circle cx={p.x} cy={p.y} r="5" fill="#3B82F6" stroke="var(--white)" strokeWidth="1.5" />
                              <text x={p.x} y={p.y - 10} fill="var(--white)" fontSize="9" fontWeight="bold" textAnchor="middle">{Math.round(p.score)}</text>
                              <text x={p.x} y="145" fill="var(--gray-400)" fontSize="8" fontWeight="bold" textAnchor="middle">{p.date}</text>
                            </g>
                          ))}
                        </g>
                      );
                    })()}
                  </svg>
                </div>
              </div>
            )}

          </div>

          {/* Right Panel: Industry Match & Missing Skills Gap */}
          <div>
            
            {/* Industry Match Percentage */}
            <div className="ats-card">
              <h3 className="ats-card-title"><HiOutlineChevronRight /> Industry Match Scores</h3>
              <div className="industry-match-list">
                {Object.entries(industryMatches).slice(0, 10).map(([ind, pct]) => (
                  <div key={ind} className="industry-match-row">
                    <span className="industry-match-name" style={{ color: ind === primaryIndustry ? '#A78BFA' : 'var(--gray-200)', fontWeight: ind === primaryIndustry ? 'bold' : '500' }}>
                      {ind === primaryIndustry ? '⭐ ' : ''}{ind}
                    </span>
                    <div className="industry-match-bar-bg">
                      <div 
                        className="industry-match-bar-fill" 
                        style={{ 
                          width: `${pct}%`,
                          background: ind === primaryIndustry 
                            ? 'linear-gradient(90deg, #8B5CF6, #EC4899)' 
                            : 'linear-gradient(90deg, #A78BFA, #3B82F6)'
                        }}
                      ></div>
                    </div>
                    <span className="industry-match-percentage">{pct}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Skill Gaps (Missing Skills Tag Grid) */}
            <div className="ats-card">
              <h3 className="ats-card-title"><HiOutlinePlusCircle /> Recommended Missing Skills</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '16px', lineHeight: '1.5' }}>
                Adding these standard tools and skills matching the <strong>{primaryIndustry}</strong> industry will boost your keyword search relevancy:
              </p>
              <div className="missing-skills-grid">
                {missingSkills.length > 0 ? (
                  missingSkills.map((skill, idx) => (
                    <div key={idx} className="missing-skill-tag">
                      <span>+ {skill}</span>
                    </div>
                  ))
                ) : (
                  <div style={{ color: '#10B981', fontSize: '0.875rem', fontWeight: 'bold' }}>
                    ✅ Excellent! No major missing skills found for your role.
                  </div>
                )}
              </div>
              <button 
                onClick={() => navigate(`/profile/review?resume_id=${resumeId}`)} 
                className="btn btn-outline-dark btn-sm"
                style={{ width: '100%', marginTop: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                📝 Edit Profile to Add Skills
              </button>
            </div>

            {/* Technical Keywords Found */}
            <div className="ats-card">
              <h3 className="ats-card-title"><HiOutlineCheckCircle /> Strong Keywords Identified</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '12px' }}>
                Keywords detected and matched against the target profile:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {metadata.keyword_details?.strong_keywords?.length > 0 ? (
                  metadata.keyword_details.strong_keywords.map((kw, idx) => (
                    <span key={idx} style={{ 
                      fontSize: '0.75rem', 
                      padding: '4px 10px', 
                      background: 'rgba(59, 130, 246, 0.08)', 
                      border: '1px solid rgba(59, 130, 246, 0.25)', 
                      color: '#60A5FA',
                      fontWeight: 'bold',
                      borderRadius: '4px'
                    }}>
                      {kw}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8125rem', color: 'var(--gray-400)' }}>None detected. Add industry jargon.</span>
                )}
              </div>
            </div>

            {/* Weak Keywords Detected */}
            {metadata.keyword_details?.weak_keywords?.length > 0 && (
              <div className="ats-card">
                <h3 className="ats-card-title" style={{ color: '#EF4444' }}><HiOutlineExclamationCircle /> Avoid Buzzwords</h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '12px' }}>
                  These low-impact/cliché terms were found in your resume. Swap them out for strong metric results:
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {metadata.keyword_details.weak_keywords.map((kw, idx) => (
                    <span key={idx} style={{ 
                      fontSize: '0.75rem', 
                      padding: '4px 10px', 
                      background: 'rgba(239, 68, 68, 0.08)', 
                      border: '1px solid rgba(239, 68, 68, 0.25)', 
                      color: '#F87171',
                      fontWeight: 'bold',
                      borderRadius: '4px'
                    }}>
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}

          </div>

        </div>

      </div>
    </div>
  );
};

export default ATSDashboard;

/**
 * ATSDashboard – Real-time ATS scoring, benchmark comparisons, keyword evaluation,
 * custom SVG charts, job matching, and actionable prioritized recommendations.
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
  HiOutlineRefresh,
  HiOutlineBriefcase,
  HiOutlineDownload,
  HiOutlineLibrary
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

  // Job matching states
  const [jobDescription, setJobDescription] = useState('');
  const [matchingJob, setMatchingJob] = useState(false);
  const [jobMatchResult, setJobMatchResult] = useState(null);

  // Recommendation filter state
  const [priorityFilter, setPriorityFilter] = useState('all');

  // Rule configurator states
  const [activeTab, setActiveTab] = useState('summary');
  const [rules, setRules] = useState([]);
  const [rulesLoading, setRulesLoading] = useState(false);
  const [rulesSearchQuery, setRulesSearchQuery] = useState('');
  const [rulesCategoryFilter, setRulesCategoryFilter] = useState('All');
  const [rulesProfessionFilter, setRulesProfessionFilter] = useState('All');
  const [editingRule, setEditingRule] = useState(null);
  const [savingRule, setSavingRule] = useState(false);

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

  const fetchRules = async () => {
    try {
      setRulesLoading(true);
      const res = await atsAPI.getRules();
      setRules(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch ATS rules list.');
    } finally {
      setRulesLoading(false);
    }
  };

  const handleToggleRule = async (rule) => {
    try {
      const updatedEnabled = !rule.enabled;
      // Optimistic update
      setRules(prev => prev.map(r => r.id === rule.id ? { ...r, enabled: updatedEnabled } : r));
      await atsAPI.updateRule(rule.id, { enabled: updatedEnabled });
      setSuccess(`Rule '${rule.name}' updated successfully!`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError('Failed to update rule.');
      // Revert on error
      setRules(prev => prev.map(r => r.id === rule.id ? { ...r, enabled: rule.enabled } : r));
    }
  };

  const handleSaveRuleEdit = async (e) => {
    e.preventDefault();
    if (!editingRule) return;
    setSavingRule(true);
    setError('');
    try {
      const res = await atsAPI.updateRule(editingRule.id, {
        points: parseInt(editingRule.points),
        severity: editingRule.severity,
        recommendation: editingRule.recommendation,
        enabled: editingRule.enabled
      });
      setRules(prev => prev.map(r => r.id === editingRule.id ? res.data : r));
      setEditingRule(null);
      setSuccess('Rule configuration updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to save rule changes.');
    } finally {
      setSavingRule(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchData();
    }
  }, [resumeId]);

  useEffect(() => {
    if (activeTab === 'rules' && rules.length === 0) {
      fetchRules();
    }
  }, [activeTab]);

  // Handle Job Match Analysis
  const handleJobMatch = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim()) return;

    setMatchingJob(true);
    setError('');
    try {
      const res = await atsAPI.matchJob(resumeId, jobDescription);
      setJobMatchResult(res.data);
      setSuccess('Job matching completed!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError('Failed to calculate job-specific matching score.');
    } finally {
      setMatchingJob(false);
    }
  };

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

  if (error && !atsData) {
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

  // Destructure ATS data from backend payload
  const overallScore = atsData.overall_score || 0;
  const confidence = atsData.confidence || 90;
  const jobReady = atsData.job_ready || false;
  const parsingQuality = atsData.parsing_quality || 95;
  const strengths = atsData.strengths || [];
  const weaknesses = atsData.weaknesses || [];
  const recommendations = atsData.recommendations || [];
  const subscores = atsData.subscores || {};
  const metadata = atsData.metadata || {};
  const benchmarkComparison = atsData.benchmark_comparison || {};
  const profession = metadata.profession || 'Software Engineer';

  // Group recommendations by priority
  const filteredRecommendations = recommendations.filter(rec => {
    if (priorityFilter === 'all') return true;
    return rec.priority.toLowerCase() === priorityFilter.toLowerCase();
  });

  const getScoreColor = (score) => {
    if (score >= 90) return '#10B981'; // Green
    if (score >= 80) return '#3B82F6'; // Blue
    if (score >= 70) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  const getScoreCategory = (score) => {
    if (score >= 95) return 'Excellent';
    if (score >= 90) return 'Very Strong';
    if (score >= 80) return 'Competitive';
    if (score >= 70) return 'Average';
    if (score >= 60) return 'Needs Improvement';
    return 'High Improvement Needed';
  };

  // Helper for Circular progress math
  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (overallScore / 100) * circumference;

  // Radar chart categories based on subscores
  const radarCategories = [
    { key: 'keywords', label: 'Keywords' },
    { key: 'skills', label: 'Skills' },
    { key: 'skill_relevance', label: 'Relevance' },
    { key: 'formatting', label: 'Formatting' },
    { key: 'experience_quality', label: 'Exp Quality' },
    { key: 'consistency', label: 'Consistency' }
  ];

  const center = 160;
  const maxRadarRadius = 100;

  const radarPoints = radarCategories.map((cat, idx) => {
    const value = subscores[cat.key] || 50;
    const angle = (idx * 2 * Math.PI) / radarCategories.length - Math.PI / 2;
    const x = center + (value / 100) * maxRadarRadius * Math.cos(angle);
    const y = center + (value / 100) * maxRadarRadius * Math.sin(angle);
    return { x, y, label: cat.label, angle, val: value };
  });

  const radarPath = radarPoints.map(p => `${p.x},${p.y}`).join(' ');

  // Group subscores by categories
  const categories = {
    "Structure & Compatibility": [
      { key: "structure", label: "Structural Relevancy" },
      { key: "compatibility", label: "ATS File Compatibility" },
      { key: "formatting", label: "Formatting & Style" },
      { key: "readability", label: "Readability Score" }
    ],
    "Core Details & Quality": [
      { key: "contact", label: "Contact Completeness" },
      { key: "summary", label: "Summary & Pitch" },
      { key: "skills", label: "Skills Density" },
      { key: "skill_relevance", label: "Skill Industry Relevance" }
    ],
    "Experience & Professional Standing": [
      { key: "experience", label: "Experience Coverage" },
      { key: "experience_quality", label: "Work Quality & Depth" },
      { key: "projects", label: "Project Focus" },
      { key: "project_quality", label: "Project Proofs & Live Links" }
    ],
    "Additional Credentials": [
      { key: "education", label: "Academic Relevancy" },
      { key: "certifications", label: "Industry Credentials" },
      { key: "achievements", label: "Key Achievements" },
      { key: "leadership", label: "Leadership Indicators" }
    ],
    "Jargon & Language Analytics": [
      { key: "keywords", label: "Keyword Matching" },
      { key: "grammar", label: "Grammar & Proofing" },
      { key: "action_verbs", label: "Strong Action Verbs" },
      { key: "quantified_achievements", label: "Quantified Results" }
    ],
    "Online Presence & Integrity": [
      { key: "portfolio", label: "Portfolio Presence" },
      { key: "linkedin", label: "LinkedIn Profiling" },
      { key: "github", label: "GitHub Validation" },
      { key: "progression", label: "Career Progression" },
      { key: "consistency", label: "Timeline Consistency" }
    ]
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="ats-dashboard-page">
      <div className="ats-container">
        
        {/* Header Action Row */}
        <div className="ats-header no-print">
          <div>
            <button onClick={() => navigate(`/resumes/${resumeId}`)} className="btn btn-outline-dark btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '12px', padding: '6px 12px' }}>
              <HiOutlineArrowLeft /> Back to Resume Details
            </button>
            <h1 className="ats-header-title">ATS Intelligence Dashboard</h1>
            <div className="ats-header-subtitle">
              Role Focus: <strong style={{ color: 'var(--white)' }}>{profession}</strong>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button 
              onClick={() => navigate(`/resumes/${resumeId}/explainable-ats`)} 
              className="btn btn-primary btn-sm"
              style={{ 
                display: 'inline-flex', 
                alignItems: 'center', 
                gap: '8px', 
                background: 'linear-gradient(135deg, #EC4899 0%, #D946EF 100%)', 
                borderColor: '#EC4899',
                fontWeight: '600'
              }}
            >
              🧠 Explainable ATS
            </button>
            <button 
              onClick={handlePrint}
              className="btn btn-outline-dark btn-sm"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <HiOutlineDownload /> Export Report
            </button>
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

        {success && <div className="edit-success no-print" style={{ marginBottom: '24px' }}>{success}</div>}

        {/* Navigation Tabs */}
        <div className="no-print" style={{ 
          display: 'flex', 
          gap: '12px', 
          marginBottom: '24px', 
          borderBottom: '1px solid var(--glass-border)', 
          paddingBottom: '12px' 
        }}>
          <button 
            onClick={() => setActiveTab('summary')}
            className={`btn btn-sm ${activeTab === 'summary' ? 'btn-primary' : 'btn-outline-dark'}`}
            style={{ 
              fontSize: '0.875rem', 
              fontWeight: '600', 
              padding: '8px 16px',
              background: activeTab === 'summary' ? 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)' : 'transparent',
              borderColor: activeTab === 'summary' ? '#8B5CF6' : 'var(--glass-border)'
            }}
          >
            📊 Evaluation Summary
          </button>
          <button 
            onClick={() => setActiveTab('rules')}
            className={`btn btn-sm ${activeTab === 'rules' ? 'btn-primary' : 'btn-outline-dark'}`}
            style={{ 
              fontSize: '0.875rem', 
              fontWeight: '600', 
              padding: '8px 16px',
              background: activeTab === 'rules' ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'transparent',
              borderColor: activeTab === 'rules' ? '#10B981' : 'var(--glass-border)'
            }}
          >
            ⚙️ ATS Rule Engine Configurator
          </button>
        </div>

        {activeTab === 'summary' && (
          <>
            {/* Hero Section: Gauge, Confidence, Parsing Quality */}
            <div className="ats-score-hero-grid">
              
              {/* Circular overall progress */}
              <div className="ats-overall-score-card">
                <div className="circular-progress-container">
                  <svg height={radius * 2} width={radius * 2} style={{ transform: 'rotate(-90deg)' }}>
                    <circle
                      stroke="rgba(255, 255, 255, 0.05)"
                      fill="transparent"
                      strokeWidth={stroke}
                      r={normalizedRadius}
                      cx={radius}
                      cy={radius}
                    />
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
                    <span className="circular-progress-number">{overallScore}</span>
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
                    {getScoreCategory(overallScore)}
                  </span>
                </div>
                <div style={{ marginTop: '16px', display: 'flex', gap: '16px', fontSize: '0.8125rem' }}>
                  <div>
                    <div style={{ color: 'var(--gray-400)' }}>Confidence</div>
                    <div style={{ color: 'var(--white)', fontWeight: 'bold' }}>{confidence}%</div>
                  </div>
                  <div style={{ width: '1px', background: 'var(--glass-border)' }}></div>
                  <div>
                    <div style={{ color: 'var(--gray-400)' }}>Parsing</div>
                    <div style={{ color: 'var(--white)', fontWeight: 'bold' }}>{parsingQuality}%</div>
                  </div>
                </div>
              </div>

              {/* Benchmark comparison card */}
              <div className="ats-overall-score-card" style={{ alignItems: 'stretch', justifyContent: 'center', textAlign: 'left' }}>
                <h3 className="ats-card-title" style={{ border: 'none', padding: 0, marginBottom: '12px' }}>
                  <HiOutlineLibrary /> Professional Benchmarks
                </h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '16px' }}>
                  How your resume compares to thousands of peer profiles evaluated for <strong>{profession}</strong> roles.
                </p>
                {benchmarkComparison.average_score ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                      <span>Standing: <strong style={{ color: '#10B981' }}>{benchmarkComparison.candidate_standing}</strong></span>
                      <span>Percentile: <strong style={{ color: '#8B5CF6' }}>{benchmarkComparison.candidate_percentile_range}</strong></span>
                    </div>
                    
                    {/* Visual Percentile Slider */}
                    <div style={{ position: 'relative', height: '8px', background: 'var(--glass-border)', borderRadius: '4px', marginTop: '24px', marginBottom: '8px' }}>
                      {/* Marker points */}
                      <div style={{ position: 'absolute', left: '25%', top: '-6px', width: '2px', height: '14px', background: 'var(--gray-500)' }} title="25th Percentile" />
                      <div style={{ position: 'absolute', left: '50%', top: '-6px', width: '2px', height: '14px', background: 'var(--gray-400)' }} title="50th Percentile (Average)" />
                      <div style={{ position: 'absolute', left: '75%', top: '-6px', width: '2px', height: '14px', background: 'var(--gray-500)' }} title="75th Percentile" />
                      <div style={{ position: 'absolute', left: '90%', top: '-6px', width: '2px', height: '14px', background: 'var(--gray-500)' }} title="90th Percentile" />
                      
                      {/* Candidate score marker */}
                      <div style={{ 
                        position: 'absolute', 
                        left: `${overallScore}%`, 
                        top: '-8px', 
                        width: '18px', 
                        height: '18px', 
                        background: getScoreColor(overallScore), 
                        borderRadius: '50%', 
                        border: '3px solid var(--white)',
                        transform: 'translateX(-50%)',
                        boxShadow: '0 0 10px rgba(139, 92, 246, 0.5)'
                      }} />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--gray-500)' }}>
                      <span>Low ({benchmarkComparison.percentile_25})</span>
                      <span>Avg ({benchmarkComparison.percentile_50})</span>
                      <span>High ({benchmarkComparison.percentile_75})</span>
                      <span>Top ({benchmarkComparison.percentile_90})</span>
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '10px 0', color: 'var(--gray-400)' }}>
                    No benchmark data available.
                  </div>
                )}
              </div>

            </div>

            {/* Phase D: Penalty & Bonus Adjustments Section */}
            {metadata.adjustments ? (
              <div className="ats-card score-adjustments-card" style={{ marginBottom: '24px' }}>
                <h3 className="ats-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px' }}>
                  <HiOutlineSparkles style={{ color: '#8B5CF6' }} /> Penalty & Bonus Score Adjustments
                </h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '20px' }}>
                  Professional ATS systems apply positive and negative scoring adjustments. Here is your resume's adjustments pipeline.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                  
                  {/* Base Score */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '10px', border: '1px solid var(--glass-border)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--gray-400)', textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.05em' }}>BASE QUALITY SCORE</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--white)', marginTop: '8px' }}>{metadata.adjustments.base_score}</div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--gray-500)', marginTop: '4px' }}>Unadjusted score</div>
                  </div>

                  {/* Penalties */}
                  <div style={{ background: 'rgba(239, 68, 68, 0.05)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(239, 68, 68, 0.2)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#EF4444', textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.05em' }}>PENALTIES DEDUCTED</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#EF4444', marginTop: '8px' }}>
                      {metadata.adjustments.penalties > 0 ? `-${metadata.adjustments.penalties}` : metadata.adjustments.penalties}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--gray-500)', marginTop: '4px' }}>Clamped max -30</div>
                  </div>

                  {/* Bonuses */}
                  <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(16, 185, 129, 0.2)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#10B981', textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.05em' }}>BONUS REWARDS</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10B981', marginTop: '8px' }}>
                      {metadata.adjustments.bonuses > 0 ? `+${metadata.adjustments.bonuses}` : metadata.adjustments.bonuses}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--gray-500)', marginTop: '4px' }}>Clamped max +20</div>
                  </div>

                  {/* Final Score */}
                  <div style={{ background: 'linear-gradient(135deg, rgba(139,92,246,0.1), rgba(139,92,246,0.2))', padding: '16px', borderRadius: '10px', border: '1px solid rgba(139,92,246,0.3)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#a78bfa', textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.05em' }}>FINAL ATS SCORE</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#a78bfa', marginTop: '8px' }}>{metadata.adjustments.final_score}</div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--gray-500)', marginTop: '4px' }}>Clamped 0 - 100</div>
                  </div>

                </div>

                {/* Detailed breakdowns */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }} className="adjustments-breakdown-grid">
                  
                  {/* Penalties List */}
                  <div style={{ background: 'var(--glass-bg)', padding: '18px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 'bold', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', marginTop: 0 }}>
                      <HiOutlineExclamationCircle /> Active Penalties ({metadata.adjustments.penalty_report?.length || 0})
                    </h4>
                    {metadata.adjustments.penalty_report && metadata.adjustments.penalty_report.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '260px', overflowY: 'auto', padding: '4px 6px 4px 2px' }}>
                        {metadata.adjustments.penalty_report.map((p, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(239, 68, 68, 0.08)', padding: '10px 14px', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)', fontSize: '0.85rem', lineHeight: '1.4' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                              <strong style={{ color: 'var(--text-color)' }}>{p.name}</strong>
                              <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)', background: 'var(--glass-bg)', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--glass-border)' }}>({p.category})</span>
                            </div>
                            <span style={{ color: 'var(--danger)', fontWeight: '800', fontSize: '0.9rem', background: 'rgba(239,68,68,0.15)', padding: '3px 8px', borderRadius: '6px', whiteSpace: 'nowrap' }}>{p.points}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ fontSize: '0.85rem', color: 'var(--subtext-color)', margin: 0 }}>Clean profile! No penalties applied.</p>
                    )}
                  </div>

                  {/* Bonuses List */}
                  <div style={{ background: 'var(--glass-bg)', padding: '18px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 'bold', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', marginTop: 0 }}>
                      <HiOutlineCheckCircle /> Active Bonuses ({metadata.adjustments.bonus_report?.length || 0})
                    </h4>
                    {metadata.adjustments.bonus_report && metadata.adjustments.bonus_report.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '260px', overflowY: 'auto', padding: '4px 6px 4px 2px' }}>
                        {metadata.adjustments.bonus_report.map((b, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(16, 185, 129, 0.08)', padding: '10px 14px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)', fontSize: '0.85rem', lineHeight: '1.4' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                              <strong style={{ color: 'var(--text-color)' }}>{b.name}</strong>
                              <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)', background: 'var(--glass-bg)', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--glass-border)' }}>({b.category})</span>
                            </div>
                            <span style={{ color: 'var(--success)', fontWeight: '800', fontSize: '0.9rem', background: 'rgba(16,185,129,0.15)', padding: '3px 8px', borderRadius: '6px', whiteSpace: 'nowrap' }}>+{b.points}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ fontSize: '0.85rem', color: 'var(--subtext-color)', margin: 0 }}>No bonuses applied. Enhance your profile to get score boosts.</p>
                    )}
                  </div>

                </div>
              </div>
            ) : (
              <div className="ats-card" style={{ textAlign: 'center', padding: '24px', marginBottom: '24px', borderColor: 'var(--glass-border)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--gray-400)', marginBottom: '12px' }}>
                  Penalty & Bonus adjustments are not computed yet for this resume.
                </p>
                <button
                  onClick={() => fetchData(true)}
                  className="btn btn-outline-dark btn-sm"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                >
                  <HiOutlineRefresh /> Generate Score Adjustments
                </button>
              </div>
            )}

            {/* Dimension Radar Chart */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }} className="ats-charts-grid">
              
              <div className="ats-card" style={{ marginBottom: 0 }}>
                <h3 className="ats-card-title"><HiOutlineChartBar /> Core Assessment Dimensions</h3>
                <div className="svg-chart-container">
                  <svg width="320" height="320" viewBox="0 0 320 320">
                    {/* Concentric rings */}
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

              {/* Job description matching input card */}
              <div className="ats-card" style={{ marginBottom: 0 }}>
                <h3 className="ats-card-title"><HiOutlineBriefcase /> Job description Matching</h3>
                
                {!jobMatchResult ? (
                  <form onSubmit={handleJobMatch} style={{ display: 'flex', flexDirection: 'column', height: 'calc(100% - 40px)', justifyContent: 'space-between' }}>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '12px' }}>
                      Paste a target Job Description to run the Job Match algorithm, detecting skills gaps, keyword match, and experience alignments.
                    </p>
                    <textarea
                      className="form-control"
                      style={{ flex: 1, minHeight: '120px', background: 'rgba(255,255,255,0.02)', borderColor: 'var(--glass-border)', color: 'var(--white)', borderRadius: '8px', padding: '12px', fontSize: '0.875rem' }}
                      placeholder="Paste job description here..."
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      required
                    />
                    <button
                      type="submit"
                      disabled={matchingJob}
                      className="btn btn-primary"
                      style={{ width: '100%', marginTop: '16px', background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)', borderColor: '#3B82F6' }}
                    >
                      {matchingJob ? 'Analyzing Job Alignment...' : 'Analyze Job Match'}
                    </button>
                  </form>
                ) : (
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
                      <div style={{ position: 'relative', width: '90px', height: '90px' }}>
                        <svg height="90" width="90" style={{ transform: 'rotate(-90deg)' }}>
                          <circle stroke="rgba(255, 255, 255, 0.05)" fill="transparent" strokeWidth="8" r="36" cx="45" cy="45" />
                          <circle
                            stroke={getScoreColor(jobMatchResult.metadata?.job_specific_results?.job_match)}
                            fill="transparent"
                            strokeWidth="8"
                            strokeDasharray={`${2 * 36 * Math.PI} ${2 * 36 * Math.PI}`}
                            strokeDashoffset={2 * 36 * Math.PI - (jobMatchResult.metadata?.job_specific_results?.job_match / 100) * 2 * 36 * Math.PI}
                            r="36"
                            cx="45"
                            cy="45"
                          />
                        </svg>
                        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                          <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{jobMatchResult.metadata?.job_specific_results?.job_match}%</span>
                        </div>
                      </div>
                      <div>
                        <h4 style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--white)' }}>Estimated Job Match Score</h4>
                        <span className="indicator-badge" style={{ 
                          marginTop: '6px',
                          background: `${getScoreColor(jobMatchResult.metadata?.job_specific_results?.job_match)}18`, 
                          borderColor: getScoreColor(jobMatchResult.metadata?.job_specific_results?.job_match),
                          color: getScoreColor(jobMatchResult.metadata?.job_specific_results?.job_match),
                        }}>
                          {jobMatchResult.metadata?.job_specific_results?.job_match >= 85 ? 'Highly Recommended' : 'Partially Recommended'}
                        </span>
                      </div>
                    </div>

                    {/* Sub score matches breakdown */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                      <div style={{ background: 'rgba(255,255,255,0.01)', padding: '10px', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                        <div style={{ fontSize: '0.6875rem', color: 'var(--gray-400)' }}>Skills Match</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'var(--white)' }}>{jobMatchResult.metadata?.job_specific_results?.skill_match || 0}%</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.01)', padding: '10px', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                        <div style={{ fontSize: '0.6875rem', color: 'var(--gray-400)' }}>Experience Match</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'var(--white)' }}>{jobMatchResult.metadata?.job_specific_results?.experience_match || 0}%</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.01)', padding: '10px', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                        <div style={{ fontSize: '0.6875rem', color: 'var(--gray-400)' }}>Education Alignment</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'var(--white)' }}>{jobMatchResult.metadata?.job_specific_results?.education_match || 0}%</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.01)', padding: '10px', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                        <div style={{ fontSize: '0.6875rem', color: 'var(--gray-400)' }}>Certification Match</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'var(--white)' }}>{jobMatchResult.metadata?.job_specific_results?.certification_match || 0}%</div>
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        setJobMatchResult(null);
                        setJobDescription('');
                      }}
                      className="btn btn-outline-dark btn-sm"
                      style={{ width: '100%', marginTop: '16px' }}
                    >
                      Reset Job Matching
                    </button>
                  </div>
                )}

              </div>

            </div>

            {/* Actionable Improvement Checklist */}
            <div className="ats-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px', marginBottom: '20px' }}>
                <h3 className="ats-card-title" style={{ border: 'none', padding: 0, margin: 0 }}>
                  <HiOutlineSparkles style={{ color: '#F59E0B' }} /> Actionable Optimization Suggestions
                </h3>
                
                {/* Filter buttons */}
                <div style={{ display: 'flex', gap: '8px' }} className="no-print">
                  {['all', 'important', 'optional'].map(p => (
                    <button
                      key={p}
                      onClick={() => setPriorityFilter(p)}
                      className={`btn btn-sm ${priorityFilter === p ? 'btn-primary' : 'btn-outline-dark'}`}
                      style={{ fontSize: '0.75rem', textTransform: 'capitalize', padding: '4px 10px' }}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="suggestions-list">
                {filteredRecommendations.length > 0 ? (
                  filteredRecommendations.map((item, idx) => (
                    <div key={idx} className={`suggestion-item ${item.priority}`}>
                      <span className={`suggestion-badge ${item.priority}`}>{item.priority}</span>
                      <div className="suggestion-content">
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span className="suggestion-category">{item.category}</span>
                          <span style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 'bold' }}>+{item.potential_boost} pts boost</span>
                        </div>
                        <div className="suggestion-text">{item.suggestion}</div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ padding: '20px 0', textAlign: 'center', color: '#10B981' }}>
                    <HiOutlineShieldCheck style={{ fontSize: '3rem', marginBottom: '8px' }} />
                    <p style={{ fontWeight: 'bold' }}>All set! No matching improvements found.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="ats-card">
              <h3 className="ats-card-title"><HiOutlineShieldCheck /> Profile Strengths & Weaknesses</h3>
              <div className="strengths-weaknesses-grid">
                
                {/* Strengths */}
                <div>
                  <h4 style={{ fontSize: '0.875rem', color: '#10B981', fontWeight: 'bold', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Strengths</h4>
                  {strengths.map((str, idx) => (
                    <div key={idx} className="strength-item">
                      <HiOutlineCheckCircle /> <span>{str}</span>
                    </div>
                  ))}
                </div>

                {/* Weaknesses */}
                <div>
                  <h4 style={{ fontSize: '0.875rem', color: '#F59E0B', fontWeight: 'bold', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Areas of Weakness</h4>
                  {weaknesses.map((weak, idx) => (
                    <div key={idx} className="weakness-item">
                      <HiOutlineExclamationCircle /> <span>{weak}</span>
                    </div>
                  ))}
                </div>

              </div>
            </div>

            {/* Detailed breakdown of 25 subscores */}
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--white)', marginTop: '36px', marginBottom: '20px' }}>
              Detailed Category Score breakdown
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }} className="ats-charts-grid">
              {Object.entries(categories).map(([catName, fields]) => (
                <div key={catName} className="ats-card" style={{ marginBottom: 0 }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--white)', marginBottom: '16px' }}>{catName}</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {fields.map(f => {
                      const val = subscores[f.key] || 0;
                      return (
                        <div key={f.key}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', marginBottom: '4px' }}>
                            <span style={{ color: 'var(--gray-300)' }}>{f.label}</span>
                            <span style={{ fontWeight: 'bold', color: getScoreColor(val) }}>{Math.round(val)}%</span>
                          </div>
                          <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${val}%`, background: getScoreColor(val), borderRadius: '3px' }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {activeTab === 'rules' && (
          <div>
            {/* Stats Banner */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '24px' }} className="ats-score-hero-grid">
              <div className="ats-overall-score-card" style={{ padding: '20px', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10B981' }}>{rules.length}</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>Total Seeded Rules</span>
              </div>
              <div className="ats-overall-score-card" style={{ padding: '20px', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3B82F6' }}>{rules.filter(r => r.enabled).length}</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>Active Rules</span>
              </div>
              <div className="ats-overall-score-card" style={{ padding: '20px', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '2rem', fontWeight: 'bold', color: '#F59E0B' }}>{rules.filter(r => !r.enabled).length}</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>Disabled Rules</span>
              </div>
              <div className="ats-overall-score-card" style={{ padding: '20px', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '2rem', fontWeight: 'bold', color: '#EF4444' }}>{rules.filter(r => r.points < 0).length}</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>Penalty Rules</span>
              </div>
            </div>

            {/* Filter controls */}
            <div className="ats-card" style={{ padding: '20px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: '250px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', color: 'var(--subtext-color)', marginBottom: '8px', fontWeight: 600 }}>Search Rules</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search by code or name..."
                    value={rulesSearchQuery}
                    onChange={(e) => setRulesSearchQuery(e.target.value)}
                    style={{ background: 'var(--glass-bg)', borderColor: 'var(--glass-border)', color: 'var(--text-color)', borderRadius: '8px', padding: '10px 14px' }}
                  />
                </div>
                <div style={{ width: '200px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', color: 'var(--subtext-color)', marginBottom: '8px', fontWeight: 600 }}>Category</label>
                  <select
                    className="form-control"
                    value={rulesCategoryFilter}
                    onChange={(e) => setRulesCategoryFilter(e.target.value)}
                    style={{ background: 'var(--bg-primary)', borderColor: 'var(--glass-border)', color: 'var(--text-color)', borderRadius: '8px', padding: '10px 14px' }}
                  >
                    <option value="All">All Categories</option>
                    {['Contact', 'Summary', 'Skills', 'Experience', 'Projects', 'Education', 'Certifications', 'Achievements', 'Formatting', 'Grammar', 'Portfolio', 'GitHub', 'LinkedIn', 'ATS Parsing', 'Consistency', 'Keyword Quality', 'Career Progression', 'Leadership', 'Soft Skills', 'Job Match'].map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div style={{ width: '200px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', color: 'var(--subtext-color)', marginBottom: '8px', fontWeight: 600 }}>Profession</label>
                  <select
                    className="form-control"
                    value={rulesProfessionFilter}
                    onChange={(e) => setRulesProfessionFilter(e.target.value)}
                    style={{ background: 'var(--bg-primary)', borderColor: 'var(--glass-border)', color: 'var(--text-color)', borderRadius: '8px', padding: '10px 14px' }}
                  >
                    <option value="All">All Professions</option>
                    {['All', 'Software Engineering', 'Full Stack', 'Backend', 'Frontend', 'AI/ML', 'Data Science', 'Mechanical', 'Civil', 'Electrical', 'Chemical', 'HR', 'Marketing', 'Finance', 'Accounting', 'Doctor', 'Teacher', 'Lawyer', 'Freelancer', 'Student', 'Designer', 'Journalist', 'Researcher'].map(prof => (
                      <option key={prof} value={prof}>{prof}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Rules List */}
            {rulesLoading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <p style={{ color: 'var(--gray-400)' }}>Loading rules configuration...</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {rules
                  .filter(r => {
                    const matchesSearch = r.name.toLowerCase().includes(rulesSearchQuery.toLowerCase()) || 
                                          r.rule_code.toLowerCase().includes(rulesSearchQuery.toLowerCase());
                    const matchesCategory = rulesCategoryFilter === 'All' || r.category_name === rulesCategoryFilter;
                    const matchesProfession = rulesProfessionFilter === 'All' || r.profession === rulesProfessionFilter;
                    return matchesSearch && matchesCategory && matchesProfession;
                  })
                  .map(rule => (
                    <div key={rule.id} className="ats-card" style={{ 
                      marginBottom: 0, 
                      padding: '20px', 
                      borderColor: rule.enabled ? 'var(--glass-border)' : 'rgba(239,68,68,0.15)',
                      opacity: rule.enabled ? 1 : 0.65
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '8px' }}>
                            <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#10B981', fontFamily: 'monospace', background: 'rgba(16,185,129,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                              {rule.rule_code}
                            </span>
                            <span className="indicator-badge" style={{ 
                              background: rule.severity === 'critical' ? 'rgba(239,68,68,0.1)' : rule.severity === 'high' ? 'rgba(245,158,11,0.1)' : 'rgba(255,255,255,0.05)',
                              borderColor: rule.severity === 'critical' ? '#EF4444' : rule.severity === 'high' ? '#F59E0B' : 'var(--glass-border)',
                              color: rule.severity === 'critical' ? '#EF4444' : rule.severity === 'high' ? '#F59E0B' : 'var(--gray-300)',
                            }}>
                              {rule.severity}
                            </span>
                            <span className="indicator-badge" style={{ background: 'rgba(139,92,246,0.1)', borderColor: '#8B5CF6', color: '#8B5CF6' }}>
                              {rule.profession}
                            </span>
                            <span className="indicator-badge" style={{ background: 'var(--glass-bg)', borderColor: 'var(--glass-border)', color: 'var(--subtext-color)' }}>
                              {rule.category_name}
                            </span>
                          </div>
                          <h4 style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--text-color)', marginBottom: '8px' }}>{rule.name}</h4>
                          <p style={{ fontSize: '0.8125rem', color: 'var(--subtext-color)', marginBottom: '12px' }}>{rule.description}</p>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>Condition:</span>
                            <code style={{ fontSize: '0.75rem', color: 'var(--primary)', background: 'var(--glass-bg)', padding: '2px 6px', borderRadius: '4px', fontFamily: 'monospace', border: '1px solid var(--glass-border)' }}>
                              {rule.condition}
                            </code>
                          </div>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px', minWidth: '120px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: rule.points >= 0 ? '#10B981' : '#EF4444' }}>
                              {rule.points >= 0 ? `+${rule.points}` : rule.points} pts
                            </span>
                            <div style={{ position: 'relative', display: 'inline-block', width: '40px', height: '24px' }}>
                              <input 
                                type="checkbox" 
                                checked={rule.enabled} 
                                onChange={() => handleToggleRule(rule)}
                                style={{ display: 'none' }}
                                id={`toggle_${rule.id}`}
                              />
                              <label 
                                htmlFor={`toggle_${rule.id}`}
                                style={{
                                  display: 'block',
                                  width: '100%',
                                  height: '100%',
                                  borderRadius: '12px',
                                  background: rule.enabled ? '#10B981' : '#374151',
                                  cursor: 'pointer',
                                  position: 'relative',
                                  transition: 'background 0.3s'
                                }}
                              >
                                <span style={{
                                  display: 'block',
                                  width: '18px',
                                  height: '18px',
                                  borderRadius: '50%',
                                  background: 'white',
                                  position: 'absolute',
                                  top: '3px',
                                  left: rule.enabled ? '19px' : '3px',
                                  transition: 'left 0.3s'
                                }} />
                              </label>
                            </div>
                          </div>
                          <button 
                            onClick={() => setEditingRule(rule)} 
                            className="btn btn-outline-dark btn-sm"
                            style={{ padding: '4px 12px', width: '100%' }}
                          >
                            Configure
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        )}

        {/* Rule Editor Overlay Modal */}
        {editingRule && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.85)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            backdropFilter: 'blur(8px)'
          }}>
            <div className="ats-card" style={{
              width: '100%',
              maxWidth: '600px',
              margin: 0,
              background: 'rgba(20, 20, 25, 0.95)',
              boxShadow: '0 0 30px rgba(16, 185, 129, 0.2)',
              border: '1px solid rgba(16, 185, 129, 0.4)'
            }}>
              <h3 className="ats-card-title" style={{ color: '#10B981', borderBottomColor: 'var(--glass-border)', paddingBottom: '12px' }}>
                Configure Rule: {editingRule.rule_code}
              </h3>
              <form onSubmit={handleSaveRuleEdit} style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
                <div>
                  <label style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Rule Name</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    value={editingRule.name} 
                    onChange={(e) => setEditingRule({ ...editingRule, name: e.target.value })} 
                    required 
                    style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'var(--glass-border)', color: 'var(--white)', borderRadius: '8px', padding: '10px' }}
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Points / Score Impact</label>
                    <input 
                      type="number" 
                      className="form-control" 
                      value={editingRule.points} 
                      onChange={(e) => setEditingRule({ ...editingRule, points: e.target.value })} 
                      required 
                      style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'var(--glass-border)', color: 'var(--white)', borderRadius: '8px', padding: '10px' }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Severity</label>
                    <select 
                      className="form-control" 
                      value={editingRule.severity} 
                      onChange={(e) => setEditingRule({ ...editingRule, severity: e.target.value })}
                      style={{ background: 'rgba(20,20,25,0.95)', borderColor: 'var(--glass-border)', color: 'var(--white)', borderRadius: '8px', padding: '10px' }}
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Python Evaluation Condition (Read Only)</label>
                  <pre style={{ 
                    background: 'rgba(0,0,0,0.3)', 
                    border: '1px solid var(--glass-border)', 
                    padding: '10px', 
                    borderRadius: '6px', 
                    fontSize: '0.75rem', 
                    color: '#34D399',
                    overflowX: 'auto',
                    fontFamily: 'monospace'
                  }}>
                    {editingRule.condition}
                  </pre>
                </div>
                <div>
                  <label style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Actionable Recommendation on Failure</label>
                  <textarea 
                    className="form-control" 
                    rows="3"
                    value={editingRule.recommendation} 
                    onChange={(e) => setEditingRule({ ...editingRule, recommendation: e.target.value })} 
                    required 
                    style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'var(--glass-border)', color: 'var(--white)', fontSize: '0.875rem', borderRadius: '8px', padding: '10px' }}
                  />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input 
                    type="checkbox" 
                    id="rule_enabled" 
                    checked={editingRule.enabled} 
                    onChange={(e) => setEditingRule({ ...editingRule, enabled: e.target.checked })}
                  />
                  <label htmlFor="rule_enabled" style={{ fontSize: '0.875rem', color: 'var(--white)' }}>Enable this rule in ATS evaluations</label>
                </div>
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '12px' }}>
                  <button type="button" onClick={() => setEditingRule(null)} className="btn btn-outline-dark">Cancel</button>
                  <button type="submit" disabled={savingRule} className="btn btn-primary" style={{ background: '#10B981', borderColor: '#10B981' }}>
                    {savingRule ? 'Saving...' : 'Save Configuration'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default ATSDashboard;

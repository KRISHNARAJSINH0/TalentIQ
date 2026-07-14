import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiOutlineSparkles, 
  HiOutlineArrowPath, 
  HiOutlineCheckCircle, 
  HiOutlineExclamationTriangle,
  HiOutlineAcademicCap,
  HiOutlineGlobeAlt,
  HiOutlineShieldCheck,
  HiOutlineArrowTrendingUp,
  HiOutlineCheckBadge,
  HiOutlineDocumentText,
  HiOutlineCpuChip,
  HiOutlineLockClosed,
  HiOutlineStar
} from 'react-icons/hi2';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  BarChart, 
  Bar, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

import { reputationAPI } from '../api/reputation';
import { resumesAPI } from '../api/resumes';
import GlassCard from '../components/GlassCard';
import SkeletonLoader from '../components/SkeletonLoader';
import '../styles/ReputationDashboard.css';

// Mapping backend badge name to icon classes
const ICON_MAP = {
  "ATS Master": { icon: HiOutlineCpuChip, color: "#D4AF37", glow: "rgba(212, 175, 55, 0.4)", border: "rgba(212, 175, 55, 0.3)" },
  "Portfolio Pro": { icon: HiOutlineGlobeAlt, color: "#60A5FA", glow: "rgba(96, 165, 250, 0.4)", border: "rgba(96, 165, 250, 0.3)" },
  "Top Performer": { icon: HiOutlineStar, color: "#F472B6", glow: "rgba(244, 114, 182, 0.4)", border: "rgba(244, 114, 182, 0.3)" },
  "Fast Learner": { icon: HiOutlineAcademicCap, color: "#34D399", glow: "rgba(52, 211, 153, 0.4)", border: "rgba(52, 211, 153, 0.3)" },
  "Career Ready": { icon: HiOutlineShieldCheck, color: "#A78BFA", glow: "rgba(167, 139, 250, 0.4)", border: "rgba(167, 139, 250, 0.3)" },
  "High Demand Talent": { icon: HiOutlineArrowTrendingUp, color: "#FB923C", glow: "rgba(251, 146, 60, 0.4)", border: "rgba(251, 146, 60, 0.3)" },
  "Elite Candidate": { icon: HiOutlineSparkles, color: "#E879F9", glow: "rgba(232, 121, 249, 0.4)", border: "rgba(232, 121, 249, 0.3)" }
};

const ALL_BADGES = [
  { name: "ATS Master", description: "Demonstrates exceptional keyword density, strong action verbs, and optimal formatting." },
  { name: "Portfolio Pro", description: "Showcases an outstanding, fully configured, and public web portfolio presence." },
  { name: "Top Performer", description: "Indicates deep domain expertise, leadership milestones, and technical project depth." },
  { name: "Fast Learner", description: "Highlights high learning activity, roadmap completions, and certifications." },
  { name: "Career Ready", description: "Equipped with complete technical, structural, and professional career attributes." },
  { name: "High Demand Talent", description: "Possesses specialized capabilities in high-growth, high-salary industry domains." },
  { name: "Elite Candidate", description: "Stands in the top percentile of talent globally for resume and industry stature." }
];

const TIER_COLORS = {
  "Elite": { bg: "rgba(212, 175, 55, 0.12)", border: "rgba(212, 175, 55, 0.4)", text: "#D4AF37", glow: "rgba(212, 175, 55, 0.35)" },
  "Excellent": { bg: "rgba(16, 185, 129, 0.12)", border: "rgba(16, 185, 129, 0.4)", text: "#10B981", glow: "rgba(16, 185, 129, 0.35)" },
  "Strong": { bg: "rgba(59, 130, 246, 0.12)", border: "rgba(59, 130, 246, 0.4)", text: "#3B82F6", glow: "rgba(59, 130, 246, 0.35)" },
  "Average": { bg: "rgba(139, 92, 246, 0.12)", border: "rgba(139, 92, 246, 0.4)", text: "#8B5CF6", glow: "rgba(139, 92, 246, 0.35)" },
  "Weak": { bg: "rgba(249, 115, 22, 0.12)", border: "rgba(249, 115, 22, 0.4)", text: "#F97316", glow: "rgba(249, 115, 22, 0.35)" },
  "Needs Improvement": { bg: "rgba(239, 68, 68, 0.12)", border: "rgba(239, 68, 68, 0.4)", text: "#EF4444", glow: "rgba(239, 68, 68, 0.35)" }
};

const MOCK_REPUTATION_DATA = {
  score: 75,
  tier: "Strong",
  details_json: {
    sub_scores: {
      ats: 82,
      skills: 75,
      projects: 80,
      portfolio: 70,
      experience: 78,
      consistency: 85,
      career: 80,
      demand: 72,
      growth: 76,
      learning: 82
    },
    industry_rank: { rank: 12, pool_size: 150, statement: "You place in the top 8% of industry software candidates." },
    benchmarks: [
      { category: "Students", score: 58, type: "benchmark" },
      { category: "Freshers", score: 65, type: "benchmark" },
      { category: "Designers", score: 75, type: "benchmark" },
      { category: "Industry Average", score: 72, type: "benchmark" },
      { category: "Software Engineers", score: 80, type: "benchmark" },
      { category: "You", score: 78, type: "candidate" },
      { category: "Top 10%", score: 85, type: "benchmark" },
      { category: "Top 5%", score: 90, type: "benchmark" }
    ],
    badges: [
      { name: "ATS Master" },
      { name: "Fast Learner" },
      { name: "Career Ready" }
    ],
    strengths: [
      "Excellent technical keyword density in professional experience sections.",
      "High project complexity score with multiple framework integrations."
    ],
    weaknesses: [
      "Digital portfolio link is missing or not configured as public.",
      "Lower experience milestones relative to target profile level."
    ],
    suggestions: [
      { text: "Configure a public digital portfolio presence", category: "Portfolio", priority: "critical", points: 15 },
      { text: "Add at least two expert-level technical skills", category: "Skills", priority: "important", points: 10 },
      { text: "Target keyword optimization for ATS scanning", category: "ATS Score", priority: "optional", points: 5 }
    ]
  }
};

const ReputationDashboard = () => {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [activeResumeId, setActiveResumeId] = useState('');
  const [reputationData, setReputationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loadingMessage, setLoadingMessage] = useState('Evaluating profile indicators...');

  // Loading message animation helper
  useEffect(() => {
    if (!calculating) return;
    const messages = [
      "Analyzing resume parsing formats...",
      "Evaluating keyword matches against industry...",
      "Auditing project complexity metrics...",
      "Checking consistency records...",
      "Estimating promotion potential and growth...",
      "Awarding descriptive credentials..."
    ];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % messages.length;
      setLoadingMessage(messages[idx]);
    }, 2000);
    return () => clearInterval(interval);
  }, [calculating]);

  // Fetch initial resume list
  const fetchResumesList = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await resumesAPI.getResumes();
      const resumesData = res.data?.results || res.data;
      const resumesArray = Array.isArray(resumesData) ? resumesData : [];
      setResumes(resumesArray);
      if (resumesArray.length > 0) {
        const active = resumesArray.find(r => r.is_active);
        const defaultId = active ? active.id : resumesArray[0].id;
        setActiveResumeId(defaultId);
      } else {
        // No resumes found: load preview mode
        setReputationData(MOCK_REPUTATION_DATA);
        setLoading(false);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch resumes. Please upload/create a resume first.');
      // Load mock for fallback styling preview
      setReputationData(MOCK_REPUTATION_DATA);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumesList();
  }, []);

  // Fetch reputation data when selected resume changes
  const fetchReputation = async (resumeId, forceRecalc = false) => {
    if (!resumeId) return;
    try {
      if (forceRecalc) {
        setCalculating(true);
        setError('');
      } else {
        setLoading(true);
      }

      let res;
      if (forceRecalc) {
        res = await reputationAPI.calculateReputation(resumeId);
        setSuccess('Reputation metrics updated successfully!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        res = await reputationAPI.getReputation(resumeId);
      }
      setReputationData(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to load reputation analysis.');
    } finally {
      setLoading(false);
      setCalculating(false);
    }
  };

  useEffect(() => {
    if (activeResumeId) {
      fetchReputation(activeResumeId);
    }
  }, [activeResumeId]);

  const handleRecalculate = () => {
    if (activeResumeId) {
      fetchReputation(activeResumeId, true);
    }
  };

  if (loading) {
    return (
      <div className="reputation-page">
        <SkeletonLoader type="card" />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
          <SkeletonLoader type="card" />
          <SkeletonLoader type="card" />
        </div>
      </div>
    );
  }

  const isEmpty = resumes.length === 0;

  // Pre-process metrics
  const score = reputationData?.score || 0;
  const tier = reputationData?.tier || "Average";
  const tierStyle = TIER_COLORS[tier] || TIER_COLORS["Average"];
  const details = reputationData?.details_json || {};
  const subScores = details.sub_scores || {};
  const industryRank = details.industry_rank || { rank: 50, pool_size: 200, statement: "Industry rank pending analysis" };

  // Format Recharts Radar Data
  const radarData = [
    { subject: 'ATS Score', value: subScores.ats || 0 },
    { subject: 'Skills', value: subScores.skills || 0 },
    { subject: 'Projects', value: subScores.projects || 0 },
    { subject: 'Portfolio', value: subScores.portfolio || 0 },
    { subject: 'Experience', value: subScores.experience || 0 },
    { subject: 'Consistency', value: subScores.consistency || 0 },
    { subject: 'Career', value: subScores.career || 0 },
    { subject: 'Demand', value: subScores.demand || 0 },
    { subject: 'Growth', value: subScores.growth || 0 },
    { subject: 'Learning', value: subScores.learning || 0 }
  ];

  // Circular progress ring calculations
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Custom tooltips for Recharts
  const CustomRadarTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel" style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.95)', border: '1px solid var(--glass-border)', borderRadius: '12px', fontSize: '0.85rem', boxShadow: '0 8px 30px rgba(0,0,0,0.3)' }}>
          <span style={{ fontWeight: 600, color: 'var(--primary)' }}>{payload[0].name}: </span>
          <span style={{ fontWeight: 700, color: '#fff' }}>{payload[0].value}/100</span>
        </div>
      );
    }
    return null;
  };

  const CustomBarTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isCandidate = data.type === 'candidate';
      return (
        <div className="glass-panel" style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.95)', border: `1px solid ${isCandidate ? 'var(--primary)' : 'var(--glass-border)'}`, borderRadius: '12px', fontSize: '0.85rem', boxShadow: '0 8px 30px rgba(0,0,0,0.3)' }}>
          <span style={{ fontWeight: 600, color: isCandidate ? 'var(--primary)' : '#94A3B8' }}>{data.category}: </span>
          <span style={{ fontWeight: 700, color: '#fff' }}>{data.score}</span>
        </div>
      );
    }
    return null;
  };

  if (isEmpty) {
    return (
      <div className="reputation-onboarding-container">
        <div className="onboarding-header">
          <span className="onboarding-badge">REPUTATION SYSTEM</span>
          <h1>Resume Reputation Engine</h1>
          <p>Verify your professional stature, employability tier, and earn descriptive credentials relative to candidate peer groups.</p>
        </div>

        <div className="onboarding-grid">
          <div className="onboarding-card">
            <div className="onboarding-icon-wrapper" style={{ color: 'var(--primary)' }}>
              <HiOutlineCpuChip size={32} />
            </div>
            <h3>ATS & Keyword Audit</h3>
            <p>Measure resume layout compliance, keyword density, and key action verbs with high precision.</p>
          </div>

          <div className="onboarding-card">
            <div className="onboarding-icon-wrapper" style={{ color: '#FB923C' }}>
              <HiOutlineCheckBadge size={32} />
            </div>
            <h3>Descriptive Credentials</h3>
            <p>Earn verified credentials like ATS Master, Portfolio Pro, and Elite Candidate based on profile depth.</p>
          </div>

          <div className="onboarding-card">
            <div className="onboarding-icon-wrapper" style={{ color: 'var(--success)' }}>
              <HiOutlineArrowTrendingUp size={32} />
            </div>
            <h3>Global Benchmarking</h3>
            <p>Compare your credentials, learning consistency, and skill sets against target industry averages.</p>
          </div>
        </div>

        <div className="onboarding-cta">
          <h2>Ready to calculate your reputation?</h2>
          <p>Upload a resume or build one using our interactive builder to begin your evaluation.</p>
          <Link to="/resumes" className="btn-recalc" style={{ textDecoration: 'none', padding: '14px 36px', fontSize: '1rem', marginTop: '12px', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <HiOutlineSparkles size={18} /> Upload or Build Resume
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="reputation-page">
      {/* SVG definitions for beautiful chart gradient fills */}
      <svg style={{ height: 0, width: 0, position: 'absolute' }}>
        <defs>
          <linearGradient id="radarFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.45}/>
            <stop offset="100%" stopColor="#7C3AED" stopOpacity={0.15}/>
          </linearGradient>
          <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#7C3AED" stopOpacity={0.7}/>
            <stop offset="100%" stopColor="var(--primary)" stopOpacity={0.95}/>
          </linearGradient>
        </defs>
      </svg>

      <div>
        {/* Top Header Card */}
        <GlassCard hoverEffect={false} className="reputation-header">
          <div className="reputation-header-text">
            <h1>
              <span style={{ color: 'var(--primary)', display: 'inline-flex', alignItems: 'center' }}>
                <HiOutlineCheckBadge size={28} style={{ marginRight: '8px' }} />
              </span>
              Resume Reputation System
            </h1>
            <p>
              Audit and measure your standing, consistency profile, portfolio stature, and employability tier.
            </p>
          </div>

          <div className="reputation-header-actions">
            <select 
              value={activeResumeId} 
              onChange={(e) => setActiveResumeId(e.target.value)} 
              className="resume-select"
              disabled={isEmpty}
            >
              {isEmpty ? (
                <option>Demo Resume (Preview)</option>
              ) : (
                resumes.map(r => (
                  <option key={r.id} value={r.id}>
                    {r.resume_title} {r.is_active ? '(Active)' : ''}
                  </option>
                ))
              )}
            </select>

            <button 
              onClick={handleRecalculate} 
              className="btn-recalc"
              disabled={calculating || isEmpty}
            >
              <HiOutlineArrowPath size={16} className={calculating ? 'spin' : ''} />
              {calculating ? 'Running Analysis...' : 'Recalculate Reputation'}
            </button>
          </div>
        </GlassCard>

        {/* Message Notifications */}
        <AnimatePresence>
          {success && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }} 
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="notification-banner"
              style={{ backgroundColor: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', color: 'var(--success)' }}
            >
              <HiOutlineCheckCircle size={18} />
              {success}
            </motion.div>
          )}
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }} 
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="notification-banner"
              style={{ backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', color: 'var(--danger)' }}
            >
              <HiOutlineExclamationTriangle size={18} />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {calculating ? (
          <GlassCard hoverEffect={false} className="loading-box">
            <div className="loader-pulse">
              <div className="loader-ring"></div>
              <div className="loader-ring"></div>
              <div className="loader-ring"></div>
            </div>
            <div className="loading-text">{loadingMessage}</div>
          </GlassCard>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', marginTop: '4px' }}>
            {/* Hero Section: Circular progress & radar chart */}
            <div className="reputation-hero-grid">
              {/* Left: Circular progress ring */}
              <GlassCard hoverEffect={true} className="hero-progress-card">
                <div className="progress-ring-container">
                  <svg className="progress-ring-svg" width="220" height="220">
                    <circle
                      className="progress-ring-bg"
                      strokeWidth="8"
                      fill="transparent"
                      r={radius}
                      cx="110"
                      cy="110"
                    />
                    <circle
                      className="progress-ring-fill"
                      strokeWidth="10"
                      stroke={tierStyle.text}
                      fill="transparent"
                      r={radius}
                      cx="110"
                      cy="110"
                      style={{
                        strokeDasharray: circumference,
                        strokeDashoffset: strokeDashoffset,
                        filter: `drop-shadow(0 0 12px ${tierStyle.glow})`
                      }}
                    />
                  </svg>
                  <div className="progress-ring-text">
                    <span className="progress-score-num">{score}</span>
                    <span className="progress-score-label">Reputation</span>
                  </div>
                </div>

                <div 
                  className="tier-badge" 
                  style={{
                    backgroundColor: tierStyle.bg,
                    border: `1px solid ${tierStyle.border}`,
                    color: tierStyle.text,
                    boxShadow: `0 4px 20px ${tierStyle.glow}`
                  }}
                >
                  <HiOutlineSparkles />
                  {tier} Stature
                </div>

                <p className="rank-text">{industryRank.statement}</p>
              </GlassCard>

              {/* Right: Radar Chart */}
              <GlassCard hoverEffect={true} style={{ padding: '28px', minHeight: '360px', background: 'var(--gradient-card)', border: '1px solid var(--glass-border)' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
                  <HiOutlineSparkles size={20} style={{ color: 'var(--primary)' }} />
                  Reputation Dimensions
                </h2>
                <div style={{ width: '100%', height: '300px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                      <PolarGrid stroke="var(--glass-border)" />
                      <PolarAngleAxis dataKey="subject" stroke="var(--subtext-color)" fontSize={11} fontWeight={500} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tickCount={6} stroke="var(--glass-border)" fontSize={10} />
                      <Radar
                        name="Dimension Score"
                        dataKey="value"
                        stroke="var(--primary)"
                        fill="url(#radarFill)"
                        fillOpacity={1}
                      />
                      <Tooltip content={<CustomRadarTooltip />} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </GlassCard>
            </div>

            {/* Secondary Grid: Benchmarks & Badges */}
            <div className="reputation-sec-grid">
              {/* Left: Benchmarks Comparison */}
              <GlassCard hoverEffect={true} className="benchmarks-card" style={{ minHeight: '380px' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
                  <HiOutlineArrowTrendingUp size={20} style={{ color: 'var(--success)' }} />
                  Global Standing Comparisons
                </h2>
                <div style={{ width: '100%', height: '300px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={details.benchmarks || []}
                      layout="vertical"
                      margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} stroke="var(--subtext-color)" fontSize={11} />
                      <YAxis dataKey="category" type="category" stroke="var(--subtext-color)" fontSize={11} width={120} />
                      <Tooltip content={<CustomBarTooltip />} />
                      <Bar
                        dataKey="score"
                        radius={[0, 6, 6, 0]}
                        fill="url(#barGradient)"
                      >
                        {(details.benchmarks || []).map((entry, index) => {
                          const isCandidate = entry.type === 'candidate';
                          return (
                            <Cell
                              key={`cell-${index}`}
                              fill={isCandidate ? 'var(--primary)' : 'rgba(255, 255, 255, 0.06)'}
                              stroke={isCandidate ? 'var(--primary)' : 'var(--glass-border)'}
                              strokeWidth={isCandidate ? 2 : 1}
                              style={{
                                filter: isCandidate ? 'drop-shadow(0 0 10px rgba(37, 99, 235, 0.5))' : 'none'
                              }}
                            />
                          );
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </GlassCard>

              {/* Right: Badges Grid */}
              <GlassCard hoverEffect={true} className="badges-card">
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
                  <HiOutlineCheckBadge size={20} style={{ color: '#FB923C' }} />
                  Descriptive Credentials
                </h2>
                <p style={{ color: 'var(--subtext-color)', fontSize: '0.88rem', margin: 0, fontFamily: 'var(--font-body)' }}>
                  Unlock high-level credentials based on your profile and resume depth.
                </p>

                <div className="badges-grid">
                  {ALL_BADGES.map((badgeInfo, bIdx) => {
                    // Check if user earned this badge
                    const earnedBadge = details.badges?.find(b => b.name === badgeInfo.name);
                    const isEarned = !!earnedBadge;
                    const config = ICON_MAP[badgeInfo.name];
                    const Icon = config ? config.icon : HiOutlineCheckBadge;
                    const badgeColor = config ? config.color : "#6B7280";

                    return (
                      <div 
                        key={bIdx} 
                        className={`badge-item-card ${isEarned ? 'earned' : 'unearned'}`}
                        title={badgeInfo.description}
                        style={{
                          borderColor: (isEarned && config) ? config.border : 'rgba(255, 255, 255, 0.05)',
                          boxShadow: (isEarned && config) ? `0 4px 15px ${config.glow}` : 'none'
                        }}
                      >
                        {!isEarned && (
                          <div className="badge-lock-icon">
                            <HiOutlineLockClosed size={10} />
                          </div>
                        )}
                        <div className="badge-icon-wrapper" style={{ color: isEarned ? badgeColor : 'var(--subtext-color)' }}>
                          <Icon />
                        </div>
                        <span className="badge-name" style={{ color: isEarned ? 'var(--text-color)' : 'var(--subtext-color)' }}>{badgeInfo.name}</span>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>
            </div>

            {/* Tertiary Section: Strengths, Weaknesses, suggestions */}
            <div className="reputation-details-grid">
              {/* Left: Strengths & Weaknesses */}
              <GlassCard hoverEffect={true} className="details-card">
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
                  <HiOutlineDocumentText size={20} style={{ color: 'var(--primary)' }} />
                  Stature Profile Analysis
                </h2>
                
                <div className="details-list">
                  {/* Strengths */}
                  {details.strengths?.map((str, sIdx) => (
                    <div key={sIdx} className="strength-item">
                      <HiOutlineCheckCircle size={18} />
                      <span>{str}</span>
                    </div>
                  ))}

                  {/* Weaknesses */}
                  {details.weaknesses?.map((wk, wIdx) => (
                    <div key={wIdx} className="weakness-item">
                      <HiOutlineExclamationTriangle size={18} />
                      <span>{wk}</span>
                    </div>
                  ))}

                  {(!details.strengths?.length && !details.weaknesses?.length) && (
                    <p style={{ color: 'var(--subtext-color)', fontSize: '0.9rem', margin: 0, fontFamily: 'var(--font-body)' }}>
                      Analysis checklist is complete. No critical highlights found.
                    </p>
                  )}
                </div>
              </GlassCard>

              {/* Right: Recommendations */}
              <GlassCard hoverEffect={true} className="details-card">
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
                  <HiOutlineSparkles size={20} style={{ color: '#8B5CF6' }} />
                  Actionable Recommendations
                </h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {details.suggestions?.map((sug, suIdx) => (
                    <div key={suIdx} className="suggestion-row">
                      <div className="suggestion-info">
                        <span className="suggestion-text">{sug.text}</span>
                        <div className="suggestion-meta">
                          <span className="suggestion-category">{sug.category}</span>
                          <span>•</span>
                          <span className={`suggestion-priority ${sug.priority}`}>{sug.priority}</span>
                        </div>
                      </div>
                      <button 
                        onClick={() => {
                          if (isEmpty) return;
                          if (sug.category === "Portfolio") {
                            navigate('/portfolio');
                          } else if (sug.category === "Skills" || sug.category === "Projects") {
                            navigate('/profile');
                          } else if (sug.category === "ATS Score") {
                            navigate(`/resumes/${activeResumeId}/ats`);
                          } else if (sug.category === "Learning") {
                            navigate('/career');
                          }
                        }}
                        className="btn-action-suggest"
                      >
                        +{sug.points} pts
                      </button>
                    </div>
                  ))}

                  {(!details.suggestions || details.suggestions.length === 0) && (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px', textAlign: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '2.5rem' }}>✨</span>
                      <h4 style={{ margin: 0, fontFamily: 'var(--font-heading)' }}>Excellent Profile Stature!</h4>
                      <p style={{ color: 'var(--subtext-color)', fontSize: '0.88rem', margin: 0, fontFamily: 'var(--font-body)' }}>
                        You have fully optimized your resume, skills match, projects depth, and digital portfolio presence.
                      </p>
                    </div>
                  )}
                </div>
              </GlassCard>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReputationDashboard;

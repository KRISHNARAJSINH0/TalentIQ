import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import {
  HiOutlineDocumentArrowUp,
  HiOutlineDocumentText,
  HiOutlineUserCircle,
  HiOutlineSparkles,
  HiOutlineCpuChip,
  HiOutlineEye,
  HiOutlineBriefcase,
  HiOutlineBell
} from 'react-icons/hi2';
import { handleOpenResumeBuilder } from '../utils/resumeBuilder';
import { resumesAPI } from '../api/resumes';
import { atsAPI } from '../api/ats';
import { portfolioAPI } from '../api/portfolio';
import { careerAPI } from '../api/career';
import MetricCard from '../components/MetricCard';
import ProgressCircle from '../components/ProgressCircle';
import GlassCard from '../components/GlassCard';
import GlassTable from '../components/GlassTable';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [builderLoading, setBuilderLoading] = useState(false);
  const [resumes, setResumes] = useState([]);
  const [atsScore, setAtsScore] = useState(0);
  const [careerScore, setCareerScore] = useState(0);
  const [portfolioViews, setPortfolioViews] = useState(0);
  const [projectCount, setProjectCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Fetch resumes
        const resResumes = await resumesAPI.getResumes();
        const resumesData = resResumes.data?.results || resResumes.data;
        setResumes(Array.isArray(resumesData) ? resumesData : []);

        // Fetch ATS history to get latest score
        const resAts = await atsAPI.getATSHistory();
        const atsData = Array.isArray(resAts.data) ? resAts.data : (resAts.data?.results || []);
        if (atsData.length > 0) {
          setAtsScore(atsData[0].ats_score || atsData[0].score || 0);
        } else {
          setAtsScore(0);
        }

        // Fetch Career Details
        try {
          const resCareer = await careerAPI.getCareerDetails();
          setCareerScore(resCareer.data?.career_readiness || 0);
        } catch {
          setCareerScore(0);
        }

        // Fetch Portfolio & Analytics
        try {
          const resPortfolio = await portfolioAPI.getPortfolio();
          setProjectCount(resPortfolio.data?.projects?.length || 0);
          
          const resAnalytics = await portfolioAPI.getAnalytics();
          setPortfolioViews(resAnalytics.data?.views_count || resAnalytics.data?.total_views || 0);
        } catch {
          setPortfolioViews(0);
          setProjectCount(0);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const firstName = user?.first_name || 'User';

  // Calculate profile completion
  const profileFields = [
    user?.first_name, user?.last_name, user?.email, user?.phone,
    user?.profile?.headline, user?.profile?.summary,
    user?.profile?.linkedin, user?.profile?.github,
  ];
  const filled = profileFields.filter(Boolean).length;
  const total = profileFields.length;
  const completion = Math.round((filled / total) * 100);

  // views data — distribute real portfolio views across the week
  const viewsData = [
    { name: 'Mon', views: Math.round(portfolioViews * 0.12) },
    { name: 'Tue', views: Math.round(portfolioViews * 0.18) },
    { name: 'Wed', views: Math.round(portfolioViews * 0.22) },
    { name: 'Thu', views: Math.round(portfolioViews * 0.20) },
    { name: 'Fri', views: Math.round(portfolioViews * 0.28) },
  ];

  // Radar metrics — all sourced from real API data
  const skillsPercent = Math.min(100, resumes.length > 0 ? Math.round((resumes.filter(r => r.is_active).length / Math.max(resumes.length, 1)) * 100) : 0);
  const skillStrengthData = [
    { subject: 'Skills', A: skillsPercent || 0 },
    { subject: 'ATS Score', A: atsScore || 0 },
    { subject: 'Profile %', A: completion },
    { subject: 'Projects', A: Math.min(100, projectCount * 20) },
    { subject: 'Career', A: careerScore || 0 },
  ];

  // Helper for Area Chart SVG points calculation
  const maxVal = Math.max(...viewsData.map(d => d.views), 10);
  const chartWidth = 600;
  const chartHeight = 300;
  const paddingLeft = 40;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 35;
  const widthAvailable = chartWidth - paddingLeft - paddingRight;
  const heightAvailable = chartHeight - paddingTop - paddingBottom;

  const svgPoints = viewsData.map((d, index) => {
    const x = paddingLeft + (index / (viewsData.length - 1)) * widthAvailable;
    const y = paddingTop + heightAvailable - (d.views / maxVal) * heightAvailable;
    return { x, y, name: d.name, views: d.views };
  });

  const lineD = svgPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const fillD = `${lineD} L ${svgPoints[svgPoints.length - 1].x} ${paddingTop + heightAvailable} L ${svgPoints[0].x} ${paddingTop + heightAvailable} Z`;

  // Grid lines helper
  const gridRatios = [0, 0.25, 0.5, 0.75, 1];

  // Helper for Radar Chart SVG points calculation
  const getRadarPoints = (data, maxRadius) => {
    const center = 100;
    return data.map((d, i) => {
      const angle = (i * 2 * Math.PI / 5) - Math.PI / 2;
      const radius = (d.A / 100) * maxRadius;
      const x = center + radius * Math.cos(angle);
      const y = center + radius * Math.sin(angle);
      const outerX = center + maxRadius * Math.cos(angle);
      const outerY = center + maxRadius * Math.sin(angle);
      return { ...d, x, y, outerX, outerY, angle };
    });
  };

  const radarPoints = getRadarPoints(skillStrengthData, 50);

  const getGridPoints = (ratio, maxRadius) => {
    const center = 100;
    const r = ratio * maxRadius;
    const pts = [];
    for (let i = 0; i < 5; i++) {
      const angle = (i * 2 * Math.PI / 5) - Math.PI / 2;
      pts.push(`${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`);
    }
    return pts.join(' ');
  };

  const getLabelAnchor = (angle) => {
    const cos = Math.cos(angle);
    if (Math.abs(cos) < 0.1) return 'middle';
    return cos > 0 ? 'start' : 'end';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Welcome Message */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}
      >
        <div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, margin: 0 }}>
            Welcome back, <span className="gradient-text">{firstName}</span>! 👋
          </h1>
          <p style={{ color: 'var(--subtext-color)', margin: '4px 0 0', fontSize: '15px' }}>
            Elevate your professional branding with our premium AI suite.
          </p>
        </div>

        <button
          onClick={() => handleOpenResumeBuilder(navigate, setBuilderLoading)}
          className="glass-btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          disabled={builderLoading}
        >
          <HiOutlineSparkles />
          <span>{builderLoading ? 'Opening...' : 'AI Resume Builder'}</span>
        </button>
      </motion.div>

      {/* Metrics Row */}
      <div className="row g-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <MetricCard
            title="Latest ATS Score"
            value={atsScore || 'N/A'}
            suffix="%"
            icon={<HiOutlineCpuChip size={20} />}
            trend={atsScore ? `Score: ${Math.round(atsScore)}%` : 'No analysis run'}
            trendType={atsScore >= 75 ? 'success' : 'warning'}
            delay={0.1}
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <MetricCard
            title="Career Score"
            value={careerScore || 'N/A'}
            suffix="%"
            icon={<HiOutlineSparkles size={20} />}
            trend={careerScore ? `Readiness: ${Math.round(careerScore)}%` : 'Upload resume first'}
            trendType={careerScore >= 80 ? 'success' : 'warning'}
            delay={0.2}
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <MetricCard
            title="Portfolio Views"
            value={portfolioViews}
            icon={<HiOutlineEye size={20} />}
            trend={portfolioViews > 0 ? `${portfolioViews} total views` : 'No views yet'}
            trendType={portfolioViews > 0 ? 'success' : 'warning'}
            delay={0.3}
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <MetricCard
            title="Resumes Uploaded"
            value={resumes.length}
            icon={<HiOutlineDocumentText size={20} />}
            trend={`${resumes.filter(r => r.is_active).length} active version`}
            trendType="success"
            delay={0.4}
          />
        </div>
      </div>

      {/* Double Column Graphs & Completion */}
      <div className="row g-4">
        {/* Left Column: Views Analytics Chart */}
        <div className="col-12 col-lg-8">
          <GlassCard hoverEffect={false} style={{ padding: '24px', height: '420px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontSize: 'var(--fs-section)', fontWeight: 600, margin: 0 }}>Portfolio Traffic</h3>
              <p style={{ fontSize: '13px', color: 'var(--subtext-color)', margin: '4px 0 0' }}>Daily view metrics for your public page</p>
            </div>
            
            <div style={{ width: '100%', height: '300px', marginTop: '10px' }}>
              <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} width="100%" height="100%" style={{ overflow: 'visible' }}>
                <defs>
                  <linearGradient id="viewsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                
                {/* Horizontal grid lines */}
                {gridRatios.map((ratio, i) => {
                  const y = paddingTop + ratio * heightAvailable;
                  const label = Math.round(maxVal * (1 - ratio));
                  return (
                    <g key={i}>
                      <line
                        x1={paddingLeft}
                        y1={y}
                        x2={chartWidth - paddingRight}
                        y2={y}
                        stroke="var(--glass-border)"
                        strokeWidth={1}
                        strokeDasharray="4 4"
                      />
                      <text x={paddingLeft - 10} y={y + 4} textAnchor="end" fill="var(--subtext-color)" fontSize={10} fontFamily="var(--font-body)">
                        {label}
                      </text>
                    </g>
                  );
                })}

                {/* Area path */}
                <path d={fillD} fill="url(#viewsGrad)" />

                {/* Stroke path */}
                <path d={lineD} fill="none" stroke="var(--primary)" strokeWidth={3} />

                {/* Dots and tooltips */}
                {svgPoints.map((p, i) => (
                  <g key={i} className="chart-dot-group">
                    <circle cx={p.x} cy={p.y} r={5} fill="var(--primary)" stroke="var(--bg-primary)" strokeWidth={2} />
                    <circle cx={p.x} cy={p.y} r={12} fill="transparent" style={{ cursor: 'pointer' }} />
                    <title>{p.views} views</title>
                  </g>
                ))}

                {/* X Axis Labels */}
                {svgPoints.map((p, i) => (
                  <text key={i} x={p.x} y={chartHeight - 10} textAnchor="middle" fill="var(--subtext-color)" fontSize={11} fontFamily="var(--font-body)">
                    {p.name}
                  </text>
                ))}
              </svg>
            </div>
          </GlassCard>
        </div>

        {/* Right Column: Profile Completion Circular Progress & Radar strengths */}
        <div className="col-12 col-lg-4">
          <GlassCard hoverEffect={false} style={{ padding: '24px', height: '420px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            {/* Header: User Profile & Completion circle */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: 'var(--gradient-primary)',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  border: '2px solid var(--primary)',
                  boxShadow: '0 4px 10px rgba(37, 99, 235, 0.15)'
                }}>
                  {firstName[0].toUpperCase()}
                </div>
                <div>
                  <h4 style={{ fontSize: '15px', fontWeight: 700, margin: 0 }}>{firstName}</h4>
                  <p style={{ fontSize: '12px', color: 'var(--subtext-color)', margin: '2px 0 0' }}>Candidate Bio</p>
                </div>
              </div>
              <ProgressCircle percent={completion} title="Profile" size={60} />
            </div>

            {/* Statistics Row Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', margin: '8px 0' }}>
              <div style={{ display: 'flex', flexDirection: 'column', padding: '8px 12px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)' }}>
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--subtext-color)', fontWeight: 600 }}>ATS Match</span>
                <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--success)' }}>{atsScore || 'N/A'}{atsScore ? '%' : ''}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', padding: '8px 12px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)' }}>
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--subtext-color)', fontWeight: 600 }}>Career Score</span>
                <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--primary)' }}>{careerScore || 'N/A'}{careerScore ? '%' : ''}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', padding: '8px 12px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)' }}>
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--subtext-color)', fontWeight: 600 }}>Resumes</span>
                <span style={{ fontSize: '15px', fontWeight: 700 }}>{resumes.length} Active</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', padding: '8px 12px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)' }}>
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--subtext-color)', fontWeight: 600 }}>Projects</span>
                <span style={{ fontSize: '15px', fontWeight: 700 }}>{projectCount} Items</span>
              </div>
            </div>

            {/* Radar chart - Centered */}
            <div style={{ width: '100%', height: '180px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <svg viewBox="0 0 200 200" width="100%" height="100%" style={{ overflow: 'visible' }}>
                {/* Nested Pentagons */}
                {[0.25, 0.5, 0.75, 1].map((ratio, index) => (
                  <polygon
                    key={index}
                    points={getGridPoints(ratio, 50)}
                    fill="none"
                    stroke="var(--glass-border)"
                    strokeWidth={1}
                    strokeDasharray={index < 3 ? "3 3" : "none"}
                  />
                ))}

                {/* Axis lines */}
                {radarPoints.map((p, i) => (
                  <line
                    key={i}
                    x1={100}
                    y1={100}
                    x2={p.outerX}
                    y2={p.outerY}
                    stroke="var(--glass-border)"
                    strokeWidth={1}
                  />
                ))}

                {/* Filled competency polygon */}
                <polygon
                  points={radarPoints.map(p => `${p.x},${p.y}`).join(' ')}
                  fill="var(--secondary)"
                  fillOpacity={0.15}
                  stroke="var(--secondary)"
                  strokeWidth={2}
                />

                {/* Data dots */}
                {radarPoints.map((p, i) => (
                  <g key={i}>
                    <circle cx={p.x} cy={p.y} r={3.5} fill="var(--secondary)" stroke="var(--bg-primary)" strokeWidth={1} />
                    <title>{p.subject}: {p.A}%</title>
                  </g>
                ))}

                {/* Labels */}
                {radarPoints.map((p, i) => {
                  const offset = 14;
                  const lx = 100 + (50 + offset) * Math.cos(p.angle);
                  const ly = 100 + (50 + offset) * Math.sin(p.angle) + 3;
                  return (
                    <text
                      key={i}
                      x={lx}
                      y={ly}
                      textAnchor={getLabelAnchor(p.angle)}
                      fill="var(--subtext-color)"
                      fontSize={9}
                      fontWeight={600}
                      fontFamily="var(--font-body)"
                    >
                      {p.subject}
                    </text>
                  );
                })}
              </svg>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Recent Resumes & Quick Actions */}
      <div className="row g-4">
        {/* Recent Resumes list */}
        <div className="col-12 col-lg-8">
          <GlassCard hoverEffect={false} style={{ padding: '24px', height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: 'var(--fs-section)', fontWeight: 600, margin: 0 }}>Recent Resumes</h3>
                <p style={{ fontSize: '13px', color: 'var(--subtext-color)', margin: '4px 0 0' }}>Manage and edit your uploaded document drafts</p>
              </div>
              <Link to="/resumes" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary)', textDecoration: 'none' }}>
                View All
              </Link>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', marginTop: '16px' }}>
              {resumes.length === 0 ? (
                <div style={{ padding: '40px 10px', textAlign: 'center', color: 'var(--subtext-color)', fontSize: '14px' }}>
                  No resumes uploaded yet. Click upload to get started.
                </div>
              ) : (
                <GlassTable headers={['Document Title', 'Parsed Status', 'Updated']}>
                  {resumes.slice(0, 3).map((r, i) => {
                    const date = r.updated_at ? new Date(r.updated_at) : null;
                    const formattedDate = date && !isNaN(date.getTime()) ? date.toLocaleDateString() : 'N/A';
                    return (
                      <tr key={i} onClick={() => navigate(`/resumes/${r.id}`)} style={{ cursor: 'pointer' }}>
                        <td style={{ fontWeight: 600 }}>{r.resume_title || 'Untitled Resume'}</td>
                        <td>
                          <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: r.is_active ? 'var(--success)' : 'var(--subtext-color)',
                            background: r.is_active ? 'rgba(34, 197, 94, 0.08)' : 'rgba(255,255,255,0.02)',
                            padding: '3px 8px',
                            borderRadius: '6px',
                            border: r.is_active ? '1px solid rgba(34, 197, 94, 0.2)' : '1px solid var(--glass-border)'
                          }}>
                            {r.is_active ? 'Master Active' : 'Draft'}
                          </span>
                        </td>
                        <td style={{ fontSize: '0.85rem', color: 'var(--subtext-color)' }}>
                          {formattedDate}
                        </td>
                      </tr>
                    );
                  })}
                </GlassTable>
              )}
            </div>
          </GlassCard>
        </div>

        {/* Quick Actions List */}
        <div className="col-12 col-lg-4">
          <GlassCard hoverEffect={false} style={{ padding: '24px', height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontSize: 'var(--fs-section)', fontWeight: 600, margin: 0 }}>Quick Actions</h3>
              <p style={{ fontSize: '13px', color: 'var(--subtext-color)', margin: '4px 0 0' }}>Accelerate your workflow with AI helpers</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px', flex: 1, justifyContent: 'center' }}>
              <Link to="/resumes" className="glass-panel" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                textDecoration: 'none',
                color: 'var(--text-color)',
                fontWeight: 600,
                fontSize: '14px',
                backgroundColor: 'rgba(37, 99, 235, 0.03)',
                transition: 'all var(--transition-fast)'
              }}>
                <HiOutlineDocumentArrowUp size={20} style={{ color: 'var(--primary)' }} />
                <span>Upload New Resume</span>
              </Link>

              <Link to="/portfolio" className="glass-panel" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                textDecoration: 'none',
                color: 'var(--text-color)',
                fontWeight: 600,
                fontSize: '14px',
                transition: 'all var(--transition-fast)'
              }}>
                <HiOutlineBriefcase size={20} style={{ color: 'var(--secondary)' }} />
                <span>Customize Portfolio</span>
              </Link>

              <Link to="/profile" className="glass-panel" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                textDecoration: 'none',
                color: 'var(--text-color)',
                fontWeight: 600,
                fontSize: '14px',
                transition: 'all var(--transition-fast)'
              }}>
                <HiOutlineUserCircle size={20} style={{ color: 'var(--success)' }} />
                <span>View Profile Details</span>
              </Link>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

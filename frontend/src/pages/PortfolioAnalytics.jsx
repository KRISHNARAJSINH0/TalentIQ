import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  HiOutlineArrowLeft, 
  HiOutlineGlobeAlt, 
  HiOutlineArrowDownTray, 
  HiOutlineShare, 
  HiOutlineChartBar,
  HiOutlineEye
} from 'react-icons/hi2';
import { portfolioAPI } from '../api/portfolio';
import '../styles/Profile.css';

const PortfolioAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const res = await portfolioAPI.getAnalytics();
        setAnalytics(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch analytics data.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container" style={{ textAlign: 'center', paddingTop: 100 }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p style={{ marginTop: 16, color: 'var(--gray-300)' }}>Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="profile-page">
        <div className="profile-container" style={{ textAlign: 'center', paddingTop: 100 }}>
          <div className="alert alert-danger" role="alert">
            {error || 'Could not load portfolio analytics.'}
          </div>
          <Link to="/portfolio" className="btn btn-outline-dark" style={{ marginTop: 16 }}>
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  // Calculate maximum views in daily trends for SVG scaling
  const maxViews = Math.max(...analytics.daily_trends.map((t) => t.views), 5);
  const chartHeight = 200;
  const chartWidth = 600;

  // Generate coordinates for SVG line chart
  const points = analytics.daily_trends.map((t, index) => {
    const x = (index / (analytics.daily_trends.length - 1)) * (chartWidth - 60) + 30;
    const y = chartHeight - (t.views / maxViews) * (chartHeight - 60) - 30;
    return { x, y, date: t.date, views: t.views };
  });

  const linePath = points.map((p, index) => `${index === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaPath = points.length > 0 
    ? `${linePath} L ${points[points.length - 1].x} ${chartHeight - 30} L ${points[0].x} ${chartHeight - 30} Z` 
    : '';

  return (
    <div className="profile-page">
      <div className="profile-container" style={{ maxWidth: '1000px' }}>
        
        {/* Header navigation */}
        <div style={{ marginBottom: '24px' }}>
          <Link 
            to="/portfolio" 
            className="btn-back"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', textDecoration: 'none', color: 'var(--gray-400)', fontSize: '0.9rem' }}
          >
            <HiOutlineArrowLeft /> Back to Portfolio Settings
          </Link>
        </div>

        {/* Title */}
        <div className="profile-card" style={{ padding: '32px', marginBottom: '24px' }}>
          <h1 className="profile-name" style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: '#10B981' }}><HiOutlineChartBar /></span>
            Portfolio Analytics
          </h1>
          <p className="profile-headline" style={{ fontSize: '0.95rem', color: 'var(--gray-400)', marginTop: '4px' }}>
            Track your visitors, section views, and resume downloads in real-time.
          </p>
        </div>

        {/* Metircs Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '24px' }} className="profile-columns-grid">
          <div className="profile-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '12px', color: '#3B82F6', fontSize: '1.5rem' }}>
              <HiOutlineEye />
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Total Views</span>
              <h3 style={{ fontSize: '1.75rem', fontWeight: 'bold', margin: '4px 0 0', color: 'var(--white)' }}>
                {analytics.total_views}
              </h3>
            </div>
          </div>

          <div className="profile-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', color: '#10B981', fontSize: '1.5rem' }}>
              <HiOutlineArrowDownTray />
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Resume Downloads</span>
              <h3 style={{ fontSize: '1.75rem', fontWeight: 'bold', margin: '4px 0 0', color: 'var(--white)' }}>
                {analytics.total_downloads}
              </h3>
            </div>
          </div>

          <div className="profile-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '12px', color: '#F59E0B', fontSize: '1.5rem' }}>
              <HiOutlineShare />
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>Total Shares</span>
              <h3 style={{ fontSize: '1.75rem', fontWeight: 'bold', margin: '4px 0 0', color: 'var(--white)' }}>
                {analytics.total_shares}
              </h3>
            </div>
          </div>
        </div>

        {/* Chart and Section Views Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }} className="profile-columns-grid">
          
          {/* Daily Trends Chart */}
          <div className="profile-card" style={{ padding: '24px' }}>
            <h3 className="profile-card-title" style={{ marginBottom: '20px', fontSize: '1.1rem' }}>
              📈 Traffic Trend (Last 7 Days)
            </h3>
            
            <div style={{ width: '100%', overflowX: 'auto' }}>
              <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: '100%', height: 'auto', background: 'rgba(255,255,255,0.01)', borderRadius: '8px' }}>
                <defs>
                  <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.3"/>
                    <stop offset="100%" stopColor="#3B82F6" stopOpacity="0"/>
                  </linearGradient>
                </defs>

                {/* Gridlines */}
                <line x1="30" y1={chartHeight - 30} x2={chartWidth - 30} y2={chartHeight - 30} stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="30" y1={chartHeight - 85} x2={chartWidth - 30} y2={chartHeight - 85} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                <line x1="30" y1={chartHeight - 140} x2={chartWidth - 30} y2={chartHeight - 140} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                <line x1="30" y1="30" x2={chartWidth - 30} y2="30" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />

                {/* Area under the line */}
                {areaPath && <path d={areaPath} fill="url(#chartGrad)" />}

                {/* Line chart path */}
                {linePath && <path d={linePath} fill="none" stroke="#3B82F6" strokeWidth="3" />}

                {/* Data points */}
                {points.map((p, idx) => (
                  <g key={idx}>
                    <circle cx={p.x} cy={p.y} r="5" fill="#3B82F6" stroke="#fff" strokeWidth="2" />
                    <text x={p.x} y={p.y - 12} fill="#fff" fontSize="10" textAnchor="middle" fontWeight="bold">
                      {p.views}
                    </text>
                    <text x={p.x} y={chartHeight - 12} fill="var(--gray-400)" fontSize="9" textAnchor="middle">
                      {new Date(p.date).toLocaleDateString(undefined, { day: '2-digit', month: 'short' })}
                    </text>
                  </g>
                ))}
              </svg>
            </div>
          </div>

          {/* Section Views List */}
          <div className="profile-card" style={{ padding: '24px' }}>
            <h3 className="profile-card-title" style={{ marginBottom: '20px', fontSize: '1.1rem' }}>
              🔍 Section Popularity
            </h3>
            
            {Object.keys(analytics.section_views).length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--gray-500)', fontSize: '0.9rem' }}>
                No sections viewed yet. Views will be tracked as visitors scroll through your public portfolio.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {Object.entries(analytics.section_views).map(([section, count], idx) => {
                  const maxCount = Math.max(...Object.values(analytics.section_views));
                  const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                  return (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                        <span style={{ textTransform: 'capitalize', color: 'var(--white)', fontWeight: 600 }}>
                          {section} Section
                        </span>
                        <span style={{ color: 'var(--gray-400)' }}>{count} views</span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ width: `${percentage}%`, height: '100%', background: 'linear-gradient(90deg, #3B82F6, #10B981)', borderRadius: '4px' }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};

export default PortfolioAnalytics;

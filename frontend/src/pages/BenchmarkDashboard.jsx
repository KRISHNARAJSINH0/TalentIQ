import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import GlassCard from '../components/GlassCard';
import {
  HiOutlineSparkles,
  HiOutlineChartBar,
  HiOutlineBriefcase,
  HiOutlineGlobeAlt,
  HiOutlineLightBulb,
  HiOutlineCheckCircle,
  HiOutlineClock,
  HiOutlineUserGroup,
  HiOutlineAcademicCap,
  HiOutlineArrowLeft,
  HiOutlineArrowTrendingUp,
  HiOutlineBuildingOffice
} from 'react-icons/hi2';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { benchmarksAPI } from '../api/benchmarks';
import '../styles/BenchmarkDashboard.css';

const BenchmarkDashboard = () => {
  const { id: resumeId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [leaderboard, setLeaderboard] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, [resumeId]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      // Fetch latest report (auto-triggers if missing)
      const reportRes = await benchmarksAPI.getLatestReport(resumeId);
      setReport(reportRes.data);

      // Fetch history
      const historyRes = await benchmarksAPI.getHistory(resumeId);
      setHistory(historyRes.data || []);

      // Fetch leaderboard
      const leaderboardRes = await benchmarksAPI.getLeaderboard(resumeId);
      setLeaderboard(leaderboardRes.data);
    } catch (err) {
      console.error('Error fetching benchmarking data', err);
      setError('Could not load benchmarking data. Please try recalculating.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    setCalculating(true);
    setError('');
    try {
      const res = await benchmarksAPI.triggerBenchmark(resumeId);
      setReport(res.data);
      
      // Refresh history & leaderboard
      const historyRes = await benchmarksAPI.getHistory(resumeId);
      setHistory(historyRes.data || []);

      const leaderboardRes = await benchmarksAPI.getLeaderboard(resumeId);
      setLeaderboard(leaderboardRes.data);
    } catch (err) {
      console.error('Failed to recalculate benchmark', err);
      setError('Recalculation failed. Please try again.');
    } finally {
      setCalculating(false);
    }
  };

  // Convert percentiles to scores (0-100 where higher is better) for the Radar chart
  const getRadarData = () => {
    if (!report || !report.comparison_metrics) return [];
    
    return Object.keys(report.comparison_metrics).map((key) => {
      const percentileVal = report.comparison_metrics[key];
      return {
        subject: key,
        Score: Math.round(100 - percentileVal),
        fullMark: 100,
      };
    });
  };

  // Convert history data for the line chart
  const getHistoryData = () => {
    return history.map((item, index) => {
      // Try to parse rank percentage from 'Top X%' or default to overall_score
      const match = (item.overall_rank || '').match(/\d+/);
      const percentileVal = match ? parseInt(match[0], 10) : 100 - item.overall_score;
      return {
        name: new Date(item.recorded_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
        Rank: 100 - percentileVal, // higher is better rank
        Score: item.overall_score,
      };
    });
  };

  if (loading) {
    return (
      <div className="benchmark-loader-container">
        <div className="benchmark-spinner"></div>
        <p>Retrieving cohort ranking & benchmarks...</p>
      </div>
    );
  }

  const radarData = getRadarData();
  const historyData = getHistoryData();

  return (
    <div className="benchmark-container">
      {/* Header */}
      <div className="benchmark-header">
        <button className="back-btn-dashboard" onClick={() => navigate(`/resumes/${resumeId}`)}>
          <HiOutlineArrowLeft className="icon" /> Back to Resume Details
        </button>
        <div className="title-section">
          <h1>Benchmark & Ranking Engine</h1>
          <p className="subtitle">
            Compare your resume against other candidates across industry, profession, and geography.
          </p>
        </div>
      </div>

      {error && <div className="benchmark-error-toast">{error}</div>}

      {/* Main Grid */}
      <div className="benchmark-grid">
        
        {/* Left Side: Summary and Percentile Gauge */}
        <div className="left-column">
          <GlassCard className="main-rank-card">
            <div className="rank-badge-glow">
              <div className="inner-badge">
                <span className="percentile-label">Overall Standing</span>
                <span className="rank-value">{report?.overall_rank}</span>
                <span className="candidate-group">Cohort Rank</span>
              </div>
            </div>
            
            <div className="cohort-stats">
              <div className="stat-row">
                <HiOutlineAcademicCap className="stat-icon" />
                <div>
                  <span className="stat-title">Profession Category</span>
                  <p className="stat-desc">{report?.details_json?.profession || 'Software Engineer'}</p>
                </div>
              </div>
              <div className="stat-row">
                <HiOutlineBriefcase className="stat-icon" />
                <div>
                  <span className="stat-title">Experience Level</span>
                  <p className="stat-desc">{report?.details_json?.experience_level || 'Mid Level'}</p>
                </div>
              </div>
              <div className="stat-row">
                <HiOutlineGlobeAlt className="stat-icon" />
                <div>
                  <span className="stat-title">Country Bucket</span>
                  <p className="stat-desc">{report?.details_json?.country || 'Remote'}</p>
                </div>
              </div>
            </div>

            <button 
              className={`recalculate-btn ${calculating ? 'loading' : ''}`}
              onClick={handleRecalculate}
              disabled={calculating}
            >
              <HiOutlineSparkles className="btn-icon" />
              {calculating ? 'Analyzing Profiles...' : 'Recalculate Ranking'}
            </button>
          </GlassCard>

          {/* Demographic rankings list */}
          <GlassCard className="demo-ranks-card">
            <h3>Demographic Rankings</h3>
            <div className="demo-ranks-grid">
              <div className="demo-rank-item">
                <div className="item-label">Profession</div>
                <div className="item-value">{report?.profession_rank}</div>
              </div>
              <div className="demo-rank-item">
                <div className="item-label">Industry</div>
                <div className="item-value">{report?.industry_rank}</div>
              </div>
              <div className="demo-rank-item">
                <div className="item-label">Country</div>
                <div className="item-value">{report?.country_rank}</div>
              </div>
              <div className="demo-rank-item">
                <div className="item-label">Experience</div>
                <div className="item-value">{report?.experience_rank}</div>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Middle Column: Radar Chart and History */}
        <div className="middle-column">
          <GlassCard className="radar-card">
            <h3>Skills & Component Distribution</h3>
            <p className="card-subtitle">Your standing relative to peer averages (higher is better)</p>
            <div className="radar-chart-container">
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid stroke="var(--glass-border)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-color)', fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'var(--subtext-color)', fontSize: 10 }} />
                  <Radar
                    name="Resume percentile"
                    dataKey="Score"
                    stroke="#8b5cf6"
                    fill="#8b5cf6"
                    fillOpacity={0.4}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          <GlassCard className="history-card">
            <h3>Ranking Progression</h3>
            <p className="card-subtitle">Track your rank improvements over time</p>
            <div className="history-chart-container">
              {historyData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={historyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
                    <XAxis dataKey="name" stroke="var(--subtext-color)" fontSize={11} />
                    <YAxis stroke="var(--subtext-color)" fontSize={11} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--bg-primary)', border: '1px solid var(--glass-border)', borderRadius: '12px', color: 'var(--text-color)' }}
                      labelStyle={{ color: 'var(--text-color)' }}
                      itemStyle={{ color: 'var(--text-color)' }}
                    />
                    <Line type="monotone" dataKey="Score" stroke="#10b981" strokeWidth={3} dot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-history">
                  <HiOutlineClock className="icon" />
                  <p>No ranking history available. Recalculate to log rankings.</p>
                </div>
              )}
            </div>
          </GlassCard>
        </div>

        {/* Right Side: Strengths, Weaknesses, and Improvement Potential */}
        <div className="right-column">
          <GlassCard className="strengths-weaknesses-card">
            <div className="strength-section">
              <h4 className="section-title strengths-title">
                <HiOutlineCheckCircle className="icon" /> Top Cohort Strengths
              </h4>
              <ul className="sw-list">
                {report?.strengths.map((str, idx) => (
                  <li key={idx} className="strength-item">
                    <span className="bullet">✓</span> {str}
                  </li>
                ))}
              </ul>
            </div>

            <div className="divider" />

            <div className="weakness-section">
              <h4 className="section-title weaknesses-title">
                <HiOutlineLightBulb className="icon" /> Priority Improvement Gaps
              </h4>
              <ul className="sw-list">
                {report?.weaknesses.map((wk, idx) => (
                  <li key={idx} className="weakness-item">
                    <span className="bullet">⚡</span> {wk}
                  </li>
                ))}
              </ul>
            </div>
          </GlassCard>

          {/* Improvement Potential Timeline */}
          <GlassCard className="improvement-potential-card">
            <h3>Estimated Rank Improvements</h3>
            <p className="card-subtitle">Complete these steps to boost your cohort standing</p>
            <div className="improvements-timeline">
              {report?.improvement_potential.map((item, idx) => (
                <div key={idx} className={`timeline-node ${idx === 0 ? 'current' : ''}`}>
                  <div className="timeline-marker">
                    <span className="step-num">{idx === 0 ? '★' : idx}</span>
                  </div>
                  <div className="node-content">
                    <span className="node-step">{item.step}</span>
                    <span className="node-rank">{item.rank}</span>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Peer Leaderboards */}
          <GlassCard className="leaderboards-card">
            <h3>Cohort Distributions</h3>
            
            <div className="leaderboard-tabs">
              <div className="leaderboard-section-title">
                <HiOutlineUserGroup className="icon" /> Career Group Standing
              </div>
              <div className="leaderboard-list">
                {leaderboard?.career_comparison.map((item, idx) => (
                  <div key={idx} className={`leaderboard-row ${item.your_level ? 'highlighted' : ''}`}>
                    <span className="row-group">{item.group}</span>
                    <span className="row-value">{item.average_score}% Avg</span>
                    {item.your_level && <span className="current-user-badge">You</span>}
                  </div>
                ))}
              </div>

              <div className="leaderboard-section-title mt-4">
                <HiOutlineBuildingOffice className="icon" /> Industry Average ATS
              </div>
              <div className="leaderboard-list">
                {leaderboard?.industry_comparison.map((item, idx) => (
                  <div key={idx} className={`leaderboard-row ${item.active ? 'highlighted' : ''}`}>
                    <span className="row-group">{item.industry}</span>
                    <span className="row-value">{item.average_score}% Avg</span>
                    {item.active && <span className="current-user-badge">Active</span>}
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>

      </div>
    </div>
  );
};

export default BenchmarkDashboard;

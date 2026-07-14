/**
 * JDAnalyzer – Phase 22: Job Description Analyzer Dashboard.
 *
 * Allows users to paste a JD, analyze it against their master resume,
 * and view match scores, gap analysis, ATS predictions, and recommendations.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from '../components/GlassCard';
import {
  HiOutlineDocumentText,
  HiOutlineSparkles,
  HiOutlineChartBar,
  HiOutlineShieldCheck,
  HiOutlineAcademicCap,
  HiOutlineBriefcase,
  HiOutlineLightBulb,
  HiOutlineScale,
  HiOutlineArrowTrendingUp,
  HiOutlineClock,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineExclamationTriangle,
  HiOutlineBookOpen,
} from 'react-icons/hi2';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, ResponsiveContainer, Tooltip,
} from 'recharts';
import { jdAPI } from '../api/jd';
import '../styles/JDAnalyzer.css';

const JDAnalyzer = () => {
  const [jdText, setJdText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await jdAPI.getHistory();
      setHistory(res.data || []);
    } catch {
      // History load is non-critical
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!jdText.trim() || jdText.trim().length < 50) {
      setError('Please paste a complete job description (at least 50 characters).');
      return;
    }
    setError('');
    setAnalyzing(true);
    try {
      const res = await jdAPI.analyzeJD(jdText);
      setResult(res.data);
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const loadReport = async (id) => {
    try {
      const res = await jdAPI.getReport(id);
      setResult(res.data);
    } catch {
      setError('Failed to load report.');
    }
  };

  // Build radar chart data
  const radarData = result ? [
    { metric: 'Skills', value: result.skills_match || 0 },
    { metric: 'Experience', value: result.experience_match || 0 },
    { metric: 'Education', value: result.education_match || 0 },
    { metric: 'Keywords', value: result.keyword_match || 0 },
    { metric: 'ATS', value: result.ats_score || 0 },
    { metric: 'Overall', value: result.match_score || 0 },
  ] : [];

  const getScoreColor = (score) => {
    if (score >= 90) return '#22C55E';
    if (score >= 80) return '#3B82F6';
    if (score >= 70) return '#F59E0B';
    if (score >= 60) return '#F97316';
    return '#EF4444';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent Match';
    if (score >= 80) return 'Strong Match';
    if (score >= 70) return 'Moderate Match';
    if (score >= 60) return 'Needs Improvement';
    return 'Weak Match';
  };

  return (
    <div className="jd-analyzer-page">

      {/* Header */}
      <GlassCard className="jd-header">
        <div className="jd-header-text">
          <h1>
            <HiOutlineDocumentText size={28} style={{ color: 'var(--primary)' }} />
            JD Analyzer
          </h1>
          <p>Paste any job description to get instant match analysis against your resume</p>
        </div>
      </GlassCard>

      {/* Input Area */}
      <GlassCard className="jd-card">
        <h2 className="jd-section-title">
          <HiOutlineSparkles size={20} style={{ color: '#8B5CF6' }} />
          Paste Job Description
        </h2>
        <form onSubmit={handleAnalyze} className="jd-input-form">
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the full job description here — include requirements, responsibilities, qualifications, and skills..."
            className="jd-textarea"
            rows={8}
          />
          {error && (
            <div className="jd-error">
              <HiOutlineExclamationTriangle size={16} />
              {error}
            </div>
          )}
          <button
            type="submit"
            className="jd-analyze-btn"
            disabled={analyzing}
          >
            {analyzing ? (
              <>
                <span className="jd-spinner" />
                Analyzing...
              </>
            ) : (
              <>
                <HiOutlineSparkles size={18} />
                Analyze Match
              </>
            )}
          </button>
        </form>
      </GlassCard>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Score Cards Grid */}
            <div className="jd-scores-grid">
              {[
                { label: 'Match Score', value: result.match_score, icon: HiOutlineChartBar, color: getScoreColor(result.match_score) },
                { label: 'ATS Score', value: result.ats_score, icon: HiOutlineShieldCheck, color: getScoreColor(result.ats_score) },
                { label: 'Skills Match', value: result.skills_match, icon: HiOutlineSparkles, color: getScoreColor(result.skills_match) },
                { label: 'Experience', value: result.experience_match, icon: HiOutlineBriefcase, color: getScoreColor(result.experience_match) },
                { label: 'Education', value: result.education_match, icon: HiOutlineAcademicCap, color: getScoreColor(result.education_match) },
                { label: 'Keywords', value: result.keyword_match, icon: HiOutlineDocumentText, color: getScoreColor(result.keyword_match) },
              ].map((card, idx) => (
                <GlassCard key={idx} hoverEffect className="jd-score-card">
                  <div className="jd-score-card-inner">
                    <div className="jd-score-icon" style={{ backgroundColor: `${card.color}15`, color: card.color }}>
                      <card.icon size={22} />
                    </div>
                    <div>
                      <div className="jd-score-label">{card.label}</div>
                      <div className="jd-score-value" style={{ color: card.color }}>{card.value}%</div>
                    </div>
                  </div>
                  <div className="jd-score-bar-track">
                    <motion.div
                      className="jd-score-bar-fill"
                      initial={{ width: 0 }}
                      animate={{ width: `${card.value}%` }}
                      transition={{ duration: 0.8, delay: idx * 0.1 }}
                      style={{ backgroundColor: card.color }}
                    />
                  </div>
                </GlassCard>
              ))}
            </div>

            {/* Main Grid: Radar + Match Verdict */}
            <div className="jd-main-grid">
              {/* Radar Chart */}
              <GlassCard className="jd-card">
                <h2 className="jd-section-title">
                  <HiOutlineChartBar size={20} style={{ color: 'var(--primary)' }} />
                  Match Radar
                </h2>
                <div className="jd-radar-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="75%">
                      <PolarGrid stroke="rgba(255,255,255,0.1)" />
                      <PolarAngleAxis dataKey="metric" stroke="var(--subtext-color)" fontSize={12} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="rgba(255,255,255,0.05)" fontSize={10} />
                      <Radar
                        name="Match"
                        dataKey="value"
                        stroke="var(--primary)"
                        fill="var(--primary)"
                        fillOpacity={0.2}
                        strokeWidth={2}
                      />
                      <Tooltip
                        contentStyle={{
                          background: 'var(--glass-bg)',
                          border: '1px solid var(--glass-border)',
                          borderRadius: '12px',
                          backdropFilter: 'blur(12px)',
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                {/* Match Verdict */}
                <div className="jd-verdict" style={{ borderColor: `${getScoreColor(result.match_score)}30` }}>
                  <span className="jd-verdict-score" style={{ color: getScoreColor(result.match_score) }}>
                    {result.match_score}%
                  </span>
                  <div>
                    <div className="jd-verdict-label" style={{ color: getScoreColor(result.match_score) }}>
                      {getScoreLabel(result.match_score)}
                    </div>
                    <div className="jd-verdict-sub">
                      {result.jd_title && `${result.jd_title}`}
                      {result.jd_company && ` at ${result.jd_company}`}
                    </div>
                  </div>
                </div>
              </GlassCard>

              {/* Right Column */}
              <div className="jd-right-column">
                {/* Strengths */}
                <GlassCard className="jd-card">
                  <h2 className="jd-section-title">
                    <HiOutlineCheckCircle size={20} style={{ color: 'var(--success)' }} />
                    Strengths
                  </h2>
                  <div className="jd-list">
                    {result.strengths?.map((s, i) => (
                      <div key={i} className="jd-list-item jd-list-success">
                        <HiOutlineCheckCircle size={16} />
                        <span>{s}</span>
                      </div>
                    ))}
                  </div>
                </GlassCard>

                {/* Weaknesses */}
                <GlassCard className="jd-card">
                  <h2 className="jd-section-title">
                    <HiOutlineXCircle size={20} style={{ color: 'var(--danger)' }} />
                    Weaknesses
                  </h2>
                  <div className="jd-list">
                    {result.weaknesses?.map((w, i) => (
                      <div key={i} className="jd-list-item jd-list-danger">
                        <HiOutlineXCircle size={16} />
                        <span>{w}</span>
                      </div>
                    ))}
                    {(!result.weaknesses || result.weaknesses.length === 0) && (
                      <p className="jd-empty-text">No significant weaknesses identified!</p>
                    )}
                  </div>
                </GlassCard>
              </div>
            </div>

            {/* Skills Gap Analysis */}
            <div className="jd-gap-grid">
              {/* Matching Skills */}
              <GlassCard className="jd-card">
                <h2 className="jd-section-title">
                  <HiOutlineCheckCircle size={20} style={{ color: 'var(--success)' }} />
                  Matching Skills
                </h2>
                <div className="jd-skill-tags">
                  {result.matching_skills?.map((skill, i) => (
                    <span key={i} className="jd-tag jd-tag-success">{skill}</span>
                  ))}
                  {(!result.matching_skills || result.matching_skills.length === 0) && (
                    <p className="jd-empty-text">No matching skills found.</p>
                  )}
                </div>
              </GlassCard>

              {/* Missing Skills */}
              <GlassCard className="jd-card">
                <h2 className="jd-section-title">
                  <HiOutlineScale size={20} style={{ color: 'var(--warning)' }} />
                  Missing Skills
                </h2>
                <div className="jd-skill-tags">
                  {result.missing_skills?.map((skill, i) => (
                    <span key={i} className="jd-tag jd-tag-warning">{skill}</span>
                  ))}
                  {(!result.missing_skills || result.missing_skills.length === 0) && (
                    <p className="jd-empty-text">You match all required skills!</p>
                  )}
                </div>
              </GlassCard>
            </div>

            {/* ATS Suggestions */}
            <GlassCard className="jd-card">
              <h2 className="jd-section-title">
                <HiOutlineArrowTrendingUp size={20} style={{ color: 'var(--primary)' }} />
                ATS Improvement Suggestions
              </h2>
              <div className="jd-suggestions-list">
                {result.suggestions?.map((sug, i) => (
                  <div key={i} className="jd-suggestion-item">
                    <div className="jd-suggestion-content">
                      <span className="jd-suggestion-action">{sug.action}</span>
                      <span className="jd-suggestion-detail">{sug.detail}</span>
                    </div>
                    <span className="jd-suggestion-impact">+{sug.ats_impact} ATS</span>
                  </div>
                ))}
              </div>
            </GlassCard>

            {/* Bottom Grid: Interview Readiness + Learning Path + Salary */}
            <div className="jd-bottom-grid">
              {/* Interview Readiness */}
              <GlassCard className="jd-card">
                <h2 className="jd-section-title">
                  <HiOutlineBriefcase size={20} style={{ color: '#8B5CF6' }} />
                  Interview Readiness
                </h2>
                <div className="jd-interview-score">
                  <span className="jd-big-score" style={{ color: getScoreColor(result.interview_readiness?.score || 0) }}>
                    {result.interview_readiness?.score || 0}%
                  </span>
                  <span className="jd-interview-label">
                    {result.interview_readiness?.ready ? 'Ready for Interview' : 'Needs Preparation'}
                  </span>
                </div>
                {result.interview_readiness?.missing_areas?.length > 0 && (
                  <div className="jd-missing-areas">
                    <h4>Missing Areas:</h4>
                    <div className="jd-skill-tags">
                      {result.interview_readiness.missing_areas.map((area, i) => (
                        <span key={i} className="jd-tag jd-tag-neutral">{area}</span>
                      ))}
                    </div>
                  </div>
                )}
              </GlassCard>

              {/* Learning Roadmap */}
              <GlassCard className="jd-card">
                <h2 className="jd-section-title">
                  <HiOutlineLightBulb size={20} style={{ color: 'var(--success)' }} />
                  Learning Roadmap
                </h2>
                <div className="jd-learning-list">
                  {result.report?.recommendations?.learning_path?.map((item, i) => (
                    <div key={i} className="jd-learning-item">
                      <div className="jd-learning-skill">
                        <HiOutlineBookOpen size={16} style={{ color: 'var(--primary)' }} />
                        <strong>{item.skill}</strong>
                      </div>
                      <div className="jd-learning-details">
                        <span>{item.course}</span>
                        <span className="jd-learning-meta">
                          {item.platform} · ~{item.estimated_hours}h
                        </span>
                      </div>
                    </div>
                  ))}
                  {(!result.report?.recommendations?.learning_path || result.report.recommendations.learning_path.length === 0) && (
                    <p className="jd-empty-text">No additional learning needed!</p>
                  )}
                </div>
              </GlassCard>

              {/* Salary Estimate */}
              <GlassCard className="jd-card">
                <h2 className="jd-section-title">
                  <HiOutlineArrowTrendingUp size={20} style={{ color: 'var(--success)' }} />
                  Salary Estimate
                </h2>
                {result.salary_estimate && (
                  <div className="jd-salary-info">
                    <div className="jd-salary-range">
                      <span className="jd-salary-value">
                        {result.salary_estimate.currency}{result.salary_estimate.min}
                        {result.salary_estimate.suffix}
                      </span>
                      <span className="jd-salary-separator">—</span>
                      <span className="jd-salary-value">
                        {result.salary_estimate.currency}{result.salary_estimate.max}
                        {result.salary_estimate.suffix}
                      </span>
                    </div>
                    <span className="jd-salary-label">
                      Estimated market range · {result.salary_estimate.seniority_adjustment} level
                    </span>
                  </div>
                )}
              </GlassCard>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Analysis History */}
      {history.length > 0 && (
        <GlassCard className="jd-card">
          <h2 className="jd-section-title">
            <HiOutlineClock size={20} style={{ color: 'var(--subtext-color)' }} />
            Analysis History
          </h2>
          <div className="jd-history-list">
            {history.map((item) => (
              <div
                key={item.id}
                className="jd-history-item"
                onClick={() => loadReport(item.id)}
                role="button"
                tabIndex={0}
              >
                <div className="jd-history-info">
                  <span className="jd-history-title">{item.jd_title || 'Untitled'}</span>
                  <span className="jd-history-company">{item.jd_company || ''}</span>
                </div>
                <div className="jd-history-scores">
                  <span className="jd-history-badge" style={{ color: getScoreColor(item.match_score) }}>
                    {item.match_score}% Match
                  </span>
                  <span className="jd-history-badge" style={{ color: getScoreColor(item.ats_score) }}>
                    {item.ats_score}% ATS
                  </span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default JDAnalyzer;

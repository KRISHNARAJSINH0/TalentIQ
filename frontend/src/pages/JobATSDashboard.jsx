/**
 * JobATSDashboard – Phase E: Job-Specific ATS Dashboard.
 *
 * Allows users to paste a Job Description and input Company Details to
 * calculate role, skill, experience, project, and company-specific ATS fits.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  HiOutlineClock,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineArrowLeft,
  HiOutlineCurrencyRupee,
  HiOutlineUserGroup,
  HiOutlineCode,
  HiOutlineExternalLink
} from 'react-icons/hi';
import { jobsAPI } from '../api/jobs';
import '../styles/JobATSDashboard.css';

const JobATSDashboard = () => {
  const { id: resumeId } = useParams();
  const navigate = useNavigate();

  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [activeTab, setActiveTab] = useState('skills');

  useEffect(() => {
    loadHistory();
  }, [resumeId]);

  const loadHistory = async () => {
    try {
      const res = await jobsAPI.getJobATSHistory();
      // Filter history for the current resume ID
      const filtered = (res.data || []).filter(item => String(item.resume) === String(resumeId));
      setHistory(filtered);
      
      // Load latest report by default if exists
      if (filtered.length > 0 && !result) {
        setResult(filtered[0].metadata || filtered[0]);
        setJobTitle(filtered[0].job_title || '');
        setCompanyName(filtered[0].company_name || '');
        setJobDescription(filtered[0].job_description || '');
      }
    } catch (err) {
      console.error('Failed to load history', err);
    }
  };

  const handleEvaluate = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim() || jobDescription.trim().length < 30) {
      setError('Please paste a complete job description (at least 30 characters).');
      return;
    }
    setError('');
    setSuccess('');
    setAnalyzing(true);
    try {
      const res = await jobsAPI.evaluateJobATS(jobDescription, companyName, jobTitle || 'Target Role');
      setResult(res.data.metadata || res.data);
      setSuccess('Job ATS evaluation completed successfully!');
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.error || 'Evaluation failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const loadReport = (report) => {
    setResult(report.metadata || report);
    setJobTitle(report.job_title || '');
    setCompanyName(report.company_name || '');
    setJobDescription(report.job_description || '');
    setSuccess(`Loaded report: ${report.job_title} at ${report.company_name}`);
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10B981'; // Emerald/Green
    if (score >= 80) return '#3B82F6'; // Blue
    if (score >= 70) return '#F59E0B'; // Amber
    if (score >= 60) return '#F97316'; // Orange
    return '#EF4444'; // Red
  };

  const getReadinessBadgeClass = (status) => {
    switch (status) {
      case 'Elite Candidate':
      case 'Highly Competitive':
        return 'badge-elite';
      case 'Interview Ready':
        return 'badge-ready';
      case 'Needs Improvement':
        return 'badge-needs-imp';
      default:
        return 'badge-not-ready';
    }
  };

  return (
    <div className="job-ats-container">
      {/* Header section with back option */}
      <div className="job-ats-header-nav">
        <button className="back-btn-job" onClick={() => navigate(`/resumes/${resumeId}`)}>
          <HiOutlineArrowLeft size={18} />
          <span>Back to Resume Details</span>
        </button>
        <span className="badge-premium-engine">
          <HiOutlineSparkles size={14} />
          ATS Phase E Engine
        </span>
      </div>

      <div className={`job-ats-layout ${!result ? 'no-results' : ''}`}>
        <div className="job-ats-left-column">
          {/* Input Panel */}
          <GlassCard className="input-panel-card">
          <h2 className="panel-title">
            <HiOutlineDocumentText size={20} style={{ color: 'var(--primary)' }} />
            Job Analysis Inputs
          </h2>
          <form onSubmit={handleEvaluate} className="evaluation-form">
            <div className="form-row-2">
              <div className="form-group-job">
                <label>Job Title</label>
                <input
                  type="text"
                  placeholder="e.g. Senior Software Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="job-input"
                />
              </div>
              <div className="form-group-job">
                <label>Company Name</label>
                <input
                  type="text"
                  placeholder="e.g. Google, Amazon, Netflix..."
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="job-input"
                />
              </div>
            </div>

            <div className="form-group-job">
              <label>Job Description</label>
              <textarea
                rows={7}
                placeholder="Paste the full job description here... include requirements, responsibilities, preferred qualifications..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="job-textarea-input"
              />
            </div>

            {error && (
              <div className="form-alert error-alert">
                <HiOutlineXCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div className="form-alert success-alert">
                <HiOutlineCheckCircle size={16} />
                <span>{success}</span>
              </div>
            )}

            <button
              type="submit"
              className="evaluate-btn-job"
              disabled={analyzing}
            >
              {analyzing ? (
                <>
                  <span className="spinner-job" />
                  Evaluating Fit...
                </>
              ) : (
                <>
                  <HiOutlineSparkles size={18} />
                  Evaluate Resume Match
                </>
              )}
            </button>
          </form>
          </GlassCard>

          {/* History List */}
          {history.length > 0 && (
            <GlassCard className="history-card-job">
              <h3 className="section-subtitle">
                <HiOutlineClock size={18} style={{ color: 'var(--subtext-color)' }} />
                Evaluation History
              </h3>
              <div className="history-items-list">
                {history.map((item, idx) => (
                  <div
                    key={idx}
                    className="history-item-row"
                    onClick={() => loadReport(item)}
                    role="button"
                    tabIndex={0}
                  >
                    <div className="history-item-meta">
                      <strong>{item.job_title}</strong>
                      <span>{item.company_name}</span>
                    </div>
                    <div className="history-item-badges">
                      <span className="history-score-badge" style={{ color: getScoreColor(item.overall_match) }}>
                        {item.overall_match}% Match
                      </span>
                      <span className="history-date-badge">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}
        </div>

        {/* Results display */}
        {result && (
          <div className="results-wrapper">
            {/* Score Grid */}
            <div className="score-summary-grid">
              <GlassCard className="summary-score-card">
                <div className="score-radial-wrapper">
                  <div className="score-gauge" style={{ 
                    '--score-color': getScoreColor(result.overall_match),
                    '--percentage': `${result.overall_match}%`
                  }}>
                    <div className="score-gauge-inner">
                      <span className="score-number">{result.overall_match}%</span>
                      <span className="score-label">Overall Match</span>
                    </div>
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="score-bar-card">
                <div className="score-indicator-row">
                  <div className="indicator-meta">
                    <span className="meta-label">ATS Compatibility Score</span>
                    <span className="meta-val" style={{ color: getScoreColor(result.ats_score) }}>{result.ats_score}%</span>
                  </div>
                  <div className="progress-track-job">
                    <div className="progress-fill-job" style={{ width: `${result.ats_score}%`, backgroundColor: getScoreColor(result.ats_score) }} />
                  </div>
                </div>

                <div className="badges-meta-row">
                  <div className="meta-badge-box">
                    <span className="badge-meta-label">Interview Readiness</span>
                    <span className={`readiness-badge ${getReadinessBadgeClass(result.interview_readiness)}`}>
                      {result.interview_readiness}
                    </span>
                  </div>
                  <div className="meta-badge-box">
                    <span className="badge-meta-label">Missing Skills</span>
                    <span className="missing-skills-badge">
                      {result.missing_skills?.length || 0} Skills
                    </span>
                  </div>
                </div>
              </GlassCard>
            </div>

            {/* Recommendations List */}
            <GlassCard className="recommendations-card">
              <h3 className="section-subtitle">
                <HiOutlineLightBulb size={18} style={{ color: 'var(--warning)' }} />
                Actionable Optimization Steps
              </h3>
              <ul className="recs-list">
                {result.recommendations?.map((rec, i) => (
                  <li key={i} className="rec-item">
                    <span className="rec-bullet">{i + 1}</span>
                    <span className="rec-text">{rec}</span>
                  </li>
                ))}
              </ul>
            </GlassCard>

            {/* Breakdown Tabs */}
            <div className="tabs-container">
              <div className="tabs-header">
                {[
                  { id: 'skills', label: 'Skill Match', icon: HiOutlineSparkles },
                  { id: 'experience', label: 'Experience Fit', icon: HiOutlineBriefcase },
                  { id: 'projects', label: 'Project Match', icon: HiOutlineCode },
                  { id: 'company', label: 'Company Fit', icon: HiOutlineUserGroup },
                  { id: 'salary', label: 'Salary Forecast', icon: HiOutlineCurrencyRupee },
                  { id: 'interview', label: 'Interview Scores', icon: HiOutlineChartBar },
                ].map(tab => (
                  <button
                    key={tab.id}
                    className={`tab-btn-job ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <tab.icon size={16} />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              <div className="tab-content-panel">
                {activeTab === 'skills' && (
                  <div className="skills-tab-content">
                    <div className="skills-grid-columns">
                      <div className="skills-col">
                        <h4>Required Skills</h4>
                        <div className="skills-tag-group">
                          {result.skills_analysis?.required_skills?.map((s, i) => (
                            <span key={i} className="skill-tag-job req-tag">
                              {s}
                              <span className="importance-dot high" title="High Importance" />
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="skills-col">
                        <h4>Preferred Skills</h4>
                        <div className="skills-tag-group">
                          {result.skills_analysis?.preferred_skills?.map((s, i) => (
                            <span key={i} className="skill-tag-job pref-tag">
                              {s}
                              <span className="importance-dot medium" title="Medium Importance" />
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="skills-grid-columns bottom-row-skills">
                      <div className="skills-col">
                        <h4>Emerging Technologies</h4>
                        <div className="skills-tag-group">
                          {result.skills_analysis?.emerging_skills?.map((s, i) => (
                            <span key={i} className="skill-tag-job emerging-tag">
                              {s}
                            </span>
                          ))}
                          {(!result.skills_analysis?.emerging_skills || result.skills_analysis.emerging_skills.length === 0) && (
                            <p className="no-items-text">No emerging skills found in JD.</p>
                          )}
                        </div>
                      </div>

                      <div className="skills-col">
                        <h4>Missing Target Skills</h4>
                        <div className="skills-tag-group">
                          {result.missing_skills?.map((s, i) => (
                            <span key={i} className="skill-tag-job missing-tag">
                              {s}
                            </span>
                          ))}
                          {(!result.missing_skills || result.missing_skills.length === 0) && (
                            <p className="success-tag-text">No missing skills detected! Perfect match.</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'experience' && (
                  <div className="experience-tab-content">
                    <div className="exp-fit-grid">
                      <div className="exp-fit-stat">
                        <span className="stat-num">{result.experience_analysis?.candidate_years || 0}</span>
                        <span className="stat-lbl">Your Experience Years</span>
                      </div>
                      <div className="exp-fit-stat">
                        <span className="stat-num">{result.experience_analysis?.required_years || 0}</span>
                        <span className="stat-lbl">Required Years</span>
                      </div>
                    </div>

                    <div className="checkpoints-section">
                      <h4>Verification Checkpoints</h4>
                      <div className="checkpoints-list">
                        <div className="checkpoint-row">
                          <span className={`check-icon ${result.experience_analysis?.has_growth ? 'pass' : 'fail'}`}>
                            {result.experience_analysis?.has_growth ? '✓' : '✗'}
                          </span>
                          <div className="check-details">
                            <strong>Hierarchical Career Growth</strong>
                            <p>Transition step in designation history (Senior, Lead, Principal, etc.).</p>
                          </div>
                        </div>

                        <div className="checkpoint-row">
                          <span className={`check-icon ${result.experience_analysis?.leadership_indicators?.length > 0 ? 'pass' : 'fail'}`}>
                            {result.experience_analysis?.leadership_indicators?.length > 0 ? '✓' : '✗'}
                          </span>
                          <div className="check-details">
                            <strong>Leadership & Management Experience</strong>
                            <p>Indicators found: {result.experience_analysis?.leadership_indicators?.join(', ') || 'None detected'}.</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'projects' && (
                  <div className="projects-tab-content">
                    <div className="projects-list-jobs">
                      {result.project_analysis?.relevant_projects?.map((proj, i) => (
                        <div key={i} className="project-job-item">
                          <div className="proj-item-header">
                            <h5>{proj}</h5>
                            <div className="proj-links">
                              {result.project_analysis?.has_github && (
                                <a href="#" className="proj-link-btn" title="GitHub Codebase">
                                  <HiOutlineCode size={14} />
                                  <span>GitHub</span>
                                </a>
                              )}
                              {result.project_analysis?.has_live_demo && (
                                <a href="#" className="proj-link-btn" title="Live Deployment">
                                  <HiOutlineExternalLink size={14} />
                                  <span>Live Demo</span>
                                </a>
                              )}
                            </div>
                          </div>
                          
                          <div className="proj-indicators-grid">
                            <div className="proj-indicator-box">
                              <strong>Architecture Validation:</strong>
                              <p>{result.project_analysis?.architecture_indicators?.join(', ') || 'None found'}</p>
                            </div>
                            <div className="proj-indicator-box">
                              <strong>Business Impact Metrics:</strong>
                              <p>{result.project_analysis?.business_impact_metrics?.join(', ') || 'None found'}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                      {(!result.project_analysis?.relevant_projects || result.project_analysis.relevant_projects.length === 0) && (
                        <p className="no-items-text">No relevant projects matched for this job.</p>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === 'company' && (
                  <div className="company-tab-content">
                    <div className="company-fit-header">
                      <h3>{result.company_analysis?.company_name} Culture Fit</h3>
                      <div className="fit-score-badge" style={{ backgroundColor: getScoreColor(result.company_analysis?.fit_score) }}>
                        {result.company_analysis?.fit_score}% Fit
                      </div>
                    </div>

                    <div className="principles-section">
                      <h4>Specific Principles Checked</h4>
                      <div className="principles-grid">
                        {result.company_analysis?.expectations?.map((exp, i) => (
                          <div key={i} className="principle-card-job">
                            <HiOutlineSparkles size={16} className="principle-icon" />
                            <span>{exp}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="fit-indicators-split">
                      <div className="fit-column">
                        <h5 className="column-title matched">Matched Indicators</h5>
                        <ul className="indicators-bullets">
                          {result.company_analysis?.matched_indicators?.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="fit-column">
                        <h5 className="column-title missing">Gaps Identified</h5>
                        <ul className="indicators-bullets">
                          {result.company_analysis?.missing_indicators?.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                          {(!result.company_analysis?.missing_indicators || result.company_analysis.missing_indicators.length === 0) && (
                            <li>No cultural indicator gaps detected!</li>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'salary' && (
                  <div className="salary-tab-content">
                    <div className="salary-comparison-card">
                      <div className="salary-row">
                        <div className="sal-box">
                          <span className="sal-lbl">Expected Salary</span>
                          <span className="sal-val highlight-sal">{result.salary_analysis?.expected_salary}</span>
                        </div>
                        <div className="sal-box">
                          <span className="sal-lbl">Market Average Forecast</span>
                          <span className="sal-val">{result.salary_analysis?.market_salary}</span>
                        </div>
                      </div>
                      
                      <div className="salary-graph-mock">
                        <div className="graph-bar-row">
                          <span>Role Benchmark</span>
                          <div className="benchmark-bar-track">
                            <div className="benchmark-bar-fill" style={{ width: '85%' }} />
                          </div>
                          <span>{result.salary_analysis?.role_salary}</span>
                        </div>
                        <div className="graph-bar-row">
                          <span>Regional Average</span>
                          <div className="benchmark-bar-track">
                            <div className="benchmark-bar-fill" style={{ width: '70%' }} />
                          </div>
                          <span>{result.salary_analysis?.country_salary}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'interview' && (
                  <div className="interview-tab-content">
                    <div className="interview-scores-list">
                      {[
                        { label: 'Technical Score', value: result.interview_analysis?.technical_score },
                        { label: 'Projects competency', value: result.interview_analysis?.projects_score },
                        { label: 'Experience relevance', value: result.interview_analysis?.experience_score },
                        { label: 'Leadership potential', value: result.interview_analysis?.leadership_score },
                        { label: 'Communication quality', value: result.interview_analysis?.communication_score },
                      ].map((item, idx) => (
                        <div key={idx} className="interview-score-item">
                          <div className="int-score-meta">
                            <span>{item.label}</span>
                            <strong style={{ color: getScoreColor(item.value) }}>{item.value}%</strong>
                          </div>
                          <div className="int-progress-track">
                            <div className="int-progress-fill" style={{ width: `${item.value}%`, backgroundColor: getScoreColor(item.value) }} />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="interview-tips-box">
                      <h4>Interview Preparation Tips</h4>
                      <ul className="tips-list">
                        {result.interview_analysis?.feedback?.map((tip, i) => (
                          <li key={i}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default JobATSDashboard;

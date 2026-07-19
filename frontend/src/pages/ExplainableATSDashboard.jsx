import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  HiOutlineArrowLeft,
  HiOutlineSparkles,
  HiOutlineCheckCircle,
  HiOutlineExclamationCircle,
  HiOutlineInformationCircle,
  HiOutlineLightBulb,
  HiOutlineTrendingUp,
  HiOutlinePresentationChartLine,
  HiOutlineShieldCheck
} from 'react-icons/hi';
import { atsAPI } from '../api/ats';
import '../styles/ExplainableATSDashboard.css';

const ExplainableATSDashboard = () => {
  const { id: resumeId } = useParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  
  // Accordion state
  const [expandedCategory, setExpandedCategory] = useState('Skills');

  // Simulator states
  const [simulatorActions, setSimulatorActions] = useState([]);
  const [simulatedResult, setSimulatedResult] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const [suggestedActions, setSuggestedActions] = useState([]);

  // Action plan states
  const [actionPlan, setActionPlan] = useState([]);
  const [priorityFilter, setPriorityFilter] = useState('all');

  useEffect(() => {
    fetchExplainabilityData();
  }, [resumeId]);

  const fetchExplainabilityData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get explanation report
      const expRes = await atsAPI.getExplanation(resumeId);
      setData(expRes.data);

      // Get initial action plan
      const planRes = await atsAPI.getActionPlan(resumeId);
      setActionPlan(planRes.data.action_plan || []);

      // Run an initial empty simulation to fetch suggested actions
      const simRes = await atsAPI.simulateScore(resumeId, []);
      setSimulatedResult(simRes.data.simulation);
      setSuggestedActions(simRes.data.suggested_actions || []);

      setLoading(false);
    } catch (err) {
      console.error(err);
      setError('Failed to load ATS explainability data. Make sure you have analyzed your resume first.');
      setLoading(false);
    }
  };

  const handleToggleSimulation = async (actionId) => {
    let updatedActions = [...simulatorActions];
    if (updatedActions.includes(actionId)) {
      updatedActions = updatedActions.filter(a => a !== actionId);
    } else {
      updatedActions.push(actionId);
    }
    setSimulatorActions(updatedActions);

    try {
      setSimulating(true);
      const res = await atsAPI.simulateScore(resumeId, updatedActions);
      setSimulatedResult(res.data.simulation);
      setSimulating(false);
    } catch (err) {
      console.error('Simulation calculation failed', err);
      setSimulating(false);
    }
  };

  const getScoreColorClass = (score) => {
    if (score >= 90) return 'text-success border-success bg-success-light';
    if (score >= 70) return 'text-warning border-warning bg-warning-light';
    return 'text-danger border-danger bg-danger-light';
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'badge-danger';
      case 'high': return 'badge-warning';
      case 'medium': return 'badge-primary';
      default: return 'badge-secondary';
    }
  };

  if (loading) {
    return (
      <div className="explainable-ats-page loading-state">
        <div className="glass-loader-card">
          <div className="spinner"></div>
          <p>Compiling Explainable ATS Audits...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="explainable-ats-page error-state">
        <div className="error-card glass-card">
          <HiOutlineExclamationCircle className="error-icon" />
          <h2>Explainability Load Error</h2>
          <p>{error}</p>
          <Link to={`/resumes/${resumeId}/ats`} className="btn-back">
            <HiOutlineArrowLeft /> Back to ATS Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const overallScore = data?.overall_score || 0;
  const confidence = data?.confidence || 95;
  const categories = data?.category_explanations || {};
  const breakdown = data?.ats_score_breakdown || {};
  const reportText = data?.natural_language_report || '';

  // Filter recommendations
  const filteredRecommendations = actionPlan.filter(rec => {
    if (priorityFilter === 'all') return true;
    return rec.priority.toLowerCase() === priorityFilter.toLowerCase();
  });

  return (
    <div className="explainable-ats-page">
      <div className="ats-container">
        
        {/* Header Area */}
        <header className="explain-header">
          <Link to={`/resumes/${resumeId}/ats`} className="back-link">
            <HiOutlineArrowLeft /> Back to ATS Analytics
          </Link>
          <div className="explain-title-block">
            <h1 className="explain-title">Explainable ATS Intelligence</h1>
            <p className="explain-subtitle">Phase G: Deep Transparent Score Explanations & Predictive Roadmap Simulator</p>
          </div>
        </header>

        {/* Hero Section */}
        <section className="explain-hero-grid">
          {/* Left: Overall Ring */}
          <div className="glass-card score-hero-card">
            <div className="circular-gauge">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="42" className="gauge-bg" />
                <circle 
                  cx="50" 
                  cy="50" 
                  r="42" 
                  className="gauge-fill" 
                  strokeDasharray="264" 
                  strokeDashoffset={264 - (264 * overallScore) / 100}
                />
              </svg>
              <div className="gauge-text">
                <span className="gauge-score">{overallScore}</span>
                <span className="gauge-label">ATS Score</span>
              </div>
            </div>
            
            <div className="confidence-indicator">
              <HiOutlineShieldCheck className="confidence-icon" />
              <span>Explanation Confidence: <strong>{confidence}%</strong></span>
            </div>
          </div>

          {/* Right: Natural Language Report Summary */}
          <div className="glass-card summary-text-card">
            <h3 className="section-subtitle">
              <HiOutlineSparkles /> Natural Language Analysis
            </h3>
            <p className="summary-paragraph">{reportText}</p>
            
            <div className="summary-badges-row">
              <div className="mini-badge">
                <span>Standing: <strong>{overallScore >= 80 ? 'Highly Competitive' : overallScore >= 70 ? 'Satisfactory' : 'Needs Optimization'}</strong></span>
              </div>
              <div className="mini-badge">
                <span>Parser Confidence: <strong>High</strong></span>
              </div>
            </div>
          </div>
        </section>

        {/* Score Contribution Breakdown */}
        <section className="glass-card breakdown-section">
          <h2 className="card-title">
            <HiOutlinePresentationChartLine /> Score Contribution Breakdown
          </h2>
          <div className="breakdown-grid">
            {Object.keys(breakdown).map((key) => {
              if (key === 'Final') return null;
              const val = breakdown[key];
              const maxVal = 100;
              // Format labels
              const label = key === 'Skills' ? 'Skills Matrix' :
                            key === 'Projects' ? 'Portfolio Projects' :
                            key === 'Experience' ? 'Work Experience' :
                            key === 'Education' ? 'Academic Record' : key;
              
              return (
                <div className="breakdown-item" key={key}>
                  <div className="breakdown-info">
                    <span className="breakdown-label">{label}</span>
                    <span className="breakdown-value">
                      {key === 'Penalties' ? `-${val} pts` : key === 'Bonuses' ? `+${val} pts` : `${val}/100`}
                    </span>
                  </div>
                  <div className="breakdown-bar-bg">
                    <div 
                      className={`breakdown-bar-fill ${key === 'Penalties' ? 'bg-danger' : key === 'Bonuses' ? 'bg-success' : 'bg-primary'}`}
                      style={{ width: `${Math.min(100, Math.max(0, val))}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Main Dashboard Layout */}
        <div className="explain-main-layout">
          
          {/* Left: Category Accordions */}
          <div className="explain-left-panel">
            <h2 className="panel-title">Category Audit Deep-Dive</h2>
            <div className="accordion-list">
              {Object.keys(categories).map((catName) => {
                const cat = categories[catName];
                const isExpanded = expandedCategory === catName;
                const scoreColor = getScoreColorClass(cat.score);

                return (
                  <div 
                    className={`accordion-item glass-card ${isExpanded ? 'expanded' : ''}`} 
                    key={catName}
                  >
                    <div 
                      className="accordion-header" 
                      onClick={() => setExpandedCategory(isExpanded ? '' : catName)}
                    >
                      <div className="header-left">
                        <span className={`category-score-badge ${scoreColor}`}>
                          {cat.score}
                        </span>
                        <span className="category-title">{catName}</span>
                      </div>
                      <div className="header-right">
                        {cat.impact > 0 ? (
                          <span className="impact-text font-semibold text-danger">
                            -{cat.impact} pts impact
                          </span>
                        ) : (
                          <span className="impact-text font-semibold text-success">
                            Optimized
                          </span>
                        )}
                        <span className="chevron-icon">{isExpanded ? '▼' : '▶'}</span>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="accordion-body">
                        <div className="body-grid">
                          <div className="body-section">
                            <span className="body-section-title">
                              <HiOutlineInformationCircle /> Why this score?
                            </span>
                            <p className="body-section-content">{cat.reason}</p>
                          </div>
                          
                          <div className="body-section">
                            <span className="body-section-title">
                              <HiOutlinePresentationChartLine /> Empirical Evidence
                            </span>
                            <p className="body-section-content evidence-text">{cat.evidence}</p>
                          </div>

                          <div className="body-section full-width">
                            <div className="recommendation-box">
                              <div className="rec-info">
                                <HiOutlineLightBulb className="rec-icon" />
                                <div>
                                  <span className="rec-title">Next Action Item</span>
                                  <p className="rec-desc">{cat.recommendation}</p>
                                </div>
                              </div>
                              {cat.estimated_improvement > 0 && (
                                <div className="rec-boost bg-primary-light text-primary">
                                  <span>Boost</span>
                                  <strong>+{cat.estimated_improvement} pts</strong>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Simulator & Actions */}
          <div className="explain-right-panel">
            
            {/* Interactive Simulator */}
            <div className="glass-card simulator-card">
              <h2 className="card-title">
                <HiOutlineTrendingUp /> Score Simulator
              </h2>
              <p className="simulator-desc">
                Toggle potential improvements below to predict your new estimated ATS Score in real-time.
              </p>

              {/* Score Comparison Display */}
              <div className="simulator-display">
                <div className="score-compare">
                  <div className="compare-block">
                    <span className="compare-label">Current</span>
                    <span className="compare-val text-muted">{overallScore}</span>
                  </div>
                  <div className="compare-arrow">➔</div>
                  <div className="compare-block">
                    <span className="compare-label">Simulated</span>
                    <span className={`compare-val ${simulating ? 'loading-pulse' : 'text-success font-bold'}`}>
                      {simulatedResult?.estimated_score || overallScore}
                    </span>
                  </div>
                </div>
                {simulatedResult?.score_boost > 0 && (
                  <div className="simulator-boost-badge">
                    🎉 +{simulatedResult.score_boost} Points Improvement Predicted!
                  </div>
                )}
              </div>

              {/* Toggles */}
              <div className="simulator-toggles">
                {suggestedActions.map((act) => {
                  const isChecked = simulatorActions.includes(act.action_id);
                  return (
                    <div 
                      key={act.action_id}
                      className={`toggle-row ${isChecked ? 'active' : ''}`}
                      onClick={() => handleToggleSimulation(act.action_id)}
                    >
                      <div className="toggle-left">
                        <span className="toggle-title">{act.name}</span>
                        <span className="toggle-desc">{act.description}</span>
                      </div>
                      <div className="toggle-right">
                        <span className="toggle-boost">+{act.points} pts</span>
                        <input 
                          type="checkbox" 
                          checked={isChecked}
                          onChange={() => {}} // Handled by div click
                          className="toggle-checkbox"
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Prioritized Checklist */}
            <div className="glass-card checklist-card">
              <h2 className="card-title">
                <HiOutlineCheckCircle /> Action Roadmap
              </h2>
              <p className="roadmap-desc">Step-by-step roadmap to maximize your score.</p>
              
              {/* Tabs */}
              <div className="tab-filters">
                {['all', 'critical', 'high', 'medium'].map(p => (
                  <button 
                    key={p}
                    className={`tab-btn ${priorityFilter === p ? 'active' : ''}`}
                    onClick={() => setPriorityFilter(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>

              {/* Roadmap list */}
              <div className="roadmap-list">
                {filteredRecommendations.length > 0 ? (
                  filteredRecommendations.map((rec, index) => (
                    <div className="roadmap-item-card" key={rec.id || index}>
                      <div className="item-header">
                        <span className={`priority-badge ${getPriorityBadgeClass(rec.priority)}`}>
                          {rec.priority}
                        </span>
                        <span className="item-boost">+{rec.score_impact} pts</span>
                      </div>
                      <span className="item-category">{rec.category}</span>
                      <p className="item-text">{rec.recommendation_text}</p>
                    </div>
                  ))
                ) : (
                  <p className="empty-checklist">No active recommendations in this filter. Your profile is in excellent standing!</p>
                )}
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
};

export default ExplainableATSDashboard;

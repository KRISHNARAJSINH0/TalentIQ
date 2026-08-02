/**
 * HeroSection Component – Premium Redesign
 * Animated hero with floating dashboard mockup, typed effect, gradient orbs.
 */

import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HiArrowRight,
  HiSparkles,
  HiCheckCircle,
  HiStar,
} from 'react-icons/hi2';
import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';

const TYPED_WORDS = ['Smart AI', 'One Click', 'Seconds'];

const HeroSection = () => {
  const { isAuthenticated } = useAuth();
  const [wordIndex, setWordIndex] = useState(0);
  const [displayed, setDisplayed] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const word = TYPED_WORDS[wordIndex];
    let timeout;
    if (!isDeleting && displayed.length < word.length) {
      timeout = setTimeout(() => setDisplayed(word.slice(0, displayed.length + 1)), 100);
    } else if (!isDeleting && displayed.length === word.length) {
      timeout = setTimeout(() => setIsDeleting(true), 1800);
    } else if (isDeleting && displayed.length > 0) {
      timeout = setTimeout(() => setDisplayed(displayed.slice(0, -1)), 55);
    } else {
      setIsDeleting(false);
      setWordIndex((i) => (i + 1) % TYPED_WORDS.length);
    }
    return () => clearTimeout(timeout);
  }, [displayed, isDeleting, wordIndex]);

  return (
    <section className="lp-hero" id="hero">
      {/* Orb backgrounds */}
      <div className="lp-orb lp-orb-1" />
      <div className="lp-orb lp-orb-2" />
      <div className="lp-orb lp-orb-3" />
      <div className="lp-grid-overlay" />

      <div className="lp-hero-inner container">
        {/* ── Left Copy ── */}
        <div className="lp-hero-copy">
          <motion.div
            className="lp-badge"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="lp-badge-dot" />
            AI-Powered Career Intelligence
          </motion.div>

          <motion.h1
            className="lp-hero-title"
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            Build Your Career
            <br />
            with{' '}
            <span className="lp-typed-wrap">
              <span className="lp-typed-text">{displayed}</span>
              <span className="lp-cursor" />
            </span>
          </motion.h1>

          <motion.p
            className="lp-hero-desc"
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Parse resumes instantly, generate stunning portfolios, crush ATS
            filters, and land your dream job — all powered by Google Gemini AI.
          </motion.p>

          <motion.ul
            className="lp-hero-perks"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            {['ATS Score Optimization', 'AI Resume Parsing', 'Portfolio in 1-Click'].map((p) => (
              <li key={p}>
                <HiCheckCircle className="lp-perk-icon" />
                {p}
              </li>
            ))}
          </motion.ul>

          <motion.div
            className="lp-hero-actions"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {isAuthenticated ? (
              <Link to="/dashboard">
                <button className="lp-btn-primary" id="hero-dashboard-btn">
                  Go to Dashboard <HiArrowRight />
                </button>
              </Link>
            ) : (
              <>
                <Link to="/register">
                  <button className="lp-btn-primary" id="hero-get-started-btn">
                    Get Started Free <HiArrowRight />
                  </button>
                </Link>
                <Link to="/login">
                  <button className="lp-btn-ghost" id="hero-login-btn">
                    Login
                  </button>
                </Link>
              </>
            )}
          </motion.div>

          {/* Social proof row */}
          <motion.div
            className="lp-social-proof"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <div className="lp-avatars">
              {['👩‍💼', '👨‍💻', '👩‍🎓', '👨‍🔬', '👩‍💻'].map((e, i) => (
                <span key={i} className="lp-avatar">{e}</span>
              ))}
            </div>
            <div className="lp-proof-text">
              <div className="lp-stars">
                {[...Array(5)].map((_, i) => <HiStar key={i} />)}
              </div>
              <span>Trusted by <strong>10,000+</strong> professionals</span>
            </div>
          </motion.div>
        </div>

        {/* ── Right Mockup ── */}
        <motion.div
          className="lp-hero-visual"
          initial={{ opacity: 0, x: 60 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
        >
          {/* Main dashboard card */}
          <div className="lp-mockup-card">
            <div className="lp-mockup-header">
              <div className="lp-mockup-dots">
                <span /><span /><span />
              </div>
              <span className="lp-mockup-title">TalentIQ Dashboard</span>
              <span className="lp-mockup-status">
                <span className="lp-mockup-status-dot" /> Live
              </span>
            </div>

            <div className="lp-mockup-body">
              {/* ATS Score ring */}
              <div className="lp-mockup-score-area">
                <div className="lp-score-ring">
                  <svg viewBox="0 0 120 120" className="lp-ring-svg">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10"/>
                    <circle
                      cx="60" cy="60" r="50" fill="none"
                      stroke="url(#scoreGrad)" strokeWidth="10"
                      strokeLinecap="round"
                      strokeDasharray="314"
                      strokeDashoffset="47"
                      transform="rotate(-90 60 60)"
                    />
                    <defs>
                      <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#2563EB"/>
                        <stop offset="100%" stopColor="#7C3AED"/>
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="lp-ring-label">
                    <span className="lp-ring-val">98</span>
                    <span className="lp-ring-sub">ATS Score</span>
                  </div>
                </div>
                <div className="lp-score-metrics">
                  {[
                    { label: 'Keywords', pct: 95, color: '#22C55E' },
                    { label: 'Format',   pct: 88, color: '#2563EB' },
                    { label: 'Impact',   pct: 92, color: '#7C3AED' },
                  ].map((m) => (
                    <div key={m.label} className="lp-metric-row">
                      <span className="lp-metric-label">{m.label}</span>
                      <div className="lp-metric-bar">
                        <div
                          className="lp-metric-fill"
                          style={{ width: `${m.pct}%`, background: m.color }}
                        />
                      </div>
                      <span className="lp-metric-val">{m.pct}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Skills tags */}
              <div className="lp-mockup-skills">
                {['React', 'Python', 'Machine Learning', 'AWS', 'Docker', 'TypeScript'].map((s) => (
                  <span key={s} className="lp-skill-tag">{s}</span>
                ))}
              </div>

              {/* AI suggestion row */}
              <div className="lp-ai-suggestion">
                <HiSparkles className="lp-ai-icon" />
                <span>AI suggests adding <strong>Kubernetes</strong> to boost score by +4pts</span>
              </div>
            </div>
          </div>

          {/* Floating notification cards */}
          <motion.div
            className="lp-float-card lp-float-top"
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          >
            <HiCheckCircle className="lp-float-icon success" />
            <div>
              <div className="lp-float-title">Resume Parsed!</div>
              <div className="lp-float-sub">42 skills extracted • 2s</div>
            </div>
          </motion.div>

          <motion.div
            className="lp-float-card lp-float-bottom"
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
          >
            <span className="lp-float-emoji">🚀</span>
            <div>
              <div className="lp-float-title">Portfolio Live</div>
              <div className="lp-float-sub">yourname.talentiq.io</div>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Stats bar */}
      <motion.div
        className="lp-stats-bar"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
      >
        <div className="container lp-stats-inner">
          {[
            { value: '10K+', label: 'Resumes Parsed' },
            { value: '98%',  label: 'ATS Pass Rate' },
            { value: '5K+',  label: 'Portfolios Built' },
            { value: '4.9★', label: 'User Rating' },
          ].map((s) => (
            <div key={s.label} className="lp-stat">
              <div className="lp-stat-val">{s.value}</div>
              <div className="lp-stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

export default HeroSection;

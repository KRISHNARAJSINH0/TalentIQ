/**
 * HeroSection Component
 * Animated hero with gradient text, CTA buttons, and floating orbs.
 */

import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowRight } from 'react-icons/hi2';

import { useAuth } from '../contexts/AuthContext';

const HeroSection = () => {
  const { isAuthenticated } = useAuth();

  return (
    <section className="hero" id="hero">
      {/* Background effects */}
      <div className="hero-orb hero-orb-1"></div>
      <div className="hero-orb hero-orb-2"></div>
      <div className="hero-orb hero-orb-3"></div>
      <div className="hero-grid"></div>

      <div className="hero-content">
        <motion.div
          className="hero-badge"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="hero-badge-dot"></span>
          AI-Powered Resume Platform
        </motion.div>

        <motion.h1
          className="hero-title"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Build Your Career with{' '}
          <span className="hero-title-highlight">Smart AI</span>
        </motion.h1>

        <motion.p
          className="hero-description"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Parse resumes instantly, generate stunning portfolios, and optimize
          for ATS — all powered by advanced artificial intelligence.
        </motion.p>

        <motion.div
          className="hero-actions"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {isAuthenticated ? (
            <Link to="/dashboard">
              <button className="btn btn-primary btn-lg">
                Go to Dashboard
                <HiArrowRight />
              </button>
            </Link>
          ) : (
            <>
              <Link to="/register">
                <button className="btn btn-primary btn-lg">
                  Get Started Free
                  <HiArrowRight />
                </button>
              </Link>
              <Link to="/login">
                <button className="btn btn-outline btn-lg">
                  Login
                </button>
              </Link>
            </>
          )}
        </motion.div>

        <motion.div
          className="hero-stats"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="hero-stat">
            <div className="hero-stat-value">10K+</div>
            <div className="hero-stat-label">Resumes Parsed</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">98%</div>
            <div className="hero-stat-label">ATS Score</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">5K+</div>
            <div className="hero-stat-label">Portfolios Built</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">4.9★</div>
            <div className="hero-stat-label">User Rating</div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;

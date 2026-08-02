/**
 * Navbar Component – Dynamic auth-aware navigation.
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { HiOutlineLightBulb } from 'react-icons/hi2';
import { RiCloseLine } from 'react-icons/ri';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import NotificationBell from './NotificationBell';
import '../styles/Navbar.css';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const closeMobile = () => setMobileOpen(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Smooth scroll to a section; if not on home page, navigate first then scroll
  const scrollToSection = (sectionId) => {
    closeMobile();
    const doScroll = () => {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    if (location.pathname !== '/') {
      navigate('/');
      setTimeout(doScroll, 400);
    } else {
      doScroll();
    }
  };

  return (
    <>
      <motion.nav
        className={`navbar ${scrolled ? 'scrolled' : ''}`}
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <div className="navbar-inner">
          <Link to="/" className="navbar-brand">
            <div className="navbar-brand-icon"><HiOutlineLightBulb /></div>
            TalentIQ
          </Link>

          <ul className="navbar-links">
            {isAuthenticated ? (
              <>
                <li><Link to="/dashboard" className="navbar-link">Dashboard</Link></li>
                <li><Link to="/resumes" className="navbar-link">Resumes</Link></li>
                <li><Link to="/profile" className="navbar-link">Profile</Link></li>
                <li><Link to="/portfolio" className="navbar-link">Portfolio</Link></li>
                <li><Link to="/career" className="navbar-link">Career AI</Link></li>
                <li><Link to="/timeline" className="navbar-link">Timeline</Link></li>
                {user?.role === 'admin' && <li><Link to="/admin" className="navbar-link">Admin</Link></li>}
              </>
            ) : (
              <>
                <li><button className="navbar-link" onClick={() => scrollToSection('features')}>Features</button></li>
                <li><button className="navbar-link" onClick={() => scrollToSection('testimonials')}>About</button></li>
              </>
            )}
          </ul>

          <div className="navbar-actions">
            {isAuthenticated ? (
              <>
                <NotificationBell />
                <span className="navbar-user-name" style={{ marginLeft: '12px' }}>
                  {user?.first_name}
                </span>
                <button className="navbar-btn-login" onClick={handleLogout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <button className="navbar-btn-login">Login</button>
                </Link>
                <Link to="/register">
                  <button className="navbar-btn-start">Get Started</button>
                </Link>
              </>
            )}
          </div>

          <button
            className="navbar-toggle"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation menu"
          >
            <span></span><span></span><span></span>
          </button>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <div className={`navbar-mobile ${mobileOpen ? 'open' : ''}`}>
        <button className="navbar-mobile-close" onClick={closeMobile}>
          <RiCloseLine />
        </button>
        {isAuthenticated ? (
          <>
            <Link to="/dashboard" className="navbar-mobile-link" onClick={closeMobile}>Dashboard</Link>
            <Link to="/resumes" className="navbar-mobile-link" onClick={closeMobile}>Resumes</Link>
            <Link to="/profile" className="navbar-mobile-link" onClick={closeMobile}>Profile</Link>
            <Link to="/portfolio" className="navbar-mobile-link" onClick={closeMobile}>Portfolio</Link>
            <Link to="/career" className="navbar-mobile-link" onClick={closeMobile}>Career AI</Link>
            <Link to="/timeline" className="navbar-mobile-link" onClick={closeMobile}>Timeline</Link>
            {user?.role === 'admin' && <Link to="/admin" className="navbar-mobile-link" onClick={closeMobile}>Admin</Link>}
            <button className="navbar-mobile-link" onClick={() => { closeMobile(); handleLogout(); }} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
              Logout
            </button>
          </>
        ) : (
          <>
            <button className="navbar-mobile-link" onClick={() => scrollToSection('features')}>Features</button>
            <button className="navbar-mobile-link" onClick={() => scrollToSection('testimonials')}>About</button>
            <Link to="/login" className="navbar-mobile-link" onClick={closeMobile}>Login</Link>
            <Link to="/register" className="navbar-mobile-link navbar-mobile-cta" onClick={closeMobile}>Get Started</Link>
          </>
        )}
      </div>
    </>
  );
};

export default Navbar;

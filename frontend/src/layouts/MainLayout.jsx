/**
 * MainLayout Component
 * Wraps pages with Navbar/Sidebar depending on auth status.
 */

import { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import GlassSidebar from '../components/GlassSidebar';
import GlassNavbar from '../components/GlassNavbar';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import * as Hi2 from 'react-icons/hi2';

const MainLayout = () => {
  const { isAuthenticated } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  if (!isAuthenticated) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--gradient-background)' }}>
        {/* Background Floating Circles */}
        <div className="floating-bg">
          <div className="floating-circle circle-1"></div>
          <div className="floating-circle circle-2"></div>
          <div className="floating-circle circle-3"></div>
        </div>
        <Navbar />
        <main style={{ flex: 1 }}>
          <Outlet />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="saas-layout">
      {/* Background Floating Circles */}
      <div className="floating-bg">
        <div className="floating-circle circle-1"></div>
        <div className="floating-circle circle-2"></div>
        <div className="floating-circle circle-3"></div>
      </div>

      {/* Left Glass Sidebar */}
      <GlassSidebar
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main SaaS Dashboard Container */}
      <div className={`saas-main-container ${isCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}`}>
        {/* Top Sticky Glass Navbar */}
        <GlassNavbar setIsMobileOpen={setIsMobileOpen} />

        {/* Center Main Content Area */}
        <main className="saas-content">
          <Outlet />
        </main>

        {/* Mobile Bottom Navigation Bar */}
        <div className="hide-on-desktop glass-panel" style={{
          position: 'fixed',
          bottom: '8px',
          left: '8px',
          right: '8px',
          height: '58px',
          zIndex: 1000,
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          borderRadius: '16px',
          backgroundColor: 'var(--glass-bg)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--glass-border)',
          padding: '0 4px',
          boxShadow: '0 -4px 24px var(--glass-shadow)',
        }}>
          <NavLink to="/dashboard" end style={({ isActive }) => ({
            color: isActive ? 'var(--primary)' : 'var(--text-color)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            fontSize: '0.65rem',
            fontWeight: 600,
            textDecoration: 'none',
            gap: '3px'
          })}>
            <Hi2.HiOutlineSquares2X2 size={20} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink to="/resumes" style={({ isActive }) => ({
            color: isActive ? 'var(--primary)' : 'var(--text-color)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            fontSize: '0.65rem',
            fontWeight: 600,
            textDecoration: 'none',
            gap: '3px'
          })}>
            <Hi2.HiOutlineDocumentText size={20} />
            <span>Resumes</span>
          </NavLink>

          <NavLink to="/career" style={({ isActive }) => ({
            color: isActive ? 'var(--primary)' : 'var(--text-color)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            fontSize: '0.65rem',
            fontWeight: 600,
            textDecoration: 'none',
            gap: '3px'
          })}>
            <Hi2.HiOutlineChatBubbleLeftRight size={20} />
            <span>Career AI</span>
          </NavLink>

          <NavLink to="/portfolio" style={({ isActive }) => ({
            color: isActive ? 'var(--primary)' : 'var(--text-color)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            fontSize: '0.65rem',
            fontWeight: 600,
            textDecoration: 'none',
            gap: '3px'
          })}>
            <Hi2.HiOutlineGlobeAlt size={20} />
            <span>Portfolio</span>
          </NavLink>

          <NavLink to="/profile" style={({ isActive }) => ({
            color: isActive ? 'var(--primary)' : 'var(--text-color)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            fontSize: '0.65rem',
            fontWeight: 600,
            textDecoration: 'none',
            gap: '3px'
          })}>
            <Hi2.HiOutlineUserCircle size={20} />
            <span>Profile</span>
          </NavLink>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;

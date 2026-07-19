import { useState } from 'react';
import { NavLink, Outlet, Navigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ThemeSwitcher from '../components/ThemeSwitcher';
import {
  HiOutlineHome,
  HiOutlineUsers,
  HiOutlineChartBar,
  HiOutlineDocumentText,
  HiOutlineCpuChip,
  HiOutlineClipboardDocumentList,
  HiOutlineLockClosed,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineArrowLeft,
  HiOutlineBars3
} from 'react-icons/hi2';
import { motion, AnimatePresence } from 'framer-motion';

const AdminLayout = () => {
  const { user, isAuthenticated } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Guard layout inside component just in case
  if (!isAuthenticated || user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  const adminMenu = [
    { to: '/admin/dashboard', label: 'Dashboard', icon: <HiOutlineHome size={22} /> },
    { to: '/admin/users', label: 'User Manager', icon: <HiOutlineUsers size={22} /> },
    { to: '/admin/analytics', label: 'Analytics', icon: <HiOutlineChartBar size={22} /> },
    { to: '/admin/reports', label: 'Reports', icon: <HiOutlineDocumentText size={22} /> },
    { to: '/admin/system', label: 'System Health', icon: <HiOutlineCpuChip size={22} /> },
    { to: '/admin/ats-calibration', label: 'ATS Calibration', icon: <HiOutlineCpuChip size={22} /> },
    { to: '/admin/logs', label: 'Audit Trail', icon: <HiOutlineClipboardDocumentList size={22} /> },
  ];


  const sidebarVariants = {
    expanded: { width: '280px' },
    collapsed: { width: '80px' }
  };

  const sidebarContent = (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '20px 14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: isCollapsed ? 'center' : 'space-between', marginBottom: '32px', height: '40px' }}>
        {!isCollapsed && (
          <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HiOutlineLockClosed /> Admin Portal
          </span>
        )}
        {isCollapsed && <HiOutlineLockClosed size={24} style={{ color: 'var(--danger)' }} />}
        
        <button
          className="hide-on-mobile"
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{ background: 'none', border: 'none', color: 'var(--subtext-color)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px' }}
        >
          {isCollapsed ? <HiOutlineChevronRight size={20} /> : <HiOutlineChevronLeft size={20} />}
        </button>

        <button
          className="hide-on-desktop"
          onClick={() => setIsMobileOpen(false)}
          style={{ background: 'none', border: 'none', color: 'var(--text-color)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
        >
          <HiOutlineChevronLeft size={24} />
        </button>
      </div>

      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {adminMenu.map((item, index) => (
          <NavLink
            key={index}
            to={item.to}
            onClick={() => setIsMobileOpen(false)}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              justifyContent: isCollapsed ? 'center' : 'flex-start',
              gap: '12px',
              padding: '12px',
              borderRadius: '16px',
              color: isActive ? '#FFFFFF' : 'var(--text-color)',
              background: isActive ? 'linear-gradient(135deg, #EF4444, #7C3AED)' : 'transparent',
              textDecoration: 'none',
              transition: 'all var(--transition-fast)',
              boxShadow: isActive ? '0 8px 24px rgba(239, 68, 68, 0.25)' : 'none',
            })}
            className="sidebar-link-item"
          >
            {item.icon}
            {!isCollapsed && <span style={{ fontSize: '0.9375rem', fontWeight: 500 }}>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Back to Candidate Portal */}
      <Link
        to="/dashboard"
        className="sidebar-link-item"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'flex-start',
          gap: '12px',
          padding: '12px',
          borderRadius: '16px',
          color: 'var(--primary)',
          textDecoration: 'none',
          transition: 'all var(--transition-fast)',
          marginTop: 'auto'
        }}
      >
        <HiOutlineArrowLeft size={20} />
        {!isCollapsed && <span style={{ fontSize: '0.9375rem', fontWeight: 500 }}>Candidate App</span>}
      </Link>
    </div>
  );

  return (
    <div className="saas-layout">
      {/* Background Circles */}
      <div className="floating-bg">
        <div className="floating-circle circle-1"></div>
        <div className="floating-circle circle-2"></div>
        <div className="floating-circle circle-3"></div>
      </div>

      {/* Desktop Sidebar */}
      <motion.aside
        className="glass-panel hide-on-mobile"
        animate={isCollapsed ? 'collapsed' : 'expanded'}
        variants={sidebarVariants}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
          bottom: '20px',
          zIndex: 1000,
          borderRadius: '24px',
          overflow: 'hidden',
        }}
      >
        {sidebarContent}
      </motion.aside>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000', zIndex: 1040 }}
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="glass-panel hide-on-desktop"
              style={{
                position: 'fixed',
                top: '12px',
                left: '12px',
                bottom: '12px',
                width: '280px',
                zIndex: 1050,
                borderRadius: '24px',
                backgroundColor: 'var(--bg-primary)',
              }}
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main Container */}
      <div className={`saas-main-container ${isCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}`}>
        {/* Top Sticky Header */}
        <header
          className="glass-panel"
          style={{
            position: 'sticky',
            top: '20px',
            left: '20px',
            right: '20px',
            height: '72px',
            zIndex: 999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
            borderRadius: '20px',
            marginBottom: '24px',
            backgroundColor: 'var(--glass-bg)',
            backdropFilter: 'blur(20px)',
            border: '1px solid var(--glass-border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              className="hide-on-desktop"
              onClick={() => setIsMobileOpen(true)}
              style={{ background: 'none', border: 'none', color: 'var(--text-color)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
            >
              <HiOutlineBars3 size={24} />
            </button>
            <span style={{ fontWeight: 700, color: 'var(--text-color)', fontSize: '1.1rem' }}>Admin Dashboard</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
            <ThemeSwitcher />
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #EF4444, #7C3AED)',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600,
            }}>
              A
            </div>
          </div>
        </header>

        {/* Content Outlet */}
        <main className="saas-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;

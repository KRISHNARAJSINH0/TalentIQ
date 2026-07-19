import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import * as Hi2 from 'react-icons/hi2';
import resumesAPI from '../api/resumes';

const GlassSidebar = ({ isCollapsed, setIsCollapsed, isMobileOpen, setIsMobileOpen }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeResumeId, setActiveResumeId] = useState(null);

  useEffect(() => {
    const fetchActiveResume = async () => {
      try {
        const response = await resumesAPI.getResumes();
        const data = response.data.results || response.data;
        if (Array.isArray(data)) {
          const active = data.find(r => r.is_active);
          if (active) {
            setActiveResumeId(active.id);
          } else {
            setActiveResumeId(null);
          }
        }
      } catch (err) {
        console.error('Failed to fetch active resume for sidebar:', err);
      }
    };

    if (user) {
      fetchActiveResume();
    }
  }, [user, location.pathname]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: <Hi2.HiOutlineSquares2X2 size={20} /> },
    { to: '/resumes', label: 'Resume', icon: <Hi2.HiOutlineDocumentText size={20} /> },
    { to: '/resumes', label: 'Parser', icon: <Hi2.HiOutlineArrowUpTray size={20} />, hash: '#upload' },
    { to: activeResumeId ? `/resumes/${activeResumeId}/ats` : '/resumes', label: 'ATS', icon: <Hi2.HiOutlineCpuChip size={20} /> },
    { to: activeResumeId ? `/resumes/${activeResumeId}/job-ats` : '/resumes', label: 'Job ATS', icon: <Hi2.HiOutlineSparkles size={20} /> },
    { to: activeResumeId ? `/resumes/${activeResumeId}/benchmark` : '/resumes', label: 'Benchmark', icon: <Hi2.HiOutlineChartBar size={20} /> },
    {to: '/portfolio', label: 'Portfolio', icon: <Hi2.HiOutlineGlobeAlt size={20} />},
    {to: '/career', label: 'Career Assistant', icon: <Hi2.HiOutlineChatBubbleLeftRight size={20} />},
    {to: '/career/reputation', label: 'Reputation', icon: <Hi2.HiOutlineCheckBadge size={20} />},
    {to: '/jobs', label: 'Job Intelligence', icon: <Hi2.HiOutlineBriefcase size={20} />},
    { to: '/jd-analyzer', label: 'JD Analyzer', icon: <Hi2.HiOutlineDocumentMagnifyingGlass size={20} /> },
    { to: '/timeline', label: 'Timeline', icon: <Hi2.HiOutlineQueueList size={20} /> },
    { to: '/notifications', label: 'Notifications', icon: <Hi2.HiOutlineBell size={20} /> },
    ...(user?.role === 'admin' ? [{ to: '/admin', label: 'Admin', icon: <Hi2.HiOutlineLockClosed size={20} /> }] : []),
    { to: '/profile/edit', label: 'Settings', icon: <Hi2.HiOutlineCog6Tooth size={20} /> },
  ];

  const sidebarVariants = {
    expanded: { width: '280px' },
    collapsed: { width: '80px' }
  };

  const content = (
    <div className="sidebar-inner" style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '16px' }}>
      {/* Sidebar Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: isCollapsed ? 'center' : 'space-between', marginBottom: '32px', height: '40px' }}>
        {!isCollapsed && (
          <span style={{ fontSize: '1.2rem', fontWeight: 800, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'flex', alignItems: 'center', gap: '8px', whiteSpace: 'nowrap' }}>
            <Hi2.HiOutlineSparkles style={{ color: '#2563EB' }} /> ResumeAI
          </span>
        )}
        {isCollapsed && <Hi2.HiOutlineSparkles size={24} style={{ color: '#2563EB' }} />}
        
        {/* Collapse Button - Desktop only */}
        <button
          className="hide-on-mobile"
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{ background: 'none', border: 'none', color: 'var(--subtext-color)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px' }}
        >
          {isCollapsed ? <Hi2.HiOutlineChevronRight size={20} /> : <Hi2.HiOutlineChevronLeft size={20} />}
        </button>
 
        {/* Close Button - Mobile only */}
        <button
          className="hide-on-desktop"
          onClick={() => setIsMobileOpen(false)}
          style={{ background: 'none', border: 'none', color: 'var(--text-color)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
        >
          <Hi2.HiXMark size={24} />
        </button>
      </div>

      {/* Navigation Items */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px', overflowY: 'auto', minHeight: 0 }} className="sidebar-nav-container">
        {navItems.map((item, index) => {
          const isActive = (() => {
            const { pathname, hash } = location;
            if (item.hash) {
              return pathname === item.to && hash === item.hash;
            }
            if (item.label === 'ATS') {
              return pathname.includes('/ats') && !pathname.includes('/job-ats') && !pathname.includes('/benchmark');
            }
            if (item.label === 'Job ATS') {
              return pathname.includes('/job-ats');
            }
            if (item.label === 'Benchmark') {
              return pathname.includes('/benchmark');
            }
            if (item.label === 'Parser') {
              return pathname === '/resumes' && hash === '#upload';
            }
            if (item.label === 'Resume') {
              return pathname.startsWith('/resumes') && !pathname.includes('/ats') && !pathname.includes('/job-ats') && !pathname.includes('/benchmark') && hash !== '#upload';
            }
            if (item.to === '/career') {
              return pathname === '/career' || pathname === '/career/roadmap' || pathname === '/career/cover-letter';
            }
            return pathname === item.to || (item.to !== '/dashboard' && pathname.startsWith(item.to));
          })();

          return (
            <Link
              key={index}
              to={item.hash ? `${item.to}${item.hash}` : item.to}
              onClick={() => setIsMobileOpen(false)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: isCollapsed ? 'center' : 'flex-start',
                gap: '12px',
                padding: isCollapsed ? '0' : '0 16px',
                height: '48px',
                borderRadius: '12px',
                color: isActive ? '#FFFFFF' : 'var(--text-color)',
                background: isActive ? 'var(--gradient-primary)' : 'transparent',
                textDecoration: 'none',
                transition: 'all var(--transition-fast)',
                boxShadow: isActive ? '0 4px 12px rgba(37, 99, 235, 0.15)' : 'none',
                transform: 'translateX(0px)',
              }}
              className={`sidebar-link-item ${isActive ? 'active' : ''}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {item.icon}
              </div>
              {!isCollapsed && <span style={{ fontSize: '16px', fontWeight: 500, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="sidebar-link-item"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'flex-start',
          gap: '12px',
          padding: isCollapsed ? '0' : '0 16px',
          height: '48px',
          borderRadius: '12px',
          color: 'var(--danger)',
          background: 'transparent',
          border: 'none',
          width: '100%',
          cursor: 'pointer',
          transition: 'all var(--transition-fast)',
          marginTop: 'auto'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Hi2.HiOutlineArrowLeftOnRectangle size={20} />
        </div>
        {!isCollapsed && <span style={{ fontSize: '16px', fontWeight: 500, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>Logout</span>}
      </button>
    </div>
  );

  return (
    <>
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
        {content}
      </motion.aside>

      {/* Mobile Drawer Sidebar */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: '#000',
                zIndex: 1040,
              }}
            />
            {/* Drawer */}
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
                background: 'var(--glass-bg)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                border: '1px solid var(--glass-border)',
                boxShadow: '0 10px 40px var(--glass-shadow)',
                overflow: 'hidden',
              }}
            >
              {content}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Global styling for Sidebar links hover translateX(4px) */}
      <style>{`
        .sidebar-link-item:hover {
          color: var(--primary) !important;
          transform: ${isCollapsed ? 'none' : 'translateX(4px)'} !important;
          background: rgba(37, 99, 235, 0.05);
        }
        html.dark .sidebar-link-item:hover {
          background: rgba(255, 255, 255, 0.05);
        }
        .sidebar-link-item.active:hover {
          color: #FFFFFF !important;
          transform: none !important;
          background: var(--gradient-primary) !important;
        }
        .sidebar-nav-container::-webkit-scrollbar {
          width: 6px;
        }
        .sidebar-nav-container::-webkit-scrollbar-track {
          background: transparent;
        }
        .sidebar-nav-container::-webkit-scrollbar-thumb {
          background: rgba(37, 99, 235, 0.15);
          border-radius: 6px;
        }
        .sidebar-nav-container::-webkit-scrollbar-thumb:hover {
          background: rgba(37, 99, 235, 0.35);
        }
        .sidebar-nav-container {
          scrollbar-width: thin;
          scrollbar-color: rgba(37, 99, 235, 0.15) transparent;
        }
      `}</style>
    </>
  );
};

export default GlassSidebar;

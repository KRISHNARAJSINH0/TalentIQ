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
    { to: 'https://resume-builder-from-talent-iq.vercel.app', label: 'Resume Builder', icon: <Hi2.HiOutlinePencilSquare size={20} />, isExternal: true },
    { to: '/resumes', label: 'Parser', icon: <Hi2.HiOutlineArrowUpTray size={20} />, hash: '#upload' },
    { to: activeResumeId ? `/resumes/${activeResumeId}/ats` : '/resumes', label: 'ATS Intelligence', icon: <Hi2.HiOutlineCpuChip size={20} /> },
    { to: activeResumeId ? `/resumes/${activeResumeId}/job-ats` : '/resumes', label: 'Job ATS Analysis', icon: <Hi2.HiOutlineSparkles size={20} /> },
    { to: activeResumeId ? `/resumes/${activeResumeId}/benchmark` : '/resumes', label: 'Benchmark Rank', icon: <Hi2.HiOutlineChartBar size={20} /> },
    { to: '/portfolio', label: 'Portfolio', icon: <Hi2.HiOutlineGlobeAlt size={20} /> },
    { to: '/career', label: 'Career Assistant', icon: <Hi2.HiOutlineChatBubbleLeftRight size={20} /> },
    { to: '/career/reputation', label: 'Reputation', icon: <Hi2.HiOutlineCheckBadge size={20} /> },
    { to: '/jobs', label: 'Job Intelligence', icon: <Hi2.HiOutlineBriefcase size={20} /> },
    { to: '/jd-analyzer', label: 'JD Analyzer', icon: <Hi2.HiOutlineDocumentMagnifyingGlass size={20} /> },
    { to: '/timeline', label: 'Timeline', icon: <Hi2.HiOutlineQueueList size={20} /> },
    { to: '/notifications', label: 'Notifications', icon: <Hi2.HiOutlineBell size={20} /> },
    ...(user?.role === 'admin' ? [{ to: '/admin', label: 'Admin Portal', icon: <Hi2.HiOutlineLockClosed size={20} /> }] : []),
    { to: '/profile/edit', label: 'Settings', icon: <Hi2.HiOutlineCog6Tooth size={20} /> },
  ];

  const sidebarVariants = {
    expanded: { width: '280px' },
    collapsed: { width: '80px' }
  };

  const content = (
    <div className="sidebar-inner" style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '16px 12px', boxSizing: 'border-box' }}>
      
      {/* Sidebar Header / Logo */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: isCollapsed ? 'center' : 'space-between', marginBottom: '24px', padding: '0 8px', height: '44px' }}>
        {!isCollapsed && (
          <span style={{ fontSize: '1.25rem', fontWeight: 800, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'flex', alignItems: 'center', gap: '10px', whiteSpace: 'nowrap', letterSpacing: '-0.02em' }}>
            <Hi2.HiOutlineLightBulb style={{ color: '#2563EB', fontSize: '1.4rem' }} /> TalentIQ
          </span>
        )}
        {isCollapsed && <Hi2.HiOutlineLightBulb size={26} style={{ color: '#2563EB' }} />}
        
        {/* Collapse Button - Desktop only */}
        <button
          className="hide-on-mobile sidebar-toggle-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          aria-label="Toggle Sidebar"
          style={{
            background: 'var(--glass-bg)',
            border: '1px solid var(--glass-border)',
            color: 'var(--subtext-color)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '32px',
            height: '32px',
            borderRadius: '10px',
            transition: 'all var(--transition-fast)'
          }}
        >
          {isCollapsed ? <Hi2.HiOutlineChevronRight size={18} /> : <Hi2.HiOutlineChevronLeft size={18} />}
        </button>

        {/* Close Button - Mobile only */}
        <button
          className="hide-on-desktop"
          onClick={() => setIsMobileOpen(false)}
          aria-label="Close Navigation"
          style={{ background: 'none', border: 'none', color: 'var(--text-color)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
        >
          <Hi2.HiXMark size={24} />
        </button>
      </div>

      {/* Navigation Items list container */}
      <nav 
        style={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '6px', 
          overflowY: 'auto', 
          minHeight: 0,
          paddingRight: '4px'
        }} 
        className="sidebar-nav-container"
      >
        {navItems.map((item, index) => {
          if (item.isExternal) {
            return (
              <a
                key={index}
                href={item.to}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsMobileOpen(false)}
                title={isCollapsed ? item.label : undefined}
                className="sidebar-nav-link"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: isCollapsed ? 'center' : 'flex-start',
                  gap: '12px',
                  padding: isCollapsed ? '0' : '0 16px',
                  height: '44px',
                  borderRadius: '12px',
                  color: 'var(--text-color)',
                  background: 'transparent',
                  textDecoration: 'none',
                  position: 'relative',
                  boxSizing: 'border-box',
                }}
              >
                <div className="nav-icon-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {item.icon}
                </div>
                {!isCollapsed && (
                  <span className="nav-label-text" style={{ fontSize: '0.92rem', fontWeight: 500, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                    {item.label}
                  </span>
                )}
              </a>
            );
          }

          const isActive = (() => {
            const { pathname, hash } = location;
            if (item.hash) {
              return pathname === item.to && hash === item.hash;
            }
            if (item.label.includes('ATS Intelligence')) {
              return pathname.includes('/ats') && !pathname.includes('/job-ats') && !pathname.includes('/benchmark');
            }
            if (item.label.includes('Job ATS Analysis')) {
              return pathname.includes('/job-ats');
            }
            if (item.label.includes('Benchmark')) {
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
              title={isCollapsed ? item.label : undefined}
              className={`sidebar-nav-link ${isActive ? 'active' : ''}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: isCollapsed ? 'center' : 'flex-start',
                gap: '12px',
                padding: isCollapsed ? '0' : '0 16px',
                height: '44px',
                borderRadius: '12px',
                color: isActive ? '#FFFFFF' : 'var(--text-color)',
                background: isActive ? 'var(--gradient-primary)' : 'transparent',
                textDecoration: 'none',
                boxShadow: isActive ? '0 4px 14px rgba(37, 99, 235, 0.25)' : 'none',
                position: 'relative',
                boxSizing: 'border-box',
              }}
            >
              <div className="nav-icon-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                {item.icon}
              </div>
              {!isCollapsed && (
                <span className="nav-label-text" style={{ fontSize: '0.92rem', fontWeight: isActive ? 700 : 500, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                  {item.label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Divider above bottom section */}
      <div style={{ margin: '14px 0 10px', height: '1px', background: 'var(--glass-border)' }} />

      {/* Bottom Section: User Info & Logout Button */}
      <div className="sidebar-bottom-section" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        
        {/* User Mini Card (shown when expanded) */}
        {!isCollapsed && user && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '8px 12px',
            borderRadius: '12px',
            background: 'var(--glass-bg)',
            border: '1px solid var(--glass-border)'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: 'var(--gradient-primary)',
              color: '#FFFFFF',
              fontWeight: 800,
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              {(user.username || user.first_name || 'U').charAt(0).toUpperCase()}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-color)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user.first_name ? `${user.first_name} ${user.last_name || ''}` : user.username}
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--subtext-color)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user.email || 'TalentIQ Member'}
              </span>
            </div>
          </div>
        )}

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="sidebar-logout-btn"
          title={isCollapsed ? "Logout" : undefined}
          aria-label="Logout"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'flex-start',
            gap: '12px',
            padding: isCollapsed ? '0' : '0 16px',
            height: '44px',
            borderRadius: '12px',
            color: 'var(--danger)',
            background: 'rgba(239, 68, 68, 0.06)',
            border: '1px solid rgba(239, 68, 68, 0.15)',
            width: '100%',
            cursor: 'pointer',
            transition: 'all var(--transition-fast)',
            boxSizing: 'border-box'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Hi2.HiOutlineArrowLeftOnRectangle size={20} />
          </div>
          {!isCollapsed && <span style={{ fontSize: '0.92rem', fontWeight: 700, whiteSpace: 'nowrap' }}>Logout</span>}
        </button>
      </div>

    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <motion.aside
        className="glass-panel hide-on-mobile"
        animate={isCollapsed ? 'collapsed' : 'expanded'}
        variants={sidebarVariants}
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
          bottom: '20px',
          zIndex: 1000,
          borderRadius: '24px',
          overflow: 'hidden',
          willChange: 'width',
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
              transition={{ type: 'spring', damping: 25, stiffness: 220 }}
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

      {/* Complete, Jiggle-Free Hover Styles */}
      <style>{`
        /* Regular nav link hover style: clean glass fill, NO translateX shifting */
        .sidebar-nav-link {
          transition: background var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast);
        }
        .sidebar-nav-link:hover {
          color: var(--primary) !important;
          background: rgba(37, 99, 235, 0.08) !important;
        }
        html.dark .sidebar-nav-link:hover {
          background: rgba(255, 255, 255, 0.08) !important;
        }
        .sidebar-nav-link.active:hover {
          color: #FFFFFF !important;
          background: var(--gradient-primary-hover) !important;
        }

        /* Toggle button hover */
        .sidebar-toggle-btn:hover {
          color: var(--primary) !important;
          border-color: var(--primary) !important;
          background: rgba(37, 99, 235, 0.1) !important;
        }

        /* Logout button hover style: dedicated red glow, NO blue override, NO translateX shift */
        .sidebar-logout-btn:hover {
          color: var(--danger) !important;
          background: rgba(239, 68, 68, 0.15) !important;
          border-color: rgba(239, 68, 68, 0.35) !important;
          box-shadow: 0 4px 14px rgba(239, 68, 68, 0.15);
        }

        /* Prevent scrollbar layout shifts (jiggle bug) */
        .sidebar-nav-container {
          scrollbar-width: thin;
          scrollbar-color: rgba(37, 99, 235, 0.2) transparent;
        }
        .sidebar-nav-container::-webkit-scrollbar {
          width: 5px;
        }
        .sidebar-nav-container::-webkit-scrollbar-track {
          background: transparent;
        }
        .sidebar-nav-container::-webkit-scrollbar-thumb {
          background: rgba(37, 99, 235, 0.2);
          border-radius: 6px;
        }
        .sidebar-nav-container::-webkit-scrollbar-thumb:hover {
          background: rgba(37, 99, 235, 0.4);
        }
      `}</style>
    </>
  );
};

export default GlassSidebar;

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ThemeSwitcher from './ThemeSwitcher';
import NotificationBell from './NotificationBell';
import {
  HiOutlineBars3,
  HiOutlineMagnifyingGlass,
  HiOutlineUserCircle,
  HiOutlineCog6Tooth,
  HiOutlineArrowLeftOnRectangle
} from 'react-icons/hi2';

const GlassNavbar = ({ setIsMobileOpen }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header
      className="glass-panel glass-topbar"
      style={{
        position: 'sticky',
        top: '12px',
        left: '12px',
        right: '12px',
        height: '60px',
        zIndex: 999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        borderRadius: '16px',
        marginBottom: '16px',
        backgroundColor: 'var(--glass-bg)',
        backdropFilter: 'blur(20px)',
        border: '1px solid var(--glass-border)',
      }}
    >
      {/* Left section: Hamburger (Mobile) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', minWidth: '120px' }}>
        <button
          className="hide-on-desktop"
          onClick={() => setIsMobileOpen(true)}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-color)',
            cursor: 'pointer',
            padding: '4px',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <HiOutlineBars3 size={24} />
        </button>

        {/* Brand name on mobile (since sidebar is hidden) */}
        <Link to="/dashboard" className="hide-on-desktop" style={{ fontSize: '1.15rem', fontWeight: 800, textDecoration: 'none', background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          ResumeAI
        </Link>
      </div>

      {/* Center section: Centered Search Bar */}
      <div className="hide-on-mobile" style={{ display: 'flex', justifyContent: 'center', flex: 1, padding: '0 24px' }}>
        <div style={{ position: 'relative', width: '100%', maxWidth: '520px' }}>
          <HiOutlineMagnifyingGlass
            size={18}
            style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--subtext-color)',
              pointerEvents: 'none',
            }}
          />
          <input
            type="text"
            placeholder="Search dashboard..."
            className="glass-input"
            style={{
              width: '100%',
              paddingLeft: '40px',
              height: '42px',
              fontSize: '0.9rem',
              borderRadius: '12px'
            }}
          />
        </div>
      </div>

      {/* Right section: Theme Toggle, Notifications, User Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', justifyContent: 'flex-end' }}>
        {/* Theme Switcher */}
        <ThemeSwitcher />

        {/* Notifications Bell */}
        <div className="glass-bell-wrapper">
          <NotificationBell />
        </div>

        {/* Profile Avatar Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '4px',
              borderRadius: '50%',
            }}
          >
            {user?.profile?.avatar ? (
              <img
                src={user.profile.avatar}
                alt="Profile"
                style={{ width: '34px', height: '34px', borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--primary)' }}
              />
            ) : (
              <div
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  background: 'var(--gradient-primary)',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                }}
              >
                {user?.first_name ? user.first_name[0].toUpperCase() : 'U'}
              </div>
            )}
          </button>

          {/* Profile Dropdown Menu */}
          {showProfileMenu && (
            <>
              {/* Overlay transparent to close on click outside */}
              <div
                onClick={() => setShowProfileMenu(false)}
                style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 998 }}
              />
              <div
                className="glass-panel"
                style={{
                  position: 'absolute',
                  right: 0,
                  top: '50px',
                  width: '220px',
                  padding: '8px',
                  zIndex: 999,
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--glass-border)',
                }}
              >
                <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--glass-border)', marginBottom: '6px' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-color)' }}>
                    {user?.first_name} {user?.last_name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--subtext-color)', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                    {user?.email}
                  </div>
                </div>

                <Link
                  to="/profile"
                  onClick={() => setShowProfileMenu(false)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 14px',
                    borderRadius: '12px',
                    textDecoration: 'none',
                    color: 'var(--text-color)',
                    fontSize: '0.875rem',
                    transition: 'background var(--transition-fast)'
                  }}
                  className="dropdown-menu-item"
                >
                  <HiOutlineUserCircle size={18} />
                  <span>My Profile</span>
                </Link>

                <Link
                  to="/profile/edit"
                  onClick={() => setShowProfileMenu(false)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 14px',
                    borderRadius: '12px',
                    textDecoration: 'none',
                    color: 'var(--text-color)',
                    fontSize: '0.875rem',
                    transition: 'background var(--transition-fast)'
                  }}
                  className="dropdown-menu-item"
                >
                  <HiOutlineCog6Tooth size={18} />
                  <span>Settings</span>
                </Link>

                <button
                  onClick={() => { setShowProfileMenu(false); handleLogout(); }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 14px',
                    borderRadius: '12px',
                    border: 'none',
                    background: 'none',
                    width: '100%',
                    textAlign: 'left',
                    color: 'var(--danger)',
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                    transition: 'background var(--transition-fast)'
                  }}
                  className="dropdown-menu-item"
                >
                  <HiOutlineArrowLeftOnRectangle size={18} />
                  <span>Logout</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      <style>{`
        .dropdown-menu-item:hover {
          background: rgba(37, 99, 235, 0.05);
        }
        html.dark .dropdown-menu-item:hover {
          background: rgba(255, 255, 255, 0.05);
        }
        /* Custom Bell container adjustment for glass style */
        .glass-bell-wrapper .bell-container {
          cursor: pointer;
          position: relative;
          width: 42px;
          height: 42px;
          border-radius: 50%;
          border: 1px solid var(--glass-border);
          background: var(--glass-bg);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all var(--transition-fast);
        }
        .glass-bell-wrapper .bell-container:hover {
          background: rgba(255, 255, 255, 0.25);
        }
        html.dark .glass-bell-wrapper .bell-container:hover {
          background: rgba(255, 255, 255, 0.10);
        }
        .glass-bell-wrapper .bell-badge {
          position: absolute;
          top: -2px;
          right: -2px;
          background: var(--danger);
          color: white;
          border-radius: 50%;
          padding: 2px 6px;
          font-size: 0.7rem;
          font-weight: bold;
        }

        /* Mobile topbar adjustments */
        @media (max-width: 768px) {
          .glass-topbar {
            height: 52px !important;
            padding: 0 12px !important;
            top: 8px !important;
            margin-bottom: 8px !important;
            border-radius: 14px !important;
          }
          .glass-bell-wrapper .bell-container {
            width: 34px;
            height: 34px;
          }
        }
      `}</style>
    </header>
  );
};

export default GlassNavbar;

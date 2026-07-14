import { Link } from 'react-router-dom';
import {
  HiOutlineBell,
  HiOutlineCheckCircle,
  HiOutlineExclamationTriangle,
  HiOutlineInformationCircle,
  HiXMark
} from 'react-icons/hi2';

const NotificationDrawer = ({ notifications, onMarkAllRead, onMarkRead, onClose }) => {
  const getIcon = (type, priority) => {
    if (priority === 'critical' || priority === 'high') {
      return <HiOutlineExclamationTriangle size={18} style={{ color: 'var(--danger)' }} />;
    }
    if (type?.includes('improved') || type?.includes('completed') || type?.includes('success')) {
      return <HiOutlineCheckCircle size={18} style={{ color: 'var(--success)' }} />;
    }
    return <HiOutlineInformationCircle size={18} style={{ color: 'var(--primary)' }} />;
  };

  return (
    <div
      className="glass-panel"
      style={{
        position: 'absolute',
        top: '56px',
        right: 0,
        width: '360px',
        maxHeight: '480px',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 1010,
        overflow: 'hidden',
        backgroundColor: 'var(--bg-primary)',
        border: '1px solid var(--glass-border)',
        boxShadow: '0 10px 40px var(--glass-shadow)',
        borderRadius: '20px',
      }}
      onMouseLeave={onClose}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 20px',
          borderBottom: '1px solid var(--glass-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: 'var(--text-color)', fontSize: '0.95rem' }}>
          <HiOutlineBell size={18} style={{ color: 'var(--primary)' }} />
          <span>Notifications</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {notifications.some((n) => !n.read) && (
            <button
              onClick={onMarkAllRead}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary)',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                padding: 0,
              }}
            >
              Mark all read
            </button>
          )}
        </div>
      </div>

      {/* List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }} className="custom-scroll">
        {notifications.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--subtext-color)', fontSize: '0.85rem' }}>
            No new notifications.
          </div>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {notifications.map((n) => (
              <li
                key={n.id}
                onClick={() => onMarkRead(n.id)}
                style={{
                  display: 'flex',
                  gap: '12px',
                  padding: '12px',
                  borderRadius: '12px',
                  cursor: 'pointer',
                  backgroundColor: n.read ? 'transparent' : 'rgba(37, 99, 235, 0.04)',
                  border: n.read ? '1px solid transparent' : '1px solid rgba(37, 99, 235, 0.1)',
                  transition: 'all var(--transition-fast)',
                }}
                className="drawer-item"
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', marginTop: '2px' }}>
                  {getIcon(n.type, n.priority)}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-color)', marginBottom: '2px', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                    {n.title}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--subtext-color)', lineHeight: 1.4, marginBottom: '4px' }}>
                    {n.message}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--subtext-color)' }}>
                    {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {!n.read && (
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--primary)',
                      marginTop: '6px'
                    }}
                  />
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div
        style={{
          padding: '12px',
          borderTop: '1px solid var(--glass-border)',
          textAlign: 'center',
          background: 'rgba(0, 0, 0, 0.02)',
        }}
      >
        <Link
          to="/notifications"
          onClick={onClose}
          style={{
            fontSize: '0.8rem',
            fontWeight: 600,
            color: 'var(--primary)',
            textDecoration: 'none',
          }}
        >
          View all notifications
        </Link>
      </div>

      <style>{`
        .drawer-item:hover {
          background-color: rgba(255, 255, 255, 0.08) !important;
        }
        html.dark .drawer-item:hover {
          background-color: rgba(255, 255, 255, 0.05) !important;
        }
      `}</style>
    </div>
  );
};

export default NotificationDrawer;

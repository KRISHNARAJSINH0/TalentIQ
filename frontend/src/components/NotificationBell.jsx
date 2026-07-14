import { useState, useEffect, useRef } from 'react';
import { HiOutlineBell } from 'react-icons/hi2';
import { notificationsAPI } from '../api/notifications';
import NotificationDrawer from './NotificationDrawer';
import '../styles/Notifications.css';

const NotificationBell = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showDrawer, setShowDrawer] = useState(false);
  const containerRef = useRef(null);

  const fetchStats = () => {
    notificationsAPI.getUnreadCount()
      .then(res => setUnreadCount(res.data.unread_count))
      .catch(() => {});

    notificationsAPI.getNotifications({ page_size: 5 })
      .then(res => setNotifications(res.data.results || res.data))
      .catch(() => {});
  };

  useEffect(() => {
    fetchStats();
    
    // Poll updates every 20 seconds
    const interval = setInterval(fetchStats, 20000);
    return () => clearInterval(interval);
  }, []);

  // Handle outside clicks to close drawer
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowDrawer(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const handleMarkAllRead = () => {
    notificationsAPI.markRead({ all: true })
      .then(() => {
        setUnreadCount(0);
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      })
      .catch(() => {});
  };

  const handleMarkRead = (id) => {
    notificationsAPI.markRead({ id })
      .then(() => {
        fetchStats();
      })
      .catch(() => {});
  };

  return (
    <div className="bell-container" ref={containerRef} onClick={() => setShowDrawer(!showDrawer)}>
      <HiOutlineBell size={22} style={{ color: 'var(--text-color)' }} />
      {unreadCount > 0 && (
        <span className="bell-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
      )}

      {showDrawer && (
        <div onClick={(e) => e.stopPropagation()}>
          <NotificationDrawer
            notifications={notifications}
            onMarkAllRead={handleMarkAllRead}
            onMarkRead={handleMarkRead}
            onClose={() => setShowDrawer(false)}
          />
        </div>
      )}
    </div>
  );
};

export default NotificationBell;

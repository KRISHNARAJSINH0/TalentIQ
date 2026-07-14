import { useState, useEffect } from 'react';
import { notificationsAPI } from '../api/notifications';
import {
  HiOutlineCheck,
  HiOutlineTrash,
  HiOutlineInbox,
  HiOutlineBell,
  HiOutlineClock,
  HiOutlineCheckCircle,
  HiOutlineExclamationTriangle,
  HiOutlineInformationCircle
} from 'react-icons/hi2';
import '../styles/Notifications.css';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [count, setCount] = useState(0);
  const [next, setNext] = useState(null);
  const [prev, setPrev] = useState(null);

  const fetchNotifications = (page = 1, filterVal = 'all', searchVal = '') => {
    setLoading(true);
    const params = { page };
    
    if (filterVal === 'unread') params.read = 'false';
    if (filterVal === 'read') params.read = 'true';
    if (filterVal !== 'all' && filterVal !== 'unread' && filterVal !== 'read') {
      params.type = filterVal;
    }
    
    // search is filtered client-side or we can search dynamically
    notificationsAPI.getNotifications(params)
      .then(res => {
        setNotifications(res.data.results || res.data);
        setCount(res.data.count || res.data.length);
        setNext(res.data.next);
        setPrev(res.data.previous);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to fetch your notifications.");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchNotifications(1, activeFilter, searchQuery);
  }, [activeFilter]);

  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
    setCurrentPage(1);
  };

  const handleMarkRead = (id) => {
    notificationsAPI.markRead({ id })
      .then(() => {
        setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      })
      .catch(() => {});
  };

  const handleMarkAllRead = () => {
    notificationsAPI.markRead({ all: true })
      .then(() => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      })
      .catch(() => {});
  };

  const handleDelete = (id, e) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    setNotifications(prev => prev.filter(n => n.id !== id));
    setCount(prev => Math.max(0, prev - 1));
    notificationsAPI.deleteNotification(id)
      .catch(err => {
        console.error("Failed to delete notification:", err);
        fetchNotifications(currentPage, activeFilter, searchQuery);
      });
  };

  const getIcon = (type, priority) => {
    if (priority === 'critical' || priority === 'high') {
      return <HiOutlineExclamationTriangle size={20} style={{ color: '#ef4444' }} />;
    }
    if (type.includes('improved') || type.includes('completed') || type.includes('success')) {
      return <HiOutlineCheckCircle size={20} style={{ color: '#10b981' }} />;
    }
    return <HiOutlineInformationCircle size={20} style={{ color: '#3b82f6' }} />;
  };

  // Group notifications helper (Today, Yesterday, Earlier)
  const getGroupHeader = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Today";
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    } else {
      return "Earlier";
    }
  };

  // Client-side search match
  const filteredNotifications = notifications.filter(n => {
    const q = searchQuery.toLowerCase();
    return n.title.toLowerCase().includes(q) || n.message.toLowerCase().includes(q);
  });

  // Grouping matches
  const groups = {};
  filteredNotifications.forEach(n => {
    const group = getGroupHeader(n.created_at);
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(n);
  });

  return (
    <div className="notif-page-container">
      <div className="notif-header-actions">
        <div>
          <h1 className="notif-title">Notification Center</h1>
          <p className="notif-subtitle">Stay up to date with resume parsed results, career score improvements, and security alerts.</p>
        </div>
        {notifications.some(n => !n.read) && (
          <button className="notif-mark-all-btn" onClick={handleMarkAllRead}>
            <HiOutlineCheck size={18} />
            <span>Mark all read</span>
          </button>
        )}
      </div>

      {/* Filter Tabs & Search Row */}
      <div className="notif-filter-card">
        <div className="notif-filter-group">
          <button
            className={`notif-filter-btn ${activeFilter === 'all' ? 'active' : ''}`}
            onClick={() => handleFilterChange('all')}
          >
            All
          </button>
          <button
            className={`notif-filter-btn ${activeFilter === 'unread' ? 'active' : ''}`}
            onClick={() => handleFilterChange('unread')}
          >
            Unread
          </button>
          <button
            className={`notif-filter-btn ${activeFilter === 'read' ? 'active' : ''}`}
            onClick={() => handleFilterChange('read')}
          >
            Read
          </button>
          <button
            className={`notif-filter-btn ${activeFilter === 'system_announcement' ? 'active' : ''}`}
            onClick={() => handleFilterChange('system_announcement')}
          >
            Announcements
          </button>
        </div>

        <input
          type="text"
          className="notif-search-input"
          placeholder="Search alerts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* List items rendering */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : error ? (
        <div className="glass-panel" style={{ padding: '16px', color: 'var(--danger)', borderRadius: '12px', border: '1px solid rgba(239,68,68,0.2)' }}>
          {error}
        </div>
      ) : filteredNotifications.length === 0 ? (
        <div className="notif-empty-card">
          <HiOutlineInbox size={48} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
          <p style={{ margin: 0, fontSize: '0.95rem' }}>No notifications to display.</p>
        </div>
      ) : (
        Object.keys(groups).map(groupName => (
          <div key={groupName}>
            <div className="notif-group-header">{groupName}</div>
            <div className="notif-list-container">
              {groups[groupName].map(n => (
                <div
                  key={n.id}
                  className={`notif-card ${!n.read ? 'unread' : ''}`}
                  onClick={() => !n.read && handleMarkRead(n.id)}
                  style={{ cursor: !n.read ? 'pointer' : 'default' }}
                >
                  {!n.read && <span className="notif-card-unread-dot" />}
                  <div className="notif-card-icon">
                    {getIcon(n.type, n.priority)}
                  </div>
                  <div className="notif-card-content">
                    <div className="notif-card-top">
                      <h4 className="notif-card-title">{n.title}</h4>
                      <span className={`notif-priority-badge notif-priority-${n.priority}`}>
                        {n.priority?.toUpperCase()}
                      </span>
                    </div>
                    <p className="notif-card-msg">{n.message}</p>
                    <div className="notif-card-meta">
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                        <HiOutlineClock size={14} />
                        {new Date(n.created_at).toLocaleString()}
                      </span>
                      {n.type_display && (
                        <span className="notif-type-tag">{n.type_display}</span>
                      )}
                      
                      <button
                        className="notif-delete-btn"
                        onClick={(e) => handleDelete(n.id, e)}
                        title="Delete notification"
                      >
                        <HiOutlineTrash size={14} /> Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}

      {/* Pagination controls */}
      {count > 10 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px', marginTop: '32px' }}>
          <button
            className="notif-filter-btn"
            disabled={!prev}
            onClick={() => {
              const prevPage = currentPage - 1;
              setCurrentPage(prevPage);
              fetchNotifications(prevPage, activeFilter, searchQuery);
            }}
            style={{ opacity: !prev ? 0.5 : 1, cursor: !prev ? 'not-allowed' : 'pointer' }}
          >
            Previous
          </button>
          <span style={{ fontSize: '0.85rem', color: 'var(--subtext-color)', fontWeight: 500 }}>
            Page {currentPage} of {Math.ceil(count / 10)}
          </span>
          <button
            className="notif-filter-btn"
            disabled={!next}
            onClick={() => {
              const nextPage = currentPage + 1;
              setCurrentPage(nextPage);
              fetchNotifications(nextPage, activeFilter, searchQuery);
            }}
            style={{ opacity: !next ? 0.5 : 1, cursor: !next ? 'not-allowed' : 'pointer' }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;

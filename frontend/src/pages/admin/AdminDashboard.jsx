import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';
import {
  HiOutlineUsers,
  HiOutlineDocumentText,
  HiOutlineGlobeAlt,
  HiOutlineCpuChip,
  HiOutlineCircleStack,
  HiOutlineCpuChip as HiOutlineCpu
} from 'react-icons/hi2';

const AdminDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    adminAPI.getDashboardSummary()
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch dashboard metrics.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  const { metrics, logs } = data;

  // Format bytes to MB
  const formatSize = (bytes) => {
    if (!bytes) return '0.00 MB';
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div>
      <div className="admin-header">
        <h1 className="admin-title">Overview</h1>
        <p className="admin-subtitle">Real-time statistics and summary logs across ResumeAI platforms.</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="admin-metrics-grid">
        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-card-title">Total Users</span>
            <HiOutlineUsers size={24} style={{ color: '#3b82f6' }} />
          </div>
          <span className="metric-card-value">{metrics.total_users}</span>
          <div className="metric-card-footer">
            <span>{metrics.active_users} Active accounts</span>
          </div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-card-title">Resumes</span>
            <HiOutlineDocumentText size={24} style={{ color: '#10b981' }} />
          </div>
          <span className="metric-card-value">{metrics.uploaded_resumes}</span>
          <div className="metric-card-footer">
            <span>Avg Completion {metrics.average_completion_percentage}%</span>
          </div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-card-title">Portfolios</span>
            <HiOutlineGlobeAlt size={24} style={{ color: '#8b5cf6' }} />
          </div>
          <span className="metric-card-value">{metrics.generated_portfolios}</span>
          <div className="metric-card-footer">
            <span>{metrics.generated_cover_letters} Cover Letters</span>
          </div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-card-title">Average ATS Score</span>
            <HiOutlineCpu size={24} style={{ color: '#f59e0b' }} />
          </div>
          <span className="metric-card-value">{metrics.average_ats_score}</span>
          <div className="metric-card-footer">
            <span>Avg Career Score: {metrics.average_career_score}</span>
          </div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-card-title">AI usage</span>
            <HiOutlineCpuChip size={24} style={{ color: '#3b82f6' }} />
          </div>
          <span className="metric-card-value">{metrics.ai_requests}</span>
          <div className="metric-card-footer">
            <span>Across {metrics.api_calls} total API Calls</span>
          </div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-card-title">Storage Space</span>
            <HiOutlineCircleStack size={24} style={{ color: '#ef4444' }} />
          </div>
          <span className="metric-card-value">{formatSize(metrics.storage_consumption)}</span>
          <div className="metric-card-footer">
            <span>Uploaded PDF/Word documents</span>
          </div>
        </div>
      </div>

      {/* Grid split for logs preview */}
      <div className="admin-grid-layout">
        {/* User Activity / API logs */}
        <div className="admin-panel">
          <h2 className="panel-title">Recent API & AI Usage Logs</h2>
          <div className="log-row-container">
            {logs.usage.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>No usage logs recorded yet.</p>
            ) : (
              logs.usage.map(log => {
                const isError = log.status_code >= 400;
                return (
                  <div key={log.id} className={`log-row ${isError ? 'error' : 'info'}`}>
                    <span>[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
                    <strong>{log.event_type.toUpperCase()}</strong> - {log.endpoint}{' '}
                    <span className={`badge ${isError ? 'badge-danger' : 'badge-success'}`}>
                      {log.status_code}
                    </span>{' '}
                    <span>({log.processing_time}s)</span> - {log.user}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Admin Audit Logs */}
        <div className="admin-panel">
          <h2 className="panel-title">Recent Admin Audit Trail</h2>
          <div className="log-row-container">
            {logs.audit.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>No admin actions recorded yet.</p>
            ) : (
              logs.audit.map(log => (
                <div key={log.id} className="log-row success" style={{ borderLeftColor: '#8b5cf6' }}>
                  <span>[{new Date(log.timestamp).toLocaleDateString()}]</span>{' '}
                  <strong>{log.action.toUpperCase()}</strong> - {log.description}{' '}
                  <span style={{ color: '#64748b' }}>by {log.admin}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

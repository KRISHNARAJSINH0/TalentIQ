import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';
import { HiOutlineArrowPath } from 'react-icons/hi2';

const AdminSystem = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    adminAPI.getSystemHealth()
      .then(res => {
        setHealth(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch system health status.");
        setLoading(false);
      });
  }, [refreshKey]);

  // Auto-refresh stats every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !health) {
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

  const formatStorage = (bytes) => {
    if (!bytes) return '0.00 GB';
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  const diskPercentage = health ? ((health.storage_used / health.storage_total) * 100).toFixed(1) : 0;

  return (
    <div>
      <div className="admin-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="admin-title">System Health</h1>
          <p className="admin-subtitle">Monitor hardware resource consumption, API services, and DB latency.</p>
        </div>
        <button className="admin-btn admin-btn-outline" onClick={() => setRefreshKey(prev => prev + 1)}>
          <HiOutlineArrowPath />
          <span>Refresh</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '24px' }}>
        {/* Resource Usage indicators */}
        <div className="admin-panel">
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '20px', color: '#0f172a' }}>Hardware Load</h3>
          
          {/* CPU Usage */}
          <div className="health-bar-container">
            <div className="health-label">
              <span>CPU Core Utilization</span>
              <span>{health.cpu_usage}%</span>
            </div>
            <div className="health-progress-bg">
              <div
                className={`health-progress-fill ${health.cpu_usage > 80 ? 'danger' : health.cpu_usage > 50 ? 'warning' : ''}`}
                style={{ width: `${health.cpu_usage}%` }}
              />
            </div>
          </div>

          {/* Memory Usage */}
          <div className="health-bar-container" style={{ marginTop: '24px' }}>
            <div className="health-label">
              <span>RAM Resource Utilization</span>
              <span>{health.memory_usage}%</span>
            </div>
            <div className="health-progress-bg">
              <div
                className={`health-progress-fill ${health.memory_usage > 85 ? 'danger' : health.memory_usage > 65 ? 'warning' : ''}`}
                style={{ width: `${health.memory_usage}%` }}
              />
            </div>
          </div>

          {/* Storage usage */}
          <div className="health-bar-container" style={{ marginTop: '24px' }}>
            <div className="health-label">
              <span>Disk Space Utilization (Media Folders)</span>
              <span>{diskPercentage}%</span>
            </div>
            <div className="health-progress-bg">
              <div
                className="health-progress-fill"
                style={{ width: `${diskPercentage}%` }}
              />
            </div>
            <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '6px', textAlign: 'right' }}>
              Used {formatStorage(health.storage_used)} of {formatStorage(health.storage_total)}
            </div>
          </div>
        </div>

        {/* Backend & services status panel */}
        <div className="admin-panel">
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '20px', color: '#0f172a' }}>Platform Engine Statuses</h3>
          
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {/* Database connectivity */}
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>
              <span style={{ fontWeight: '600', color: '#475569' }}>Django Postgres Database</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-success" style={{ background: health.database_status === 'healthy' ? '#d1fae5' : '#fee2e2', color: health.database_status === 'healthy' ? '#065f46' : '#991b1b' }}>
                  {health.database_status.toUpperCase()}
                </span>
                <span style={{ fontSize: '0.85rem', color: '#64748b' }}>({health.database_latency_ms}ms)</span>
              </div>
            </li>

            {/* AI Service connection */}
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>
              <span style={{ fontWeight: '600', color: '#475569' }}>Google Gemini AI API</span>
              <span className={`badge ${health.ai_service_status === 'healthy' ? 'badge-success' : 'badge-warning'}`}>
                {health.ai_service_status.toUpperCase()}
              </span>
            </li>

            {/* Background Workers status */}
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>
              <span style={{ fontWeight: '600', color: '#475569' }}>Background Queues (Celery/Thread)</span>
              <span className="badge badge-success">
                {health.queue_status.toUpperCase()}
              </span>
            </li>

            {/* Background job list */}
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
              <span style={{ fontWeight: '600', color: '#475569' }}>Active Background Job Processes</span>
              <span style={{ fontWeight: 'bold', color: '#0f172a' }}>{health.background_jobs_count} Jobs</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdminSystem;

import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';

const AdminLogs = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Log viewer filter states
  const [logType, setLogType] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    adminAPI.getDashboardSummary()
      .then(res => {
        setData(res.data.logs);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch system logs.");
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

  const handleLogTypeChange = (e) => setLogType(e.target.value);
  const handleSearchChange = (e) => setSearch(e.target.value);

  // Merge and sort logs by timestamp
  const usageLogs = data.usage.map(u => ({
    id: u.id,
    type: 'usage',
    title: u.event_type.toUpperCase(),
    details: `${u.endpoint} (${u.status_code}) - ${u.processing_time}s`,
    actor: u.user,
    timestamp: u.timestamp,
    status: u.status_code >= 400 ? 'error' : 'info'
  }));

  const auditLogs = data.audit.map(a => ({
    id: a.id,
    type: 'audit',
    title: a.action.toUpperCase(),
    details: `${a.description} (IP: ${a.ip_address || 'local'})`,
    actor: a.admin,
    timestamp: a.timestamp,
    status: 'success'
  }));

  let mergedLogs = [...usageLogs, ...auditLogs].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  // Apply filters
  if (logType === 'usage') {
    mergedLogs = mergedLogs.filter(l => l.type === 'usage');
  } else if (logType === 'audit') {
    mergedLogs = mergedLogs.filter(l => l.type === 'audit');
  }

  if (search) {
    const q = search.toLowerCase();
    mergedLogs = mergedLogs.filter(l => 
      l.title.toLowerCase().includes(q) || 
      l.details.toLowerCase().includes(q) || 
      l.actor.toLowerCase().includes(q)
    );
  }

  return (
    <div>
      <div className="admin-header">
        <h1 className="admin-title">Audit Trail</h1>
        <p className="admin-subtitle">Inspect historical admin activities, security audit lines, and API calls.</p>
      </div>

      <div className="admin-panel" style={{ marginBottom: '24px' }}>
        <div className="admin-controls">
          <input
            type="text"
            className="admin-input"
            placeholder="Search logs by actor, endpoint, or details..."
            value={search}
            onChange={handleSearchChange}
            style={{ minWidth: '320px' }}
          />

          <select className="admin-select" value={logType} onChange={handleLogTypeChange}>
            <option value="all">All Logs Types</option>
            <option value="audit">Admin Audits Only</option>
            <option value="usage">API & AI Usage Logs</option>
          </select>
        </div>

        {/* Logs list viewer */}
        <div className="log-row-container">
          {mergedLogs.length === 0 ? (
            <p style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No logs found matching search criteria.</p>
          ) : (
            mergedLogs.map(log => (
              <div key={log.id} className={`log-row ${log.status}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 'bold', color: '#0f172a' }}>
                    [{log.type.toUpperCase()}] {log.title}
                  </span>
                  <span style={{ color: '#64748b' }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>
                <div>{log.details}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '6px', textAlign: 'right' }}>
                  Actor: <strong>{log.actor}</strong>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminLogs;

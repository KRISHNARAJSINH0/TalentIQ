import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';
import { HiOutlineArrowDownTray } from 'react-icons/hi2';

const AdminReports = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exportType, setExportType] = useState('users');
  const [exporting, setExporting] = useState(false);

  // Tab state
  const [activeTab, setActiveTab] = useState('resumes');

  useEffect(() => {
    adminAPI.getReports()
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch reports tables data.");
        setLoading(false);
      });
  }, []);

  const handleExportCSV = () => {
    setExporting(true);
    adminAPI.exportReport(exportType)
      .then(res => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${exportType}_report_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        setExporting(false);
      })
      .catch(() => {
        alert("Failed to export report CSV.");
        setExporting(false);
      });
  };

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

  const { resumes, portfolios, ats } = data;

  const formatSize = (bytes) => {
    if (!bytes) return '0.00 MB';
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div>
      <div className="admin-header">
        <h1 className="admin-title">Reports</h1>
        <p className="admin-subtitle">Compile and download tabular CSV statistics for audit or presentation.</p>
      </div>

      {/* Exporter control panel */}
      <div className="admin-panel" style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', color: '#0f172a' }}>Export System Reports</h3>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: '600', color: '#475569', marginBottom: '6px' }}>Select Dataset</label>
            <select className="admin-select" value={exportType} onChange={(e) => setExportType(e.target.value)} style={{ minWidth: '220px' }}>
              <option value="users">Registered Users List</option>
              <option value="resumes">Resumes Database Log</option>
              <option value="ats">ATS Evaluations Log</option>
              <option value="usage">System API Usage Logs</option>
            </select>
          </div>

          <button
            className="admin-btn admin-btn-primary"
            onClick={handleExportCSV}
            disabled={exporting}
            style={{ marginTop: '22px' }}
          >
            <HiOutlineArrowDownTray />
            <span>{exporting ? 'Generating...' : 'Download CSV Report'}</span>
          </button>
        </div>
      </div>

      {/* Tabs list preview */}
      <div className="admin-panel">
        <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0', marginBottom: '20px', gap: '16px' }}>
          <button
            className={`admin-btn ${activeTab === 'resumes' ? 'admin-btn-primary' : 'admin-btn-outline'}`}
            onClick={() => setActiveTab('resumes')}
            style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0, padding: '10px 20px' }}
          >
            Uploaded Resumes ({resumes.length})
          </button>
          <button
            className={`admin-btn ${activeTab === 'portfolios' ? 'admin-btn-primary' : 'admin-btn-outline'}`}
            onClick={() => setActiveTab('portfolios')}
            style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0, padding: '10px 20px' }}
          >
            Generated Portfolios ({portfolios.length})
          </button>
          <button
            className={`admin-btn ${activeTab === 'ats' ? 'admin-btn-primary' : 'admin-btn-outline'}`}
            onClick={() => setActiveTab('ats')}
            style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0, padding: '10px 20px' }}
          >
            ATS Evaluations ({ats.length})
          </button>
        </div>

        {/* Tab content rendering */}
        {activeTab === 'resumes' && (
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Resume Title</th>
                  <th>User Account</th>
                  <th>Size</th>
                  <th>Parsing Status</th>
                  <th>Upload Date</th>
                </tr>
              </thead>
              <tbody>
                {resumes.map(r => (
                  <tr key={r.id}>
                    <td><strong>{r.title}</strong></td>
                    <td>{r.email}</td>
                    <td>{formatSize(r.size)}</td>
                    <td>
                      <span className={`badge ${r.status === 'completed' ? 'badge-success' : r.status === 'failed' ? 'badge-danger' : 'badge-warning'}`}>
                        {r.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{new Date(r.date).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'portfolios' && (
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>User Portfolio URL</th>
                  <th>User Account</th>
                  <th>Selected Theme</th>
                  <th>Views</th>
                  <th>Downloads</th>
                  <th>Shares</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {portfolios.map(p => (
                  <tr key={p.id}>
                    <td>
                      <a href={`/u/${p.slug}`} target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 'bold' }}>
                        /u/{p.slug}
                      </a>
                    </td>
                    <td>{p.email}</td>
                    <td>
                      <span className="badge badge-primary">{p.theme.toUpperCase()}</span>
                    </td>
                    <td>{p.views}</td>
                    <td>{p.downloads}</td>
                    <td>{p.shares}</td>
                    <td>{new Date(p.date).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'ats' && (
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>User Account</th>
                  <th>Resume Name</th>
                  <th>Score</th>
                  <th>Processing Time</th>
                  <th>Evaluation Date</th>
                </tr>
              </thead>
              <tbody>
                {ats.map(a => (
                  <tr key={a.id}>
                    <td>{a.email}</td>
                    <td><strong>{a.title}</strong></td>
                    <td>
                      <span className={`badge ${a.score >= 80 ? 'badge-success' : a.score >= 50 ? 'badge-warning' : 'badge-danger'}`} style={{ fontSize: '0.85rem' }}>
                        {a.score} / 100
                      </span>
                    </td>
                    <td>{a.duration}s</td>
                    <td>{new Date(a.date).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminReports;

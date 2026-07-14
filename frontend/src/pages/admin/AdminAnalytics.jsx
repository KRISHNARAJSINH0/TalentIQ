import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';

const AdminAnalytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    adminAPI.getAnalytics()
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch analytics statistics.");
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

  const { growth, ats_distribution, insights } = data;

  // Helpers to calculate heights for custom SVG bar charts
  const maxGrowthCount = Math.max(...growth.map(d => d.new_users), 1);
  const maxAtsCount = Math.max(...ats_distribution.map(d => d.count), 1);

  return (
    <div>
      <div className="admin-header">
        <h1 className="admin-title">Analytics</h1>
        <p className="admin-subtitle">Deep dive into user trends, resume metrics, and market intelligence.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        {/* User Growth SVG Chart */}
        <div className="chart-box">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: '#0f172a', fontWeight: '700' }}>User Registrations Trend (Last 12 Months)</h3>
          <div style={{ position: 'relative', height: '240px', background: '#f8fafc', borderRadius: '8px', padding: '20px' }}>
            {growth.length === 0 ? (
              <p style={{ color: '#64748b', textAlign: 'center', marginTop: '80px' }}>No registrations recorded yet.</p>
            ) : (
              <div style={{ display: 'flex', height: '180px', alignItems: 'flex-end', justifyContent: 'space-around' }}>
                {growth.map(g => {
                  const percentage = (g.new_users / maxGrowthCount) * 100;
                  return (
                    <div key={g.date} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                      <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '4px' }}>
                        {g.new_users}
                      </div>
                      <div
                        style={{
                          height: `${Math.max(percentage, 5)}%`,
                          width: '24px',
                          background: 'linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%)',
                          borderRadius: '4px 4px 0 0',
                          transition: 'height 0.4s ease'
                        }}
                        title={`New registrations: ${g.new_users}`}
                      />
                      <div style={{ color: '#64748b', fontSize: '0.7rem', marginTop: '8px', transform: 'rotate(-25deg)', whiteSpace: 'nowrap' }}>
                        {g.date}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* ATS Score Distribution Chart */}
        <div className="chart-box">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: '#0f172a', fontWeight: '700' }}>ATS Score Distributions</h3>
          <div style={{ position: 'relative', height: '240px', background: '#f8fafc', borderRadius: '8px', padding: '20px' }}>
            <div style={{ display: 'flex', height: '180px', alignItems: 'flex-end', justifyContent: 'space-around' }}>
              {ats_distribution.map(d => {
                const percentage = (d.count / maxAtsCount) * 100;
                return (
                  <div key={d.range} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                    <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '4px' }}>
                      {d.count}
                    </div>
                    <div
                      style={{
                        height: `${Math.max(percentage, 5)}%`,
                        width: '36px',
                        background: 'linear-gradient(180deg, #10b981 0%, #047857 100%)',
                        borderRadius: '4px 4px 0 0',
                        transition: 'height 0.4s ease'
                      }}
                      title={`${d.count} resumes scored in range ${d.range}`}
                    />
                    <div style={{ color: '#475569', fontSize: '0.8rem', fontWeight: '600', marginTop: '8px' }}>
                      {d.range}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Industry Insights Cards */}
      <h2 style={{ fontSize: '1.4rem', fontWeight: '700', color: '#0f172a', margin: '32px 0 16px' }}>Resume AI Market Insights</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Popular Roles */}
        <div className="admin-panel">
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '14px', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px' }}>
            Trending Designations
          </h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {insights.roles.map((item, idx) => (
              <li key={item.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.9rem', color: '#475569' }}>
                  <strong style={{ color: '#0f172a', marginRight: '6px' }}>#{idx+1}</strong> {item.name}
                </span>
                <span className="badge badge-primary">{item.count} Resumes</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Popular Skills */}
        <div className="admin-panel">
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '14px', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px' }}>
            Most Popular Skills
          </h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {insights.skills.map((item, idx) => (
              <li key={item.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.9rem', color: '#475569' }}>
                  <strong style={{ color: '#0f172a', marginRight: '6px' }}>#{idx+1}</strong> {item.name}
                </span>
                <span className="badge badge-success">{item.count} times</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Popular Technologies */}
        <div className="admin-panel">
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '14px', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px' }}>
            Most Used Technologies
          </h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {insights.technologies.map((item, idx) => (
              <li key={item.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.9rem', color: '#475569' }}>
                  <strong style={{ color: '#0f172a', marginRight: '6px' }}>#{idx+1}</strong> {item.name}
                </span>
                <span className="badge badge-purple">{item.count} items</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalytics;

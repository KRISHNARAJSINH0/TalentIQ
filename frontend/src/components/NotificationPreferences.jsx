import { useState, useEffect } from 'react';
import { notificationsAPI } from '../api/notifications';
import '../styles/Notifications.css';

const NotificationPreferences = () => {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    notificationsAPI.getPreferences()
      .then(res => {
        setPreferences(res.data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load your notification preferences.");
        setLoading(false);
      });
  }, []);

  const handleToggle = (key) => {
    const updated = { ...preferences, [key]: !preferences[key] };
    setPreferences(updated);
    setSaving(true);
    setSuccess(false);

    notificationsAPI.updatePreferences({ [key]: updated[key] })
      .then(() => {
        setSaving(false);
        setSuccess(true);
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(false), 3000);
      })
      .catch(() => {
        setSaving(false);
        setError("Failed to save changes.");
      });
  };

  if (loading) {
    return <div className="text-center py-4">Loading preferences...</div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="card shadow-sm p-4">
      <h3 className="h5 font-weight-bold mb-3">Notification Settings</h3>
      <p className="text-muted small mb-4">Choose what alerts you would like to receive and which delivery channels you prefer.</p>

      {success && <div className="alert alert-success py-2 small">Settings saved successfully.</div>}

      <div className="pref-list">
        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">Email Notifications</div>
            <div className="pref-desc">Receive summaries, digests, and recommendations straight to your inbox.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_email}
              onChange={() => handleToggle('enable_email')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>

        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">ATS Alert Updates</div>
            <div className="pref-desc">Get alerted when your ATS score improves or decreases on resume uploads.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_ats_alerts}
              onChange={() => handleToggle('enable_ats_alerts')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>

        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">Career AI Suggestions</div>
            <div className="pref-desc">Receive notifications about skill recommendations and job suggestions.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_career_alerts}
              onChange={() => handleToggle('enable_career_alerts')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>

        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">Portfolio Views</div>
            <div className="pref-desc">Get notified when recruiters view or download your portfolio pages.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_portfolio_alerts}
              onChange={() => handleToggle('enable_portfolio_alerts')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>

        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">Weekly Digest Reports</div>
            <div className="pref-desc">Weekly compilation of resume checks, progress metrics, and highlights.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_weekly_reports}
              onChange={() => handleToggle('enable_weekly_reports')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>

        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">Monthly Growth Reviews</div>
            <div className="pref-desc">Deep-dive summary of skill strength and monthly roadmap milestones.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_monthly_reports}
              onChange={() => handleToggle('enable_monthly_reports')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>

        <div className="pref-row">
          <div className="pref-info">
            <div className="pref-title">Security & Account Alerts</div>
            <div className="pref-desc">Important verification codes, login alerts, and privacy updates.</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.enable_security_notifications}
              onChange={() => handleToggle('enable_security_notifications')}
              disabled={saving}
            />
            <span className="slider"></span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default NotificationPreferences;

/**
 * EditProfile Page – Update user and profile information.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import authService from '../services/authService';
import NotificationPreferences from '../components/NotificationPreferences';
import '../styles/Profile.css';

const Field = ({ label, name, type = 'text', placeholder = '', formData, errors, handleChange }) => (
  <div className="edit-field">
    <label className="edit-label">{label}</label>
    <input
      className={`edit-input ${errors[name] ? 'edit-input-error' : ''}`}
      name={name} type={type} placeholder={placeholder}
      value={formData[name] || ''} onChange={handleChange}
    />
    {errors[name] && <span className="edit-field-error">{errors[name]}</span>}
  </div>
);

const EditProfile = () => {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();
  const profile = user?.profile || {};

  const [formData, setFormData] = useState({
    first_name: '', last_name: '', phone: '',
    headline: '', summary: '',
    address: '', city: '', state: '', country: '', postal_code: '',
    website: '', github: '', linkedin: '', portfolio_url: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  // Password change
  const [pwData, setPwData] = useState({
    current_password: '', new_password: '', confirm_password: '',
  });
  const [pwErrors, setPwErrors] = useState({});
  const [pwLoading, setPwLoading] = useState(false);
  const [pwSuccess, setPwSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        headline: profile.headline || '',
        summary: profile.summary || '',
        address: profile.address || '',
        city: profile.city || '',
        state: profile.state || '',
        country: profile.country || '',
        postal_code: profile.postal_code || '',
        website: profile.website || '',
        github: profile.github || '',
        linkedin: profile.linkedin || '',
        portfolio_url: profile.portfolio_url || '',
      });
    }
  }, [user, profile]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);
    setSuccess('');

    try {
      await authService.updateProfile(formData);
      await updateUser();
      setSuccess('Profile updated successfully!');
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object') {
        const fe = {};
        for (const [k, v] of Object.entries(data)) fe[k] = Array.isArray(v) ? v[0] : v;
        setErrors(fe);
      } else {
        setErrors({ general: 'Update failed.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePwChange = (e) => {
    setPwData({ ...pwData, [e.target.name]: e.target.value });
    setPwSuccess('');
  };

  const handlePwSubmit = async (e) => {
    e.preventDefault();
    setPwErrors({});
    setPwLoading(true);
    setPwSuccess('');

    try {
      await authService.changePassword(pwData);
      setPwSuccess('Password changed successfully!');
      setPwData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object') {
        const fe = {};
        for (const [k, v] of Object.entries(data)) fe[k] = Array.isArray(v) ? v[0] : v;
        setPwErrors(fe);
      } else {
        setPwErrors({ general: 'Password change failed.' });
      }
    } finally {
      setPwLoading(false);
    }
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="edit-header">
            <h1 className="edit-title">Edit Profile</h1>
            <button onClick={() => navigate('/profile')} className="btn btn-outline-dark btn-sm">
              Cancel
            </button>
          </div>

          {success && <div className="edit-success">{success}</div>}
          {errors.general && <div className="auth-error">{errors.general}</div>}

          <form onSubmit={handleSubmit}>
            {/* Personal */}
            <div className="edit-section">
              <h3 className="edit-section-title">Personal Information</h3>
              <div className="edit-row">
                <Field label="First Name" name="first_name" formData={formData} errors={errors} handleChange={handleChange} />
                <Field label="Last Name" name="last_name" formData={formData} errors={errors} handleChange={handleChange} />
              </div>
              <Field label="Phone" name="phone" placeholder="+1234567890" formData={formData} errors={errors} handleChange={handleChange} />
              <Field label="Headline" name="headline" placeholder="Full Stack Developer | React & Django" formData={formData} errors={errors} handleChange={handleChange} />
              <div className="edit-field">
                <label className="edit-label">Summary</label>
                <textarea
                  className="edit-input edit-textarea" name="summary"
                  placeholder="Brief professional summary..."
                  value={formData.summary} onChange={handleChange} rows={4}
                />
              </div>
            </div>

            {/* Location */}
            <div className="edit-section">
              <h3 className="edit-section-title">Location</h3>
              <Field label="Address" name="address" formData={formData} errors={errors} handleChange={handleChange} />
              <div className="edit-row">
                <Field label="City" name="city" formData={formData} errors={errors} handleChange={handleChange} />
                <Field label="State" name="state" formData={formData} errors={errors} handleChange={handleChange} />
              </div>
              <div className="edit-row">
                <Field label="Country" name="country" formData={formData} errors={errors} handleChange={handleChange} />
                <Field label="Postal Code" name="postal_code" formData={formData} errors={errors} handleChange={handleChange} />
              </div>
            </div>

            {/* Links */}
            <div className="edit-section">
              <h3 className="edit-section-title">Social & Links</h3>
              <Field label="Website" name="website" type="url" placeholder="https://example.com" formData={formData} errors={errors} handleChange={handleChange} />
              <Field label="GitHub" name="github" type="url" placeholder="https://github.com/username" formData={formData} errors={errors} handleChange={handleChange} />
              <Field label="LinkedIn" name="linkedin" type="url" placeholder="https://linkedin.com/in/username" formData={formData} errors={errors} handleChange={handleChange} />
              <Field label="Portfolio URL" name="portfolio_url" type="url" placeholder="https://portfolio.dev" formData={formData} errors={errors} handleChange={handleChange} />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
              {loading ? <span className="spinner-border spinner-border-sm" /> : 'Save Changes'}
            </button>
          </form>

          {/* Password Change */}
          <div className="edit-section" style={{ marginTop: 48 }}>
            <h3 className="edit-section-title">Change Password</h3>
            {pwSuccess && <div className="edit-success">{pwSuccess}</div>}
            {pwErrors.general && <div className="auth-error">{pwErrors.general}</div>}
            <form onSubmit={handlePwSubmit}>
              <div className="edit-field">
                <label className="edit-label">Current Password</label>
                <input className={`edit-input ${pwErrors.current_password ? 'edit-input-error' : ''}`}
                  name="current_password" type="password" value={pwData.current_password} onChange={handlePwChange} required />
                {pwErrors.current_password && <span className="edit-field-error">{pwErrors.current_password}</span>}
              </div>
              <div className="edit-row">
                <div className="edit-field">
                  <label className="edit-label">New Password</label>
                  <input className={`edit-input ${pwErrors.new_password ? 'edit-input-error' : ''}`}
                    name="new_password" type="password" value={pwData.new_password} onChange={handlePwChange} required />
                  {pwErrors.new_password && <span className="edit-field-error">{pwErrors.new_password}</span>}
                </div>
                <div className="edit-field">
                  <label className="edit-label">Confirm Password</label>
                  <input className={`edit-input ${pwErrors.confirm_password ? 'edit-input-error' : ''}`}
                    name="confirm_password" type="password" value={pwData.confirm_password} onChange={handlePwChange} required />
                  {pwErrors.confirm_password && <span className="edit-field-error">{pwErrors.confirm_password}</span>}
                </div>
              </div>
              <button type="submit" className="btn btn-outline-dark" disabled={pwLoading} style={{ width: '100%' }}>
                {pwLoading ? <span className="spinner-border spinner-border-sm" /> : 'Change Password'}
              </button>
            </form>
          </div>

          <div style={{ marginTop: 48 }}>
            <NotificationPreferences />
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default EditProfile;

/**
 * Register Page – Real registration form.
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Auth.css';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    confirm_password: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    try {
      await register(formData);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object' && data !== null) {
        const fieldErrors = {};
        for (const [key, val] of Object.entries(data)) {
          fieldErrors[key] = Array.isArray(val) ? val[0] : val;
        }
        setErrors(fieldErrors);
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="hero-orb hero-orb-1"></div>
      <div className="hero-orb hero-orb-2"></div>

      <motion.div
        className="auth-card"
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <h1 className="auth-card-title">Create Account</h1>
        <p className="auth-card-subtitle">Start building your career with AI</p>

        {errors.general && (
          <div className="auth-error">{errors.general}</div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-row">
            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-first-name">First Name</label>
              <input
                id="reg-first-name" className={`auth-input ${errors.first_name ? 'auth-input-error' : ''}`}
                name="first_name" type="text" placeholder="John"
                value={formData.first_name} onChange={handleChange} required
              />
              {errors.first_name && <span className="auth-field-error">{errors.first_name}</span>}
            </div>
            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-last-name">Last Name</label>
              <input
                id="reg-last-name" className={`auth-input ${errors.last_name ? 'auth-input-error' : ''}`}
                name="last_name" type="text" placeholder="Doe"
                value={formData.last_name} onChange={handleChange} required
              />
              {errors.last_name && <span className="auth-field-error">{errors.last_name}</span>}
            </div>
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-username">Username</label>
            <input
              id="reg-username" className={`auth-input ${errors.username ? 'auth-input-error' : ''}`}
              name="username" type="text" placeholder="johndoe"
              value={formData.username} onChange={handleChange} autoComplete="username" required
            />
            {errors.username && <span className="auth-field-error">{errors.username}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-email">Email Address</label>
            <input
              id="reg-email" className={`auth-input ${errors.email ? 'auth-input-error' : ''}`}
              name="email" type="email" placeholder="you@example.com"
              value={formData.email} onChange={handleChange} autoComplete="email" required
            />
            {errors.email && <span className="auth-field-error">{errors.email}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-password">Password</label>
            <input
              id="reg-password" className={`auth-input ${errors.password ? 'auth-input-error' : ''}`}
              name="password" type="password" placeholder="••••••••"
              value={formData.password} onChange={handleChange} autoComplete="new-password" required
            />
            {errors.password && <span className="auth-field-error">{errors.password}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-confirm">Confirm Password</label>
            <input
              id="reg-confirm" className={`auth-input ${errors.confirm_password ? 'auth-input-error' : ''}`}
              name="confirm_password" type="password" placeholder="••••••••"
              value={formData.confirm_password} onChange={handleChange} autoComplete="new-password" required
            />
            {errors.confirm_password && <span className="auth-field-error">{errors.confirm_password}</span>}
          </div>

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? (
              <span className="spinner-border spinner-border-sm" role="status" />
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?
          <Link to="/login">Sign In</Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Register;

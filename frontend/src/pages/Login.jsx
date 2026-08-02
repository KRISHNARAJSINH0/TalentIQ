/**
 * Login Page – Real authentication form.
 */

import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Auth.css';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/dashboard';

  const [formData, setFormData] = useState({
    login: '',
    password: '',
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
      await login(formData);
      navigate(from, { replace: true });
    } catch (err) {
      const data = err.response?.data;
      if (data?.non_field_errors) {
        setErrors({ general: data.non_field_errors[0] });
      } else if (typeof data === 'object' && data !== null) {
        const fieldErrors = {};
        for (const [key, val] of Object.entries(data)) {
          fieldErrors[key] = Array.isArray(val) ? val[0] : val;
        }
        setErrors(fieldErrors);
      } else {
        setErrors({ general: 'Login failed. Please try again.' });
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
        <h1 className="auth-card-title">Welcome Back</h1>
        <p className="auth-card-subtitle">Sign in to your TalentIQ account</p>

        {errors.general && (
          <div className="auth-error">{errors.general}</div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-field">
              Email or Username
            </label>
            <input
              id="login-field"
              className={`auth-input ${errors.login ? 'auth-input-error' : ''}`}
              name="login"
              type="text"
              placeholder="you@example.com"
              value={formData.login}
              onChange={handleChange}
              autoComplete="username"
              required
            />
            {errors.login && <span className="auth-field-error">{errors.login}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="login-password">
              Password
            </label>
            <input
              id="login-password"
              className={`auth-input ${errors.password ? 'auth-input-error' : ''}`}
              name="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              autoComplete="current-password"
              required
            />
            {errors.password && <span className="auth-field-error">{errors.password}</span>}
          </div>

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? (
              <span className="spinner-border spinner-border-sm" role="status" />
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <p className="auth-footer">
          Don&apos;t have an account?
          <Link to="/register">Sign Up</Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Login;

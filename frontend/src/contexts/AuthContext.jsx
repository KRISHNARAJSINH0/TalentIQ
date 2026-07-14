/**
 * AuthContext – Global authentication state management.
 *
 * Stores user, tokens, and auth status.
 * Persists login across page refresh via localStorage.
 * Provides login, register, logout, and updateUser functions.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [loading, setLoading] = useState(true);

  // ── Restore session from localStorage on mount ──
  useEffect(() => {
    const savedTokens = JSON.parse(localStorage.getItem('tokens') || 'null');
    const savedUser = JSON.parse(localStorage.getItem('user') || 'null');

    if (savedTokens && savedUser) {
      setTokens(savedTokens);
      setUser(savedUser);
      // Verify token is still valid by fetching fresh user data
      authService
        .getCurrentUser()
        .then((res) => {
          setUser(res.data);
          localStorage.setItem('user', JSON.stringify(res.data));
        })
        .catch(() => {
          // Token expired and refresh also failed
          localStorage.removeItem('tokens');
          localStorage.removeItem('user');
          setTokens(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // ── Persist to localStorage whenever tokens/user change ──
  const saveSession = useCallback((userData, tokenData) => {
    setUser(userData);
    setTokens(tokenData);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('tokens', JSON.stringify(tokenData));
  }, []);

  // ── Register ──
  const register = useCallback(async (formData) => {
    const { data } = await authService.register(formData);
    saveSession(data.user, data.tokens);
    return data;
  }, [saveSession]);

  // ── Login ──
  const login = useCallback(async (formData) => {
    const { data } = await authService.login(formData);
    saveSession(data.user, data.tokens);
    return data;
  }, [saveSession]);

  // ── Logout ──
  const logout = useCallback(async () => {
    try {
      const savedTokens = JSON.parse(localStorage.getItem('tokens') || 'null');
      if (savedTokens?.refresh) {
        await authService.logout(savedTokens.refresh);
      }
    } catch {
      // Ignore logout API errors – clear local state regardless
    } finally {
      setUser(null);
      setTokens(null);
      localStorage.removeItem('user');
      localStorage.removeItem('tokens');
    }
  }, []);

  // ── Update user data (after profile edit) ──
  const updateUser = useCallback(async () => {
    try {
      const { data } = await authService.getCurrentUser();
      setUser(data);
      localStorage.setItem('user', JSON.stringify(data));
      return data;
    } catch (error) {
      throw error;
    }
  }, []);

  const isAuthenticated = !!tokens && !!user;

  const value = {
    user,
    tokens,
    loading,
    isAuthenticated,
    register,
    login,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

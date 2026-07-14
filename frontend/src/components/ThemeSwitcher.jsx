import { useState, useEffect } from 'react';
import { HiOutlineSun, HiOutlineMoon } from 'react-icons/hi2';

const ThemeSwitcher = () => {
  const [isDark, setIsDark] = useState(() => {
    // Check local storage or system preferences
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="glass-btn-secondary"
      style={{
        padding: '10px',
        borderRadius: '50%',
        width: '42px',
        height: '42px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid var(--glass-border)',
        fontSize: '1.25rem',
      }}
      aria-label="Toggle dark mode"
    >
      {isDark ? <HiOutlineSun style={{ color: '#F59E0B' }} /> : <HiOutlineMoon style={{ color: '#7C3AED' }} />}
    </button>
  );
};

export default ThemeSwitcher;

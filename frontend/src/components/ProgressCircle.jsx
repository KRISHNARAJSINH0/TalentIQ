import { motion } from 'framer-motion';

const ProgressCircle = ({ percent = 0, size = 140, strokeWidth = 12, title = '' }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  
  // Ensure percent is between 0 and 100
  const cleanPercent = Math.max(0, Math.min(100, percent));
  const strokeDashoffset = circumference - (cleanPercent / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="var(--glass-border)"
            strokeWidth={strokeWidth}
          />
          {/* Active Gradient stroke */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="url(#progress-gradient)"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            strokeLinecap="round"
          />
          {/* Gradient Definitions */}
          <defs>
            <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#2563EB" />
              <stop offset="100%" stopColor="#7C3AED" />
            </linearGradient>
          </defs>
        </svg>

        {/* Text inside the circle */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{
            fontSize: `${size * 0.22}px`,
            fontWeight: 700,
            fontFamily: 'var(--font-number)',
            color: 'var(--text-color)',
            lineHeight: 1
          }}>
            {cleanPercent}%
          </span>
          {title && (
            <span style={{
              fontSize: `${size * 0.10}px`,
              fontWeight: 600,
              color: 'var(--subtext-color)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginTop: `${size * 0.04}px`
            }}>
              {title}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressCircle;

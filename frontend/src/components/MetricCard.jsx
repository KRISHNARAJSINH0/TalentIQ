import { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

const MetricCard = ({ title, value, prefix = '', suffix = '', icon, trend, trendType = 'success', delay = 0 }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    // If value is not a number, just set it directly
    const numValue = Number(value);
    if (isNaN(numValue)) {
      setDisplayValue(value);
      return;
    }

    let start = 0;
    const end = numValue;
    if (start === end) {
      setDisplayValue(end);
      return;
    }

    const duration = 1200; // CountUp duration in ms
    const range = end - start;
    let current = start;
    const increment = end > start ? Math.ceil(range / 60) : Math.floor(range / 60);
    const stepTime = 16; // ~60fps

    const timer = setInterval(() => {
      current += increment;
      if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
        clearInterval(timer);
        setDisplayValue(end);
      } else {
        setDisplayValue(Math.round(current));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [value]);

  const getTrendColor = () => {
    if (trendType === 'success') return 'var(--success)';
    if (trendType === 'danger') return 'var(--danger)';
    return 'var(--warning)';
  };

  return (
    <GlassCard delay={delay} style={{ display: 'flex', flexDirection: 'column', height: '140px', padding: '16px', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--subtext-color)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {title}
        </span>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'rgba(37, 99, 235, 0.08)',
          color: 'var(--primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          {icon}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: 'auto' }}>
        <span style={{
          fontSize: 'var(--fs-metric)',
          fontWeight: 700,
          fontFamily: 'var(--font-number)',
          color: 'var(--text-color)',
          lineHeight: 1
        }}>
          {prefix}{typeof displayValue === 'number' ? displayValue.toLocaleString() : displayValue}{typeof displayValue === 'number' ? suffix : ''}
        </span>
        
        {trend && (
          <div style={{ display: 'flex' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: 600,
              color: getTrendColor(),
              background: `${getTrendColor()}12`,
              padding: '2px 8px',
              borderRadius: '6px',
              whiteSpace: 'nowrap'
            }}>
              {trend}
            </span>
          </div>
        )}
      </div>
    </GlassCard>
  );
};

export default MetricCard;

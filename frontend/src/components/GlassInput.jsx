const GlassInput = ({ label, icon, error, style = {}, ...props }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%', ...style }}>
      {label && (
        <label style={{
          fontSize: '0.85rem',
          fontWeight: 600,
          color: 'var(--text-color)',
          fontFamily: 'var(--font-heading)'
        }}>
          {label}
        </label>
      )}
      <div style={{ position: 'relative', width: '100%' }}>
        {icon && (
          <div style={{
            position: 'absolute',
            left: '14px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'var(--subtext-color)',
            display: 'flex',
            alignItems: 'center',
            pointerEvents: 'none'
          }}>
            {icon}
          </div>
        )}
        <input
          className="glass-input"
          style={{
            width: '100%',
            paddingLeft: icon ? '40px' : '16px',
            height: '46px',
            fontSize: '0.9rem',
          }}
          {...props}
        />
      </div>
      {error && (
        <span style={{
          fontSize: '0.75rem',
          color: 'var(--danger)',
          marginTop: '2px',
          fontWeight: 500
        }}>
          {error}
        </span>
      )}
    </div>
  );
};

export default GlassInput;

const SkeletonLoader = ({ type = 'card', count = 1 }) => {
  const items = Array.from({ length: count });

  const renderSkeleton = () => {
    switch (type) {
      case 'table':
        return (
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
              <div className="shimmer-bg" style={{ height: '24px', flex: 1, borderRadius: '6px' }} />
              <div className="shimmer-bg" style={{ height: '24px', flex: 1, borderRadius: '6px' }} />
              <div className="shimmer-bg" style={{ height: '24px', flex: 1, borderRadius: '6px' }} />
            </div>
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} style={{ display: 'flex', gap: '10px', padding: '12px 0', borderBottom: '1px solid var(--glass-border)' }}>
                <div className="shimmer-bg" style={{ height: '20px', flex: 1, borderRadius: '4px' }} />
                <div className="shimmer-bg" style={{ height: '20px', flex: 1, borderRadius: '4px' }} />
                <div className="shimmer-bg" style={{ height: '20px', flex: 1, borderRadius: '4px' }} />
              </div>
            ))}
          </div>
        );
      case 'list':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {items.map((_, i) => (
              <div key={i} className="glass-panel" style={{ display: 'flex', gap: '16px', padding: '16px', alignItems: 'center' }}>
                <div className="shimmer-bg" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div className="shimmer-bg" style={{ height: '16px', width: '40%', borderRadius: '4px' }} />
                  <div className="shimmer-bg" style={{ height: '12px', width: '70%', borderRadius: '4px' }} />
                </div>
              </div>
            ))}
          </div>
        );
      case 'chart':
        return (
          <div className="glass-panel" style={{ padding: '24px', height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', height: '80%', paddingBottom: '16px', borderBottom: '2px solid var(--glass-border)' }}>
              <div className="shimmer-bg" style={{ width: '12%', height: '30%', borderRadius: '6px 6px 0 0' }} />
              <div className="shimmer-bg" style={{ width: '12%', height: '70%', borderRadius: '6px 6px 0 0' }} />
              <div className="shimmer-bg" style={{ width: '12%', height: '50%', borderRadius: '6px 6px 0 0' }} />
              <div className="shimmer-bg" style={{ width: '12%', height: '85%', borderRadius: '6px 6px 0 0' }} />
              <div className="shimmer-bg" style={{ width: '12%', height: '40%', borderRadius: '6px 6px 0 0' }} />
              <div className="shimmer-bg" style={{ width: '12%', height: '60%', borderRadius: '6px 6px 0 0' }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div className="shimmer-bg" style={{ height: '12px', width: '10%', borderRadius: '4px' }} />
              <div className="shimmer-bg" style={{ height: '12px', width: '10%', borderRadius: '4px' }} />
              <div className="shimmer-bg" style={{ height: '12px', width: '10%', borderRadius: '4px' }} />
            </div>
          </div>
        );
      case 'card':
      default:
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
            {items.map((_, i) => (
              <div key={i} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div className="shimmer-bg" style={{ height: '14px', width: '50%', borderRadius: '4px' }} />
                  <div className="shimmer-bg" style={{ height: '32px', width: '32px', borderRadius: '8px' }} />
                </div>
                <div className="shimmer-bg" style={{ height: '28px', width: '80%', borderRadius: '6px' }} />
                <div className="shimmer-bg" style={{ height: '12px', width: '35%', borderRadius: '4px' }} />
              </div>
            ))}
          </div>
        );
    }
  };

  return renderSkeleton();
};

export default SkeletonLoader;

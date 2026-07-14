import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { HiOutlineAcademicCap, HiOutlineChevronLeft, HiOutlineBookOpen } from 'react-icons/hi2';
import { careerAPI } from '../api/career';
import '../styles/Profile.css';

const RoadmapUI = () => {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchRoadmap = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await careerAPI.getRoadmap();
      setRoadmap(res.data);
    } catch (err) {
      console.error(err);
      setError('No active roadmap found. Please run profile analysis on the Career Dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const handleCheckboxChange = async (milestoneTitle, itemName, currentVal) => {
    try {
      // Toggle value locally first for premium snappy responsive UI
      const updatedMilestones = roadmap.milestones.map((ms) => {
        if (ms.milestone_title === milestoneTitle) {
          return {
            ...ms,
            items: ms.items.map((it) => {
              if (it.name === itemName) {
                return { ...it, is_completed: !currentVal };
              }
              return it;
            })
          };
        }
        return ms;
      });
      setRoadmap({ ...roadmap, milestones: updatedMilestones });

      // Save state to backend
      await careerAPI.updateProgress({
        milestone_title: milestoneTitle,
        item_name: itemName,
        is_completed: !currentVal
      });
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container" style={{ textAlign: 'center', paddingTop: 100 }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p style={{ marginTop: 16, color: 'var(--gray-300)' }}>Building your learning roadmap...</p>
        </div>
      </div>
    );
  }

  if (error || !roadmap) {
    return (
      <div className="profile-page">
        <div className="profile-container" style={{ maxWidth: '600px', textAlign: 'center', paddingTop: 80 }}>
          <div className="profile-card" style={{ padding: '32px' }}>
            <span style={{ fontSize: '3rem', display: 'block', marginBottom: '16px' }}>🗺️</span>
            <h2>No Roadmap Available</h2>
            <p style={{ color: 'var(--gray-400)', margin: '12px 0 24px' }}>
              Please generate a career analysis first to map out your technical pathway and milestones.
            </p>
            <Link to="/career" className="btn btn-primary">Go to Career Dashboard</Link>
          </div>
        </div>
      </div>
    );
  }

  // Calculate completion percentage
  let totalItems = 0;
  let completedItems = 0;
  roadmap.milestones?.forEach(ms => {
    ms.items?.forEach(it => {
      totalItems++;
      if (it.is_completed) completedItems++;
    });
  });
  const percent = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;

  return (
    <div className="profile-page">
      <div className="profile-container" style={{ maxWidth: '900px' }}>
        
        {/* Header Navigation */}
        <div style={{ marginBottom: '24px' }}>
          <Link to="/career" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#8B5CF6', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem' }}>
            <HiOutlineChevronLeft /> Back to Dashboard
          </Link>
        </div>

        {/* Hero Card */}
        <div className="profile-card" style={{ padding: '32px', marginBottom: '24px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', color: '#8B5CF6' }}>Learning Roadmap</span>
              <h2 className="profile-name" style={{ fontSize: '1.75rem', marginTop: '6px', color: 'var(--text-color)' }}>
                Technical Specialization Pathway
              </h2>
              <p className="profile-headline" style={{ color: 'var(--subtext-color)', marginTop: '4px' }}>
                Estimated Duration: <strong style={{ color: 'var(--text-color)' }}>{roadmap.estimated_duration || '12 Months'}</strong>
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--subtext-color)' }}>Roadmap Progress</span>
              <h3 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10B981', margin: '4px 0 0' }}>{percent}%</h3>
            </div>
          </div>

          <div style={{ width: '100%', height: '6px', background: 'var(--glass-border)', borderRadius: '3px', marginTop: '20px', overflow: 'hidden' }}>
            <div style={{ width: `${percent}%`, height: '100%', background: 'linear-gradient(90deg, #8B5CF6 0%, #10B981 100%)', transition: 'width 0.4s ease' }}></div>
          </div>
        </div>

        {/* Milestone Steps Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {roadmap.milestones?.map((ms, idx) => {
            // Count milestone completed items
            const msTotal = ms.items?.length || 0;
            const msDone = ms.items?.filter(it => it.is_completed).length || 0;

            return (
              <div key={idx} className="profile-card" style={{ padding: '24px', borderLeft: msDone === msTotal && msTotal > 0 ? '4px solid #10B981' : '1px solid var(--glass-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
                  <h4 style={{ fontSize: '1.1rem', color: 'var(--text-color)', fontWeight: 700, margin: 0 }}>
                    {ms.milestone_title}
                  </h4>
                  <span style={{ fontSize: '0.75rem', padding: '3px 10px', borderRadius: '12px', background: 'var(--glass-border)', color: 'var(--subtext-color)', fontWeight: 600 }}>
                    {msDone}/{msTotal} completed
                  </span>
                </div>
                
                <p style={{ fontSize: '0.85rem', color: 'var(--subtext-color)', marginBottom: '18px', lineHeight: '1.5' }}>
                  {ms.description}
                </p>

                {/* Items List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {ms.items?.map((item, itemIdx) => (
                    <div 
                      key={itemIdx} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between', 
                        padding: '12px 16px', 
                        background: 'rgba(255,255,255,0.02)', 
                        border: '1px solid var(--glass-border)', 
                        borderRadius: '8px',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <input
                          type="checkbox"
                          checked={item.is_completed || false}
                          onChange={() => handleCheckboxChange(ms.milestone_title, item.name, item.is_completed)}
                          style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: '#8B5CF6' }}
                        />
                        <div style={{ textDecoration: item.is_completed ? 'line-through' : 'none', opacity: item.is_completed ? 0.6 : 1 }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-color)' }}>{item.name}</span>
                          <div style={{ display: 'flex', gap: '8px', marginTop: '4px', alignItems: 'center', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', background: 'rgba(139, 92, 246, 0.12)', color: 'var(--primary)', fontWeight: 600 }}>
                              {item.category}
                            </span>
                            {item.resource && (
                              <span style={{ fontSize: '0.7rem', color: 'var(--subtext-color)', display: 'flex', alignItems: 'center', gap: '3px' }}>
                                <HiOutlineBookOpen /> {item.resource}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
};

export default RoadmapUI;

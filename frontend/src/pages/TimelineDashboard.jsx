import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { 
  HiOutlineSparkles, 
  HiOutlineArrowUp, 
  HiOutlineAcademicCap, 
  HiOutlineBriefcase, 
  HiOutlineDocumentText, 
  HiOutlineBadgeCheck, 
  HiOutlinePlusCircle, 
  HiOutlineX,
  HiOutlineFilter,
  HiOutlineSearch
} from 'react-icons/hi';
import { timelineAPI } from '../api/timeline';
import '../styles/Timeline.css';

const TimelineDashboard = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [stats, setStats] = useState({ ats_growth: 0, skill_trends: [], career_trends: [], learning_progress: [] });

  // Event creation form modal
  const [showLogModal, setShowLogModal] = useState(false);
  const [newEvent, setNewEvent] = useState({ event_type: 'theme_changed', title: '', description: '' });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await timelineAPI.getTimelineEvents({
        page,
        search,
        event_type: filterType
      });
      setEvents(res.data.results || []);
      setHasMore(!!res.data.next);
      setHasPrev(!!res.data.previous);
    } catch (err) {
      console.error('Failed to load timeline events', err);
    } finally {
      setLoading(false);
    }
  }, [page, search, filterType]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await timelineAPI.getTimelineHistory();
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load history metrics', err);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handleFilterChange = (e) => {
    setFilterType(e.target.value);
    setPage(1);
  };

  const handleLogEvent = async (e) => {
    e.preventDefault();
    if (!newEvent.title.trim()) {
      setError('Title is required.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await timelineAPI.createTimelineEvent({
        event_type: newEvent.event_type,
        title: newEvent.title,
        description: newEvent.description,
        metadata: { logged_manually: true }
      });
      setNewEvent({ event_type: 'theme_changed', title: '', description: '' });
      setShowLogModal(false);
      fetchEvents();
      fetchStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to log event.');
    } finally {
      setSubmitting(false);
    }
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'resume_uploaded':
        return <HiOutlineDocumentText />;
      case 'resume_updated':
        return <HiOutlineArrowUp />;
      case 'ats_improved':
        return <HiOutlineBadgeCheck />;
      case 'skill_added':
      case 'skill_removed':
        return <HiOutlineSparkles />;
      case 'experience_added':
        return <HiOutlineBriefcase />;
      case 'certificate_added':
        return <HiOutlineAcademicCap />;
      default:
        return <HiOutlineSparkles />;
    }
  };

  const getEventClass = (type) => {
    if (type.includes('resume')) return 'type-resume';
    if (type.includes('ats')) return 'type-ats';
    if (type.includes('skill')) return 'type-skill';
    if (type.includes('portfolio')) return 'type-portfolio';
    return 'type-career';
  };

  const latestCareer = stats.career_trends?.[stats.career_trends.length - 1] || { career_score: 0, growth_score: 0 };
  const latestSkillsCount = stats.skill_trends?.[stats.skill_trends.length - 1]?.count || 0;
  const latestAtsScore = stats.ats_history?.[stats.ats_history.length - 1]?.score || 0;

  return (
    <div className="timeline-container">
      <div className="timeline-header">
        <div>
          <h1>Career Timeline</h1>
          <p className="text-muted">Track your skills addition, ATS score achievements, and career progress.</p>
        </div>
        <div className="d-flex gap-3">
          <Link to="/timeline/compare" className="btn btn-outline-secondary rounded-pill px-4">Compare Versions</Link>
          <Link to="/timeline/analytics" className="btn btn-primary rounded-pill px-4">Growth Analytics</Link>
        </div>
      </div>

      <div className="row g-4">
        {/* Main Timeline Stream */}
        <div className="col-lg-8">
          <div className="d-flex flex-wrap gap-3 mb-4 align-items-center justify-content-between">
            <div className="position-relative flex-grow-1" style={{ maxWidth: '400px' }}>
              <span className="position-absolute top-50 start-0 translate-middle-y ps-3 text-muted">
                <HiOutlineSearch />
              </span>
              <input
                type="text"
                placeholder="Search event title, description..."
                value={search}
                onChange={handleSearchChange}
                className="form-control rounded-pill ps-5"
              />
            </div>

            <div className="d-flex align-items-center gap-2">
              <HiOutlineFilter className="text-muted" />
              <select
                value={filterType}
                onChange={handleFilterChange}
                className="form-select rounded-pill"
              >
                <option value="">All Events</option>
                <option value="resume_uploaded">Resume Uploaded</option>
                <option value="resume_updated">Resume Updated</option>
                <option value="ats_improved">ATS Improved</option>
                <option value="skill_added">Skill Added</option>
                <option value="skill_removed">Skill Removed</option>
                <option value="project_added">Project Added</option>
                <option value="experience_added">Experience Added</option>
                <option value="portfolio_published">Portfolio Published</option>
                <option value="cover_letter_generated">Cover Letter</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-5 timeline-card-panel rounded-4">
              <HiOutlineSparkles className="display-4 text-muted mb-3" />
              <h4>No events recorded yet</h4>
              <p className="text-muted">Start by uploading your resume, editing your profile, or generating cover letters.</p>
            </div>
          ) : (
            <>
              <div className="timeline-track-wrapper">
                {events.map((event) => (
                  <div className="timeline-node" key={event.id}>
                    <div className="timeline-node-icon">
                      {getEventIcon(event.event_type)}
                    </div>
                    <div className="timeline-card">
                      <div className="timeline-card-header">
                        <span className="timeline-card-title">{event.title}</span>
                        <span className={`timeline-card-type ${getEventClass(event.event_type)}`}>
                          {event.event_type_display}
                        </span>
                      </div>
                      <div className="timeline-card-date">{event.created_at_formatted}</div>
                      {event.description && <p className="timeline-card-desc mb-0">{event.description}</p>}
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              <div className="d-flex justify-content-between align-items-center mt-4">
                <button
                  onClick={() => setPage((p) => Math.max(p - 1, 1))}
                  disabled={!hasPrev}
                  className="btn btn-outline-secondary rounded-pill px-4"
                >
                  Previous
                </button>
                <span className="pagination-text">Page {page}</span>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!hasMore}
                  className="btn btn-outline-secondary rounded-pill px-4"
                >
                  Next
                </button>
              </div>
            </>
          )}
        </div>

        {/* Sidebar Summary Widget panel */}
        <div className="col-lg-4">
          <div className="timeline-card-panel mb-4">
            <h4 className="mb-4">Growth Summary</h4>
            <div className="mb-4">
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">Latest ATS Score</span>
                <span className="text-success fw-bold">{latestAtsScore}/100</span>
              </div>
              <div className="progress" style={{ height: '8px' }}>
                <div 
                  className="progress-bar bg-success" 
                  role="progressbar" 
                  style={{ width: `${latestAtsScore}%` }} 
                  aria-valuenow={latestAtsScore} 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                ></div>
              </div>
            </div>

            <div className="mb-4">
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">Active Skills Added</span>
                <span className="text-info fw-bold">{latestSkillsCount} Skills</span>
              </div>
              <div className="progress" style={{ height: '8px' }}>
                <div 
                  className="progress-bar bg-info" 
                  role="progressbar" 
                  style={{ width: `${Math.min(latestSkillsCount * 5, 100)}%` }}
                  aria-valuenow={latestSkillsCount} 
                  aria-valuemin="0" 
                  aria-valuemax="20"
                ></div>
              </div>
            </div>

            <div className="mb-4">
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">Career Match Score</span>
                <span className="text-warning fw-bold">{latestCareer.career_score ? latestCareer.career_score.toFixed(1) : 0}%</span>
              </div>
              <div className="progress" style={{ height: '8px' }}>
                <div 
                  className="progress-bar bg-warning" 
                  role="progressbar" 
                  style={{ width: `${latestCareer.career_score || 0}%` }}
                  aria-valuenow={latestCareer.career_score || 0} 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                ></div>
              </div>
            </div>

            <button 
              onClick={() => setShowLogModal(true)}
              className="btn btn-outline-primary rounded-pill w-100 mt-2 d-flex align-items-center justify-content-center gap-2"
            >
              <HiOutlinePlusCircle /> Log Custom Event
            </button>
          </div>

          <div className="timeline-card-panel">
            <h4 className="mb-3">Quick Navigation</h4>
            <div className="list-group list-group-flush bg-transparent">
              <Link to="/resumes" className="list-group-item bg-transparent border-bottom py-3 ps-0 d-flex justify-content-between align-items-center" style={{ color: 'inherit' }}>
                <span>Manage Resumes</span>
                <span className="badge bg-primary rounded-pill">&gt;</span>
              </Link>
              <Link to="/profile" className="list-group-item bg-transparent border-bottom py-3 ps-0 d-flex justify-content-between align-items-center" style={{ color: 'inherit' }}>
                <span>Edit Profile Master</span>
                <span className="badge bg-primary rounded-pill">&gt;</span>
              </Link>
              <Link to="/portfolio" className="list-group-item bg-transparent border-0 py-3 ps-0 d-flex justify-content-between align-items-center" style={{ color: 'inherit' }}>
                <span>Portfolio Settings</span>
                <span className="badge bg-primary rounded-pill">&gt;</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Manual Event Modal */}
      {showLogModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.6)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content timeline-modal-content rounded-4 p-3">
              <div className="modal-header border-0 pb-0">
                <h5 className="modal-title d-flex align-items-center gap-2">
                  <HiOutlinePlusCircle className="text-primary fs-4" /> Log Custom Event
                </h5>
                <button type="button" className="btn bg-transparent border-0 text-body fs-4" onClick={() => setShowLogModal(false)}>
                  <HiOutlineX />
                </button>
              </div>
              <form onSubmit={handleLogEvent}>
                <div className="modal-body">
                  {error && <div className="alert alert-danger py-2">{error}</div>}
                  <div className="mb-3">
                    <label className="form-label">Event Type</label>
                    <select
                      value={newEvent.event_type}
                      onChange={(e) => setNewEvent({ ...newEvent, event_type: e.target.value })}
                      className="form-select"
                    >
                      <option value="theme_changed">Theme Changed</option>
                      <option value="cover_letter_generated">Generated Cover Letter</option>
                      <option value="career_roadmap_started">Started Career Roadmap</option>
                      <option value="roadmap_completed">Completed Career Roadmap</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Title</label>
                    <input
                      type="text"
                      value={newEvent.title}
                      onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                      className="form-control"
                      placeholder="e.g. Switched to corporate minimalist theme"
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Description / Details</label>
                    <textarea
                      value={newEvent.description}
                      onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                      className="form-control"
                      rows="3"
                      placeholder="Enter optional description..."
                    ></textarea>
                  </div>
                </div>
                <div className="modal-footer border-0 pt-0">
                  <button type="button" className="btn btn-outline-secondary rounded-pill px-4" onClick={() => setShowLogModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary rounded-pill px-4" disabled={submitting}>
                    {submitting ? 'Saving...' : 'Add Event'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimelineDashboard;

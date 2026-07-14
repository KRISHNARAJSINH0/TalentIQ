import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { 
  HiOutlineChevronLeft, 
  HiOutlineDuplicate, 
  HiOutlinePlus, 
  HiOutlineMinus,
  HiOutlineCheck,
  HiOutlineSparkles
} from 'react-icons/hi';
import { timelineAPI } from '../api/timeline';
import '../styles/Timeline.css';

const TimelineCompare = () => {
  const [versions, setVersions] = useState([]);
  const [loadingVersions, setLoadingVersions] = useState(true);

  // Selected version IDs for comparison
  const [v1, setV1] = useState('');
  const [v2, setV2] = useState('');
  const [v3, setV3] = useState('');
  
  const [compareData, setCompareData] = useState(null);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        const res = await timelineAPI.getTimelineVersions();
        setVersions(res.data || []);
        if (res.data.length >= 2) {
          setV1(res.data[1].id); // default base version
          setV2(res.data[0].id); // default target version
        } else if (res.data.length === 1) {
          setV1(res.data[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch versions', err);
      } finally {
        setLoadingVersions(false);
      }
    };
    fetchVersions();
  }, []);

  const handleCompare = useCallback(async () => {
    if (!v1 || !v2) {
      setError('Please select at least two versions to compare.');
      return;
    }
    setComparing(true);
    setError(null);
    try {
      const res = await timelineAPI.compareTimelineVersions(v1, v2, v3 || null);
      setCompareData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to compare snapshots.');
    } finally {
      setComparing(false);
    }
  }, [v1, v2, v3]);

  // Trigger compare automatically if defaults are populated
  useEffect(() => {
    if (v1 && v2 && !compareData && !comparing) {
      handleCompare();
    }
  }, [v1, v2, compareData, comparing, handleCompare]);

  return (
    <div className="timeline-container">
      <div className="mb-4">
        <Link to="/timeline" className="btn btn-link text-decoration-none p-0 d-flex align-items-center gap-2" style={{ color: 'var(--primary, #2563eb)' }}>
          <HiOutlineChevronLeft /> Back to Career Timeline
        </Link>
      </div>

      <div className="timeline-header align-items-start">
        <div>
          <h1>Version Comparison Engine</h1>
          <p className="text-muted">Compare master profile snapshots across different timeframes to inspect changes.</p>
        </div>
      </div>

      <div className="compare-container">
        {/* Selection panel */}
        <div className="compare-selector">
          <h3>Select Snapshots</h3>
          {loadingVersions ? (
            <div className="text-center py-4">
              <div className="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>
          ) : versions.length < 2 ? (
            <div className="alert alert-warning py-2 mb-0">
              You need at least 2 versions to perform a comparison. Upload more resumes or update your profile to trigger snapshots.
            </div>
          ) : (
            <div>
              <div className="mb-3">
                <label className="form-label text-muted small fw-bold">Base Version (V1)</label>
                <select 
                  value={v1} 
                  onChange={(e) => setV1(e.target.value)}
                  className="compare-select-field"
                >
                  <option value="">Choose version...</option>
                  {versions.map((ver) => (
                    <option key={ver.id} value={ver.id}>
                      Version {ver.version_number} ({ver.summary})
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label text-muted small fw-bold">Target Version (V2)</label>
                <select 
                  value={v2} 
                  onChange={(e) => setV2(e.target.value)}
                  className="compare-select-field"
                >
                  <option value="">Choose version...</option>
                  {versions.map((ver) => (
                    <option key={ver.id} value={ver.id}>
                      Version {ver.version_number} ({ver.summary})
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-4">
                <label className="form-label text-muted small fw-bold">Third Version (Optional V3)</label>
                <select 
                  value={v3} 
                  onChange={(e) => setV3(e.target.value)}
                  className="compare-select-field"
                >
                  <option value="">None</option>
                  {versions.map((ver) => (
                    <option key={ver.id} value={ver.id}>
                      Version {ver.version_number} ({ver.summary})
                    </option>
                  ))}
                </select>
              </div>

              <button 
                onClick={handleCompare}
                disabled={comparing}
                className="btn btn-primary w-100 rounded-pill py-2.5 d-flex align-items-center justify-content-center gap-2"
              >
                <HiOutlineDuplicate /> {comparing ? 'Comparing...' : 'Compare Snapshots'}
              </button>
            </div>
          )}
        </div>

        {/* Results panel */}
        <div className="compare-content">
          {error && <div className="alert alert-danger">{error}</div>}

          {comparing ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status"></div>
              <p className="text-muted mt-3">Analyzing snapshot changes...</p>
            </div>
          ) : !compareData ? (
            <div className="text-center py-5 timeline-card-panel rounded-4">
              <HiOutlineDuplicate className="display-4 text-muted mb-3" />
              <h4>Select versions to compare</h4>
              <p className="text-muted">Choose your resume versions on the left panel to inspect differences.</p>
            </div>
          ) : (
            <div>
              {/* Header metrics comparing scores */}
              <div className="row g-4 mb-4">
                <div className="col-md-6 col-lg-4">
                  <div className="timeline-card-panel p-3 text-center">
                    <span className="text-muted small uppercase">Base (Version {compareData.v1.version_number}) ATS</span>
                    <h3 className="text-info mt-2 mb-0">{compareData.v1.ats_score}/100</h3>
                  </div>
                </div>
                <div className="col-md-6 col-lg-4">
                  <div className="timeline-card-panel p-3 text-center">
                    <span className="text-muted small uppercase">Target (Version {compareData.v2.version_number}) ATS</span>
                    <h3 className="text-success mt-2 mb-0">{compareData.v2.ats_score}/100</h3>
                  </div>
                </div>
                {compareData.v3 && (
                  <div className="col-md-12 col-lg-4">
                    <div className="timeline-card-panel p-3 text-center">
                      <span className="text-muted small uppercase">Third (Version {compareData.v3.version_number}) ATS</span>
                      <h3 className="text-warning mt-2 mb-0">{compareData.v3.ats_score}/100</h3>
                    </div>
                  </div>
                )}
              </div>

              {/* Diffs: v1 vs v2 */}
              <div className="timeline-card-panel mb-4">
                <h4 className="border-bottom pb-3 mb-4 d-flex align-items-center gap-2">
                  <HiOutlineSparkles className="text-success" /> Diff: Version {compareData.v1.version_number} vs Version {compareData.v2.version_number}
                </h4>

                {/* Added/Removed Skills */}
                <div className="mb-4">
                  <h6 className="text-muted mb-3">Skills Changes</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {compareData.diff_v1_v2.added_skills.map((skill) => (
                      <span key={skill} className="diff-tag diff-added">
                        <HiOutlinePlus size={12} /> {skill}
                      </span>
                    ))}
                    {compareData.diff_v1_v2.removed_skills.map((skill) => (
                      <span key={skill} className="diff-tag diff-removed">
                        <HiOutlineMinus size={12} /> {skill}
                      </span>
                    ))}
                    {compareData.diff_v1_v2.added_skills.length === 0 && compareData.diff_v1_v2.removed_skills.length === 0 && (
                      <span className="text-muted small italic">No skills changed between these snapshots.</span>
                    )}
                  </div>
                </div>

                {/* Added Experiences */}
                <div className="mb-4">
                  <h6 className="text-muted mb-3">New Experience Additions</h6>
                  {compareData.diff_v1_v2.new_experience.length === 0 ? (
                    <p className="text-muted small italic mb-0">No new work experience added.</p>
                  ) : (
                    <div className="list-group list-group-flush bg-transparent">
                      {compareData.diff_v1_v2.new_experience.map((exp, idx) => (
                        <div key={idx} className="list-group-item bg-transparent border-bottom ps-0 py-3" style={{ color: 'inherit' }}>
                          <h6 className="fw-bold mb-1">{exp.designation} <span className="text-success small ms-2"><HiOutlineCheck /> Added</span></h6>
                          <div className="text-muted small">{exp.company} | {exp.start_date} - {exp.end_date || 'Present'}</div>
                          {exp.description && <p className="small text-muted mt-2 mb-0">{exp.description}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Added Projects */}
                <div className="mb-4">
                  <h6 className="text-muted mb-3">New Projects Added</h6>
                  {compareData.diff_v1_v2.new_projects.length === 0 ? (
                    <p className="text-muted small italic mb-0">No new projects added.</p>
                  ) : (
                    <div className="list-group list-group-flush bg-transparent">
                      {compareData.diff_v1_v2.new_projects.map((proj, idx) => (
                        <div key={idx} className="list-group-item bg-transparent border-bottom ps-0 py-3" style={{ color: 'inherit' }}>
                          <h6 className="fw-bold mb-1">{proj.project_name} <span className="text-success small ms-2"><HiOutlineCheck /> Added</span></h6>
                          <div className="text-muted small">Technologies: {proj.technologies || 'None specified'}</div>
                          {proj.description && <p className="small text-muted mt-2 mb-0">{proj.description}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Added Certificates */}
                <div>
                  <h6 className="text-muted mb-3">New Certifications Added</h6>
                  {compareData.diff_v1_v2.new_certificates.length === 0 ? (
                    <p className="text-muted small italic mb-0">No new certifications added.</p>
                  ) : (
                    <div className="list-group list-group-flush bg-transparent">
                      {compareData.diff_v1_v2.new_certificates.map((cert, idx) => (
                        <div key={idx} className="list-group-item bg-transparent border-0 ps-0 py-3" style={{ color: 'inherit' }}>
                          <h6 className="fw-bold mb-1">{cert.certificate_name} <span className="text-success small ms-2"><HiOutlineCheck /> Added</span></h6>
                          <div className="text-muted small">Issued by: {cert.organization} | Date: {cert.issue_date}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Diffs: v2 vs v3 (if v3 is selected) */}
              {compareData.v3 && compareData.diff_v2_v3 && (
                <div className="timeline-card-panel">
                  <h4 className="border-bottom pb-3 mb-4 d-flex align-items-center gap-2">
                    <HiOutlineSparkles className="text-warning" /> Diff: Version {compareData.v2.version_number} vs Version {compareData.v3.version_number}
                  </h4>

                  {/* Added/Removed Skills */}
                  <div className="mb-4">
                    <h6 className="text-muted mb-3">Skills Changes</h6>
                    <div className="d-flex flex-wrap gap-2">
                      {compareData.diff_v2_v3.added_skills.map((skill) => (
                        <span key={skill} className="diff-tag diff-added">
                          <HiOutlinePlus size={12} /> {skill}
                        </span>
                      ))}
                      {compareData.diff_v2_v3.removed_skills.map((skill) => (
                        <span key={skill} className="diff-tag diff-removed">
                          <HiOutlineMinus size={12} /> {skill}
                        </span>
                      ))}
                      {compareData.diff_v2_v3.added_skills.length === 0 && compareData.diff_v2_v3.removed_skills.length === 0 && (
                        <span className="text-muted small italic">No skills changed between these snapshots.</span>
                      )}
                    </div>
                  </div>

                  {/* Added Experiences */}
                  <div className="mb-4">
                    <h6 className="text-muted mb-3">New Experience Additions</h6>
                    {compareData.diff_v2_v3.new_experience.length === 0 ? (
                      <p className="text-muted small italic mb-0">No new work experience added.</p>
                    ) : (
                      <div className="list-group list-group-flush bg-transparent">
                        {compareData.diff_v2_v3.new_experience.map((exp, idx) => (
                          <div key={idx} className="list-group-item bg-transparent border-bottom ps-0 py-3" style={{ color: 'inherit' }}>
                            <h6 className="fw-bold mb-1">{exp.designation} <span className="text-success small ms-2"><HiOutlineCheck /> Added</span></h6>
                            <div className="text-muted small">{exp.company} | {exp.start_date} - {exp.end_date || 'Present'}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TimelineCompare;

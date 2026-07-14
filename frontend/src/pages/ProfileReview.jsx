import { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HiOutlineUser,
  HiOutlineDocumentText,
  HiOutlineBriefcase,
  HiOutlineAcademicCap,
  HiOutlineSquare3Stack3D,
  HiOutlineLanguage,
  HiOutlineHeart,
  HiOutlineUserGroup,
  HiOutlineClipboardDocumentCheck,
  HiOutlinePlus,
  HiOutlineTrash,
  HiOutlineArrowUp,
  HiOutlineArrowDown,
  HiOutlineCheckCircle,
  HiOutlineExclamationCircle,
} from 'react-icons/hi2';

import { profilesAPI } from '../api/profiles';
import '../styles/Profile.css';
import '../styles/ProfileReview.css';

const FieldRow = ({ label, name, source, error, children }) => {
  const getSourceClass = (src) => {
    if (!src) return 'manual';
    return ['regex', 'spacy', 'gemini', 'manual'].includes(src.toLowerCase())
      ? src.toLowerCase()
      : 'manual';
  };

  return (
    <div className="edit-field">
      <div className="field-header-row">
        <label className="edit-label">{label}</label>
        <span className="field-meta-info">
          Source: <span className={`indicator-badge ${getSourceClass(source)}`}>{source || 'manual'}</span>
        </span>
      </div>
      {children}
      {error && <span className="edit-field-error">{error}</span>}
    </div>
  );
};

const ProfileReview = () => {
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('resume_id');
  const navigate = useNavigate();

  // State management
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState(null);
  const [activeTab, setActiveTab] = useState('personal');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  // Skill add inputs
  const [newGeneralSkill, setNewGeneralSkill] = useState('');
  const [newTechSkill, setNewTechSkill] = useState('');
  const [newSoftSkill, setNewSoftSkill] = useState('');

  const summaryRef = useRef(null);

  // Load data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const res = await profilesAPI.getMasterProfile(resumeId);
        setProfile(res.data);
        setFormData(res.data);
      } catch (err) {
        setError('Failed to load profile data.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [resumeId]);

  if (loading) {
    return (
      <div className="profile-review-page">
        <div className="profile-container" style={{ textAlign: 'center', paddingTop: 100 }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading Master Profile...</span>
          </div>
          <p style={{ marginTop: 16, color: 'var(--gray-300)' }}>Assembling and loading your Master Profile...</p>
        </div>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="profile-review-page">
        <div className="profile-container">
          <div className="auth-error">Error loading profile data. Please try again.</div>
        </div>
      </div>
    );
  }

  // Input change handler
  const handleInputChange = (field, val, isNestedUser = false) => {
    setSuccess('');
    setFieldErrors({ ...fieldErrors, [field]: null });
    if (isNestedUser) {
      setFormData({
        ...formData,
        [field]: val,
      });
    } else {
      setFormData({
        ...formData,
        [field]: val,
      });
    }
  };

  // Skill editor helpers
  const handleAddSkill = (skillType, skillName, setInputState) => {
    if (!skillName.trim()) return;
    const currentSkills = formData.skills || [];
    // Check duplicate
    const exists = currentSkills.some(
      (s) => s.skill_name.toLowerCase() === skillName.trim().toLowerCase() && s.skill_type === skillType
    );
    if (exists) {
      setFieldErrors({ ...fieldErrors, skills: `Duplicate skill '${skillName}' in category '${skillType}'.` });
      return;
    }

    const updated = [...currentSkills, { skill_name: skillName.trim(), skill_level: 'intermediate', skill_type: skillType }];
    setFormData({ ...formData, skills: updated });
    setInputState('');
    setFieldErrors({ ...fieldErrors, skills: null });
  };

  const handleDeleteSkill = (index) => {
    const currentSkills = [...(formData.skills || [])];
    currentSkills.splice(index, 1);
    setFormData({ ...formData, skills: currentSkills });
  };

  // Generic Array Item managers
  const handleAddArrayItem = (key, defaultObj) => {
    const list = [...(formData[key] || [])];
    setFormData({ ...formData, [key]: [...list, defaultObj] });
  };

  const handleUpdateArrayItem = (key, index, field, value) => {
    const list = [...(formData[key] || [])];
    list[index] = { ...list[index], [field]: value };
    setFormData({ ...formData, [key]: list });
  };

  const handleDeleteArrayItem = (key, index) => {
    const list = [...(formData[key] || [])];
    list.splice(index, 1);
    setFormData({ ...formData, [key]: list });
  };

  const handleMoveArrayItem = (key, index, direction) => {
    const list = [...(formData[key] || [])];
    if (direction === 'up' && index > 0) {
      const temp = list[index];
      list[index] = list[index - 1];
      list[index - 1] = temp;
    } else if (direction === 'down' && index < list.length - 1) {
      const temp = list[index];
      list[index] = list[index + 1];
      list[index + 1] = temp;
    }
    setFormData({ ...formData, [key]: list });
  };

  // Rich Text Markup helper
  const insertMarkup = (prefix, suffix = '') => {
    const textarea = summaryRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selected = text.substring(start, end);
    const replacement = prefix + selected + suffix;

    const newSummary = text.substring(0, start) + replacement + text.substring(end);
    handleInputChange('summary', newSummary);

    // Focus and select back
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + prefix.length, start + prefix.length + selected.length);
    }, 0);
  };

  // Save section / profile
  const handleSave = async (e) => {
    if (e) e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    setFieldErrors({});

    try {
      const res = await profilesAPI.updateMasterProfile(formData);
      setProfile(res.data);
      setFormData(res.data);
      setSuccess('Master Profile saved successfully! Redirecting...');
      setTimeout(() => {
        navigate('/profile');
      }, 1500);
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object') {
        setFieldErrors(data);
        setError('Validation failed. Please review highlighted fields.');
      } else {
        setError('An unexpected error occurred while saving.');
      }
    } finally {
      setSaving(false);
    }
  };

  // Verify section / profile
  const handleVerify = async (sectionName = null) => {
    setVerifying(true);
    setError('');
    setSuccess('');

    try {
      const res = await profilesAPI.verifySection(sectionName, true);
      setProfile(res.data);
      setFormData(res.data);
      setSuccess(`${sectionName ? sectionName.toUpperCase() + ' section' : 'Profile'} marked as verified!`);
    } catch (err) {
      setError('Verification update failed.');
    } finally {
      setVerifying(false);
    }
  };

  // Sidebar navigation options
  const sidebarItems = [
    { id: 'personal', label: 'Personal Info', icon: <HiOutlineUser /> },
    { id: 'summary_skills', label: 'Summary & Skills', icon: <HiOutlineDocumentText /> },
    { id: 'experience', label: 'Experience', icon: <HiOutlineBriefcase /> },
    { id: 'education', label: 'Education', icon: <HiOutlineAcademicCap /> },
    { id: 'projects', label: 'Projects', icon: <HiOutlineSquare3Stack3D /> },
    { id: 'certs_langs', label: 'Certs & Languages', icon: <HiOutlineLanguage /> },
    { id: 'honors_vol', label: 'Honors & Volunteer', icon: <HiOutlineHeart /> },
    { id: 'references', label: 'References', icon: <HiOutlineUserGroup /> },
    { id: 'history', label: 'Audit Log & History', icon: <HiOutlineClipboardDocumentCheck /> },
  ];

  return (
    <div className="profile-review-page">
      <div className="review-container">
        {/* Sidebar Nav */}
        <aside className="review-sidebar">
          <div className="nav-card">
            <h4 className="nav-title">Master Sections</h4>
            <ul className="nav-list">
              {sidebarItems.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveTab(item.id)}
                    className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* Main Review Form */}
        <main className="review-main">
          {/* Header Action Row */}
          <div className="review-panel-header">
            <div>
              <h1 className="review-panel-title">Master Resume Profile</h1>
              <div className="badge-group" style={{ marginTop: 8 }}>
                {profile.is_verified ? (
                  <span className="indicator-badge verified">
                    <HiOutlineCheckCircle /> Profile Verified
                  </span>
                ) : (
                  <span className="indicator-badge pending">
                    <HiOutlineExclamationCircle /> Pending Overall Verification
                  </span>
                )}
                {profile.last_edited_at && (
                  <span className="field-meta-info">
                    Last Updated: {new Date(profile.last_edited_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
            <div className="review-header-actions">
              <button
                onClick={() => handleVerify(null)}
                disabled={verifying || saving}
                className="btn btn-outline-dark btn-sm"
              >
                {verifying ? 'Verifying...' : 'Verify Entire Profile'}
              </button>
              <button
                onClick={handleSave}
                disabled={saving || verifying}
                className="btn btn-primary btn-sm"
              >
                {saving ? 'Saving...' : 'Save All Changes'}
              </button>
            </div>
          </div>

          {/* Feedback banners */}
          {success && <div className="edit-success">{success}</div>}
          {error && (
            <div className="auth-error" style={{ marginBottom: 16, textAlign: 'left' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>⚠️ {error}</div>
              {Object.keys(fieldErrors).length > 0 && (
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.825rem', listStyleType: 'disc' }}>
                  {Object.entries(fieldErrors).map(([key, val]) => {
                    if (typeof val === 'string') {
                      return <li key={key}><strong>{key.replace('_', ' ')}</strong>: {val}</li>;
                    }
                    if (Array.isArray(val) && val.every(item => typeof item === 'string')) {
                      return <li key={key}><strong>{key.replace('_', ' ')}</strong>: {val.join(', ')}</li>;
                    }
                    if (Array.isArray(val)) {
                      // Nested arrays like experience/education errors
                      const subErrors = [];
                      val.forEach((item, idx) => {
                        if (item && typeof item === 'object') {
                          Object.entries(item).forEach(([subKey, subVal]) => {
                            subErrors.push(`Item #${idx + 1} (${subKey.replace('_', ' ')}): ${Array.isArray(subVal) ? subVal.join(', ') : subVal}`);
                          });
                        } else if (typeof item === 'string') {
                          subErrors.push(item);
                        }
                      });
                      if (subErrors.length > 0) {
                        return (
                          <li key={key}>
                            <strong>{key.replace('_', ' ')}</strong>:
                            <ul style={{ paddingLeft: '15px', listStyleType: 'circle' }}>
                              {subErrors.map((se, sIdx) => <li key={sIdx}>{se}</li>)}
                            </ul>
                          </li>
                        );
                      }
                    }
                    return null;
                  })}
                </ul>
              )}
            </div>
          )}

          {/* Tab Content Panels */}
          <div className="edit-section">
            {/* 1. PERSONAL INFORMATION */}
            {activeTab === 'personal' && (
              <div>
                <h3 className="edit-section-title">Personal Information</h3>
                <div className="edit-row">
                  <FieldRow label="First Name" name="first_name" source={formData.source_of_value?.first_name} error={fieldErrors.first_name || fieldErrors.user?.first_name}>
                    <input
                      className="edit-input"
                      value={formData.first_name || ''}
                      onChange={(e) => handleInputChange('first_name', e.target.value)}
                    />
                  </FieldRow>
                  <FieldRow label="Last Name" name="last_name" source={formData.source_of_value?.last_name} error={fieldErrors.last_name || fieldErrors.user?.last_name}>
                    <input
                      className="edit-input"
                      value={formData.last_name || ''}
                      onChange={(e) => handleInputChange('last_name', e.target.value)}
                    />
                  </FieldRow>
                </div>

                <div className="edit-row">
                  <FieldRow label="Email Address" name="email" source={formData.source_of_value?.email} error={fieldErrors.email || fieldErrors.user?.email}>
                    <input
                      className="edit-input"
                      type="email"
                      value={formData.email || ''}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                    />
                  </FieldRow>
                  <FieldRow label="Phone Number" name="phone" source={formData.source_of_value?.phone} error={fieldErrors.phone || fieldErrors.user?.phone}>
                    <input
                      className="edit-input"
                      value={formData.phone || ''}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                    />
                  </FieldRow>
                </div>

                <FieldRow label="Headline" name="headline" source={formData.source_of_value?.headline} error={fieldErrors.headline}>
                  <input
                    className="edit-input"
                    placeholder="e.g. Senior Software Engineer"
                    value={formData.headline || ''}
                    onChange={(e) => handleInputChange('headline', e.target.value)}
                  />
                </FieldRow>

                <div className="edit-row">
                  <FieldRow label="City" name="city" source={formData.source_of_value?.city} error={fieldErrors.city}>
                    <input className="edit-input" value={formData.city || ''} onChange={(e) => handleInputChange('city', e.target.value)} />
                  </FieldRow>
                  <FieldRow label="State" name="state" source={formData.source_of_value?.state} error={fieldErrors.state}>
                    <input className="edit-input" value={formData.state || ''} onChange={(e) => handleInputChange('state', e.target.value)} />
                  </FieldRow>
                </div>

                <div className="edit-row">
                  <FieldRow label="Country" name="country" source={formData.source_of_value?.country} error={fieldErrors.country}>
                    <input className="edit-input" value={formData.country || ''} onChange={(e) => handleInputChange('country', e.target.value)} />
                  </FieldRow>
                  <FieldRow label="Postal Code" name="postal_code" source={formData.source_of_value?.postal_code} error={fieldErrors.postal_code}>
                    <input className="edit-input" value={formData.postal_code || ''} onChange={(e) => handleInputChange('postal_code', e.target.value)} />
                  </FieldRow>
                </div>

                <FieldRow label="Address" name="address" source={formData.source_of_value?.address} error={fieldErrors.address}>
                  <input className="edit-input" value={formData.address || ''} onChange={(e) => handleInputChange('address', e.target.value)} />
                </FieldRow>

                <h4 className="edit-section-title" style={{ marginTop: 24 }}>Socials & Web Profiles</h4>
                <div className="edit-row">
                  <FieldRow label="LinkedIn Profile" name="linkedin" source={formData.source_of_value?.linkedin} error={fieldErrors.linkedin}>
                    <input className="edit-input" type="url" value={formData.linkedin || ''} onChange={(e) => handleInputChange('linkedin', e.target.value)} />
                  </FieldRow>
                  <FieldRow label="GitHub Profile" name="github" source={formData.source_of_value?.github} error={fieldErrors.github}>
                    <input className="edit-input" type="url" value={formData.github || ''} onChange={(e) => handleInputChange('github', e.target.value)} />
                  </FieldRow>
                </div>
                <div className="edit-row">
                  <FieldRow label="Personal Website" name="website" source={formData.source_of_value?.website} error={fieldErrors.website}>
                    <input className="edit-input" type="url" value={formData.website || ''} onChange={(e) => handleInputChange('website', e.target.value)} />
                  </FieldRow>
                  <FieldRow label="Portfolio URL" name="portfolio_url" source={formData.source_of_value?.portfolio_url} error={fieldErrors.portfolio_url}>
                    <input className="edit-input" type="url" value={formData.portfolio_url || ''} onChange={(e) => handleInputChange('portfolio_url', e.target.value)} />
                  </FieldRow>
                </div>
              </div>
            )}

            {/* 2. SUMMARY & SKILLS */}
            {activeTab === 'summary_skills' && (
              <div>
                <h3 className="edit-section-title">Professional Summary</h3>
                <FieldRow label="Bio Summary" name="summary" source={formData.source_of_value?.summary} error={fieldErrors.summary}>
                  <div className="rich-text-editor-panel">
                    <div className="editor-toolbar">
                      <button type="button" className="toolbar-btn" onClick={() => insertMarkup('**', '**')}>Bold</button>
                      <button type="button" className="toolbar-btn" onClick={() => insertMarkup('*', '*')}>Italic</button>
                      <button type="button" className="toolbar-btn" onClick={() => insertMarkup('### ')}>Heading</button>
                      <button type="button" className="toolbar-btn" onClick={() => insertMarkup('- ')}>Bullet List</button>
                    </div>
                    <textarea
                      ref={summaryRef}
                      className="edit-input edit-textarea"
                      rows={6}
                      value={formData.summary || ''}
                      onChange={(e) => handleInputChange('summary', e.target.value)}
                    />
                  </div>
                </FieldRow>

                <h3 className="edit-section-title" style={{ marginTop: 32 }}>Skills Editor</h3>
                {fieldErrors.skills && <div className="auth-error" style={{ marginBottom: 12 }}>{fieldErrors.skills}</div>}
                <div className="skill-tag-container">
                  {/* General Skills */}
                  <div className="skill-tag-group">
                    <div className="skill-group-title">General Skills</div>
                    <div className="skills-list-pills">
                      {(formData.skills || [])
                        .filter((s) => s.skill_type === 'general')
                        .map((s, index) => {
                          const originalIndex = formData.skills.indexOf(s);
                          return (
                            <span key={index} className="skill-pill">
                              {s.skill_name}
                              <button type="button" className="skill-pill-delete" onClick={() => handleDeleteSkill(originalIndex)}>
                                &times;
                              </button>
                            </span>
                          );
                        })}
                    </div>
                    <div className="skill-add-input-row">
                      <input
                        className="skill-add-input"
                        placeholder="Add general skill (e.g. Project Management)"
                        value={newGeneralSkill}
                        onChange={(e) => setNewGeneralSkill(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddSkill('general', newGeneralSkill, setNewGeneralSkill)}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-dark btn-sm"
                        onClick={() => handleAddSkill('general', newGeneralSkill, setNewGeneralSkill)}
                      >
                        Add
                      </button>
                    </div>
                  </div>

                  {/* Technical Skills */}
                  <div className="skill-tag-group">
                    <div className="skill-group-title">Technical Skills</div>
                    <div className="skills-list-pills">
                      {(formData.skills || [])
                        .filter((s) => s.skill_type === 'technical')
                        .map((s, index) => {
                          const originalIndex = formData.skills.indexOf(s);
                          return (
                            <span key={index} className="skill-pill">
                              {s.skill_name}
                              <button type="button" className="skill-pill-delete" onClick={() => handleDeleteSkill(originalIndex)}>
                                &times;
                              </button>
                            </span>
                          );
                        })}
                    </div>
                    <div className="skill-add-input-row">
                      <input
                        className="skill-add-input"
                        placeholder="Add technical skill (e.g. ReactJS, Docker)"
                        value={newTechSkill}
                        onChange={(e) => setNewTechSkill(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddSkill('technical', newTechSkill, setNewTechSkill)}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-dark btn-sm"
                        onClick={() => handleAddSkill('technical', newTechSkill, setNewTechSkill)}
                      >
                        Add
                      </button>
                    </div>
                  </div>

                  {/* Soft Skills */}
                  <div className="skill-tag-group">
                    <div className="skill-group-title">Soft Skills</div>
                    <div className="skills-list-pills">
                      {(formData.skills || [])
                        .filter((s) => s.skill_type === 'soft')
                        .map((s, index) => {
                          const originalIndex = formData.skills.indexOf(s);
                          return (
                            <span key={index} className="skill-pill">
                              {s.skill_name}
                              <button type="button" className="skill-pill-delete" onClick={() => handleDeleteSkill(originalIndex)}>
                                &times;
                              </button>
                            </span>
                          );
                        })}
                    </div>
                    <div className="skill-add-input-row">
                      <input
                        className="skill-add-input"
                        placeholder="Add soft skill (e.g. Communication, Teamwork)"
                        value={newSoftSkill}
                        onChange={(e) => setNewSoftSkill(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddSkill('soft', newSoftSkill, setNewSoftSkill)}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-dark btn-sm"
                        onClick={() => handleAddSkill('soft', newSoftSkill, setNewSoftSkill)}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 3. EXPERIENCE */}
            {activeTab === 'experience' && (
              <div>
                <h3 className="edit-section-title">Work Experience</h3>
                <div className="dynamic-form-list">
                  {(formData.experiences || []).map((exp, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Experience #{index + 1}</span>
                        <div className="item-ordering-buttons">
                          <button type="button" className="btn-order-move" onClick={() => handleMoveArrayItem('experiences', index, 'up')}>
                            <HiOutlineArrowUp />
                          </button>
                          <button type="button" className="btn-order-move" onClick={() => handleMoveArrayItem('experiences', index, 'down')}>
                            <HiOutlineArrowDown />
                          </button>
                          <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('experiences', index)}>
                            <HiOutlineTrash /> Remove
                          </button>
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Company Name</label>
                          <input
                            className="edit-input"
                            value={exp.company || ''}
                            onChange={(e) => handleUpdateArrayItem('experiences', index, 'company', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Job Title / Designation</label>
                          <input
                            className="edit-input"
                            value={exp.designation || ''}
                            onChange={(e) => handleUpdateArrayItem('experiences', index, 'designation', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Employment Type</label>
                          <select
                            className="edit-input"
                            style={{ background: '#1e293b' }}
                            value={exp.employment_type || 'full_time'}
                            onChange={(e) => handleUpdateArrayItem('experiences', index, 'employment_type', e.target.value)}
                          >
                            <option value="full_time">Full-Time</option>
                            <option value="part_time">Part-Time</option>
                            <option value="internship">Internship</option>
                            <option value="freelance">Freelance</option>
                            <option value="contract">Contract</option>
                          </select>
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Start Date</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={exp.start_date || ''}
                            onChange={(e) => handleUpdateArrayItem('experiences', index, 'start_date', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">End Date (Leave blank if current)</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={exp.end_date || ''}
                            onChange={(e) => handleUpdateArrayItem('experiences', index, 'end_date', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-field">
                        <label className="edit-label">Description / Achievements</label>
                        <textarea
                          className="edit-input edit-textarea"
                          rows={4}
                          value={exp.description || ''}
                          onChange={(e) => handleUpdateArrayItem('experiences', index, 'description', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('experiences', { company: '', designation: '', employment_type: 'full_time', start_date: '', end_date: '', description: '' })}
                >
                  <HiOutlinePlus /> Add New Experience
                </button>
              </div>
            )}

            {/* 4. EDUCATION */}
            {activeTab === 'education' && (
              <div>
                <h3 className="edit-section-title">Education Records</h3>
                <div className="dynamic-form-list">
                  {(formData.educations || []).map((edu, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Education #{index + 1}</span>
                        <div className="item-ordering-buttons">
                          <button type="button" className="btn-order-move" onClick={() => handleMoveArrayItem('educations', index, 'up')}>
                            <HiOutlineArrowUp />
                          </button>
                          <button type="button" className="btn-order-move" onClick={() => handleMoveArrayItem('educations', index, 'down')}>
                            <HiOutlineArrowDown />
                          </button>
                          <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('educations', index)}>
                            <HiOutlineTrash /> Remove
                          </button>
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Institution / University</label>
                          <input
                            className="edit-input"
                            value={edu.institute || ''}
                            onChange={(e) => handleUpdateArrayItem('educations', index, 'institute', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Degree</label>
                          <input
                            className="edit-input"
                            placeholder="e.g. Bachelor of Science"
                            value={edu.degree || ''}
                            onChange={(e) => handleUpdateArrayItem('educations', index, 'degree', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Field of Study</label>
                          <input
                            className="edit-input"
                            placeholder="e.g. Computer Science"
                            value={edu.field_of_study || ''}
                            onChange={(e) => handleUpdateArrayItem('educations', index, 'field_of_study', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Grade / CGPA</label>
                          <input
                            className="edit-input"
                            placeholder="e.g. 3.8/4.0 or 9.2 CGPA"
                            value={edu.grade || ''}
                            onChange={(e) => handleUpdateArrayItem('educations', index, 'grade', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Start Date</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={edu.start_date || ''}
                            onChange={(e) => handleUpdateArrayItem('educations', index, 'start_date', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">End Date (Leave blank if ongoing)</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={edu.end_date || ''}
                            onChange={(e) => handleUpdateArrayItem('educations', index, 'end_date', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('educations', { institute: '', degree: '', field_of_study: '', start_date: '', end_date: '', grade: '' })}
                >
                  <HiOutlinePlus /> Add New Education Record
                </button>
              </div>
            )}

            {/* 5. PROJECTS */}
            {activeTab === 'projects' && (
              <div>
                <h3 className="edit-section-title">Projects</h3>
                {fieldErrors.projects && <div className="auth-error" style={{ marginBottom: 12 }}>{fieldErrors.projects}</div>}
                <div className="dynamic-form-list">
                  {(formData.projects || []).map((proj, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Project #{index + 1}</span>
                        <div className="item-ordering-buttons">
                          <button type="button" className="btn-order-move" onClick={() => handleMoveArrayItem('projects', index, 'up')}>
                            <HiOutlineArrowUp />
                          </button>
                          <button type="button" className="btn-order-move" onClick={() => handleMoveArrayItem('projects', index, 'down')}>
                            <HiOutlineArrowDown />
                          </button>
                          <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('projects', index)}>
                            <HiOutlineTrash /> Remove
                          </button>
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Project Name</label>
                          <input
                            className="edit-input"
                            value={proj.project_name || ''}
                            onChange={(e) => handleUpdateArrayItem('projects', index, 'project_name', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Technologies Used (Comma-separated)</label>
                          <input
                            className="edit-input"
                            placeholder="React, Django, PostgreSQL"
                            value={proj.technologies || ''}
                            onChange={(e) => handleUpdateArrayItem('projects', index, 'technologies', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">GitHub URL</label>
                          <input
                            className="edit-input"
                            type="url"
                            value={proj.github_url || ''}
                            onChange={(e) => handleUpdateArrayItem('projects', index, 'github_url', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Live Demo URL</label>
                          <input
                            className="edit-input"
                            type="url"
                            value={proj.live_url || ''}
                            onChange={(e) => handleUpdateArrayItem('projects', index, 'live_url', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-field">
                        <label className="edit-label">Description</label>
                        <textarea
                          className="edit-input edit-textarea"
                          rows={4}
                          value={proj.description || ''}
                          onChange={(e) => handleUpdateArrayItem('projects', index, 'description', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('projects', { project_name: '', technologies: '', description: '', github_url: '', live_url: '' })}
                >
                  <HiOutlinePlus /> Add New Project
                </button>
              </div>
            )}

            {/* 6. CERTS & LANGUAGES */}
            {activeTab === 'certs_langs' && (
              <div>
                <h3 className="edit-section-title">Certifications</h3>
                <div className="dynamic-form-list" style={{ marginBottom: 36 }}>
                  {(formData.certifications || []).map((cert, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Certificate #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('certifications', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Certificate Name</label>
                          <input
                            className="edit-input"
                            value={cert.certificate_name || ''}
                            onChange={(e) => handleUpdateArrayItem('certifications', index, 'certificate_name', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Issuing Organization</label>
                          <input
                            className="edit-input"
                            value={cert.organization || ''}
                            onChange={(e) => handleUpdateArrayItem('certifications', index, 'organization', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Issue Date</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={cert.issue_date || ''}
                            onChange={(e) => handleUpdateArrayItem('certifications', index, 'issue_date', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Credential URL</label>
                          <input
                            className="edit-input"
                            type="url"
                            value={cert.credential_url || ''}
                            onChange={(e) => handleUpdateArrayItem('certifications', index, 'credential_url', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('certifications', { certificate_name: '', organization: '', issue_date: '', credential_url: '' })}
                >
                  <HiOutlinePlus /> Add Certification
                </button>

                <h3 className="edit-section-title" style={{ marginTop: 40 }}>Languages</h3>
                <div className="dynamic-form-list">
                  {(formData.languages || []).map((lang, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Language #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('languages', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>

                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Language Name</label>
                          <input
                            className="edit-input"
                            value={lang.language_name || ''}
                            onChange={(e) => handleUpdateArrayItem('languages', index, 'language_name', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Proficiency</label>
                          <select
                            className="edit-input"
                            style={{ background: '#1e293b' }}
                            value={lang.proficiency || 'professional'}
                            onChange={(e) => handleUpdateArrayItem('languages', index, 'proficiency', e.target.value)}
                          >
                            <option value="elementary">Elementary</option>
                            <option value="limited_working">Limited Working</option>
                            <option value="professional">Professional Working</option>
                            <option value="full_professional">Full Professional</option>
                            <option value="native">Native / Bilingual</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('languages', { language_name: '', proficiency: 'professional' })}
                >
                  <HiOutlinePlus /> Add Language
                </button>
              </div>
            )}

            {/* 7. HONORS, VOLUNTEER & HOBBIES */}
            {activeTab === 'honors_vol' && (
              <div>
                <h3 className="edit-section-title">Achievements</h3>
                <div className="dynamic-form-list" style={{ marginBottom: 30 }}>
                  {(formData.achievements || []).map((ach, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Achievement #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('achievements', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>
                      <div className="edit-field">
                        <label className="edit-label">Description</label>
                        <input
                          className="edit-input"
                          value={ach.description || ''}
                          onChange={(e) => handleUpdateArrayItem('achievements', index, 'description', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('achievements', { description: '' })}
                >
                  <HiOutlinePlus /> Add Achievement
                </button>

                <h3 className="edit-section-title" style={{ marginTop: 40 }}>Awards</h3>
                <div className="dynamic-form-list" style={{ marginBottom: 30 }}>
                  {(formData.awards || []).map((awd, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Award #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('awards', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>
                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Award Title</label>
                          <input
                            className="edit-input"
                            value={awd.title || ''}
                            onChange={(e) => handleUpdateArrayItem('awards', index, 'title', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Issuer</label>
                          <input
                            className="edit-input"
                            value={awd.issuer || ''}
                            onChange={(e) => handleUpdateArrayItem('awards', index, 'issuer', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="edit-field">
                        <label className="edit-label">Date Awarded</label>
                        <input
                          className="edit-input"
                          type="date"
                          value={awd.date_awarded || ''}
                          onChange={(e) => handleUpdateArrayItem('awards', index, 'date_awarded', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('awards', { title: '', issuer: '', date_awarded: '' })}
                >
                  <HiOutlinePlus /> Add Award
                </button>

                <h3 className="edit-section-title" style={{ marginTop: 40 }}>Volunteer Work</h3>
                <div className="dynamic-form-list" style={{ marginBottom: 30 }}>
                  {(formData.volunteer_work || []).map((vol, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Volunteer Record #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('volunteer_work', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>
                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Organization</label>
                          <input
                            className="edit-input"
                            value={vol.organization || ''}
                            onChange={(e) => handleUpdateArrayItem('volunteer_work', index, 'organization', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Role</label>
                          <input
                            className="edit-input"
                            value={vol.role || ''}
                            onChange={(e) => handleUpdateArrayItem('volunteer_work', index, 'role', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Start Date</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={vol.start_date || ''}
                            onChange={(e) => handleUpdateArrayItem('volunteer_work', index, 'start_date', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">End Date</label>
                          <input
                            className="edit-input"
                            type="date"
                            value={vol.end_date || ''}
                            onChange={(e) => handleUpdateArrayItem('volunteer_work', index, 'end_date', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="edit-field">
                        <label className="edit-label">Description</label>
                        <textarea
                          className="edit-input edit-textarea"
                          rows={3}
                          value={vol.description || ''}
                          onChange={(e) => handleUpdateArrayItem('volunteer_work', index, 'description', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('volunteer_work', { organization: '', role: '', start_date: '', end_date: '', description: '' })}
                >
                  <HiOutlinePlus /> Add Volunteer Record
                </button>

                <h3 className="edit-section-title" style={{ marginTop: 40 }}>Hobbies</h3>
                <div className="dynamic-form-list">
                  {(formData.hobbies || []).map((hob, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Hobby #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('hobbies', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>
                      <div className="edit-field">
                        <label className="edit-label">Hobby Name</label>
                        <input
                          className="edit-input"
                          value={hob.hobby_name || ''}
                          onChange={(e) => handleUpdateArrayItem('hobbies', index, 'hobby_name', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('hobbies', { hobby_name: '' })}
                >
                  <HiOutlinePlus /> Add Hobby
                </button>
              </div>
            )}

            {/* 8. REFERENCES */}
            {activeTab === 'references' && (
              <div>
                <h3 className="edit-section-title">References</h3>
                <div className="dynamic-form-list">
                  {(formData.references || []).map((ref, index) => (
                    <div key={index} className="dynamic-form-item">
                      <div className="item-index-header">
                        <span className="item-index-label">Reference #{index + 1}</span>
                        <button type="button" className="btn-item-delete" onClick={() => handleDeleteArrayItem('references', index)}>
                          <HiOutlineTrash /> Remove
                        </button>
                      </div>
                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Name</label>
                          <input
                            className="edit-input"
                            value={ref.name || ''}
                            onChange={(e) => handleUpdateArrayItem('references', index, 'name', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Relationship</label>
                          <input
                            className="edit-input"
                            value={ref.relationship || ''}
                            onChange={(e) => handleUpdateArrayItem('references', index, 'relationship', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="edit-row">
                        <div className="edit-field">
                          <label className="edit-label">Company / Organization</label>
                          <input
                            className="edit-input"
                            value={ref.company || ''}
                            onChange={(e) => handleUpdateArrayItem('references', index, 'company', e.target.value)}
                          />
                        </div>
                        <div className="edit-field">
                          <label className="edit-label">Contact (Email or Phone)</label>
                          <input
                            className="edit-input"
                            value={ref.contact || ''}
                            onChange={(e) => handleUpdateArrayItem('references', index, 'contact', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  className="btn-add-item"
                  onClick={() => handleAddArrayItem('references', { name: '', relationship: '', company: '', contact: '' })}
                >
                  <HiOutlinePlus /> Add Reference
                </button>
              </div>
            )}

            {/* 9. AUDIT LOG & HISTORY */}
            {activeTab === 'history' && (
              <div>
                <h3 className="edit-section-title">Profile Modification Audit Trail</h3>
                <p style={{ color: 'var(--gray-400)', fontSize: '0.875rem', marginBottom: 16 }}>
                  Below is a detailed log of all modifications made to this master profile, including original vs new values and their source.
                </p>
                <div className="audit-table-wrapper">
                  <table className="audit-table">
                    <thead>
                      <tr>
                        <th>Date & Time</th>
                        <th>Section</th>
                        <th>Field Name</th>
                        <th>Old Value</th>
                        <th>New Value</th>
                        <th>Source</th>
                        <th>Edited By</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(profile.edit_history || []).length === 0 ? (
                        <tr>
                          <td colSpan="7" style={{ textAlign: 'center', color: 'var(--gray-500)', padding: 20 }}>
                            No modifications logged yet.
                          </td>
                        </tr>
                      ) : (
                        profile.edit_history.map((log) => (
                          <tr key={log.id}>
                            <td>{new Date(log.created_at).toLocaleString()}</td>
                            <td style={{ fontWeight: 600 }}>{log.section}</td>
                            <td>{log.field_name}</td>
                            <td style={{ color: '#fca5a5', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {log.old_value || 'None'}
                            </td>
                            <td style={{ color: '#86efac', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {log.new_value || 'None'}
                            </td>
                            <td>
                              <span className={`indicator-badge ${log.source.toLowerCase()}`}>{log.source}</span>
                            </td>
                            <td>{log.edited_by_username || 'System'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Quick save banner at the bottom */}
          <div className="edit-section" style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, padding: 16 }}>
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn btn-outline-dark"
            >
              Back to Dashboard
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="btn btn-primary"
            >
              {saving ? 'Saving...' : 'Save All Changes'}
            </button>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ProfileReview;

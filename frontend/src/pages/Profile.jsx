/**
 * Profile Page – Read-only user profile view.
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HiOutlinePencilSquare,
  HiOutlineEnvelope,
  HiOutlinePhone,
  HiOutlineMapPin,
  HiOutlineGlobeAlt,
  HiOutlineLink,
  HiOutlineBriefcase,
  HiOutlineAcademicCap,
  HiOutlineSquare3Stack3D,
  HiOutlineLanguage,
  HiOutlineStar,
  HiOutlineHeart,
  HiOutlineBookmark,
  HiOutlineBookOpen,
} from 'react-icons/hi2'; // We can safely import from react-icons/hi2
import { profilesAPI } from '../api/profiles';
import { handleOpenResumeBuilder } from '../utils/resumeBuilder';
import '../styles/Profile.css';

// Safe icon import helper to avoid library resolved issues
import * as HiIcons from 'react-icons/hi2';

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [builderLoading, setBuilderLoading] = useState(false);

  const getIcon = (name, fallback) => {
    const IconComponent = HiIcons[name];
    return IconComponent ? <IconComponent /> : fallback;
  };

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const res = await profilesAPI.getMasterProfile();
        setProfile(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load profile details.');
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container" style={{ textAlign: 'center', paddingTop: 100 }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading Profile...</span>
          </div>
          <p style={{ marginTop: 16, color: 'var(--gray-300)' }}>Loading your profile from the database...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <div className="auth-error">{error || 'No profile data found.'}</div>
          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Link to="/profile/review" className="btn btn-primary">
              Initialize Profile
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Location string helper
  const locationString = [profile.address, profile.city, profile.state, profile.country]
    .filter(Boolean)
    .join(', ');

  return (
    <div className="profile-page">
      <div className="profile-container" style={{ maxWidth: '1100px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header Card */}
          <div className="profile-card" style={{ padding: '32px', marginBottom: '32px', border: '1px solid rgba(34, 211, 238, 0.15)' }}>
            <div className="profile-header" style={{ marginBottom: 0, gap: '32px' }}>
              <div className="profile-avatar" style={{ width: '100px', height: '100px', fontSize: '2rem' }}>
                <span>{profile.first_name?.[0]}{profile.last_name?.[0]}</span>
              </div>
              <div className="profile-header-info">
                <h1 className="profile-name" style={{ fontSize: '2rem' }}>
                  {profile.first_name} {profile.last_name}
                </h1>
                <p className="profile-headline" style={{ fontSize: '1.05rem', color: 'var(--primary-light)' }}>
                  {profile.headline || 'Resume Professional'}
                </p>
                
                {/* Meta details */}
                <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginTop: '16px', fontSize: '0.875rem', color: 'var(--gray-400)' }}>
                  {profile.email && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      {getIcon('HiOutlineEnvelope', '📧')} {profile.email}
                    </span>
                  )}
                  {profile.phone && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      {getIcon('HiOutlinePhone', '📞')} {profile.phone}
                    </span>
                  )}
                  {locationString && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      {getIcon('HiOutlineMapPin', '📍')} {locationString}
                    </span>
                  )}
                </div>

                {/* Social Links */}
                <div style={{ display: 'flex', gap: '16px', marginTop: '16px', flexWrap: 'wrap' }}>
                  {profile.linkedin && (
                    <a href={profile.linkedin} target="_blank" rel="noopener noreferrer" className="profile-info-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                      {getIcon('HiOutlineLink', '🔗')} LinkedIn
                    </a>
                  )}
                  {profile.github && (
                    <a href={profile.github} target="_blank" rel="noopener noreferrer" className="profile-info-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                      {getIcon('HiOutlineLink', '🔗')} GitHub
                    </a>
                  )}
                  {profile.website && (
                    <a href={profile.website} target="_blank" rel="noopener noreferrer" className="profile-info-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                      {getIcon('HiOutlineGlobeAlt', '🌐')} Website
                    </a>
                  )}
                  {profile.portfolio_url && (
                    <a href={profile.portfolio_url} target="_blank" rel="noopener noreferrer" className="profile-info-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                      {getIcon('HiOutlineGlobeAlt', '🌐')} Portfolio
                    </a>
                  )}
                </div>
              </div>

              {/* Edit Profile Action */}
              <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <Link to="/profile/review" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                  {getIcon('HiOutlinePencilSquare', '📝')} Edit & Verify Profile
                </Link>
                <button
                  onClick={() => handleOpenResumeBuilder(navigate, setBuilderLoading)}
                  className="btn btn-primary"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
                    border: 'none'
                  }}
                  disabled={builderLoading}
                >
                  {getIcon('HiOutlineSparkles', '✨')} {builderLoading ? 'Opening...' : 'Open Resume Builder'}
                </button>
              </div>
            </div>
          </div>

          {/* Two Column Layout */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }} className="profile-columns-grid">
            
            {/* Left Column (Main content) */}
            <div>
              {/* Summary */}
              {profile.summary && (
                <div className="profile-card">
                  <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineBookmark', '📝')} Executive Summary
                  </h3>
                  <p className="profile-card-text" style={{ whiteSpace: 'pre-wrap' }}>{profile.summary}</p>
                </div>
              )}

              {/* Experience */}
              {profile.experiences && profile.experiences.length > 0 && (
                <div className="profile-card">
                  <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineBriefcase', '💼')} Work Experience
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '16px' }}>
                    {profile.experiences.map((exp, index) => (
                      <div key={index} style={{ borderBottom: index < profile.experiences.length - 1 ? '1px solid rgba(255, 255, 255, 0.05)' : 'none', paddingBottom: index < profile.experiences.length - 1 ? '20px' : '0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                          <h4 style={{ margin: 0, color: 'var(--white)', fontSize: '1.05rem', fontWeight: 700 }}>
                            {exp.designation} <span style={{ color: 'var(--primary-light)', fontWeight: 400 }}>at {exp.company}</span>
                          </h4>
                          <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>
                            {exp.start_date} &ndash; {exp.end_date || 'Present'}
                          </span>
                        </div>
                        {exp.employment_type && (
                          <span style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--gray-300)', padding: '2px 8px', borderRadius: '4px', display: 'inline-block', marginTop: '6px', textTransform: 'capitalize' }}>
                            {exp.employment_type.replace('_', ' ')}
                          </span>
                        )}
                        {exp.description && (
                          <p style={{ fontSize: '0.875rem', color: 'var(--gray-300)', marginTop: '12px', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                            {exp.description}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {profile.educations && profile.educations.length > 0 && (
                <div className="profile-card">
                  <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineAcademicCap', '🎓')} Education
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '16px' }}>
                    {profile.educations.map((edu, index) => (
                      <div key={index} style={{ borderBottom: index < profile.educations.length - 1 ? '1px solid rgba(255, 255, 255, 0.05)' : 'none', paddingBottom: index < profile.educations.length - 1 ? '20px' : '0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                          <h4 style={{ margin: 0, color: 'var(--white)', fontSize: '1.05rem', fontWeight: 700 }}>
                            {edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}
                          </h4>
                          <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>
                            {edu.start_date} &ndash; {edu.end_date || 'Ongoing'}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.875rem', color: 'var(--primary-light)', marginTop: '4px', marginBottom: '4px' }}>
                          {edu.institute}
                        </p>
                        {edu.grade && (
                          <span style={{ fontSize: '0.78rem', color: 'var(--gray-400)' }}>
                            Grade: <strong>{edu.grade}</strong>
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects */}
              {profile.projects && profile.projects.length > 0 && (
                <div className="profile-card">
                  <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineSquare3Stack3D', '📂')} Projects
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '16px' }}>
                    {profile.projects.map((proj, index) => (
                      <div key={index} style={{ borderBottom: index < profile.projects.length - 1 ? '1px solid rgba(255, 255, 255, 0.05)' : 'none', paddingBottom: index < profile.projects.length - 1 ? '20px' : '0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                          <h4 style={{ margin: 0, color: 'var(--white)', fontSize: '1.05rem', fontWeight: 700 }}>
                            {proj.project_name}
                          </h4>
                          {proj.github_url && (
                            <a href={proj.github_url} target="_blank" rel="noopener noreferrer" className="profile-info-link" style={{ fontSize: '0.8rem' }}>
                              {getIcon('HiOutlineLink', '🔗')} Repository
                            </a>
                          )}
                        </div>
                        {proj.technologies && (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
                            {proj.technologies.split(',').map((tech, tIdx) => (
                              <span key={tIdx} style={{ fontSize: '0.72rem', background: 'rgba(34, 211, 238, 0.08)', border: '1px solid rgba(34, 211, 238, 0.2)', color: 'var(--primary-light)', padding: '2px 8px', borderRadius: '4px' }}>
                                {tech.trim()}
                              </span>
                            ))}
                          </div>
                        )}
                        {proj.description && (
                          <p style={{ fontSize: '0.875rem', color: 'var(--gray-300)', marginTop: '12px', lineHeight: '1.6' }}>
                            {proj.description}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column (Sidebar metrics & meta) */}
            <div>
              {/* Skills */}
              {profile.skills && profile.skills.length > 0 && (
                <div className="profile-card" style={{ padding: '24px' }}>
                  <h3 className="profile-card-title" style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineStar', '⭐')} Skills
                  </h3>
                  
                  {/* Technical */}
                  {profile.skills.some(s => s.skill_type === 'technical') && (
                    <div style={{ marginTop: '16px' }}>
                      <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--gray-400)', fontWeight: 600, letterSpacing: '0.05em' }}>Technical</span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
                        {profile.skills.filter(s => s.skill_type === 'technical').map((s, idx) => (
                          <span key={idx} style={{ fontSize: '0.75rem', background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.2)', color: '#C084FC', padding: '3px 8px', borderRadius: '4px' }}>
                            {s.skill_name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Soft */}
                  {profile.skills.some(s => s.skill_type === 'soft') && (
                    <div style={{ marginTop: '20px' }}>
                      <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--gray-400)', fontWeight: 600, letterSpacing: '0.05em' }}>Soft Skills</span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
                        {profile.skills.filter(s => s.skill_type === 'soft').map((s, idx) => (
                          <span key={idx} style={{ fontSize: '0.75rem', background: 'rgba(34, 211, 238, 0.1)', border: '1px solid rgba(34, 211, 238, 0.2)', color: 'var(--primary-light)', padding: '3px 8px', borderRadius: '4px' }}>
                            {s.skill_name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* General */}
                  {profile.skills.some(s => s.skill_type === 'general' || !s.skill_type) && (
                    <div style={{ marginTop: '20px' }}>
                      <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--gray-400)', fontWeight: 600, letterSpacing: '0.05em' }}>General</span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
                        {profile.skills.filter(s => s.skill_type === 'general' || !s.skill_type).map((s, idx) => (
                          <span key={idx} style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--gray-300)', padding: '3px 8px', borderRadius: '4px' }}>
                            {s.skill_name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Languages */}
              {profile.languages && profile.languages.length > 0 && (
                <div className="profile-card" style={{ padding: '24px' }}>
                  <h3 className="profile-card-title" style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineLanguage', '🌐')} Languages
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                    {profile.languages.map((lang, idx) => (
                      <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span style={{ color: 'var(--white)', fontWeight: 500 }}>{lang.language_name}</span>
                        <span style={{ color: 'var(--gray-400)', textTransform: 'capitalize' }}>{lang.proficiency || 'General'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications */}
              {profile.certifications && profile.certifications.length > 0 && (
                <div className="profile-card" style={{ padding: '24px' }}>
                  <h3 className="profile-card-title" style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineBookOpen', '📜')} Certifications
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '12px' }}>
                    {profile.certifications.map((cert, idx) => (
                      <div key={idx}>
                        <h4 style={{ margin: 0, fontSize: '0.85rem', color: 'var(--white)', fontWeight: 600 }}>{cert.certificate_name}</h4>
                        <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--gray-400)' }}>
                          {cert.organization} {cert.issue_date ? `| ${cert.issue_date}` : ''}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Honors & Awards */}
              {profile.awards && profile.awards.length > 0 && (
                <div className="profile-card" style={{ padding: '24px' }}>
                  <h3 className="profile-card-title" style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineStar', '🏆')} Awards & Honors
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '12px' }}>
                    {profile.awards.map((award, idx) => (
                      <div key={idx}>
                        <h4 style={{ margin: 0, fontSize: '0.85rem', color: 'var(--white)', fontWeight: 600 }}>{award.title}</h4>
                        <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--gray-400)' }}>
                          Issued by {award.issuer} {award.date_awarded ? `(${award.date_awarded})` : ''}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Volunteer Work */}
              {profile.volunteer_work && profile.volunteer_work.length > 0 && (
                <div className="profile-card" style={{ padding: '24px' }}>
                  <h3 className="profile-card-title" style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getIcon('HiOutlineHeart', '🤝')} Volunteer Work
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '12px' }}>
                    {profile.volunteer_work.map((vol, idx) => (
                      <div key={idx}>
                        <h4 style={{ margin: 0, fontSize: '0.85rem', color: 'var(--white)', fontWeight: 600 }}>
                          {vol.role} <span style={{ fontWeight: 400, color: 'var(--gray-400)' }}>at {vol.organization}</span>
                        </h4>
                        <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--gray-400)' }}>
                          {vol.start_date} &ndash; {vol.end_date || 'Present'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Profile;

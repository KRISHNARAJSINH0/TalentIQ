import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  HiOutlineEnvelope, 
  HiOutlinePhone, 
  HiOutlineMapPin, 
  HiOutlineGlobeAlt, 
  HiOutlineLink,
  HiOutlineBriefcase,
  HiOutlineAcademicCap,
  HiOutlineCalendar,
  HiOutlineArrowDownTray,
  HiOutlineShare,
  HiOutlineSparkles
} from 'react-icons/hi2';
import { portfolioAPI } from '../api/portfolio';
// Dynamically inject styles for the 11 themes
const THEME_STYLES = {
  modern: {
    bg: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
    textColor: '#f8fafc',
    cardBg: 'rgba(30, 41, 59, 0.7)',
    borderColor: 'rgba(99, 102, 241, 0.2)',
    accent: '#6366f1',
    font: "'Inter', sans-serif",
  },
  minimal: {
    bg: '#fcfcfc',
    textColor: '#171717',
    cardBg: '#ffffff',
    borderColor: '#e5e5e5',
    accent: '#000000',
    font: "'Inter', sans-serif",
  },
  developer: {
    bg: '#050505',
    textColor: '#38bdf8',
    cardBg: '#0e1726',
    borderColor: '#0284c7',
    accent: '#0ea5e9',
    font: "'Courier New', Courier, monospace",
  },
  corporate: {
    bg: '#f1f5f9',
    textColor: '#1e293b',
    cardBg: '#ffffff',
    borderColor: '#cbd5e1',
    accent: '#0f172a',
    font: "'Outfit', sans-serif",
  },
  creative: {
    bg: 'linear-gradient(135deg, #fdf2f8 0%, #f5e1fd 100%)',
    textColor: '#3b0764',
    cardBg: '#ffffff',
    borderColor: '#f472b6',
    accent: '#ec4899',
    font: "'Poppins', sans-serif",
  },
  dark: {
    bg: '#121212',
    textColor: '#e0e0e0',
    cardBg: '#1e1e1e',
    borderColor: '#333333',
    accent: '#a78bfa',
    font: "'Outfit', sans-serif",
  },
  light: {
    bg: '#f8fafc',
    textColor: '#0f172a',
    cardBg: '#ffffff',
    borderColor: '#e2e8f0',
    accent: '#2563eb',
    font: "'Inter', sans-serif",
  },
  glassmorphism: {
    bg: 'linear-gradient(135deg, #020617 0%, #1e1b4b 50%, #030712 100%)',
    textColor: '#f1f5f9',
    cardBg: 'rgba(255, 255, 255, 0.03)',
    borderColor: 'rgba(255, 255, 255, 0.08)',
    accent: '#38bdf8',
    font: "'Inter', sans-serif",
    backdropFilter: 'blur(12px)',
  },
  professional: {
    bg: '#ffffff',
    textColor: '#334155',
    cardBg: '#f8fafc',
    borderColor: '#cbd5e1',
    accent: '#0f172a',
    font: "'Merriweather', serif",
  },
  student: {
    bg: 'linear-gradient(135deg, #ecfeff 0%, #e0f2fe 100%)',
    textColor: '#0f172a',
    cardBg: '#ffffff',
    borderColor: '#bae6fd',
    accent: '#0284c7',
    font: "'Inter', sans-serif",
  },
  researcher: {
    bg: '#fafafa',
    textColor: '#27272a',
    cardBg: '#ffffff',
    borderColor: '#e4e4e7',
    accent: '#18181b',
    font: "'Times New Roman', Times, serif",
  }
};

const PortfolioPublic = () => {
  const { slug } = useParams();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Section refs for tracking views
  const sectionRefs = {
    hero: useRef(null),
    about: useRef(null),
    skills: useRef(null),
    experience: useRef(null),
    projects: useRef(null),
    education: useRef(null),
    certifications: useRef(null),
  };

  useEffect(() => {
    const fetchPublicPortfolio = async () => {
      try {
        setLoading(true);
        const res = await portfolioAPI.getPublicPortfolio(slug);
        setPortfolio(res.data);
      } catch (err) {
        console.error(err);
        setError('Portfolio not found or set to private.');
      } finally {
        setLoading(false);
      }
    };
    if (slug) {
      fetchPublicPortfolio();
    }
  }, [slug]);

  // Setup intersection observer to log section view analytics
  useEffect(() => {
    if (!portfolio) return;
    
    const loggedSections = new Set();
    const observerOptions = {
      root: null,
      threshold: 0.3, // log when 30% of the section is visible
    };

    const observerCallback = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const sectionId = entry.target.id;
          if (!loggedSections.has(sectionId)) {
            loggedSections.add(sectionId);
            // Log section view to backend
            portfolioAPI.logActivity({
              slug: portfolio.slug,
              event_type: 'section_view',
              section_name: sectionId,
            }).catch(err => console.error('Failed to log section view:', err));
          }
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);
    Object.values(sectionRefs).forEach((ref) => {
      if (ref.current) observer.observe(ref.current);
    });

    return () => {
      Object.values(sectionRefs).forEach((ref) => {
        if (ref.current) observer.unobserve(ref.current);
      });
    };
  }, [portfolio]);

  const handleDownloadLog = async () => {
    if (!portfolio) return;
    try {
      await portfolioAPI.logActivity({
        slug: portfolio.slug,
        event_type: 'download',
      });
      // Handle the download action
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(portfolio.portfolio_json, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `${portfolio.slug}_verified_resume.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (err) {
      console.error(err);
    }
  };

  const handleShareLog = async () => {
    if (!portfolio) return;
    try {
      await portfolioAPI.logActivity({
        slug: portfolio.slug,
        event_type: 'share',
      });
      await navigator.clipboard.writeText(window.location.href);
      alert('Portfolio URL copied to clipboard!');
    } catch (err) {
      console.error(err);
    }
  };

  const data = portfolio?.portfolio_json || {};

  // Inject SEO metadata dynamically using DOM APIs to avoid external library dependencies
  useEffect(() => {
    if (!portfolio || !data) return;

    // Set Document Title
    const fullName = `${data.first_name || ''} ${data.last_name || ''}`.trim();
    document.title = fullName ? `${fullName} - Professional Portfolio` : 'Professional Portfolio';

    // Set Meta Tags
    const updateMetaTag = (name, value, isProperty = false) => {
      let element = isProperty 
        ? document.querySelector(`meta[property="${name}"]`)
        : document.querySelector(`meta[name="${name}"]`);
      if (!element) {
        element = document.createElement('meta');
        if (isProperty) element.setAttribute('property', name);
        else element.setAttribute('name', name);
        document.head.appendChild(element);
      }
      element.setAttribute('content', value);
    };

    updateMetaTag('description', data.summary || `${fullName || 'Candidate'}'s professional experience and project portfolio.`);
    updateMetaTag('keywords', `${data.first_name || ''}, portfolio, resume, projects, career`);
    updateMetaTag('og:title', fullName ? `${fullName} - Portfolio` : 'Portfolio', true);
    updateMetaTag('og:description', data.summary || 'Professional Experience Portfolio.', true);
    updateMetaTag('og:type', 'profile', true);
    updateMetaTag('og:url', window.location.href, true);

    // Set Canonical URL Link
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', window.location.href);

    // Structured Data JSON-LD
    const jsonLdSchema = {
      "@context": "https://schema.org",
      "@type": "Person",
      "name": fullName,
      "jobTitle": data.headline || '',
      "email": data.email || '',
      "description": data.summary || '',
      "address": {
        "@type": "PostalAddress",
        "addressLocality": data.city || '',
        "addressRegion": data.state || '',
        "addressCountry": data.country || ''
      },
      "sameAs": [
        data.linkedin || '',
        data.github || '',
        data.website || ''
      ].filter(Boolean)
    };

    let scriptElement = document.getElementById('jsonLdPortfolioSchema');
    if (!scriptElement) {
      scriptElement = document.createElement('script');
      scriptElement.id = 'jsonLdPortfolioSchema';
      scriptElement.type = 'application/ld+json';
      document.head.appendChild(scriptElement);
    }
    scriptElement.textContent = JSON.stringify(jsonLdSchema);

    return () => {
      // Clean up JSON-LD on unmount
      const script = document.getElementById('jsonLdPortfolioSchema');
      if (script) script.remove();
    };
  }, [portfolio, data]);

  if (loading) {
    return (
      <div style={{ background: '#0f172a', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#fff' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spinner-border text-primary" role="status"></div>
          <p style={{ marginTop: '16px' }}>Loading Portfolio...</p>
        </div>
      </div>
    );
  }

  if (error || !portfolio) {
    return (
      <div style={{ background: '#0f172a', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#fff', padding: '24px' }}>
        <div style={{ textAlign: 'center', maxWidth: '500px', border: '1px solid rgba(239,68,68,0.2)', padding: '32px', borderRadius: '12px', background: 'rgba(30,41,59,0.5)' }}>
          <span style={{ fontSize: '3rem' }}>🔒</span>
          <h2 style={{ marginTop: '16px', color: '#EF4444' }}>Access Restricted</h2>
          <p style={{ color: '#94a3b8', margin: '16px 0 24px', lineHeight: '1.6' }}>{error || 'This portfolio is private or does not exist.'}</p>
          <Link to="/dashboard" className="btn btn-primary" style={{ padding: '10px 20px' }}>Go to Dashboard</Link>
        </div>
      </div>
    );
  }

  const currentTheme = portfolio.theme || 'modern';
  const styles = THEME_STYLES[currentTheme] || THEME_STYLES.modern;

  // Group skills by category if available, otherwise general list
  const skillsList = data.skills || [];
  const categorizedSkills = skillsList.reduce((acc, skill) => {
    const type = skill.skill_type || 'technical';
    if (!acc[type]) acc[type] = [];
    acc[type].push(skill.skill_name);
    return acc;
  }, {});

  return (
    <div style={{
      background: styles.bg,
      color: styles.textColor,
      fontFamily: styles.font,
      minHeight: '100vh',
      transition: 'all 0.5s ease',
      paddingBottom: '60px'
    }}>
      {/* Embedded styles to support dynamic theme properties */}
      <style>{`
        .pf-container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
        .pf-card { 
          background: ${styles.cardBg}; 
          border: 1px solid ${styles.borderColor}; 
          border-radius: 12px; 
          padding: 32px; 
          margin-bottom: 32px;
          backdrop-filter: ${styles.backdropFilter || 'none'};
          box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }
        .pf-title { 
          font-size: 1.5rem; 
          font-weight: 700; 
          margin-bottom: 24px; 
          display: flex; 
          align-items: center; 
          gap: 10px;
          color: ${styles.accent};
        }
        .pf-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          border-radius: 6px;
          font-weight: 600;
          text-decoration: none;
          cursor: pointer;
          transition: all 0.3s ease;
          border: none;
        }
        .pf-btn-primary {
          background: ${styles.accent};
          color: ${styles.textColor === '#171717' || styles.textColor === '#1e293b' || styles.textColor === '#334155' || styles.textColor === '#27272a' ? '#fff' : '#000'};
        }
        .pf-btn-outline {
          background: transparent;
          border: 1px solid ${styles.borderColor};
          color: ${styles.textColor};
        }
        .pf-tag {
          font-size: 0.75rem;
          padding: 4px 10px;
          border-radius: 4px;
          background: rgba(255,255,255,0.05);
          border: 1px solid ${styles.borderColor};
          color: ${styles.textColor};
        }
        .pf-timeline-item {
          position: relative;
          padding-left: 24px;
          border-left: 2px solid ${styles.borderColor};
          margin-bottom: 24px;
        }
        .pf-timeline-dot {
          position: absolute;
          left: -6px;
          top: 6px;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: ${styles.accent};
        }
      `}</style>

      {/* Navigation Header */}
      <div style={{ borderBottom: `1px solid ${styles.borderColor}`, padding: '16px 0', marginBottom: '40px' }}>
        <div className="pf-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '1.25rem', fontWeight: 800, color: styles.accent, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <HiOutlineGlobeAlt /> {data.first_name || 'Portfolio'}
          </span>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={handleShareLog} className="pf-btn pf-btn-outline" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              <HiOutlineShare /> Share
            </button>
            <button onClick={handleDownloadLog} className="pf-btn pf-btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              <HiOutlineArrowDownTray /> Resume Data
            </button>
          </div>
        </div>
      </div>

      <div className="pf-container">
        
        {/* HERO SECTION */}
        <section id="hero" ref={sectionRefs.hero} className="pf-card" style={{ textAlign: 'center', padding: '60px 24px' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Initials Avatar */}
            <div style={{
              width: '100px',
              height: '100px',
              borderRadius: '50%',
              background: `linear-gradient(135deg, ${styles.accent}, rgba(255,255,255,0.1))`,
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2.5rem',
              fontWeight: 800,
              margin: '0 auto 24px',
              border: `2px solid ${styles.accent}`
            }}>
              {data.first_name?.[0]}{data.last_name?.[0]}
            </div>

            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '10px' }}>
              {data.first_name} {data.last_name}
            </h1>
            <p style={{ fontSize: '1.25rem', color: styles.accent, fontWeight: 600, marginBottom: '8px' }}>
              {data.headline || 'Software Professional'}
            </p>
            
            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap', color: 'var(--gray-400)', fontSize: '0.85rem', marginBottom: '24px' }}>
              {data.email && <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><HiOutlineEnvelope /> {data.email}</span>}
              {data.phone && <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><HiOutlinePhone /> {data.phone}</span>}
              {(data.city || data.country) && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <HiOutlineMapPin /> {data.city}{data.state ? `, ${data.state}` : ''}{data.country ? `, ${data.country}` : ''}
                </span>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
              {data.email && (
                <a href={`mailto:${data.email}`} className="pf-btn pf-btn-primary">
                  📨 Contact Me
                </a>
              )}
              {data.linkedin && (
                <a href={data.linkedin} target="_blank" rel="noopener noreferrer" className="pf-btn pf-btn-outline">
                  🔗 LinkedIn
                </a>
              )}
            </div>
          </motion.div>
        </section>

        {/* ABOUT ME SECTION */}
        {data.summary && (
          <section id="about" ref={sectionRefs.about} className="pf-card">
            <h3 className="pf-title"><HiOutlineSparkles /> About Me</h3>
            <p style={{ lineHeight: '1.7', fontSize: '1rem', whiteSpace: 'pre-line' }}>{data.summary}</p>
          </section>
        )}

        {/* SKILLS SECTION */}
        {skillsList.length > 0 && (
          <section id="skills" ref={sectionRefs.skills} className="pf-card">
            <h3 className="pf-title">🛠️ Skills</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {Object.entries(categorizedSkills).map(([cat, skills]) => (
                <div key={cat}>
                  <span style={{ textTransform: 'capitalize', fontWeight: 'bold', fontSize: '0.9rem', color: styles.accent, display: 'block', marginBottom: '8px' }}>
                    {cat}
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {skills.map((s, idx) => (
                      <span key={idx} className="pf-tag">{s}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* WORK EXPERIENCE */}
        {data.experiences && data.experiences.length > 0 && (
          <section id="experience" ref={sectionRefs.experience} className="pf-card">
            <h3 className="pf-title"><HiOutlineBriefcase /> Professional Experience</h3>
            <div>
              {data.experiences.map((exp, idx) => (
                <div key={idx} className="pf-timeline-item">
                  <div className="pf-timeline-dot"></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
                    <h4 style={{ fontSize: '1.1rem', fontWeight: 'bold', margin: 0 }}>
                      {exp.designation} <span style={{ color: styles.accent }}>@ {exp.company}</span>
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <HiOutlineCalendar /> {exp.start_date} – {exp.end_date || 'Present'}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--gray-400)', margin: '0 0 8px' }}>
                    Employment: {exp.employment_type || 'Full Time'}
                  </p>
                  <p style={{ fontSize: '0.9rem', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
                    {exp.description}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* PROJECTS SECTION */}
        {data.projects && data.projects.length > 0 && (
          <section id="projects" ref={sectionRefs.projects} className="pf-card">
            <h3 className="pf-title">🚀 Featured Projects</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
              {data.projects.map((proj, idx) => (
                <div key={idx} style={{ 
                  padding: '24px', 
                  background: 'rgba(255,255,255,0.01)', 
                  border: `1px solid ${styles.borderColor}`, 
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}>
                  <div>
                    <h4 style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '8px' }}>{proj.project_name}</h4>
                    <p style={{ fontSize: '0.85rem', lineHeight: '1.5', marginBottom: '16px' }}>{proj.description}</p>
                    
                    {proj.technologies && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '20px' }}>
                        {proj.technologies.split(',').map((tech, tIdx) => (
                          <span key={tIdx} className="pf-tag" style={{ background: 'transparent' }}>{tech.trim()}</span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    {proj.github_url && (
                      <a href={proj.github_url} target="_blank" rel="noopener noreferrer" className="pf-btn pf-btn-outline" style={{ flex: 1, padding: '6px 12px', fontSize: '0.75rem', justifyContent: 'center' }}>
                        💻 GitHub
                      </a>
                    )}
                    {proj.live_url && (
                      <a href={proj.live_url} target="_blank" rel="noopener noreferrer" className="pf-btn pf-btn-primary" style={{ flex: 1, padding: '6px 12px', fontSize: '0.75rem', justifyContent: 'center' }}>
                        🌐 Live Demo
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* EDUCATION SECTION */}
        {data.educations && data.educations.length > 0 && (
          <section id="education" ref={sectionRefs.education} className="pf-card">
            <h3 className="pf-title"><HiOutlineAcademicCap /> Education</h3>
            <div>
              {data.educations.map((edu, idx) => (
                <div key={idx} className="pf-timeline-item">
                  <div className="pf-timeline-dot"></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
                    <h4 style={{ fontSize: '1.1rem', fontWeight: 'bold', margin: 0 }}>
                      {edu.degree} <span style={{ color: styles.accent }}>in {edu.field_of_study}</span>
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <HiOutlineCalendar /> {edu.start_date} – {edu.end_date}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--gray-400)', margin: '0 0 4px' }}>{edu.institute}</p>
                  {edu.grade && <span className="pf-tag" style={{ background: 'transparent' }}>Grade: {edu.grade}</span>}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* CERTIFICATIONS */}
        {data.certifications && data.certifications.length > 0 && (
          <section id="certifications" ref={sectionRefs.certifications} className="pf-card">
            <h3 className="pf-title">📜 Certifications</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {data.certifications.map((cert, idx) => (
                <div key={idx} style={{ padding: '16px', background: 'rgba(255,255,255,0.01)', border: `1px solid ${styles.borderColor}`, borderRadius: '6px' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 'bold', margin: '0 0 4px' }}>{cert.certificate_name}</h4>
                  <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>Issued by: {cert.organization} ({cert.issue_date})</span>
                </div>
              ))}
            </div>
          </section>
        )}

      </div>
    </div>
  );
};

export default PortfolioPublic;

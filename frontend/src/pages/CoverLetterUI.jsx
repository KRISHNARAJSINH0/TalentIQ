import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  HiOutlineChevronLeft, 
  HiOutlineClipboardDocument, 
  HiOutlineArrowDownTray,
  HiOutlinePencilSquare,
  HiOutlineFolderOpen,
  HiOutlineSparkles,
  HiOutlineCheck
} from 'react-icons/hi2';
import { careerAPI } from '../api/career';
import '../styles/Profile.css';

const CoverLetterUI = () => {
  const [company, setCompany] = useState('');
  const [position, setPosition] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState('Professional');
  const [letterType, setLetterType] = useState('Job Application');
  
  const [generating, setGenerating] = useState(false);
  const [content, setContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const tones = ['Formal', 'Professional', 'Creative', 'Startup', 'Corporate', 'Friendly'];
  const letterTypes = [
    'Job Application',
    'Internship Cover Letter',
    'Freelancer Proposal',
    'Research Application',
    'Academic Letter',
    'Scholarship Letter'
  ];

  const fetchHistory = async () => {
    try {
      const res = await careerAPI.getCoverLetterHistory();
      setHistory(res.data);
    } catch (err) {
      console.error('Failed to fetch cover letter history:', err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!company || !position) {
      setError('Please provide both the Company and Position fields.');
      return;
    }

    try {
      setGenerating(true);
      setError('');
      setSuccess('');
      const res = await careerAPI.generateCoverLetter({
        company,
        position,
        job_description: jobDescription,
        tone,
        cover_letter_type: letterType
      });
      setContent(res.data.content);
      setSuccess('Cover Letter generated successfully!');
      fetchHistory();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error(err);
      setError('Failed to generate cover letter. Make sure your profile is verified.');
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${company.replace(/\s+/g, '_')}_${position.replace(/\s+/g, '_')}_cover_letter.txt`;
    document.body.appendChild(element);
    element.click();
    element.remove();
  };

  const selectFromHistory = (letter) => {
    setCompany(letter.company);
    setPosition(letter.position);
    setJobDescription(letter.job_description || '');
    setTone(letter.tone || 'Professional');
    setLetterType(letter.cover_letter_type || 'Job Application');
    setContent(letter.content);
    setIsEditing(false);
  };

  return (
    <div className="profile-page">
      <div className="profile-container" style={{ maxWidth: '1200px' }}>
        
        {/* Navigation back */}
        <div style={{ marginBottom: '24px' }}>
          <Link to="/career" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#8B5CF6', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem' }}>
            <HiOutlineChevronLeft /> Back to Dashboard
          </Link>
        </div>

        {/* 2 Column Form / Preview Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px' }} className="profile-columns-grid">
          
          {/* Left Column: Form & History */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Generation Form */}
            <div className="profile-card" style={{ padding: '24px' }}>
              <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                <HiOutlineSparkles style={{ color: '#8B5CF6' }} /> Write Custom Letter
              </h3>
              
              <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--gray-300)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                      Company Name *
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={company}
                      onChange={(e) => setCompany(e.target.value)}
                      placeholder="e.g. Google"
                      required
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--gray-300)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                      Job Title / Position *
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={position}
                      onChange={(e) => setPosition(e.target.value)}
                      placeholder="e.g. Senior Developer"
                      required
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--gray-300)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                      Tone / Voice
                    </label>
                    <select
                      className="form-control"
                      value={tone}
                      onChange={(e) => setTone(e.target.value)}
                    >
                      {tones.map((t, idx) => (
                        <option key={idx} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--gray-300)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                      Letter Type
                    </label>
                    <select
                      className="form-control"
                      value={letterType}
                      onChange={(e) => setLetterType(e.target.value)}
                    >
                      {letterTypes.map((lt, idx) => (
                        <option key={idx} value={lt}>{lt}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--gray-300)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    Job Description (Optional)
                  </label>
                  <textarea
                    className="form-control"
                    rows={4}
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste job description keywords here to optimize candidate alignment..."
                    style={{ resize: 'none' }}
                  />
                </div>

                {error && <div className="edit-error">{error}</div>}
                {success && <div className="edit-success">{success}</div>}

                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{
                    background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
                    border: 'none',
                    fontWeight: 600,
                    padding: '12px'
                  }}
                  disabled={generating}
                >
                  {generating ? 'Generating Letter...' : 'Generate with AI'}
                </button>
              </form>
            </div>

            {/* History Section */}
            <div className="profile-card" style={{ padding: '24px' }}>
              <h3 className="profile-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <HiOutlineFolderOpen /> Letter History
              </h3>
              
              {history.length === 0 ? (
                <p style={{ color: 'var(--gray-500)', fontSize: '0.85rem', margin: 0 }}>
                  No previously generated cover letters found.
                </p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '300px', overflowY: 'auto' }}>
                  {history.map((letter, idx) => (
                    <div 
                      key={idx}
                      onClick={() => selectFromHistory(letter)}
                      style={{ 
                        padding: '10px 14px', 
                        background: 'rgba(255,255,255,0.01)', 
                        border: '1px solid var(--glass-border)', 
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      className="history-item"
                    >
                      <strong style={{ color: '#fff', fontSize: '0.85rem', display: 'block' }}>{letter.position}</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>at {letter.company} ({letter.tone} tone)</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Right Column: Live Editor/Preview Screen */}
          <div className="profile-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', minHeight: '500px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px', marginBottom: '16px' }}>
              <h3 className="profile-card-title" style={{ margin: 0 }}>
                Cover Letter Preview
              </h3>
              
              {content && (
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button 
                    onClick={() => setIsEditing(!isEditing)}
                    className="btn btn-outline-dark" 
                    style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <HiOutlinePencilSquare /> {isEditing ? 'Preview' : 'Edit'}
                  </button>
                  <button 
                    onClick={handleCopy}
                    className="btn btn-outline-dark" 
                    style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    {copied ? <HiOutlineCheck style={{ color: '#10B981' }} /> : <HiOutlineClipboardDocument />} {copied ? 'Copied' : 'Copy'}
                  </button>
                  <button 
                    onClick={handleDownload}
                    className="btn btn-outline-dark" 
                    style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <HiOutlineArrowDownTray /> Download
                  </button>
                </div>
              )}
            </div>

            {content ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {isEditing ? (
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    style={{ 
                      width: '100%', 
                      flex: 1, 
                      background: 'rgba(0,0,0,0.2)', 
                      border: '1px solid var(--glass-border)', 
                      borderRadius: '8px', 
                      color: '#fff', 
                      padding: '16px', 
                      fontFamily: 'monospace', 
                      fontSize: '0.9rem',
                      lineHeight: '1.6',
                      resize: 'none'
                    }}
                  />
                ) : (
                  <div 
                    style={{ 
                      whiteSpace: 'pre-wrap', 
                      lineHeight: '1.7', 
                      color: 'var(--gray-200)', 
                      fontSize: '0.92rem', 
                      padding: '8px',
                      fontFamily: "'Inter', sans-serif" 
                    }}
                  >
                    {content}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', color: 'var(--gray-500)', gap: '12px' }}>
                <span style={{ fontSize: '3rem' }}>✉️</span>
                <p style={{ margin: 0, fontSize: '0.9rem' }}>Fill in application parameters and generate your cover letter.</p>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};

export default CoverLetterUI;

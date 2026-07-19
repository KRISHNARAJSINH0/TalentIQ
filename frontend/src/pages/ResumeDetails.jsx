import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import resumesAPI from '../api/resumes';
import { atsAPI } from '../api/ats';
import AIWorkflow from '../components/AIWorkflow';
import { 
  HiOutlineArrowDownTray,
  HiOutlineTrash,
  HiOutlineCheck,
  HiOutlineCpuChip,
  HiOutlineDocumentDuplicate,
  HiOutlineSparkles,
  HiOutlineChartBar
} from 'react-icons/hi2';
import '../styles/Resumes.css';

const ResumeDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [extractionError, setExtractionError] = useState('');
  const [copied, setCopied] = useState(false);
  const [regexData, setRegexData] = useState(null);
  const [regexAnalyzing, setRegexAnalyzing] = useState(false);
  const [regexError, setRegexError] = useState('');
  const [regexCopied, setRegexCopied] = useState(false);
  const [spacyData, setSpacyData] = useState(null);
  const [spacyAnalyzing, setSpacyAnalyzing] = useState(false);
  const [spacyError, setSpacyError] = useState('');
  const [spacyCopied, setSpacyCopied] = useState(false);
  const [spacySearch, setSpacySearch] = useState('');
  const [collapsedSections, setCollapsedSections] = useState({
    names: false,
    locations: false,
    organizations: false,
    dates: false,
    education: false,
    jobs: false,
    skills: false,
  });

  const [aiData, setAiData] = useState(null);
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  const [aiError, setAiError] = useState('');
  const [aiCopied, setAiCopied] = useState(false);
  const [aiSearch, setAiSearch] = useState('');
  const [aiCollapsedSections, setAiCollapsedSections] = useState({
    summary: false,
    general: false,
    skills: false,
    experience: false,
    education: false,
    projects: false,
    certifications: false,
    others: false,
  });

  const [masterData, setMasterData] = useState(null);
  const [masterMerging, setMasterMerging] = useState(false);
  const [masterError, setMasterError] = useState('');
  const [masterCopied, setMasterCopied] = useState(false);
  const [masterCollapsedSections, setMasterCollapsedSections] = useState({
    personal: false,
    skills: false,
    experience: false,
    education: false,
    projects: false,
    certifications: false,
    languages: false,
    others: false,
  });

  const [atsScoreData, setAtsScoreData] = useState(null);
  const [atsRunning, setAtsRunning] = useState(false);
  const [atsError, setAtsError] = useState('');

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const fetchDetails = async () => {
    try {
      setLoading(true);
      const response = await resumesAPI.getResumeDetails(id);
      setResume(response.data);
      if (response.data.extraction_status === 'completed') {
        const textRes = await resumesAPI.getResumeText(id);
        setExtractedText(textRes.data.extracted_text);
      }
      if (response.data.regex_status === 'completed') {
        const regexRes = await resumesAPI.getRegexData(id);
        setRegexData(regexRes.data.regex_json);
      }
      if (response.data.spacy_status === 'completed') {
        const spacyRes = await resumesAPI.getSpacyData(id);
        setSpacyData(spacyRes.data.spacy_json);
      }
      if (response.data.ai_status === 'completed') {
        const aiRes = await resumesAPI.getAIData(id);
        setAiData(aiRes.data.ai_json);
      }
      if (response.data.validation_status === 'completed' || response.data.validation_status === 'failed') {
        try {
          const masterRes = await resumesAPI.getMasterProfile(id);
          setMasterData(masterRes.data.master_resume_json);
          try {
            const atsRes = await atsAPI.getLatestATS(id);
            setAtsScoreData(atsRes.data);
          } catch (atsErr) {
            console.log('No latest ATS score found yet.');
          }
        } catch (err) {
          console.error('Failed to load master profile:', err);
        }
      }
    } catch (err) {
      console.error('Failed to load resume details:', err);
      setError('Resume not found or access denied.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!resume) return;
    try {
      const response = await resumesAPI.downloadResume(resume.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', resume.original_filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      setError('Failed to download resume file.');
    }
  };

  const handleActivate = async () => {
    if (!resume) return;
    try {
      await resumesAPI.activateResume(resume.id);
      setSuccess('Resume version activated successfully.');
      fetchDetails();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error('Activation failed:', err);
      setError('Failed to activate resume version.');
    }
  };

  const handleDelete = async () => {
    if (!resume) return;
    if (!window.confirm('Are you sure you want to delete this resume? (This is a soft-delete)')) {
      return;
    }

    try {
      await resumesAPI.deleteResume(resume.id);
      navigate('/resumes');
    } catch (err) {
      console.error('Delete failed:', err);
      setError('Failed to delete resume.');
    }
  };

  const fetchExtractedText = async () => {
    try {
      const response = await resumesAPI.getResumeText(id);
      setExtractedText(response.data.extracted_text);
    } catch (err) {
      console.error('Failed to fetch extracted text:', err);
    }
  };

  const handleExtractText = async () => {
    if (!resume) return;
    try {
      setExtracting(true);
      setExtractionError('');
      const response = await resumesAPI.extractResume(resume.id);
      
      setResume(prev => ({
        ...prev,
        extraction_status: response.data.status,
        extraction_time: response.data.extraction_date,
        processing_duration: response.data.processing_time,
        error_message: response.data.error_message
      }));
      
      if (response.data.status === 'completed') {
        await fetchExtractedText();
        setSuccess('Text extracted successfully!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        setExtractionError(response.data.error_message || 'Extraction failed.');
      }
    } catch (err) {
      console.error('Extraction failed:', err);
      const errorMsg = err.response?.data?.error_message || 'An unexpected error occurred during extraction.';
      setExtractionError(errorMsg);
      fetchDetails();
    } finally {
      setExtracting(false);
    }
  };

  const handleCopyText = () => {
    if (!extractedText) return;
    navigator.clipboard.writeText(extractedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadText = () => {
    if (!extractedText) return;
    const blob = new Blob([extractedText], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `${resume.original_filename.split('.')[0]}_extracted.txt`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleRunRegexAnalysis = async () => {
    if (!resume) return;
    try {
      setRegexAnalyzing(true);
      setRegexError('');
      const response = await resumesAPI.runRegexAnalysis(resume.id);
      
      setResume(prev => ({
        ...prev,
        regex_status: response.data.status,
        regex_completed_at: response.data.completed_at,
        regex_processing_time: response.data.processing_time,
      }));
      
      if (response.data.status === 'completed') {
        setRegexData(response.data.regex_json);
        setSuccess('Regex Analysis completed successfully!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        setRegexError(response.data.regex_json?.error || 'Analysis failed.');
      }
    } catch (err) {
      console.error('Regex analysis failed:', err);
      const errorMsg = err.response?.data?.error_message || 'An unexpected error occurred during regex analysis.';
      setRegexError(errorMsg);
      fetchDetails();
    } finally {
      setRegexAnalyzing(false);
    }
  };

  const handleCopyJSON = () => {
    if (!regexData) return;
    navigator.clipboard.writeText(JSON.stringify(regexData, null, 2));
    setRegexCopied(true);
    setTimeout(() => setRegexCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    if (!regexData) return;
    const blob = new Blob([JSON.stringify(regexData, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `${resume.original_filename.split('.')[0]}_regex.json`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleRunSpacyAnalysis = async () => {
    if (!resume) return;
    try {
      setSpacyAnalyzing(true);
      setSpacyError('');
      const response = await resumesAPI.runSpacyAnalysis(resume.id);
      
      setResume(prev => ({
        ...prev,
        spacy_status: response.data.status,
        spacy_completed_at: response.data.completed_at,
        spacy_processing_time: response.data.processing_time,
      }));
      
      if (response.data.status === 'completed') {
        setSpacyData(response.data.spacy_json);
        setSuccess('spaCy NLP Analysis completed successfully!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        setSpacyError(response.data.spacy_json?.error || 'Analysis failed.');
      }
    } catch (err) {
      console.error('spaCy analysis failed:', err);
      const errorMsg = err.response?.data?.error_message || err.response?.data?.spacy_json?.error || 'An unexpected error occurred during spaCy analysis.';
      setSpacyError(errorMsg);
      fetchDetails();
    } finally {
      setSpacyAnalyzing(false);
    }
  };

  const handleCopySpacyJSON = () => {
    if (!spacyData) return;
    navigator.clipboard.writeText(JSON.stringify(spacyData, null, 2));
    setSpacyCopied(true);
    setTimeout(() => setSpacyCopied(false), 2000);
  };

  const handleDownloadSpacyJSON = () => {
    if (!spacyData) return;
    const blob = new Blob([JSON.stringify(spacyData, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `${resume.original_filename.split('.')[0]}_spacy.json`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleRunAiParsing = async () => {
    if (!resume) return;
    try {
      setAiAnalyzing(true);
      setAiError('');
      const response = await resumesAPI.runAIParsing(resume.id);
      
      setResume(prev => ({
        ...prev,
        ai_status: response.data.status,
        ai_completed_at: response.data.completed_at,
        ai_processing_time: response.data.processing_time,
        ai_model: response.data.ai_model,
        ai_prompt_version: response.data.ai_prompt_version,
      }));
      
      if (response.data.status === 'completed') {
        setAiData(response.data.ai_json);
        setSuccess('Gemini AI Resume Parsing completed successfully!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        setAiError(response.data.ai_json?.error || 'Gemini parsing failed.');
      }
    } catch (err) {
      console.error('Gemini AI parsing failed:', err);
      const errorMsg = err.response?.data?.error_message || 'An unexpected error occurred during Gemini AI parsing.';
      setAiError(errorMsg);
      fetchDetails();
    } finally {
      setAiAnalyzing(false);
    }
  };

  const handleCopyAiJSON = () => {
    if (!aiData) return;
    navigator.clipboard.writeText(JSON.stringify(aiData, null, 2));
    setAiCopied(true);
    setTimeout(() => setAiCopied(false), 2000);
  };

  const handleDownloadAiJSON = () => {
    if (!aiData) return;
    const blob = new Blob([JSON.stringify(aiData, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `${resume.original_filename.split('.')[0]}_ai.json`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const toggleSection = (section) => {
    setCollapsedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const toggleAiSection = (section) => {
    setAiCollapsedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleRunMasterMerge = async () => {
    if (!resume) return;
    try {
      setMasterMerging(true);
      setMasterError('');
      const response = await resumesAPI.mergeProfile(resume.id);
      
      setResume(prev => ({
        ...prev,
        validation_status: response.data.validation_status,
        validation_time: response.data.validation_time,
        completion_percentage: response.data.completion_percentage,
      }));
      
      setMasterData(response.data.master_resume_json);
      setSuccess('Master profile generated and validated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error('Master merge failed:', err);
      const errorMsg = err.response?.data?.error_message || 'An unexpected error occurred during master profile merging.';
      setMasterError(errorMsg);
      fetchDetails();
    } finally {
      setMasterMerging(false);
    }
  };

  const handleRunATSAnalysis = async () => {
    if (!resume) return;
    try {
      setAtsRunning(true);
      setAtsError('');
      const response = await atsAPI.analyzeResume(resume.id);
      setAtsScoreData(response.data);
      setSuccess('ATS scoring analysis completed successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      console.error('ATS scoring failed:', err);
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || 'An unexpected error occurred during ATS analysis.';
      setAtsError(errorMsg);
    } finally {
      setAtsRunning(false);
    }
  };

  const handleCopyMasterJSON = () => {
    if (!masterData) return;
    navigator.clipboard.writeText(JSON.stringify(masterData, null, 2));
    setMasterCopied(true);
    setTimeout(() => setMasterCopied(false), 2000);
  };

  const handleDownloadMasterJSON = () => {
    if (!masterData) return;
    const blob = new Blob([JSON.stringify(masterData, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `${resume.original_filename.split('.')[0]}_master.json`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const toggleMasterSection = (section) => {
    setMasterCollapsedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getCurrentStage = () => {
    if (!resume) return 'upload';
    if (resume.extraction_status !== 'completed') return 'upload';
    if (resume.regex_status !== 'completed') return 'extract';
    if (resume.spacy_status !== 'completed') return 'regex';
    if (resume.ai_status !== 'completed') return 'spacy';
    if (resume.validation_status === 'completed') return 'master';
    if (resume.validation_status === 'failed') return 'validation';
    return 'gemini';
  };

  if (loading) {
    return (
      <div className="resumes-page">
        <div className="resumes-container" style={{ textAlign: 'center' }}>
          <div className="skeleton-row" style={{ height: '40px', width: '200px', margin: '0 auto 30px' }}></div>
          <div className="skeleton-row" style={{ height: '300px' }}></div>
        </div>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="resumes-page">
        <div className="resumes-container" style={{ textAlign: 'center' }}>
          <div className="auth-error" style={{ marginBottom: '24px' }}>{error || 'An error occurred'}</div>
          <Link to="/resumes" className="btn-large btn-large-secondary" style={{ display: 'inline-flex', width: 'auto' }}>
            Back to Resumes
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="resumes-page">
      <div className="resumes-container">
        
        {/* Back Link */}
        <div style={{ marginBottom: '24px' }}>
          <Link to="/resumes" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            ← Back to Resumes
          </Link>
        </div>

        {/* Title Section */}
        <div className="resumes-title-section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h1 className="resumes-title">{resume.resume_title}</h1>
            <p className="resumes-subtitle">Resume Version Control Details</p>
          </div>
          <div>
            <span className="badge-version" style={{ fontSize: '1rem', padding: '6px 16px' }}>v{resume.version}</span>
          </div>
        </div>

        {/* Alerts */}
        {success && (
          <div className="auth-error" style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.3)', color: '#34D399', marginBottom: '24px' }}>
            {success}
          </div>
        )}

        {/* AI Processing Pipeline Visualisation */}
        <div className="details-card" style={{ marginBottom: '32px' }}>
          <AIWorkflow currentStage={getCurrentStage()} />
        </div>

        {/* Details Grid */}
        <div className="detail-grid">
          {/* Main Info */}
          <div className="details-card">
            <h3 className="history-card-title" style={{ marginBottom: '24px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
              File Details & Metadata
            </h3>
            
            <div className="info-list">
              <div className="info-row">
                <span className="info-label">Original Filename</span>
                <span className="info-val">{resume.original_filename}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Stored Filename (Secure UUID)</span>
                <span className="info-val" style={{ fontFamily: 'monospace', fontSize: '0.8rem', opacity: 0.8 }}>
                  {resume.stored_filename}
                </span>
              </div>
              <div className="info-row">
                <span className="info-label">File Size</span>
                <span className="info-val">{formatBytes(resume.file_size)}</span>
              </div>
              <div className="info-row">
                <span className="info-label">MIME Content Type</span>
                <span className="info-val">{resume.mime_type}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Upload Date & Time</span>
                <span className="info-val">{formatDate(resume.upload_date)}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Status</span>
                <span className="info-val">
                  {resume.is_active ? (
                    <span className="badge-status active">Active Version</span>
                  ) : (
                    <span className="badge-status inactive">Inactive</span>
                  )}
                </span>
              </div>
            </div>
          </div>

          {/* Action sidebar */}
          <div className="actions-card">
            <h3 className="history-card-title" style={{ fontSize: '1.125rem', marginBottom: '8px' }}>
              Actions
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginBottom: '16px', lineHeight: 1.4 }}>
              Perform administrative operations on this resume file.
            </p>

            <Link to={`/resumes/${resume.id}/job-ats`} className="btn-large btn-large-primary" style={{ width: '100%', display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)', border: 'none', color: 'white', textDecoration: 'none', marginBottom: '8px', fontWeight: 600 }}>
              <HiOutlineSparkles size={20} /> Job-Specific ATS Match
            </Link>

            <Link to={`/resumes/${resume.id}/benchmark`} className="btn-large btn-large-primary" style={{ width: '100%', display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)', border: 'none', color: 'white', textDecoration: 'none', marginBottom: '8px', fontWeight: 600 }}>
              <HiOutlineChartBar size={20} /> Cohort Benchmarks & Rankings
            </Link>

            <button onClick={handleDownload} className="btn-large btn-large-primary" style={{ width: '100%', display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center' }}>
              <HiOutlineArrowDownTray size={20} /> Download File
            </button>

            {!resume.is_active && (
              <button onClick={handleActivate} className="btn-large btn-large-secondary" style={{ width: '100%', display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center' }}>
                <HiOutlineCheck size={20} /> Set Active Version
              </button>
            )}

            <button onClick={handleDelete} className="btn-large btn-large-danger" style={{ width: '100%', display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center' }}>
              <HiOutlineTrash size={20} /> Delete Resume
            </button>
          </div>
        </div>

        {/* Text Extraction Panel */}
        <div className="details-card" style={{ marginTop: '32px', width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
            <div>
              <h3 className="history-card-title" style={{ margin: 0 }}>
                Resume Text Extraction Engine
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>
                Extract and view raw text structure from your resume file.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span className={`badge-status ${
                resume.extraction_status === 'completed' ? 'completed' :
                resume.extraction_status === 'processing' ? 'processing' :
                resume.extraction_status === 'failed' ? 'failed' : 'pending'
              }`}>
                {resume.extraction_status ? resume.extraction_status.toUpperCase() : 'PENDING'}
              </span>
              
              <button 
                onClick={handleExtractText} 
                className="btn-large btn-large-primary" 
                style={{ padding: '8px 16px', fontSize: '0.875rem', width: 'auto', display: 'flex', gap: '8px', alignItems: 'center', margin: 0 }}
                disabled={extracting || resume.extraction_status === 'processing'}
              >
                {extracting ? (
                  <>
                    <span className="spinner-border spinner-border-sm" style={{ width: '1rem', height: '1rem' }} /> Extracting...
                  </>
                ) : (
                  <>
                    <HiOutlineCpuChip size={18} /> Extract Text
                  </>
                )}
              </button>
            </div>
          </div>

          {extractionError && (
            <div className="auth-error" style={{ marginBottom: '20px' }}>
              {extractionError}
            </div>
          )}

          {resume.extraction_status === 'completed' && extractedText && (
            <div className="extraction-viewer-container">
              <div className="extraction-viewer-header">
                <span className="extraction-viewer-meta">
                  Processing Time: {resume.processing_duration}s | Text Length: {extractedText.length} chars
                </span>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button onClick={handleCopyText} className="extraction-action-btn" style={{ display: 'inline-flex', gap: '6px', alignItems: 'center' }}>
                    {copied ? (
                      <>
                        <HiOutlineCheck size={14} /> Copied
                      </>
                    ) : (
                      <>
                        <HiOutlineDocumentDuplicate size={14} /> Copy Text
                      </>
                    )}
                  </button>
                  <button onClick={handleDownloadText} className="extraction-action-btn" style={{ display: 'inline-flex', gap: '6px', alignItems: 'center' }}>
                    <HiOutlineArrowDownTray size={14} /> Download Text
                  </button>
                </div>
              </div>
              <textarea 
                className="extraction-text-area" 
                value={extractedText} 
                readOnly 
              />
            </div>
          )}

          {resume.extraction_status === 'pending' && !extracting && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>This resume has not been processed yet. Click "Extract Text" to run the extraction engine.</p>
            </div>
          )}

          {extracting && (
            <div style={{ padding: '40px 20px', textAlign: 'center' }}>
              <div className="skeleton-row" style={{ height: '20px', width: '60%', margin: '0 auto 12px' }}></div>
              <div className="skeleton-row" style={{ height: '20px', width: '80%', margin: '0 auto 12px' }}></div>
              <div className="skeleton-row" style={{ height: '120px', width: '100%', margin: '0 auto' }}></div>
            </div>
          )}
        </div>

        {/* Regex Extraction Panel */}
        <div className="details-card" style={{ marginTop: '32px', width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
            <div>
              <h3 className="history-card-title" style={{ margin: 0 }}>
                Regex Extraction Engine (Phase 6)
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>
                Run deterministic regex patterns to extract clean emails, phone numbers, and profile URLs.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span className={`badge-status ${
                resume.regex_status === 'completed' ? 'completed' :
                resume.regex_status === 'processing' ? 'processing' :
                resume.regex_status === 'failed' ? 'failed' : 'pending'
              }`}>
                {resume.regex_status ? resume.regex_status.toUpperCase() : 'PENDING'}
              </span>
              
              <button 
                onClick={handleRunRegexAnalysis} 
                className="btn-large btn-large-primary" 
                style={{ padding: '8px 16px', fontSize: '0.875rem', width: 'auto', display: 'flex', gap: '8px', alignItems: 'center', margin: 0 }}
                disabled={regexAnalyzing || resume.regex_status === 'processing' || resume.extraction_status !== 'completed'}
                title={resume.extraction_status !== 'completed' ? 'Please run Text Extraction first.' : 'Run Regex Analysis'}
              >
                {regexAnalyzing ? (
                  <>
                    <span className="spinner-border spinner-border-sm" style={{ width: '1rem', height: '1rem' }} /> Analyzing...
                  </>
                ) : (
                  <>
                    <HiOutlineSparkles size={18} /> Run Regex Analysis
                  </>
                )}
              </button>
            </div>
          </div>

          {regexError && (
            <div className="auth-error" style={{ marginBottom: '20px' }}>
              {regexError}
            </div>
          )}

          {resume.regex_status === 'completed' && regexData && (
            <div style={{ marginTop: '24px' }}>
              {/* Grid of Key Info */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
                
                {/* Contact Info Card */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', padding: '16px', borderRadius: '12px' }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    📧 Contact Information
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                    <div><strong>Primary Email:</strong> {regexData.email || 'None'}</div>
                    {regexData.secondary_emails?.length > 0 && (
                      <div><strong>Secondary Emails:</strong> {regexData.secondary_emails.join(', ')}</div>
                    )}
                    <div><strong>Primary Phone:</strong> {regexData.phone || 'None'}</div>
                    {regexData.secondary_phones?.length > 0 && (
                      <div><strong>Secondary Phones:</strong> {regexData.secondary_phones.join(', ')}</div>
                    )}
                  </div>
                </div>

                {/* Social / Developer Profiles */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', padding: '16px', borderRadius: '12px' }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    🔗 Profiles & Links
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                    <div>
                      <strong>LinkedIn:</strong> {regexData.linkedin ? (
                        <a href={regexData.linkedin} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>View Profile</a>
                      ) : 'None'}
                    </div>
                    <div>
                      <strong>GitHub:</strong> {regexData.github ? (
                        <a href={regexData.github} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>View Profile</a>
                      ) : 'None'}
                    </div>
                    <div>
                      <strong>StackOverflow:</strong> {regexData.stackoverflow ? (
                        <a href={regexData.stackoverflow} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>View Profile</a>
                      ) : 'None'}
                    </div>
                    <div>
                      <strong>Kaggle:</strong> {regexData.kaggle ? (
                        <a href={regexData.kaggle} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>View Profile</a>
                      ) : 'None'}
                    </div>
                  </div>
                </div>

                {/* Websites & Location */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', padding: '16px', borderRadius: '12px' }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    🌐 Websites & Location
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                    <div>
                      <strong>Portfolio:</strong> {regexData.portfolio ? (
                        <a href={regexData.portfolio} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>Visit Site</a>
                      ) : 'None'}
                    </div>
                    <div>
                      <strong>Personal Website:</strong> {regexData.personal_website ? (
                        <a href={regexData.personal_website} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>Visit Site</a>
                      ) : 'None'}
                    </div>
                    <div>
                      <strong>Twitter/X:</strong> {regexData.twitter ? (
                        <a href={regexData.twitter} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>View Profile</a>
                      ) : 'None'}
                    </div>
                    <div>
                      <strong>Medium:</strong> {regexData.medium ? (
                        <a href={regexData.medium} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>View Profile</a>
                      ) : 'None'}
                    </div>
                    <div><strong>Address:</strong> {regexData.address || 'None'}</div>
                    <div><strong>Pincode / ZIP:</strong> {regexData.pincode || 'None'}</div>
                  </div>
                </div>
              </div>

              {/* Other URLs (if any) */}
              {regexData.other_urls?.length > 0 && (
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', padding: '16px', borderRadius: '12px', marginBottom: '24px' }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: 'var(--primary)' }}>
                    📂 Other Detected Links
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.85rem' }}>
                    {regexData.other_urls.map((url, idx) => (
                      <div key={idx}>
                        <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline', wordBreak: 'break-all' }}>
                          {url}
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Raw JSON Viewer */}
              <div className="text-viewer-container">
                <div className="text-viewer-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 16px', background: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--glass-border)', borderTopLeftRadius: '12px', borderTopRightRadius: '12px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', fontFamily: 'monospace' }}>
                    Processing Time: {resume.regex_processing_time}s
                  </span>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={handleCopyJSON} className="btn-small" style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--white)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                      {regexCopied ? (
                        <>
                          <HiOutlineCheck size={14} /> Copied
                        </>
                      ) : (
                        <>
                          <HiOutlineDocumentDuplicate size={14} /> Copy JSON
                        </>
                      )}
                    </button>
                    <button onClick={handleDownloadJSON} className="btn-small" style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--white)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                      <HiOutlineArrowDownTray size={14} /> Download JSON
                    </button>
                  </div>
                </div>
                <textarea 
                  className="code-json-viewer color-regex" 
                  value={JSON.stringify(regexData, null, 2)} 
                  readOnly 
                />
              </div>
            </div>
          )}

          {resume.regex_status === 'pending' && !regexAnalyzing && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                {resume.extraction_status === 'completed' 
                  ? 'This resume text is ready for Regex Analysis. Click "Run Regex Analysis" above to process.' 
                  : 'Please extract resume text first before running Regex Analysis.'}
              </p>
            </div>
          )}

          {regexAnalyzing && (
            <div style={{ padding: '40px 20px', textAlign: 'center' }}>
              <div className="skeleton-row" style={{ height: '20px', width: '50%', margin: '0 auto 12px' }}></div>
              <div className="skeleton-row" style={{ height: '120px', width: '100%', margin: '0 auto' }}></div>
            </div>
          )}
        </div>

        {/* spaCy NLP Extraction Panel */}
        <div className="details-card" style={{ marginTop: '32px', width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
            <div>
              <h3 className="history-card-title" style={{ margin: 0 }}>
                spaCy NLP Extraction Engine (Phase 7)
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>
                Run Natural Language Processing (NLP) models to extract candidates' names, organizations, locations, dates, degrees, and job titles.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span className={`badge-status ${
                resume.spacy_status === 'completed' ? 'completed' :
                resume.spacy_status === 'processing' ? 'processing' :
                resume.spacy_status === 'failed' ? 'failed' : 'pending'
              }`}>
                {resume.spacy_status ? resume.spacy_status.toUpperCase() : 'PENDING'}
              </span>
              
              <button 
                onClick={handleRunSpacyAnalysis} 
                className="btn-large btn-large-primary" 
                style={{ padding: '8px 16px', fontSize: '0.875rem', width: 'auto', display: 'flex', gap: '8px', alignItems: 'center', margin: 0 }}
                disabled={spacyAnalyzing || resume.spacy_status === 'processing' || resume.extraction_status !== 'completed'}
                title={resume.extraction_status !== 'completed' ? 'Please run Text Extraction first.' : 'Run spaCy NLP Analysis'}
              >
                {spacyAnalyzing ? (
                  <>
                    <span className="spinner-border spinner-border-sm" style={{ width: '1rem', height: '1rem' }} /> Analyzing...
                  </>
                ) : (
                  <>
                    <HiOutlineSparkles size={18} /> Run NLP Analysis
                  </>
                )}
              </button>
            </div>
          </div>

          {spacyError && (
            <div className="auth-error" style={{ marginBottom: '20px' }}>
              {spacyError}
            </div>
          )}

          {resume.spacy_status === 'completed' && spacyData && (
            <div style={{ marginTop: '24px' }}>
              
              {/* Search Bar for Entities */}
              <div style={{ marginBottom: '20px' }}>
                <input 
                  type="text" 
                  className="spacy-search-input" 
                  placeholder="🔍 Search detected entities (e.g. 'Google', 'Bachelor', 'New York')..."
                  value={spacySearch}
                  onChange={(e) => setSpacySearch(e.target.value)}
                />
              </div>

              {/* Entity Viewer Grid */}
              <div className="spacy-entity-grid">
                
                {/* 1. Name */}
                {(!spacySearch || (spacyData.name && spacyData.name.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('names')}>
                      <h4 className="spacy-section-title">👤 Primary Candidate Name</h4>
                      <span className="spacy-section-toggle">{collapsedSections.names ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.names && (
                      <div className="spacy-name-display">
                        {spacyData.name || 'No name detected'}
                      </div>
                    )}
                  </div>
                )}

                {/* 2. Job Titles */}
                {(!spacySearch || spacyData.job_titles?.some(j => j.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('jobs')}>
                      <h4 className="spacy-section-title">
                        💼 Job Titles <span className="spacy-count-badge">{spacyData.job_titles?.filter(j => !spacySearch || j.toLowerCase().includes(spacySearch.toLowerCase())).length || 0}</span>
                      </h4>
                      <span className="spacy-section-toggle">{collapsedSections.jobs ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.jobs && (
                      <div className="spacy-tags-wrap">
                        {spacyData.job_titles?.filter(j => !spacySearch || j.toLowerCase().includes(spacySearch.toLowerCase())).length > 0
                          ? spacyData.job_titles.filter(j => !spacySearch || j.toLowerCase().includes(spacySearch.toLowerCase())).map((job, idx) => (
                              <span key={idx} className="spacy-job-tag">{job}</span>
                            ))
                          : <span className="spacy-empty-text">None detected</span>
                        }
                      </div>
                    )}
                  </div>
                )}

                {/* 3. Skills (NEW) */}
                {(!spacySearch || spacyData.skills?.some(s => s.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('skills')}>
                      <h4 className="spacy-section-title">
                        🛠️ Skills & Technologies <span className="spacy-count-badge">{spacyData.skills?.filter(s => !spacySearch || s.toLowerCase().includes(spacySearch.toLowerCase())).length || 0}</span>
                      </h4>
                      <span className="spacy-section-toggle">{collapsedSections.skills ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.skills && (
                      <div className="spacy-tags-wrap">
                        {spacyData.skills?.filter(s => !spacySearch || s.toLowerCase().includes(spacySearch.toLowerCase())).length > 0
                          ? spacyData.skills.filter(s => !spacySearch || s.toLowerCase().includes(spacySearch.toLowerCase())).map((skill, idx) => (
                              <span key={idx} className="spacy-skill-tag">{skill}</span>
                            ))
                          : <span className="spacy-empty-text">None detected</span>
                        }
                      </div>
                    )}
                  </div>
                )}

                {/* 4. Education & Degrees */}
                {(!spacySearch || spacyData.education_entities?.some(e => e.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('education')}>
                      <h4 className="spacy-section-title">
                        🎓 Education Entities <span className="spacy-count-badge">{spacyData.education_entities?.filter(e => !spacySearch || e.toLowerCase().includes(spacySearch.toLowerCase())).length || 0}</span>
                      </h4>
                      <span className="spacy-section-toggle">{collapsedSections.education ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.education && (
                      <div className="spacy-tags-wrap" style={{ flexDirection: 'column' }}>
                        {spacyData.education_entities?.filter(e => !spacySearch || e.toLowerCase().includes(spacySearch.toLowerCase())).length > 0
                          ? spacyData.education_entities.filter(e => !spacySearch || e.toLowerCase().includes(spacySearch.toLowerCase())).map((edu, idx) => (
                              <span key={idx} className="spacy-edu-tag">{edu}</span>
                            ))
                          : <span className="spacy-empty-text">None detected</span>
                        }
                      </div>
                    )}
                  </div>
                )}

                {/* 5. Organizations */}
                {(!spacySearch || spacyData.organizations?.some(o => o.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('organizations')}>
                      <h4 className="spacy-section-title">
                        🏢 Organizations <span className="spacy-count-badge">{spacyData.organizations?.filter(o => !spacySearch || o.toLowerCase().includes(spacySearch.toLowerCase())).length || 0}</span>
                      </h4>
                      <span className="spacy-section-toggle">{collapsedSections.organizations ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.organizations && (
                      <div className="spacy-tags-wrap">
                        {spacyData.organizations?.filter(o => !spacySearch || o.toLowerCase().includes(spacySearch.toLowerCase())).length > 0
                          ? spacyData.organizations.filter(o => !spacySearch || o.toLowerCase().includes(spacySearch.toLowerCase())).map((org, idx) => (
                              <span key={idx} className="spacy-entity-tag">{org}</span>
                            ))
                          : <span className="spacy-empty-text">None detected</span>
                        }
                      </div>
                    )}
                  </div>
                )}

                {/* 6. Locations */}
                {(!spacySearch || spacyData.locations?.some(l => l.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('locations')}>
                      <h4 className="spacy-section-title">
                        📍 Locations <span className="spacy-count-badge">{spacyData.locations?.filter(l => !spacySearch || l.toLowerCase().includes(spacySearch.toLowerCase())).length || 0}</span>
                      </h4>
                      <span className="spacy-section-toggle">{collapsedSections.locations ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.locations && (
                      <div className="spacy-tags-wrap">
                        {spacyData.locations?.filter(l => !spacySearch || l.toLowerCase().includes(spacySearch.toLowerCase())).length > 0
                          ? spacyData.locations.filter(l => !spacySearch || l.toLowerCase().includes(spacySearch.toLowerCase())).map((loc, idx) => (
                              <span key={idx} className="spacy-entity-tag">{loc}</span>
                            ))
                          : <span className="spacy-empty-text">None detected</span>
                        }
                      </div>
                    )}
                  </div>
                )}

                {/* 7. Dates */}
                {(!spacySearch || spacyData.dates?.some(d => d.toLowerCase().includes(spacySearch.toLowerCase()))) && (
                  <div className="spacy-entity-card">
                    <div className="spacy-section-header" onClick={() => toggleSection('dates')}>
                      <h4 className="spacy-section-title">
                        📅 Dates & Ranges <span className="spacy-count-badge">{spacyData.dates?.filter(d => !spacySearch || d.toLowerCase().includes(spacySearch.toLowerCase())).length || 0}</span>
                      </h4>
                      <span className="spacy-section-toggle">{collapsedSections.dates ? '➕' : '➖'}</span>
                    </div>
                    {!collapsedSections.dates && (
                      <div className="spacy-tags-wrap">
                        {spacyData.dates?.filter(d => !spacySearch || d.toLowerCase().includes(spacySearch.toLowerCase())).length > 0
                          ? spacyData.dates.filter(d => !spacySearch || d.toLowerCase().includes(spacySearch.toLowerCase())).map((date, idx) => (
                              <span key={idx} className="spacy-date-tag">{date}</span>
                            ))
                          : <span className="spacy-empty-text">None detected</span>
                        }
                      </div>
                    )}
                  </div>
                )}

              </div>


              {/* Raw JSON Viewer */}
              <div className="text-viewer-container">
                <div className="spacy-json-header">
                  <span className="spacy-json-meta">
                    Processing Time: {resume.spacy_processing_time}s
                  </span>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={handleCopySpacyJSON} className="spacy-json-btn">
                      {spacyCopied ? (
                        <>
                          <HiOutlineCheck size={14} /> Copied
                        </>
                      ) : (
                        <>
                          <HiOutlineDocumentDuplicate size={14} /> Copy JSON
                        </>
                      )}
                    </button>
                    <button onClick={handleDownloadSpacyJSON} className="spacy-json-btn">
                      <HiOutlineArrowDownTray size={14} /> Download JSON
                    </button>
                  </div>
                </div>
                <textarea 
                  className="spacy-json-viewer" 
                  value={JSON.stringify(spacyData, null, 2)} 
                  readOnly 
                />
              </div>
            </div>
          )}

          {resume.spacy_status === 'pending' && !spacyAnalyzing && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                {resume.extraction_status === 'completed' 
                  ? 'This resume text is ready for NLP Analysis. Click "Run NLP Analysis" above to process.' 
                  : 'Please extract resume text first before running NLP Analysis.'}
              </p>
            </div>
          )}

          {spacyAnalyzing && (
            <div style={{ padding: '40px 20px', textAlign: 'center' }}>
              <div className="skeleton-row" style={{ height: '20px', width: '50%', margin: '0 auto 12px' }}></div>
              <div className="skeleton-row" style={{ height: '120px', width: '100%', margin: '0 auto' }}></div>
            </div>
          )}
        </div>

        {/* Gemini AI Resume Parsing Engine Panel */}
        <div className="gemini-engine-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px', borderBottom: '1px solid rgba(139, 92, 246, 0.2)', paddingBottom: '16px' }}>
            <div>
              <h3 className="history-card-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                ✨ Gemini AI Resume Parsing Engine (Phase 8)
              </h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: 'var(--subtext-color)' }}>
                Advanced semantic entity extraction and structure normalization using Gemini 1.5 Pro/Flash.
              </p>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className={`badge badge-${
                resume.ai_status === 'completed' ? 'completed' :
                resume.ai_status === 'processing' ? 'processing' :
                resume.ai_status === 'failed' ? 'failed' : 'pending'
              }`} style={{ margin: 0, border: resume.ai_status === 'completed' ? '1px solid #10B981' : resume.ai_status === 'processing' ? '1px solid #8B5CF6' : 'inherit' }}>
                {resume.ai_status ? resume.ai_status.toUpperCase() : 'PENDING'}
              </span>
              
              <button 
                onClick={handleRunAiParsing} 
                className="btn-large" 
                style={{ 
                  padding: '8px 16px', 
                  fontSize: '0.875rem', 
                  width: 'auto', 
                  display: 'flex', 
                  gap: '8px', 
                  alignItems: 'center', 
                  margin: 0,
                  background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(139, 92, 246, 0.25)',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
                disabled={aiAnalyzing || resume.ai_status === 'processing' || resume.extraction_status !== 'completed'}
                title={resume.extraction_status !== 'completed' ? 'Please run Text Extraction first.' : 'Run Gemini AI Parsing'}
              >
                {aiAnalyzing ? (
                  <>
                    <span className="spinner" style={{ borderLeftColor: 'transparent', borderTopColor: 'white', borderRightColor: 'white', borderBottomColor: 'white' }}></span>
                    Parsing with Gemini...
                  </>
                ) : (
                  <>
                    <HiOutlineSparkles size={18} /> Run AI Parsing
                  </>
                )}
              </button>
            </div>
          </div>

          {aiError && (
            <div className="error-message" style={{ margin: '0 0 20px 0', borderLeft: '4px solid var(--red-500)' }}>
              {aiError}
            </div>
          )}

          {resume.ai_status === 'completed' && aiData && (
            <div>
              {/* Search Bar */}
              <div style={{ marginBottom: '20px' }}>
                <input
                  type="text"
                  placeholder="🔍 Search AI extracted details (e.g. Python, Stanford, Google)..."
                  className="gemini-search-input"
                  value={aiSearch}
                  onChange={(e) => setAiSearch(e.target.value)}
                />
              </div>

              {/* Grid Layout for Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', marginBottom: '24px' }}>
                
                {/* 1. Summary Card */}
                {(!aiSearch || 
                  (aiData.summary && aiData.summary.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  (aiData.job_role && aiData.job_role.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  (aiData.current_company && aiData.current_company.toLowerCase().includes(aiSearch.toLowerCase()))
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('summary')}>
                      <h4 className="gemini-card-header-title">
                        👤 Professional Summary & Job Profile
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.summary ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.summary && (
                      <div style={{ marginTop: '12px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '16px' }}>
                          <div>
                            <span className="gemini-field-label">Expected/Target Job Role:</span>
                            <div className="gemini-field-value">{aiData.job_role || 'Not specified'}</div>
                          </div>
                          <div>
                            <span className="gemini-field-label">Total Experience Stated:</span>
                            <div className="gemini-field-value">{aiData.years_of_experience || 'Not specified'}</div>
                          </div>
                          <div>
                            <span className="gemini-field-label">Current Company & Designation:</span>
                            <div className="gemini-field-value">
                              {aiData.current_company || aiData.current_designation ? `${aiData.current_designation || 'Role'} at ${aiData.current_company || 'Company'}` : 'Not specified'}
                            </div>
                          </div>
                        </div>
                        <div>
                          <span className="gemini-field-label">Summary:</span>
                          <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '4px 0 0 0', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                            {aiData.summary || 'No summary available.'}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 2. Skills Card */}
                {(!aiSearch || 
                  aiData.skills?.some(s => s.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.technical_skills?.some(s => s.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.soft_skills?.some(s => s.toLowerCase().includes(aiSearch.toLowerCase()))
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('skills')}>
                      <h4 className="gemini-card-header-title">
                        🛠️ Skills Inventory
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.skills ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.skills && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {aiData.technical_skills && aiData.technical_skills.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>Technical Skills:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {aiData.technical_skills.filter(s => !aiSearch || s.toLowerCase().includes(aiSearch.toLowerCase())).map((skill, idx) => (
                                <span key={idx} className="gemini-tag-tech">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {aiData.soft_skills && aiData.soft_skills.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>Soft Skills:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {aiData.soft_skills.filter(s => !aiSearch || s.toLowerCase().includes(aiSearch.toLowerCase())).map((skill, idx) => (
                                <span key={idx} className="gemini-tag-soft">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {aiData.skills && aiData.skills.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>General/Other Skills:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {aiData.skills.filter(s => !aiSearch || s.toLowerCase().includes(aiSearch.toLowerCase())).map((skill, idx) => (
                                <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 10px', background: 'var(--glass-bg)', color: 'var(--text-color)', borderRadius: '6px', border: '1px solid var(--glass-border)', fontWeight: 600 }}>
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 3. Experience Card */}
                {(!aiSearch || 
                  aiData.experience?.some(exp => 
                    exp.company?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                    exp.designation?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                    exp.description?.toLowerCase().includes(aiSearch.toLowerCase())
                  )
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('experience')}>
                      <h4 className="gemini-card-header-title">
                        💼 Professional Experience ({aiData.experience?.length || 0})
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.experience ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.experience && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {aiData.experience && aiData.experience.length > 0 ? (
                          aiData.experience.filter(exp => 
                            !aiSearch || 
                            exp.company?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                            exp.designation?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                            exp.description?.toLowerCase().includes(aiSearch.toLowerCase())
                          ).map((exp, idx) => (
                            <div key={idx} style={{ padding: '12px', background: 'var(--glass-bg)', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-color)' }}>
                                  {exp.designation || 'Position'}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                                  {exp.start_date || 'Start'} – {exp.end_date || 'Present'}
                                </div>
                              </div>
                              <div style={{ fontSize: '0.8rem', color: 'var(--primary)', marginBottom: '8px', fontWeight: 600 }}>
                                🏢 {exp.company || 'Company'}
                              </div>
                              {exp.description && (
                                <p style={{ fontSize: '0.8rem', color: 'var(--subtext-color)', margin: 0, lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                                  {exp.description}
                                </p>
                              )}
                            </div>
                          ))
                        ) : (
                          <div style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>No work experience detected.</div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 4. Education Card */}
                {(!aiSearch || 
                  aiData.education?.some(edu => 
                    edu.institution?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                    edu.degree?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                    edu.field_of_study?.toLowerCase().includes(aiSearch.toLowerCase())
                  )
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('education')}>
                      <h4 className="gemini-card-header-title">
                        🎓 Education History ({aiData.education?.length || 0})
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.education ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.education && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {aiData.education && aiData.education.length > 0 ? (
                          aiData.education.filter(edu => 
                            !aiSearch || 
                            edu.institution?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                            edu.degree?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                            edu.field_of_study?.toLowerCase().includes(aiSearch.toLowerCase())
                          ).map((edu, idx) => (
                            <div key={idx} style={{ padding: '12px', background: 'var(--glass-bg)', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-color)' }}>
                                  {edu.degree || 'Degree'} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                                  {edu.start_year || 'Start'} – {edu.end_year || 'Completed'}
                                </div>
                              </div>
                              <div style={{ fontSize: '0.8rem', color: 'var(--primary)', margin: 0, fontWeight: 600 }}>
                                🏫 {edu.institution || 'Institution'}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>No education records detected.</div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 5. Projects Card */}
                {(!aiSearch || 
                  aiData.projects?.some(proj => 
                    proj.title?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                    proj.description?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                    proj.technologies?.some(t => t.toLowerCase().includes(aiSearch.toLowerCase()))
                  )
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('projects')}>
                      <h4 className="gemini-card-header-title">
                        💻 Key Projects ({aiData.projects?.length || 0})
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.projects ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.projects && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {aiData.projects && aiData.projects.length > 0 ? (
                          aiData.projects.filter(proj => 
                            !aiSearch || 
                            proj.title?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                            proj.description?.toLowerCase().includes(aiSearch.toLowerCase()) ||
                            proj.technologies?.some(t => t.toLowerCase().includes(aiSearch.toLowerCase()))
                          ).map((proj, idx) => (
                            <div key={idx} style={{ padding: '12px', background: 'var(--glass-bg)', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-color)', marginBottom: '8px' }}>
                                🚀 {proj.title || 'Project Title'}
                              </div>
                              {proj.description && (
                                <p style={{ fontSize: '0.8rem', color: 'var(--subtext-color)', margin: '0 0 10px 0', lineHeight: '1.5' }}>
                                  {proj.description}
                                </p>
                              )}
                              {proj.technologies && proj.technologies.length > 0 && (
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                  {proj.technologies.map((tech, tIdx) => (
                                    <span key={tIdx} style={{ fontSize: '0.7rem', padding: '2px 6px', background: 'rgba(139, 92, 246, 0.1)', color: 'var(--primary)', borderRadius: '4px', border: '1px solid rgba(139, 92, 246, 0.2)', fontWeight: 600 }}>
                                      {tech}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))
                        ) : (
                          <div style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>No projects detected.</div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 6. Certifications & Awards Card */}
                {(!aiSearch || 
                  aiData.certifications?.some(c => c.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.awards?.some(a => a.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.achievements?.some(a => a.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.publications?.some(p => p.toLowerCase().includes(aiSearch.toLowerCase()))
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('certifications')}>
                      <h4 className="gemini-card-header-title">
                        🏆 Certifications, Awards & Achievements
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.certifications ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.certifications && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {aiData.certifications && aiData.certifications.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>📜 Certifications:</span>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.8rem', color: 'var(--text-color)' }}>
                              {aiData.certifications.filter(c => !aiSearch || c.toLowerCase().includes(aiSearch.toLowerCase())).map((cert, idx) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{cert}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {aiData.awards && aiData.awards.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>🏅 Awards & Honors:</span>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.8rem', color: 'var(--text-color)' }}>
                              {aiData.awards.filter(a => !aiSearch || a.toLowerCase().includes(aiSearch.toLowerCase())).map((award, idx) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{award}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {aiData.achievements && aiData.achievements.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>🎯 Key Achievements:</span>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.8rem', color: 'var(--text-color)' }}>
                              {aiData.achievements.filter(a => !aiSearch || a.toLowerCase().includes(aiSearch.toLowerCase())).map((ach, idx) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{ach}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {aiData.publications && aiData.publications.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>📚 Publications & Papers:</span>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.8rem', color: 'var(--text-color)' }}>
                              {aiData.publications.filter(p => !aiSearch || p.toLowerCase().includes(aiSearch.toLowerCase())).map((pub, idx) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{pub}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {(!aiData.certifications?.length && !aiData.awards?.length && !aiData.achievements?.length && !aiData.publications?.length) && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>No awards or certifications detected.</div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 7. Others & References Card */}
                {(!aiSearch || 
                  aiData.languages?.some(l => l.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.hobbies?.some(h => h.toLowerCase().includes(aiSearch.toLowerCase())) ||
                  aiData.references?.some(r => r.name?.toLowerCase().includes(aiSearch.toLowerCase()) || r.contact?.toLowerCase().includes(aiSearch.toLowerCase()))
                ) && (
                  <div className="gemini-info-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleAiSection('others')}>
                      <h4 className="gemini-card-header-title">
                        🌐 Languages, Hobbies & References
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>{aiCollapsedSections.others ? '➕' : '➖'}</span>
                    </div>
                    {!aiCollapsedSections.others && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {aiData.languages && aiData.languages.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>🗣️ Languages Spoken:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {aiData.languages.filter(l => !aiSearch || l.toLowerCase().includes(aiSearch.toLowerCase())).map((lang, idx) => (
                                <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'var(--glass-bg)', color: 'var(--text-color)', borderRadius: '6px', border: '1px solid var(--glass-border)', fontWeight: 600 }}>
                                  {lang}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {aiData.hobbies && aiData.hobbies.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>🎨 Hobbies & Interests:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {aiData.hobbies.filter(h => !aiSearch || h.toLowerCase().includes(aiSearch.toLowerCase())).map((hob, idx) => (
                                <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'var(--glass-bg)', color: 'var(--text-color)', borderRadius: '6px', border: '1px solid var(--glass-border)', fontWeight: 600 }}>
                                  {hob}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {aiData.references && aiData.references.length > 0 && (
                          <div>
                            <span className="gemini-field-label" style={{ marginBottom: '6px' }}>📞 References:</span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                              {aiData.references.filter(r => !aiSearch || r.name?.toLowerCase().includes(aiSearch.toLowerCase()) || r.contact?.toLowerCase().includes(aiSearch.toLowerCase())).map((ref, idx) => (
                                <div key={idx} style={{ padding: '8px 12px', background: 'var(--glass-bg)', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid var(--glass-border)' }}>
                                  <div style={{ fontWeight: 600, color: 'var(--text-color)' }}>{ref.name || 'Reference Person'}</div>
                                  {ref.relationship && <div style={{ color: 'var(--primary)', fontSize: '0.75rem' }}>{ref.relationship}</div>}
                                  {ref.contact && <div style={{ color: 'var(--subtext-color)', marginTop: '2px' }}>Contact: {ref.contact}</div>}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {(!aiData.languages?.length && !aiData.hobbies?.length && !aiData.references?.length) && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--subtext-color)' }}>No languages, hobbies or references detected.</div>
                        )}
                      </div>
                    )}
                  </div>
                )}

              </div>

              {/* Raw JSON Viewer */}
              <div className="extraction-viewer-container">
                <div className="extraction-viewer-header">
                  <span className="extraction-viewer-meta">
                    Model: {resume.ai_model || 'gemini-1.5-flash'} | Prompt: {resume.ai_prompt_version || 'v1'} | Time: {resume.ai_processing_time}s
                  </span>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={handleCopyAiJSON} className="btn-small" style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--white)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                      {aiCopied ? (
                        <>
                          <HiOutlineCheck size={14} /> Copied
                        </>
                      ) : (
                        <>
                          <HiOutlineDocumentDuplicate size={14} /> Copy JSON
                        </>
                      )}
                    </button>
                    <button onClick={handleDownloadAiJSON} className="btn-small" style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--white)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                      <HiOutlineArrowDownTray size={14} /> Download JSON
                    </button>
                  </div>
                </div>
                <textarea 
                  className="code-json-viewer color-ai" 
                  value={JSON.stringify(aiData, null, 2)} 
                  readOnly 
                />
              </div>
            </div>
          )}

          {resume.ai_status === 'pending' && !aiAnalyzing && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                {resume.extraction_status === 'completed' 
                  ? 'This resume text is ready for Gemini AI Parsing. Click "Run AI Parsing" above to process.' 
                  : 'Please extract resume text first before running Gemini AI Parsing.'}
              </p>
            </div>
          )}

          {aiAnalyzing && (
            <div style={{ padding: '40px 20px', textAlign: 'center' }}>
              <div className="skeleton-row" style={{ height: '20px', width: '50%', margin: '0 auto 12px', background: 'linear-gradient(90deg, rgba(139, 92, 246, 0.1) 25%, rgba(139, 92, 246, 0.2) 50%, rgba(139, 92, 246, 0.1) 75%)' }}></div>
              <div className="skeleton-row" style={{ height: '120px', width: '100%', margin: '0 auto', background: 'linear-gradient(90deg, rgba(139, 92, 246, 0.1) 25%, rgba(139, 92, 246, 0.2) 50%, rgba(139, 92, 246, 0.1) 75%)' }}></div>
            </div>
          )}
        </div>

        {/* Master Profile Validation Engine Panel */}
        <div className="details-card" style={{ marginTop: '32px', width: '100%', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
            <div>
              <h3 className="history-card-title" style={{ margin: 0, color: '#10B981' }}>
                Master Resume Validation Engine (Phase 9)
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>
                Consolidate and normalize Regex, spaCy, and Gemini data into a canonical profile.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span className={`badge-status ${
                resume.validation_status === 'completed' ? 'completed' :
                resume.validation_status === 'processing' ? 'processing' :
                resume.validation_status === 'failed' ? 'failed' : 'pending'
              }`}>
                {resume.validation_status ? resume.validation_status.toUpperCase() : 'PENDING'}
              </span>
              
              {resume.validation_status === 'completed' && (
                <button
                  onClick={() => navigate(`/profile/review?resume_id=${resume.id}`)}
                  className="btn-large btn-large-primary"
                  style={{
                    padding: '8px 16px',
                    fontSize: '0.875rem',
                    width: 'auto',
                    display: 'flex',
                    gap: '8px',
                    alignItems: 'center',
                    margin: 0,
                    background: 'linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)',
                    borderColor: '#06B6D4'
                  }}
                >
                  <HiOutlineCheck size={18} /> Review & Verify Profile
                </button>
              )}

              <button 
                onClick={handleRunMasterMerge} 
                className="btn-large btn-large-primary" 
                style={{ 
                  padding: '8px 16px', 
                  fontSize: '0.875rem', 
                  width: 'auto', 
                  display: 'flex', 
                  gap: '8px', 
                  alignItems: 'center', 
                  margin: 0,
                  background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                  borderColor: '#10B981'
                }}
                disabled={masterMerging || resume.validation_status === 'processing' || resume.ai_status !== 'completed'}
                title={resume.ai_status !== 'completed' ? 'Please run AI Parsing first.' : 'Generate Master Profile'}
              >
                {masterMerging ? (
                  <>
                    <span className="spinner-border spinner-border-sm" style={{ width: '1rem', height: '1rem' }} /> Merging...
                  </>
                ) : (
                  <>
                    <HiOutlineSparkles size={18} /> Generate Master Profile
                  </>
                )}
              </button>
            </div>
          </div>

          {masterError && (
            <div className="auth-error" style={{ marginBottom: '20px' }}>
              {masterError}
            </div>
          )}

          {/* Completion Meter */}
          {(resume.validation_status === 'completed' || resume.validation_status === 'failed') && (
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', padding: '20px', borderRadius: '12px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--white)' }}>Resume Completion Meter</span>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#10B981' }}>{resume.completion_percentage}%</span>
              </div>
              <div style={{ width: '100%', height: '10px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '5px', overflow: 'hidden' }}>
                <div style={{ 
                  width: `${resume.completion_percentage}%`, 
                  height: '100%', 
                  background: `linear-gradient(90deg, #F59E0B 0%, #10B981 ${resume.completion_percentage}%)`,
                  borderRadius: '5px',
                  transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
                }}></div>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--gray-400)', marginTop: '8px', marginBottom: 0 }}>
                Completion score is calculated based on presence of key fields: Personal Info (15%), Summary (10%), Skills (15%), Experience (20%), Education (15%), Projects (10%), Certifications (10%), and Languages (5%).
              </p>
            </div>
          )}

          {resume.validation_status === 'completed' && masterData && (
            <div style={{ marginTop: '24px' }}>
              {/* Grid of Sections */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', marginBottom: '24px' }}>
                
                {/* 1. Personal & Contact Card */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('personal')}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      👤 Personal Details & Contact Information
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.personal ? '➕' : '➖'}</span>
                  </div>
                  {!masterCollapsedSections.personal && (
                    <div style={{ marginTop: '12px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', fontSize: '0.85rem' }}>
                      <div><strong>Full Name:</strong> {masterData.name || 'Not Provided'}</div>
                      <div><strong>Email:</strong> {masterData.email || 'Not Provided'}</div>
                      <div><strong>Phone:</strong> {masterData.phone || 'Not Provided'}</div>
                      <div>
                        <strong>LinkedIn:</strong> {masterData.linkedin ? (
                          <a href={masterData.linkedin} target="_blank" rel="noopener noreferrer" style={{ color: '#10B981', textDecoration: 'underline' }}>View Profile</a>
                        ) : 'Not Provided'}
                      </div>
                      <div>
                        <strong>GitHub:</strong> {masterData.github ? (
                          <a href={masterData.github} target="_blank" rel="noopener noreferrer" style={{ color: '#10B981', textDecoration: 'underline' }}>View Profile</a>
                        ) : 'Not Provided'}
                      </div>
                      <div>
                        <strong>Portfolio:</strong> {masterData.portfolio ? (
                          <a href={masterData.portfolio} target="_blank" rel="noopener noreferrer" style={{ color: '#10B981', textDecoration: 'underline' }}>Visit Site</a>
                        ) : 'Not Provided'}
                      </div>
                      {masterData.personal_website && (
                        <div>
                          <strong>Personal Website:</strong> <a href={masterData.personal_website} target="_blank" rel="noopener noreferrer" style={{ color: '#10B981', textDecoration: 'underline' }}>Visit Site</a>
                        </div>
                      )}
                      {masterData.stackoverflow && (
                        <div>
                          <strong>StackOverflow:</strong> <a href={masterData.stackoverflow} target="_blank" rel="noopener noreferrer" style={{ color: '#10B981', textDecoration: 'underline' }}>View Profile</a>
                        </div>
                      )}
                      <div><strong>Address:</strong> {masterData.address || 'Not Provided'}</div>
                      <div><strong>Pincode:</strong> {masterData.pincode || 'Not Provided'}</div>
                    </div>
                  )}
                </div>

                {/* 2. Professional Summary */}
                {masterData.summary && (
                  <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', color: '#10B981' }}>📝 Professional Summary</h4>
                    <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--gray-300)', lineHeight: '1.6' }}>{masterData.summary}</p>
                  </div>
                )}

                {/* 3. Skill Inventory */}
                {((masterData.skills && masterData.skills.length > 0) || 
                  (masterData.technical_skills && masterData.technical_skills.length > 0) || 
                  (masterData.soft_skills && masterData.soft_skills.length > 0)) && (
                  <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('skills')}>
                      <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        🛠️ Skill Inventory
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.skills ? '➕' : '➖'}</span>
                    </div>
                    {!masterCollapsedSections.skills && (
                      <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {masterData.technical_skills && masterData.technical_skills.length > 0 && (
                          <div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Technical Skills:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {masterData.technical_skills.map((skill, idx) => (
                                <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'rgba(16, 185, 129, 0.1)', color: '#34D399', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {masterData.soft_skills && masterData.soft_skills.length > 0 && (
                          <div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Soft Skills:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {masterData.soft_skills.map((skill, idx) => (
                                <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--white)', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {masterData.skills && masterData.skills.length > 0 && (
                          <div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>General Skills:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {masterData.skills.map((skill, idx) => (
                                <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--white)', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 4. Experience Card */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('experience')}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      💼 Professional Experience
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.experience ? '➕' : '➖'}</span>
                  </div>
                  {!masterCollapsedSections.experience && (
                    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {masterData.experience && masterData.experience.length > 0 ? (
                        masterData.experience.map((exp, idx) => (
                          <div key={idx} style={{ borderLeft: '2px solid #10B981', paddingLeft: '12px', fontSize: '0.85rem' }}>
                            <div style={{ fontWeight: 600, color: 'white', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
                              <span>{exp.designation || 'Position'} @ {exp.company || 'Company'}</span>
                              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>
                                {exp.start_date || '?'} - {exp.end_date || 'Present'}
                              </span>
                            </div>
                            {exp.description && (
                              <p style={{ margin: '6px 0 0 0', color: 'var(--gray-300)', fontSize: '0.8rem', lineHeight: '1.5' }}>
                                {exp.description}
                              </p>
                            )}
                          </div>
                        ))
                      ) : (
                        <div style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>No work history detected.</div>
                      )}
                    </div>
                  )}
                </div>

                {/* 5. Education Card */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('education')}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      🎓 Education History
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.education ? '➕' : '➖'}</span>
                  </div>
                  {!masterCollapsedSections.education && (
                    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {masterData.education && masterData.education.length > 0 ? (
                        masterData.education.map((edu, idx) => (
                          <div key={idx} style={{ borderLeft: '2px solid #10B981', paddingLeft: '12px', fontSize: '0.85rem' }}>
                            <div style={{ fontWeight: 600, color: 'white', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
                              <span>{edu.degree || 'Degree'} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}</span>
                              <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>
                                {edu.start_year || '?'} - {edu.end_year || '?'}
                              </span>
                            </div>
                            <div style={{ color: 'var(--gray-300)', fontSize: '0.8rem', marginTop: '2px' }}>
                              {edu.institution || 'Institution'}
                            </div>
                          </div>
                        ))
                      ) : (
                        <div style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>No education history detected.</div>
                      )}
                    </div>
                  )}
                </div>

                {/* 6. Projects Card */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('projects')}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      📁 Projects
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.projects ? '➕' : '➖'}</span>
                  </div>
                  {!masterCollapsedSections.projects && (
                    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {masterData.projects && masterData.projects.length > 0 ? (
                        masterData.projects.map((proj, idx) => (
                          <div key={idx} style={{ borderLeft: '2px solid #10B981', paddingLeft: '12px', fontSize: '0.85rem' }}>
                            <div style={{ fontWeight: 600, color: 'white' }}>{proj.title || 'Project'}</div>
                            {proj.description && (
                              <p style={{ margin: '4px 0', color: 'var(--gray-300)', fontSize: '0.8rem', lineHeight: '1.5' }}>
                                {proj.description}
                              </p>
                            )}
                            {proj.technologies && proj.technologies.length > 0 && (
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
                                {proj.technologies.map((tech, tIdx) => (
                                  <span key={tIdx} style={{ fontSize: '0.7rem', padding: '2px 6px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--gray-300)', borderRadius: '4px', border: '1px solid var(--glass-border)' }}>
                                    {tech}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))
                      ) : (
                        <div style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>No projects detected.</div>
                      )}
                    </div>
                  )}
                </div>

                {/* 7. Certifications & Languages Card */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('certifications')}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      📜 Certifications & Languages
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.certifications ? '➕' : '➖'}</span>
                  </div>
                  {!masterCollapsedSections.certifications && (
                    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {masterData.certifications && masterData.certifications.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Certifications:</span>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.8rem', color: 'var(--gray-200)' }}>
                            {masterData.certifications.map((cert, idx) => (
                              <div key={idx}>✓ {cert}</div>
                            ))}
                          </div>
                        </div>
                      )}
                      {masterData.languages && masterData.languages.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Languages:</span>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {masterData.languages.map((lang, idx) => (
                              <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'rgba(255,255,255,0.05)', color: 'var(--white)', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                                {lang}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {(!masterData.certifications?.length && !masterData.languages?.length) && (
                        <div style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>No certifications or languages detected.</div>
                      )}
                    </div>
                  )}
                </div>

                {/* 8. Hobbies, Publications, Achievements & References */}
                <div className="info-card-sub" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleMasterSection('others')}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      🌐 Hobbies, Publications & References
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)' }}>{masterCollapsedSections.others ? '➕' : '➖'}</span>
                  </div>
                  {!masterCollapsedSections.others && (
                    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {masterData.hobbies && masterData.hobbies.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Hobbies & Interests:</span>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {masterData.hobbies.map((hob, idx) => (
                              <span key={idx} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'rgba(255,255,255,0.05)', color: 'var(--white)', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
                                {hob}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {masterData.publications && masterData.publications.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Publications:</span>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.8rem', color: 'var(--gray-200)' }}>
                            {masterData.publications.map((pub, idx) => (
                              <div key={idx}>• {pub}</div>
                            ))}
                          </div>
                        </div>
                      )}
                      {masterData.achievements && masterData.achievements.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>Achievements:</span>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.8rem', color: 'var(--gray-200)' }}>
                            {masterData.achievements.map((ach, idx) => (
                              <div key={idx}>• {ach}</div>
                            ))}
                          </div>
                        </div>
                      )}
                      {masterData.references && masterData.references.length > 0 && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block', marginBottom: '6px' }}>References:</span>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {masterData.references.map((ref, idx) => (
                              <div key={idx} style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.15)', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid var(--glass-border)' }}>
                                <div style={{ fontWeight: 600, color: 'white' }}>{ref.name || 'Reference Person'}</div>
                                {ref.company && <div style={{ color: '#10B981', fontSize: '0.75rem' }}>{ref.company}</div>}
                                {ref.contact && <div style={{ color: 'var(--gray-300)', marginTop: '2px' }}>Contact: {ref.contact}</div>}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

              </div>

              {/* Raw JSON Viewer */}
              <div className="text-viewer-container" style={{ border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <div className="text-viewer-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 16px', background: 'rgba(16, 185, 129, 0.05)', borderBottom: '1px solid rgba(16, 185, 129, 0.2)', borderTopLeftRadius: '12px', borderTopRightRadius: '12px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', fontFamily: 'monospace' }}>
                    Validation Engine | Checked: {formatDate(resume.validation_time)}
                  </span>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={handleCopyMasterJSON} className="btn-small" style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--white)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                      {masterCopied ? (
                        <>
                          <HiOutlineCheck size={14} /> Copied
                        </>
                      ) : (
                        <>
                          <HiOutlineDocumentDuplicate size={14} /> Copy JSON
                        </>
                      )}
                    </button>
                    <button onClick={handleDownloadMasterJSON} className="btn-small" style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--white)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                      <HiOutlineArrowDownTray size={14} /> Download JSON
                    </button>
                  </div>
                </div>
                <textarea 
                  className="code-json-viewer color-master" 
                  value={JSON.stringify(masterData, null, 2)} 
                  readOnly 
                />
              </div>
            </div>
          )}

          {resume.validation_status === 'pending' && !masterMerging && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                {resume.ai_status === 'completed' 
                  ? 'All parsed sources (Regex, spaCy, and Gemini) are ready. Click "Generate Master Profile" to build the canonical profile.' 
                  : 'Please complete all parsing engines first (Text, Regex, spaCy, and AI) before building the Master Profile.'}
              </p>
            </div>
          )}

          {masterMerging && (
            <div style={{ padding: '40px 20px', textAlign: 'center' }}>
              <div className="skeleton-row" style={{ height: '20px', width: '50%', margin: '0 auto 12px', background: 'linear-gradient(90deg, rgba(16, 185, 129, 0.1) 25%, rgba(16, 185, 129, 0.2) 50%, rgba(16, 185, 129, 0.1) 75%)' }}></div>
              <div className="skeleton-row" style={{ height: '120px', width: '100%', margin: '0 auto', background: 'linear-gradient(90deg, rgba(16, 185, 129, 0.1) 25%, rgba(16, 185, 129, 0.2) 50%, rgba(16, 185, 129, 0.1) 75%)' }}></div>
            </div>
          )}
        </div>

        {/* ATS Resume Analysis Engine (Phase 11) */}
        <div className="details-card" style={{ marginTop: '32px', width: '100%', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
            <div>
              <h3 className="history-card-title" style={{ margin: 0, color: '#A78BFA' }}>
                ATS Resume Analysis Engine (Phase 11)
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--gray-400)', marginTop: '4px' }}>
                Measure candidate compatibility, keyword scoring, grammar analysis, and view real-time recommendations.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              {atsScoreData && (
                <button
                  onClick={() => navigate(`/resumes/${resume.id}/ats`)}
                  className="btn-large btn-large-primary"
                  style={{
                    padding: '8px 16px',
                    fontSize: '0.875rem',
                    width: 'auto',
                    display: 'flex',
                    gap: '8px',
                    alignItems: 'center',
                    margin: 0,
                    background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                    borderColor: '#3B82F6'
                  }}
                >
                  <HiOutlineCpuChip size={18} /> View ATS Dashboard
                </button>
              )}
              
              <button 
                onClick={handleRunATSAnalysis} 
                className="btn-large btn-large-primary" 
                style={{ 
                  padding: '8px 16px', 
                  fontSize: '0.875rem', 
                  width: 'auto', 
                  display: 'flex', 
                  gap: '8px', 
                  alignItems: 'center', 
                  margin: 0,
                  background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
                  borderColor: '#8B5CF6'
                }}
                disabled={atsRunning || resume.validation_status !== 'completed'}
                title={resume.validation_status !== 'completed' ? 'Please generate and verify Master Profile first.' : 'Analyze Resume'}
              >
                {atsRunning ? (
                  <>
                    <span className="spinner-border spinner-border-sm" style={{ width: '1rem', height: '1rem' }} /> Scoring...
                  </>
                ) : (
                  <>
                    <HiOutlineSparkles size={18} /> Run ATS Analysis
                  </>
                )}
              </button>
            </div>
          </div>

          {atsError && (
            <div className="auth-error" style={{ marginBottom: '20px' }}>
              {atsError}
            </div>
          )}

          {resume.validation_status !== 'completed' ? (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                Please generate and verify the Master Resume Profile above before running the ATS analysis.
              </p>
            </div>
          ) : atsScoreData ? (
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--glass-border)', padding: '20px', borderRadius: '12px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'center' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block' }}>OVERALL ATS SCORE</span>
                  <span style={{ fontSize: '2rem', fontWeight: 800, color: '#A78BFA' }}>
                    {Math.round(atsScoreData.ats_score)}/100
                  </span>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block' }}>PRIMARY INDUSTRY</span>
                  <span style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--white)' }}>
                    {atsScoreData.ats_json?.metadata?.primary_industry || 'Software Engineering'}
                  </span>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)', display: 'block' }}>SUGGESTIONS</span>
                  <span style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F59E0B' }}>
                    {atsScoreData.suggestions?.length || 0} items to optimize
                  </span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <button 
                    onClick={() => navigate(`/resumes/${resume.id}/ats`)}
                    className="btn btn-outline-light btn-sm"
                    style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                  >
                    View Interactive Dashboard →
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--gray-400)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                Profile is verified. Click "Run ATS Analysis" above to calculate and review your compatibility score.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumeDetails;

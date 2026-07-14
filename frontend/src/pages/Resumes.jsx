import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import resumesAPI from '../api/resumes';
import GlassCard from '../components/GlassCard';
import GlassInput from '../components/GlassInput';
import GlassTable from '../components/GlassTable';
import SkeletonLoader from '../components/SkeletonLoader';
import {
  HiOutlineCloudArrowUp,
  HiOutlineArrowDownTray,
  HiOutlineTrash,
  HiOutlineCheckBadge,
  HiOutlineEye,
  HiOutlineDocumentText
} from 'react-icons/hi2';

const Resumes = () => {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [customTitle, setCustomTitle] = useState('');

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      const response = await resumesAPI.getResumes();
      const data = response.data.results || response.data;
      setResumes(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load resumes:', err);
      showError('Failed to load resumes history.');
    } finally {
      setLoading(false);
    }
  };

  const showError = (msg) => {
    setErrorMessage(msg);
    setSuccessMessage('');
    setTimeout(() => setErrorMessage(''), 6000);
  };

  const showSuccess = (msg) => {
    setSuccessMessage(msg);
    setErrorMessage('');
    setTimeout(() => setSuccessMessage(''), 5000);
  };

  // Drag & Drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  const triggerBrowse = () => {
    fileInputRef.current.click();
  };

  const validateFile = (file) => {
    const allowedExtensions = ['.pdf', '.docx'];
    const allowedMimeTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowedExtensions.includes(fileExt) && !allowedMimeTypes.includes(file.type)) {
      return 'Only PDF (.pdf) and Word (.docx) files are supported.';
    }

    if (file.size < 1024) {
      return 'File size must be at least 1 KB.';
    }

    if (file.size > 10 * 1024 * 1024) {
      return 'File size exceeds the 10 MB limit.';
    }

    return null;
  };

  const uploadFile = async (file) => {
    const valError = validateFile(file);
    if (valError) {
      showError(valError);
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      setErrorMessage('');

      await resumesAPI.uploadResume(file, customTitle, (progress) => {
        setUploadProgress(progress);
      });

      showSuccess(`"${file.name}" uploaded successfully!`);
      setCustomTitle('');
      fetchResumes();
    } catch (err) {
      console.error('Upload failed:', err);
      const serverMsg = err.response?.data?.original_file?.[0] || err.response?.data?.detail || 'Upload failed.';
      showError(serverMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (id, filename) => {
    try {
      const response = await resumesAPI.downloadResume(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      showError('Failed to download resume file.');
    }
  };

  const handleActivate = async (e, id) => {
    e.stopPropagation();
    try {
      await resumesAPI.activateResume(id);
      showSuccess('Resume version activated successfully.');
      fetchResumes();
    } catch (err) {
      console.error('Activation failed:', err);
      showError('Failed to activate resume version.');
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this resume? (This is a soft-delete)')) {
      return;
    }

    try {
      await resumesAPI.deleteResume(id);
      showSuccess('Resume deleted.');
      fetchResumes();
    } catch (err) {
      console.error('Delete failed:', err);
      showError('Failed to delete resume.');
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: 0 }}>Resume Management</h1>
        <p style={{ color: 'var(--subtext-color)', margin: '4px 0 0', fontSize: '0.95rem' }}>
          Upload, analyze, and select active versions of your resumes securely.
        </p>
      </div>

      {/* Alerts */}
      {errorMessage && (
        <div className="glass-panel" style={{
          padding: '14px 20px',
          backgroundColor: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: '16px',
          color: 'var(--danger)',
          fontWeight: 500,
          fontSize: '0.9rem'
        }}>
          {errorMessage}
        </div>
      )}
      
      {successMessage && (
        <div className="glass-panel" style={{
          padding: '14px 20px',
          backgroundColor: 'rgba(34, 197, 94, 0.08)',
          border: '1px solid rgba(34, 197, 94, 0.25)',
          borderRadius: '16px',
          color: 'var(--success)',
          fontWeight: 500,
          fontSize: '0.9rem'
        }}>
          {successMessage}
        </div>
      )}

      {/* Grid: Upload Box + List History */}
      <div className="resumes-grid-container">
        
        {/* Upload Card */}
        <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', height: 'fit-content' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>Upload New Document</h3>
          
          <GlassInput
            label="Optional: Custom Title"
            type="text"
            placeholder="e.g. Senior Backend Architect - 2026"
            value={customTitle}
            onChange={(e) => setCustomTitle(e.target.value)}
            disabled={uploading}
            icon={<HiOutlineDocumentText size={18} />}
          />

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={triggerBrowse}
            style={{
              border: isDragging ? '2px dashed var(--primary)' : '2px dashed var(--glass-border)',
              borderRadius: '16px',
              padding: '40px 20px',
              textAlign: 'center',
              cursor: uploading ? 'not-allowed' : 'pointer',
              backgroundColor: isDragging ? 'rgba(37, 99, 235, 0.05)' : 'rgba(255, 255, 255, 0.02)',
              transition: 'all var(--transition-fast)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px'
            }}
            className="upload-dropzone"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".pdf,.docx"
              disabled={uploading}
              style={{ display: 'none' }}
            />
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'rgba(37, 99, 235, 0.08)',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <HiOutlineCloudArrowUp size={28} />
            </div>
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-color)', fontSize: '0.95rem' }}>Drag & Drop your resume here</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--subtext-color)', marginTop: '4px' }}>or click to browse from device</div>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--subtext-color)', opacity: 0.8, marginTop: '8px' }}>
              Supported formats: PDF, DOCX (1 KB - 10 MB)
            </div>
          </div>

          {uploading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-color)', fontWeight: 600 }}>
                <span>Uploading draft...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--glass-border)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${uploadProgress}%`, height: '100%', backgroundColor: 'var(--primary)', transition: 'width 0.1s ease-out' }}></div>
              </div>
            </div>
          )}
        </GlassCard>

        {/* History List Card */}
        <GlassCard hoverEffect={false} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>Version History</h3>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--subtext-color)',
              background: 'var(--glass-border)',
              padding: '3px 10px',
              borderRadius: '12px'
            }}>
              {resumes.length} {resumes.length === 1 ? 'version' : 'versions'}
            </span>
          </div>

          {loading ? (
            <SkeletonLoader type="table" />
          ) : resumes.length === 0 ? (
            <div style={{ padding: '60px 20px', textAlign: 'center', color: 'var(--subtext-color)' }}>
              <HiOutlineDocumentText size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-color)', margin: 0 }}>No Resumes Uploaded Yet</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--subtext-color)', marginTop: '6px', maxWidth: '300px', marginInline: 'auto' }}>
                Drag and drop your first resume draft on the left to initialize AI processing.
              </p>
            </div>
          ) : (
            <GlassTable headers={['Version', 'Document Details', 'Size', 'Status', 'Actions']}>
              {resumes.map((resume) => (
                <tr key={resume.id} onClick={() => navigate(`/resumes/${resume.id}`)} style={{ cursor: 'pointer' }}>
                  <td>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      fontFamily: 'var(--font-number)',
                      color: 'var(--primary)',
                      background: 'rgba(37, 99, 235, 0.08)',
                      padding: '2px 8px',
                      borderRadius: '6px'
                    }}>
                      v{resume.version}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-color)', fontSize: '0.9rem', marginBottom: '2px' }}>
                      {resume.resume_title || 'Untitled Resume'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--subtext-color)' }}>
                      Uploaded {formatDate(resume.upload_date)}
                    </div>
                  </td>
                  <td style={{ fontSize: '0.85rem', fontFamily: 'var(--font-number)' }}>
                    {formatBytes(resume.file_size)}
                  </td>
                  <td>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      whiteSpace: 'nowrap',
                      display: 'inline-flex',
                      alignItems: 'center',
                      lineHeight: '1.2',
                      color: resume.is_active ? 'var(--success)' : 'var(--subtext-color)',
                      background: resume.is_active ? 'rgba(34, 197, 94, 0.08)' : 'rgba(255,255,255,0.02)',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      border: resume.is_active ? '1px solid rgba(34, 197, 94, 0.2)' : '1px solid var(--glass-border)'
                    }}>
                      {resume.is_active ? 'Active Master' : 'Draft'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }} onClick={(e) => e.stopPropagation()}>
                      <Link to={`/resumes/${resume.id}`} className="glass-panel" style={{
                        padding: '6px',
                        borderRadius: '8px',
                        color: 'var(--text-color)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textDecoration: 'none'
                      }} title="View Pipeline Details">
                        <HiOutlineEye size={16} />
                      </Link>
                      
                      <button
                        className="glass-panel"
                        onClick={() => handleDownload(resume.id, resume.original_filename)}
                        style={{
                          padding: '6px',
                          borderRadius: '8px',
                          color: 'var(--text-color)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          border: 'none',
                          cursor: 'pointer'
                        }}
                        title="Download Document"
                      >
                        <HiOutlineArrowDownTray size={16} />
                      </button>

                      {!resume.is_active && (
                        <button
                          className="glass-panel"
                          onClick={(e) => handleActivate(e, resume.id)}
                          style={{
                            padding: '4px 10px',
                            borderRadius: '8px',
                            color: 'var(--success)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: 'none',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                          title="Activate Version"
                        >
                          Activate
                        </button>
                      )}

                      <button
                        className="glass-panel"
                        onClick={(e) => handleDelete(e, resume.id)}
                        style={{
                          padding: '6px',
                          borderRadius: '8px',
                          color: 'var(--danger)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          border: 'none',
                          cursor: 'pointer'
                        }}
                        title="Delete Draft"
                      >
                        <HiOutlineTrash size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </GlassTable>
          )}
        </GlassCard>
      </div>

      <style>{`
        .upload-dropzone:hover {
          border-color: var(--primary) !important;
          background-color: rgba(37, 99, 235, 0.04) !important;
        }
      `}</style>
    </div>
  );
};

export default Resumes;

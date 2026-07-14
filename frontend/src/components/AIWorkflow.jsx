import { motion } from 'framer-motion';
import {
  HiOutlineDocumentArrowUp,
  HiOutlineDocumentText,
  HiOutlineCpuChip,
  HiOutlineSparkles,
  HiOutlineCheckCircle,
  HiOutlineCommandLine,
  HiOutlineDocumentCheck
} from 'react-icons/hi2';

const AIWorkflow = ({ currentStage = 'upload' }) => {
  const stages = [
    { id: 'upload', label: 'Upload', icon: <HiOutlineDocumentArrowUp size={20} /> },
    { id: 'extract', label: 'Extract Text', icon: <HiOutlineDocumentText size={20} /> },
    { id: 'regex', label: 'Regex', icon: <HiOutlineCommandLine size={20} /> },
    { id: 'spacy', label: 'spaCy NER', icon: <HiOutlineCpuChip size={20} /> },
    { id: 'gemini', label: 'Gemini AI', icon: <HiOutlineSparkles size={20} /> },
    { id: 'validation', label: 'Validation', icon: <HiOutlineDocumentCheck size={20} /> },
    { id: 'master', label: 'Master Resume', icon: <HiOutlineCheckCircle size={20} /> },
  ];

  const getStageIndex = (stageId) => stages.findIndex((s) => s.id === stageId);
  const currentIndex = getStageIndex(currentStage);

  const getStatus = (index) => {
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'current';
    return 'pending';
  };

  const getStatusColors = (status) => {
    switch (status) {
      case 'completed':
        return {
          bg: 'rgba(34, 197, 94, 0.08)',
          border: 'rgba(34, 197, 94, 0.3)',
          text: 'var(--success)',
          glow: '0 0 15px rgba(34, 197, 94, 0.15)'
        };
      case 'current':
        return {
          bg: 'rgba(37, 99, 235, 0.08)',
          border: 'var(--primary)',
          text: 'var(--primary)',
          glow: '0 0 20px rgba(37, 99, 235, 0.25)'
        };
      case 'pending':
      default:
        return {
          bg: 'rgba(255, 255, 255, 0.02)',
          border: 'var(--glass-border)',
          text: 'var(--subtext-color)',
          glow: 'none'
        };
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-color)' }}>
        AI Parsing Pipeline
      </h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
        gap: '12px',
        width: '100%'
      }}>
        {stages.map((stage, index) => {
          const status = getStatus(index);
          const colors = getStatusColors(status);

          return (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-panel"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '16px 12px',
                textAlign: 'center',
                backgroundColor: colors.bg,
                borderColor: colors.border,
                boxShadow: colors.glow,
                gap: '10px',
                position: 'relative'
              }}
            >
              {/* Connector Line (except for last item) */}
              {index < stages.length - 1 && (
                <div className="hide-on-mobile" style={{
                  position: 'absolute',
                  right: '-12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '12px',
                  height: '2px',
                  backgroundColor: index < currentIndex ? 'var(--success)' : 'var(--glass-border)',
                  zIndex: 2
                }} />
              )}
              
              <div style={{
                color: colors.text,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {stage.icon}
              </div>
              
              <span style={{
                fontSize: '0.8rem',
                fontWeight: 600,
                color: colors.text
              }}>
                {stage.label}
              </span>

              {status === 'completed' && (
                <span style={{
                  position: 'absolute',
                  top: '6px',
                  right: '6px',
                  color: 'var(--success)',
                  fontSize: '0.75rem',
                  lineHeight: 1
                }}>
                  ✓
                </span>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default AIWorkflow;

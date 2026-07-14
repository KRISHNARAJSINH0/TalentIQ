/**
 * FeaturesSection Component
 * Feature cards grid with icons and hover animations.
 */

import { motion } from 'framer-motion';
import {
  HiOutlineDocumentText,
  HiOutlineSparkles,
  HiOutlineGlobeAlt,
  HiOutlineChartBar,
  HiOutlineShieldCheck,
  HiOutlineBolt,
} from 'react-icons/hi2';

const features = [
  {
    icon: <HiOutlineDocumentText />,
    title: 'Smart Resume Parsing',
    description:
      'Upload any resume format and our AI extracts structured data instantly — skills, experience, education, and more.',
  },
  {
    icon: <HiOutlineSparkles />,
    title: 'AI-Powered Analysis',
    description:
      'Leverage Google Gemini AI to analyze resume content, suggest improvements, and optimize for target roles.',
  },
  {
    icon: <HiOutlineGlobeAlt />,
    title: 'Portfolio Builder',
    description:
      'Generate beautiful, responsive portfolio websites from your parsed resume data with one click.',
  },
  {
    icon: <HiOutlineChartBar />,
    title: 'ATS Optimization',
    description:
      'Score your resume against ATS systems and get actionable feedback to increase your interview chances.',
  },
  {
    icon: <HiOutlineShieldCheck />,
    title: 'Secure & Private',
    description:
      'Your data is encrypted and never shared. Full control over your information with GDPR compliance.',
  },
  {
    icon: <HiOutlineBolt />,
    title: 'Lightning Fast',
    description:
      'Process resumes in seconds, not minutes. Our optimized pipeline delivers results at blazing speed.',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' },
  },
};

const FeaturesSection = () => {
  return (
    <section className="features" id="features">
      <div className="container">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Everything You Need to{' '}
          <span className="gradient-text">Stand Out</span>
        </motion.h2>

        <motion.p
          className="section-subtitle"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          From parsing to portfolio, ResumeAI handles your entire career
          toolkit with cutting-edge artificial intelligence.
        </motion.p>
      </div>

      <motion.div
        className="features-grid container"
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-100px' }}
      >
        {features.map((feature, index) => (
          <motion.div
            key={index}
            className="feature-card"
            variants={cardVariants}
          >
            <div className="feature-icon">{feature.icon}</div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
};

export default FeaturesSection;

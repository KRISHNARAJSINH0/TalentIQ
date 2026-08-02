/**
 * FeaturesSection Component – Premium Redesign
 * Feature cards + How-It-Works + Workflow steps.
 */

import { motion } from 'framer-motion';
import {
  HiOutlineDocumentText,
  HiOutlineSparkles,
  HiOutlineGlobeAlt,
  HiOutlineChartBar,
  HiOutlineShieldCheck,
  HiOutlineBolt,
  HiOutlineTrophy,
  HiOutlineAcademicCap,
} from 'react-icons/hi2';

const features = [
  {
    icon: <HiOutlineDocumentText />,
    title: 'Smart Resume Parsing',
    description:
      'Upload PDF or DOCX. Our AI extracts skills, experience, education, and achievements with 99% accuracy in under 2 seconds.',
    color: '#2563EB',
    tag: 'Core',
  },
  {
    icon: <HiOutlineSparkles />,
    title: 'AI-Powered Analysis',
    description:
      'Powered by Google Gemini AI — get tailored suggestions, keyword optimizations, and impact improvements for any job role.',
    color: '#7C3AED',
    tag: 'AI',
  },
  {
    icon: <HiOutlineGlobeAlt />,
    title: 'One-Click Portfolio',
    description:
      'Generate a beautiful, responsive personal portfolio website from your parsed resume. Share a live link with recruiters.',
    color: '#06B6D4',
    tag: 'Portfolio',
  },
  {
    icon: <HiOutlineChartBar />,
    title: 'ATS Score Engine',
    description:
      'Real-time ATS scoring against 50+ applicant tracking systems. Get keyword density analysis and format compatibility checks.',
    color: '#F59E0B',
    tag: 'ATS',
  },
  {
    icon: <HiOutlineTrophy />,
    title: 'Reputation System',
    description:
      'Build your professional reputation score. Benchmark against industry peers and track your career growth over time.',
    color: '#EF4444',
    tag: 'Career',
  },
  {
    icon: <HiOutlineAcademicCap />,
    title: 'Career Roadmap',
    description:
      'Get AI-generated personalized learning paths, skill gap analysis, and job match scores to accelerate your career growth.',
    color: '#22C55E',
    tag: 'Growth',
  },
  {
    icon: <HiOutlineShieldCheck />,
    title: 'Secure & Private',
    description:
      'Enterprise-grade encryption. Your data is never sold or shared. Full GDPR compliance with data deletion on demand.',
    color: '#2563EB',
    tag: 'Security',
  },
  {
    icon: <HiOutlineBolt />,
    title: 'Lightning Fast',
    description:
      'Sub-2-second parsing, instant scoring, and real-time feedback. Built on optimized AI pipelines for blazing speed.',
    color: '#7C3AED',
    tag: 'Performance',
  },
];

const steps = [
  {
    num: '01',
    title: 'Upload Your Resume',
    desc: 'Drop your PDF or DOCX file. We instantly extract all structured data using AI parsing.',
    icon: '📄',
  },
  {
    num: '02',
    title: 'AI Analyzes & Scores',
    desc: 'Gemini AI evaluates your resume for ATS compatibility, keyword density, and impact.',
    icon: '🤖',
  },
  {
    num: '03',
    title: 'Get Actionable Insights',
    desc: 'Receive a detailed report with specific improvements to maximize your interview rate.',
    icon: '📊',
  },
  {
    num: '04',
    title: 'Launch Your Portfolio',
    desc: 'Generate a stunning portfolio website and share a live link with recruiters instantly.',
    icon: '🚀',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
};

const FeaturesSection = () => {
  return (
    <>
      {/* ── How It Works ── */}
      <section className="lp-how" id="how-it-works">
        <div className="container">
          <motion.div
            className="lp-section-head"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="lp-section-badge">How It Works</span>
            <h2 className="lp-section-title">
              From Upload to Hired in{' '}
              <span className="gradient-text">4 Simple Steps</span>
            </h2>
            <p className="lp-section-sub">
              TalentIQ streamlines your entire job application process — no
              guesswork, just results.
            </p>
          </motion.div>

          <div className="lp-steps">
            {steps.map((step, i) => (
              <motion.div
                key={step.num}
                className="lp-step"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="lp-step-icon">{step.icon}</div>
                <div className="lp-step-num">{step.num}</div>
                <h3 className="lp-step-title">{step.title}</h3>
                <p className="lp-step-desc">{step.desc}</p>
                {i < steps.length - 1 && <div className="lp-step-arrow">→</div>}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features Grid ── */}
      <section className="lp-features" id="features">
        <div className="container">
          <motion.div
            className="lp-section-head"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="lp-section-badge">Features</span>
            <h2 className="lp-section-title">
              Everything You Need to{' '}
              <span className="gradient-text">Stand Out</span>
            </h2>
            <p className="lp-section-sub">
              From parsing to portfolio, TalentIQ handles your entire career
              toolkit with cutting-edge AI — all in one platform.
            </p>
          </motion.div>
        </div>

        <motion.div
          className="lp-features-grid container"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
        >
          {features.map((feat, i) => (
            <motion.div
              key={i}
              className="lp-feature-card"
              variants={cardVariants}
              style={{ '--feat-color': feat.color }}
            >
              <div className="lp-feat-tag">{feat.tag}</div>
              <div
                className="lp-feat-icon"
                style={{ color: feat.color, background: `${feat.color}18` }}
              >
                {feat.icon}
              </div>
              <h3 className="lp-feat-title">{feat.title}</h3>
              <p className="lp-feat-desc">{feat.description}</p>
              <div className="lp-feat-glow" style={{ background: feat.color }} />
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ── Testimonials ── */}
      <section className="lp-testimonials" id="testimonials">
        <div className="container">
          <motion.div
            className="lp-section-head"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="lp-section-badge">Testimonials</span>
            <h2 className="lp-section-title">
              Loved by{' '}
              <span className="gradient-text">Career Builders</span>
            </h2>
          </motion.div>

          <div className="lp-testimonials-grid">
            {[
              {
                name: 'Priya Sharma',
                role: 'Software Engineer at Google',
                avatar: '👩‍💻',
                text: 'TalentIQ boosted my ATS score from 62% to 98% in minutes. I got 3 interview callbacks in the same week!',
                stars: 5,
              },
              {
                name: 'Arjun Mehta',
                role: 'Data Scientist at Amazon',
                avatar: '👨‍🔬',
                text: 'The AI analysis is incredibly detailed. It identified keyword gaps I had no idea about. Landed my dream job!',
                stars: 5,
              },
              {
                name: 'Sarah Chen',
                role: 'Product Manager at Meta',
                avatar: '👩‍💼',
                text: 'The portfolio builder is stunning. My portfolio site got compliments from every recruiter I spoke with.',
                stars: 5,
              },
              {
                name: 'Rahul Patel',
                role: 'Full-Stack Dev at Startup',
                avatar: '👨‍💻',
                text: 'Career roadmap feature is a game changer. It showed me exactly which skills to learn for my next promotion.',
                stars: 5,
              },
              {
                name: 'Emily Rodriguez',
                role: 'UX Designer at Airbnb',
                avatar: '👩‍🎨',
                text: 'Uploaded my resume, got actionable feedback in 2 seconds. The UI is gorgeous and the insights are spot-on.',
                stars: 5,
              },
              {
                name: 'Kevin Thompson',
                role: 'DevOps Engineer at Netflix',
                avatar: '🧑‍💻',
                text: 'ATS optimization alone is worth it. TalentIQ helped me get past HR filters at top tech companies.',
                stars: 5,
              },
            ].map((t, i) => (
              <motion.div
                key={i}
                className="lp-testi-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <div className="lp-testi-stars">
                  {'★'.repeat(t.stars)}
                </div>
                <p className="lp-testi-text">"{t.text}"</p>
                <div className="lp-testi-author">
                  <span className="lp-testi-avatar">{t.avatar}</span>
                  <div>
                    <div className="lp-testi-name">{t.name}</div>
                    <div className="lp-testi-role">{t.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section className="lp-cta" id="cta">
        <div className="container">
          <motion.div
            className="lp-cta-card"
            initial={{ opacity: 0, scale: 0.97 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="lp-cta-orb-1" />
            <div className="lp-cta-orb-2" />
            <div className="lp-cta-content">
              <span className="lp-cta-badge">🚀 Start Free Today</span>
              <h2 className="lp-cta-title">
                Ready to Land Your Dream Job?
              </h2>
              <p className="lp-cta-sub">
                Join 10,000+ professionals who use TalentIQ to build standout
                resumes, crush ATS filters, and accelerate their careers.
              </p>
              <div className="lp-cta-actions">
                <a href="/register">
                  <button className="lp-btn-primary" id="cta-signup-btn">
                    Get Started for Free →
                  </button>
                </a>
                <a href="/login">
                  <button className="lp-btn-ghost-white" id="cta-login-btn">
                    Already have an account?
                  </button>
                </a>
              </div>
              <div className="lp-cta-perks">
                {['No credit card required', 'Free forever plan', 'Cancel anytime'].map((p) => (
                  <span key={p} className="lp-cta-perk">✓ {p}</span>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
};

export default FeaturesSection;

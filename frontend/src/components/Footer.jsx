/**
 * Footer Component
 * Site-wide footer with brand, links, and social icons.
 */

import { Link } from 'react-router-dom';
import { HiOutlineLightBulb } from 'react-icons/hi2';
import { RiGithubFill, RiTwitterXFill, RiLinkedinFill } from 'react-icons/ri';
import '../styles/Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          {/* Brand */}
          <div className="footer-brand">
            <div className="footer-logo">
              <div className="footer-logo-icon">
                <HiOutlineLightBulb />
              </div>
              TalentIQ
            </div>
            <p className="footer-description">
              AI-powered resume parsing, portfolio generation, and ATS
              optimization — all in one platform.
            </p>
            <div className="footer-socials">
              <a href="#" className="footer-social-link" aria-label="GitHub">
                <RiGithubFill />
              </a>
              <a href="#" className="footer-social-link" aria-label="Twitter">
                <RiTwitterXFill />
              </a>
              <a href="#" className="footer-social-link" aria-label="LinkedIn">
                <RiLinkedinFill />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="footer-column-title">Product</h4>
            <ul className="footer-links">
              <li><a href="/#features" className="footer-link">Features</a></li>
              <li><a href="#" className="footer-link">Pricing</a></li>
              <li><a href="#" className="footer-link">API</a></li>
              <li><a href="#" className="footer-link">Integrations</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="footer-column-title">Company</h4>
            <ul className="footer-links">
              <li><a href="#" className="footer-link">About</a></li>
              <li><a href="#" className="footer-link">Blog</a></li>
              <li><a href="#" className="footer-link">Careers</a></li>
              <li><a href="#" className="footer-link">Contact</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="footer-column-title">Legal</h4>
            <ul className="footer-links">
              <li><a href="#" className="footer-link">Privacy</a></li>
              <li><a href="#" className="footer-link">Terms</a></li>
              <li><a href="#" className="footer-link">Security</a></li>
              <li><a href="#" className="footer-link">GDPR</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="footer-bottom">
          <div className="footer-bottom-inner">
            <span>&copy; {currentYear} TalentIQ. All rights reserved.</span>
            <div className="footer-bottom-links">
              <a href="#" className="footer-bottom-link">Privacy Policy</a>
              <a href="#" className="footer-bottom-link">Terms of Service</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

/**
 * Landing Page
 * Assembles the hero and features sections.
 */

import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import '../styles/Landing.css';

const Landing = () => {
  return (
    <>
      <HeroSection />
      <FeaturesSection />
    </>
  );
};

export default Landing;

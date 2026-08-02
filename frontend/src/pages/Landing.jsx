/**
 * Landing Page
 * Assembles: Hero → How It Works → Features → Testimonials → CTA
 * Note: Footer is rendered by MainLayout for all unauthenticated pages.
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

import { Suspense, useEffect } from 'react';
import Navbar from './components/Navbar';
import HeroSection from './sections/HeroSection';
import FeaturesSection from './sections/FeaturesSection';
import InsightsSection from './sections/InsightsSection';
import AssessmentsSection from './sections/AssessmentsSection';
import Footer from './components/Footer';
import InteractiveBackground from './components/InteractiveBackground';

const App = () => {
  useEffect(() => {
    document.body.dir = 'rtl';
    document.documentElement.lang = 'ar';
  }, []);

  return (
    <Suspense fallback={<div style={{ padding: '4rem', textAlign: 'center' }}>جار التحميل...</div>}>
      <div style={{ position: 'relative', minHeight: '100vh', overflow: 'hidden' }}>
        <InteractiveBackground />
        <Navbar />
        <main>
          <HeroSection />
          <FeaturesSection />
          <InsightsSection />
          <AssessmentsSection />
        </main>
        <Footer />
      </div>
    </Suspense>
  );
};

export default App;

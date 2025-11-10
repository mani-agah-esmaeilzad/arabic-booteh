import { useTranslation } from 'react-i18next';
import { ArrowBack, PlayArrow } from '@mui/icons-material';

const HeroSection = () => {
  const { t } = useTranslation();

  return (
    <section className="hero" id="home">
      <div className="container hero-content">
        <div>
          <span className="badge" style={{ marginBottom: '1rem' }}>{t('nav.assessments')}</span>
          <h1>{t('hero.title')}</h1>
          <p>{t('hero.subtitle')}</p>
          <div className="hero-actions">
            <button className="primary">
              <ArrowBack style={{ transform: 'scaleX(-1)' }} />
              {t('hero.ctaPrimary')}
            </button>
            <button className="secondary">
              <PlayArrow />
              {t('hero.ctaSecondary')}
            </button>
          </div>
        </div>
        <div className="card" style={{ minHeight: '320px' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>{t('features.analytics')}</h3>
          <p className="text-muted" style={{ marginBottom: '2rem' }}>{t('features.analyticsDesc')}</p>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {[72, 84, 91].map((value) => (
              <div key={value} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ width: '3.5rem', height: '3.5rem', borderRadius: '50%', background: 'var(--accent-soft)', display: 'grid', placeItems: 'center', color: 'var(--accent)' }}>
                  {value}%
                </div>
                <div>
                  <strong>{t('hero.scoreLabel', { value: Math.round(value / 3) })}</strong>
                  <p className="text-muted" style={{ margin: 0, fontSize: '0.85rem' }}>{t('hero.scoreInsight')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

import { useTranslation } from 'react-i18next';
import { AutoAwesome, Insights, Language, RocketLaunch } from '@mui/icons-material';

const FeaturesSection = () => {
  const { t } = useTranslation();
  const features = [
    { icon: <Insights />, title: t('features.analytics'), description: t('features.analyticsDesc') },
    { icon: <AutoAwesome />, title: t('features.conversations'), description: t('features.conversationsDesc') },
    { icon: <Language />, title: t('features.localization'), description: t('features.localizationDesc') },
    { icon: <RocketLaunch />, title: t('features.automation'), description: t('features.automationDesc') }
  ];

  return (
    <section id="solutions">
      <div className="container">
        <h2 style={{ textAlign: 'center', marginBottom: '3rem', fontSize: '2.4rem' }}>{t('features.title')}</h2>
        <div className="grid columns-2">
          {features.map((feature) => (
            <div key={feature.title} className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ width: '3rem', height: '3rem', borderRadius: '50%', background: 'var(--accent-soft)', display: 'grid', placeItems: 'center', color: 'var(--accent)' }}>
                  {feature.icon}
                </div>
                <h3 style={{ margin: 0 }}>{feature.title}</h3>
              </div>
              <p className="text-muted">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;

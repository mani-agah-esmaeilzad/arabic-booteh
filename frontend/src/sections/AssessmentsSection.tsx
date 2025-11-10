import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { fetchMysteryAssessments, fetchPersonalityTests, MysteryAssessment, PersonalityTest } from '../lib/api';

const AssessmentsSection = () => {
  const { t, i18n } = useTranslation();
  const [mystery, setMystery] = useState<MysteryAssessment[]>([]);
  const [tests, setTests] = useState<PersonalityTest[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchMysteryAssessments(), fetchPersonalityTests()])
      .then(([mysteryData, testData]) => {
        setMystery(mysteryData);
        setTests(testData);
      })
      .catch(() => setError(t('errors.failedToLoad')));
  }, [i18n.language, t]);

  return (
    <section id="assessments">
      <div className="container">
        <h2 style={{ textAlign: 'center', marginBottom: '3rem', fontSize: '2.2rem' }}>{t('assessments.title')}</h2>
        {error && <p className="text-muted" style={{ textAlign: 'center' }}>{error}</p>}
        <div className="grid columns-2">
          <div className="card assessment-card">
            <h3>{t('assessments.mystery')}</h3>
            <p className="text-muted" style={{ marginBottom: '1.5rem' }}>{t('assessments.mysteryDesc')}</p>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '0.75rem' }}>
              {mystery.slice(0, 4).map((item) => (
                <li key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                  <span>{item.name}</span>
                  <button type="button" className="secondary">{t('assessments.explore')}</button>
                </li>
              ))}
            </ul>
          </div>
          <div className="card assessment-card">
            <h3>{t('assessments.personality')}</h3>
            <p className="text-muted" style={{ marginBottom: '1.5rem' }}>{t('assessments.personalityDesc')}</p>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '0.75rem' }}>
              {tests.slice(0, 4).map((test) => (
                <li key={test.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                  <span>{test.title}</span>
                  <button type="button" className="secondary">{t('assessments.tryNow')}</button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AssessmentsSection;

import LanguageSwitcher from './LanguageSwitcher';
import { useTranslation } from 'react-i18next';

const Navbar = () => {
  const { t } = useTranslation();

  const scrollTo = (id: string) => {
    const section = document.getElementById(id);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav>
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="badge">Booteh</div>
          <span style={{ fontWeight: 600, letterSpacing: '0.04em' }}>منصة بوتة</span>
        </div>
        <ul>
          <li><button type="button" className="secondary" onClick={() => scrollTo('home')}>{t('nav.home')}</button></li>
          <li><button type="button" className="secondary" onClick={() => scrollTo('solutions')}>{t('nav.solutions')}</button></li>
          <li><button type="button" className="secondary" onClick={() => scrollTo('insights')}>{t('nav.insights')}</button></li>
          <li><button type="button" className="secondary" onClick={() => scrollTo('assessments')}>{t('nav.assessments')}</button></li>
          <li><a className="secondary" href="mailto:hello@booteh.ai">{t('nav.contact')}</a></li>
        </ul>
        <LanguageSwitcher />
      </div>
    </nav>
  );
};

export default Navbar;

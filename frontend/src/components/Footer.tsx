import { useTranslation } from 'react-i18next';

const Footer = () => {
  const { t } = useTranslation();
  return (
    <footer>
      <div className="container">
        <span className="text-muted">{t('footer.rights', { year: new Date().getFullYear() })}</span>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <a className="secondary" href="#privacy">{t('footer.privacy')}</a>
          <a className="secondary" href="#terms">{t('footer.terms')}</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

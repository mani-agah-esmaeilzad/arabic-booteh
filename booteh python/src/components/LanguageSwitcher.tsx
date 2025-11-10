import { ChangeEvent, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();

  const currentValue = useMemo(() => (i18n.language.startsWith('ar') ? 'ar' : 'en'), [i18n.language]);

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const newLang = event.target.value;
    i18n.changeLanguage(newLang);
    const dir = newLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLang;
    document.documentElement.dir = dir;
    document.body.dir = dir;
  };

  return (
    <div className="language-switcher" aria-label={t('languageSwitcher.label')}>
      <select onChange={handleChange} value={currentValue}>
        <option value="ar">العربية</option>
        <option value="en">English</option>
      </select>
    </div>
  );
};

export default LanguageSwitcher;

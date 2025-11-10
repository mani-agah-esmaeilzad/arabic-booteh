import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  ar: {
    translation: {
      nav: {
        home: 'الرئيسية',
        solutions: 'الحلول',
        insights: 'المدونة',
        assessments: 'التقييمات',
        contact: 'تواصل معنا'
      },
      hero: {
        title: 'منصة بوتة لتجارب تعلم عميقة ومدعومة بالذكاء الاصطناعي',
        subtitle: 'نمزج بين التحليلات السلوكية والمحتوى التفاعلي لنساعد فرقك على الازدهار.',
        ctaPrimary: 'ابدأ الآن',
        ctaSecondary: 'احجز عرضاً مباشراً',
        scoreLabel: 'مؤشر الأداء رقم {{value}}',
        scoreInsight: 'تحليل فوري للشخصية'
      },
      features: {
        title: 'لماذا تختار بوتة؟',
        analytics: 'تحليلات شخصية فورية',
        analyticsDesc: 'واجهات عربية بالكامل مع قراءة بصرية للمهارات والكفاءات الأساسية.',
        conversations: 'مغامرات محادثة ثلاثية الأبعاد',
        conversationsDesc: 'تجارب غامرة داخل عوالم ثلاثية الأبعاد تتكيف مع قرارات المتعلمين.',
        localization: 'تعدد اللغات بلا مجهود',
        localizationDesc: 'محتوى عربي وإنجليزي مع تبديل فوري، وبدون التأثير على الأداء.',
        automation: 'أتمتة متكاملة مع فريقك',
        automationDesc: 'ربط مباشر مع أدوات الموارد البشرية ولوحات البيانات لديك.'
      },
      insights: {
        title: 'آخر المقالات',
        empty: 'لا توجد مقالات الآن، ترقب التحديثات القادمة.'
      },
      assessments: {
        title: 'تقييمات جاهزة للانطلاق',
        mystery: 'مغامرات الغموض',
        mysteryDesc: 'جلسات محادثة تفاعلية مليئة بالقرارات الحرجة والسيناريوهات المتفرعة.',
        personality: 'اختبارات الشخصية',
        personalityDesc: 'مقاييس موثوقة لتحديد أنماط التفكير واتخاذ القرار والذكاء العاطفي.',
        explore: 'استكشف',
        tryNow: 'جرب الآن'
      },
      footer: {
        rights: '© {{year}} بوتة. جميع الحقوق محفوظة.',
        privacy: 'الخصوصية',
        terms: 'الشروط'
      },
      languageSwitcher: {
        label: 'اللغة'
      },
      errors: {
        failedToLoad: 'تعذر تحميل البيانات. حاول مرة أخرى لاحقًا.'
      },
      common: {
        readMore: 'اقرأ المزيد'
      }
    }
  },
  en: {
    translation: {
      nav: {
        home: 'Home',
        solutions: 'Solutions',
        insights: 'Insights',
        assessments: 'Assessments',
        contact: 'Contact'
      },
      hero: {
        title: 'Booteh: immersive AI-powered learning journeys',
        subtitle: 'We blend behavioural analytics with interactive stories to help your teams thrive.',
        ctaPrimary: 'Get started',
        ctaSecondary: 'Book a live demo',
        scoreLabel: 'Performance signal #{{value}}',
        scoreInsight: 'AI Persona Insight'
      },
      features: {
        title: 'Why teams love Booteh',
        analytics: 'Instant behavioural analytics',
        analyticsDesc: 'Fully localized dashboards with visual readings of critical competencies.',
        conversations: '3D conversation adventures',
        conversationsDesc: 'Immersive worlds that adapt to every decision a learner makes.',
        localization: 'Effortless multilingual content',
        localizationDesc: 'Arabic and English experiences with instant switching and zero downtime.',
        automation: 'Automation that works with you',
        automationDesc: 'Direct integrations with HR tools and analytics suites.'
      },
      insights: {
        title: 'Latest articles',
        empty: 'No articles yet. Check back soon.'
      },
      assessments: {
        title: 'Assessments ready to deploy',
        mystery: 'Mystery adventures',
        mysteryDesc: 'Interactive conversations packed with high-stakes decisions and branching storylines.',
        personality: 'Personality diagnostics',
        personalityDesc: 'Trusted measures of thinking styles, decision making, and emotional intelligence.',
        explore: 'Explore',
        tryNow: 'Try now'
      },
      footer: {
        rights: '© {{year}} Booteh. All rights reserved.',
        privacy: 'Privacy',
        terms: 'Terms'
      },
      languageSwitcher: {
        label: 'Language'
      },
      errors: {
        failedToLoad: 'We could not load data. Please try again later.'
      },
      common: {
        readMore: 'Read more'
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'ar',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;

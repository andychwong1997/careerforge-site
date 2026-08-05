/* ============================================
   CareerForge 鑄途 — i18n Script
   Toggles between 繁體 / 简体 / English
   Stores user preference in localStorage
   ============================================ */

(function() {
  const STORAGE_KEY = 'cf_lang';
  const SUPPORTED = ['zh-Hant', 'zh-Hans', 'en'];
  const LABELS = { 'zh-Hant': '繁體', 'zh-Hans': '简体', 'en': 'EN' };

  function detectLang() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && SUPPORTED.includes(saved)) return saved;
    const nav = (navigator.language || 'zh-Hant').toLowerCase();
    if (nav.startsWith('zh-cn') || nav === 'zh-hans') return 'zh-Hans';
    if (nav.startsWith('en')) return 'en';
    return 'zh-Hant';
  }

  function applyLang(lang) {
    if (!SUPPORTED.includes(lang)) lang = 'zh-Hant';
    document.documentElement.lang = lang;
    document.documentElement.setAttribute('data-lang', lang);

    // Update all data-i18n elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const val = window.I18N?.[lang]?.[key];
      if (val !== undefined) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = val;
        } else {
          el.innerHTML = val;
        }
      }
    });

    // Update form labels / placeholders via data-i18n-attr
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const val = window.I18N?.[lang]?.[key];
      if (val !== undefined) el.placeholder = val;
    });

    // Update select options via data-i18n-option
    document.querySelectorAll('[data-i18n-option]').forEach(opt => {
      const key = el => null; // noop
      const key2 = opt.getAttribute('data-i18n-option');
      const val = window.I18N?.[lang]?.[key2];
      if (val !== undefined) opt.textContent = val;
    });

    // Update lang switcher label
    const cur = document.querySelector('.lang-current');
    if (cur) cur.textContent = LABELS[lang];

    localStorage.setItem(STORAGE_KEY, lang);
  }

  function setupSwitcher() {
    const switcher = document.querySelector('.lang-switcher');
    if (!switcher) return;
    switcher.addEventListener('click', (e) => {
      const target = e.target.closest('[data-lang-target]');
      if (!target) return;
      e.preventDefault();
      applyLang(target.getAttribute('data-lang-target'));
    });
  }

  // Init
  document.addEventListener('DOMContentLoaded', () => {
    const lang = detectLang();
    applyLang(lang);
    setupSwitcher();
  });
})();
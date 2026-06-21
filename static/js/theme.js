/* ==========================================
   THEME TOGGLE
   Gère le basculement clair/sombre et
   sauvegarde le choix dans localStorage.
   ========================================== */

(function () {
    const STORAGE_KEY = 'sdf-theme';
    const DARK        = 'dark';
    const LIGHT       = 'light';

    const html   = document.documentElement;
    const btn    = document.getElementById('theme-toggle');
    const iconEl = document.getElementById('theme-icon');

    // Icônes SVG inline (lune = thème sombre, soleil = thème clair)
    const ICON_MOON = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
    const ICON_SUN  = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        if (iconEl) {
            iconEl.innerHTML = theme === DARK ? ICON_SUN : ICON_MOON;
        }
        if (btn) {
            btn.setAttribute('aria-label', theme === DARK ? 'Passer au thème clair' : 'Passer au thème sombre');
            btn.title = theme === DARK ? 'Thème clair' : 'Thème sombre';
        }
    }

    function toggle() {
        const current = html.getAttribute('data-theme') || LIGHT;
        const next    = current === DARK ? LIGHT : DARK;
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
    }

    // Appliquer le thème sauvegardé dès le chargement (avant le rendu)
    const saved = localStorage.getItem(STORAGE_KEY) || LIGHT;
    applyTheme(saved);

    // Brancher le bouton une fois le DOM prêt
    if (btn) {
        btn.addEventListener('click', toggle);
    } else {
        document.addEventListener('DOMContentLoaded', function () {
            const b = document.getElementById('theme-toggle');
            if (b) b.addEventListener('click', toggle);
        });
    }
})();
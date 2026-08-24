/**
 * Sidebar — toggle de recolher (desktop) e drawer (mobile).
 *
 * Estados (controlados via classes em <html>):
 *   - sidebar-collapsed   : sidebar recolhida no desktop (só ícones)
 *   - sidebar-mobile-open : drawer aberto no mobile
 *
 * Persistência: localStorage 'tereza:sidebar-collapsed'
 *
 * O state inicial é aplicado no <head> (script inline anti-FOUC) — este arquivo
 * só conecta os listeners e re-renderiza os ícones Lucide quando os botões mudam.
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'tereza:sidebar-collapsed';
    const root = document.documentElement;

    /** Reaplica os ícones Lucide depois que classes mudam (alguns são SVGs trocados). */
    function refreshIcons() {
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    }

    /** Atualiza aria-expanded em todos os toggles para refletir o estado real. */
    function syncAria() {
        const collapsed = root.classList.contains('sidebar-collapsed');
        document.querySelectorAll('[data-sidebar-toggle]').forEach((btn) => {
            btn.setAttribute('aria-expanded', String(!collapsed));
            btn.setAttribute('aria-label', collapsed ? 'Expandir menu' : 'Recolher menu');
        });
    }

    /** Toggle desktop — recolher/expandir, persiste em localStorage. */
    function toggleCollapse() {
        const nowCollapsed = root.classList.toggle('sidebar-collapsed');
        try {
            localStorage.setItem(STORAGE_KEY, nowCollapsed ? '1' : '0');
        } catch (e) {
            /* storage indisponível — ignora */
        }
        syncAria();
    }

    /** Toggle mobile — abre/fecha o drawer (não persiste). */
    function toggleMobile() {
        root.classList.toggle('sidebar-mobile-open');
    }

    /** Fecha o drawer ao clicar no backdrop ou ao trocar para >= md. */
    function closeMobile() {
        root.classList.remove('sidebar-mobile-open');
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-sidebar-toggle]')
            .forEach((b) => b.addEventListener('click', toggleCollapse));

        document.querySelectorAll('[data-sidebar-mobile-toggle]')
            .forEach((b) => b.addEventListener('click', toggleMobile));

        document.querySelectorAll('[data-sidebar-backdrop]')
            .forEach((el) => el.addEventListener('click', closeMobile));

        // ESC fecha o drawer mobile
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && root.classList.contains('sidebar-mobile-open')) {
                closeMobile();
            }
        });

        // Ao redimensionar pra >= md, garante que o drawer mobile não fique preso
        const mql = window.matchMedia('(min-width: 768px)');
        mql.addEventListener('change', (e) => { if (e.matches) closeMobile(); });

        syncAria();
        refreshIcons();
    });
})();

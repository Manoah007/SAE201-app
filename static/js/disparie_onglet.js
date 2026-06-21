/**
 * Gère le changement d'onglets (Graphique / Indicateurs / Tableau)
 * @param {Event} event - L'événement de clic
 * @param {string} tabId - L'ID de l'onglet à afficher
 */
function switchTab(event, tabId) {
    // 1. Masquer tous les contenus d'onglets
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // 2. Désactiver tous les boutons d'onglets
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // 3. Activer l'onglet et le bouton actuels
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    event.currentTarget.classList.add('active');
}
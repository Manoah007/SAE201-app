/**********************************************************************/
/** SCRIPT EN JS POUR GÉRÉ LES CAS DE FILTRES RÉGIONS ET DÉPARTEMENTS */
/**********************************************************************/

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // 1. MÉCANIQUE D'INTERFACE (Ouverture, Fermeture, Compteurs)
    // ---------------------------------------------------------
    const containers = document.querySelectorAll('.multi-select-container');
    const form = document.getElementById('form-filtres');

    containers.forEach(container => {
        const btn = container.querySelector('.select-btn');
        const dropdown = container.querySelector('.dropdown-content');
        // Attention: Assure-toi que la classe dans ton HTML est bien "btnText" ou "btn-text"
        const btnText = container.querySelector('.btnText') || container.querySelector('.btn-text');
        const defaultText = btnText.textContent; 
        const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');

        // OUVERTURE / FERMETURE au clic sur le bouton
        btn.addEventListener('click', (event) => {
            containers.forEach(c => {
                if (c !== container) c.querySelector('.dropdown-content').classList.remove('show');
            });
            dropdown.classList.toggle('show');
            event.stopPropagation();
        });

        // MISE À JOUR DU TEXTE DU BOUTON au changement des cases
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const checkedBoxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');
                const checkedCount = checkedBoxes.length;

                if (checkedCount === 0) {
                    btnText.textContent = defaultText; 
                } else if (checkedCount === 1) {
                    btnText.textContent = checkedBoxes[0].parentElement.textContent.trim();
                } else {
                    btnText.textContent = `${checkedCount} sélectionnés`;
                }
            });
        });
    });

    // FERMETURE DU MENU si on clique n'importe où à l'extérieur
    document.addEventListener('click', () => {
        containers.forEach(container => {
            container.querySelector('.dropdown-content').classList.remove('show');
        });
    });

    // ---------------------------------------------------------
    // 2. MÉCANIQUE DE CASCADE (Filtre : Régions -> Départements)
    // ---------------------------------------------------------
    const regionCheckboxes = document.querySelectorAll('input[name="regions"]');
    const departementCheckboxes = document.querySelectorAll('input[name="departements"]');

    function filtrerDepartements() {
        // A. On récupère les IDs de toutes les régions actuellement cochées (hors "ALL")
        const regionsSelectionnees = Array.from(regionCheckboxes)
            .filter(cb => cb.checked && cb.value !== 'ALL')
            .map(cb => cb.value);

        // B. On vérifie si on doit tout afficher (soit "Toutes régions" est coché, soit aucune région n'est cochée)
        const afficherTout = document.querySelector('input[name="regions"][value="ALL"]').checked || regionsSelectionnees.length === 0;

        // C. On boucle sur chaque département pour le masquer ou l'afficher
        departementCheckboxes.forEach(deptCb => {
            const deptLabel = deptCb.parentElement; // C'est le <label> entier qu'il faut masquer, pas juste la case
            const deptRegionId = deptCb.getAttribute('data-region');

            // On ignore l'option "Tous départements" pour qu'elle reste toujours visible
            if (deptCb.value === 'ALL') return;

            if (afficherTout || regionsSelectionnees.includes(deptRegionId)) {
                // Si le département correspond à la région, on l'affiche (retire le display: none)
                deptLabel.style.display = ''; 
            } else {
                // Sinon, on le masque !
                deptLabel.style.display = 'none'; 
                
                // Si la case était cochée alors qu'elle vient d'être masquée, on la décoche
                if (deptCb.checked) {
                    deptCb.checked = false;
                    // On déclenche manuellement l'événement 'change' pour mettre à jour le bouton (ex: passer de "3 sélectionnés" à "2")
                    deptCb.dispatchEvent(new Event('change')); 
                }
            }
        });
    }

    // On écoute les clics sur les cases "Régions" pour déclencher le filtrage
    regionCheckboxes.forEach(cb => {
        cb.addEventListener('change', filtrerDepartements);
    });
});

/*************************************************************/
/** SCRIPT EN JS POUR GÉRÉ LES ONGLETS GRAPHIQUE ET TABLEAU **/
/*************************************************************/

/**
 * Fonction pour basculer entre les onglets
 * @param {Event} event - L'événement du clic
 * @param {string} tabId - L'ID du contenu de l'onglet à afficher
 */
function switchTab(event, tabId) {
    // 1. Masquer tous les contenus d'onglets
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // 2. Retirer l'état "actif" de tous les boutons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
    });

    // 3. Afficher l'onglet ciblé en lui ajoutant la classe "active"
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // 4. Ajouter la classe "active" au bouton qui vient d'être cliqué
    event.currentTarget.classList.add('active');
}
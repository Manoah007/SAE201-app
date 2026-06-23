/**********************************************************************/
/** SCRIPT EN JS POUR GÉRÉ LES CAS DE FILTRES RÉGIONS ET DÉPARTEMENTS */
/**********************************************************************/

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // MÉCANIQUE D'INTERFACE (Ouverture, Fermeture, Compteurs)
    // ---------------------------------------------------------
    const containers = document.querySelectorAll('.multi-select-container');
    const form = document.getElementById('form-filtres');

    containers.forEach(container => {
        const btn = container.querySelector('.select-btn');
        const dropdown = container.querySelector('.dropdown-content');
        const btnText = container.querySelector('.btnText') || container.querySelector('.btn-text');
        const defaultText = btnText.textContent; 
        
        // On récupère TOUS les inputs (checkboxes ET radios)
        const inputs = dropdown.querySelectorAll('input[type="checkbox"], input[type="radio"]');

        // OUVERTURE / FERMETURE au clic sur le bouton
        btn.addEventListener('click', (event) => {
            containers.forEach(c => {
                if (c !== container) c.querySelector('.dropdown-content').classList.remove('show');
            });
            dropdown.classList.toggle('show');
            event.stopPropagation();
        });

        // Empêche le clic dans le menu de fermer le menu
        dropdown.addEventListener('click', (event) => {
            event.stopPropagation(); 
        });

        // MISE À JOUR DU TEXTE ET COMPORTEMENT au changement des cases/radios
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                
                if (input.type === 'radio') {
                    // --- Logique pour l'ANNÉE (choix unique) ---
                    if (input.checked) {
                        btnText.textContent = input.parentElement.textContent.trim();
                        dropdown.classList.remove('show'); // Ferme le menu
                    }
                } else {
                    // --- Logique pour RÉGIONS / DÉPARTEMENTS (choix multiples) ---
                    const checkedBoxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');
                    const checkedCount = checkedBoxes.length;

                    if (checkedCount === 0) {
                        btnText.textContent = defaultText; 
                    } else if (checkedCount === 1) {
                        btnText.textContent = checkedBoxes[0].parentElement.textContent.trim();
                    } else {
                        btnText.textContent = `${checkedCount} sélectionnés`;
                    }
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
    // MÉCANIQUE DE CASCADE (Filtre : Régions -> Départements)
    // ---------------------------------------------------------
    const regionCheckboxes = document.querySelectorAll('input[name="regions"]');
    const departementCheckboxes = document.querySelectorAll('input[name="departements"]');

    function filtrerDepartements() {
        const regionsSelectionnees = Array.from(regionCheckboxes)
            .filter(cb => cb.checked && cb.value !== 'ALL')
            .map(cb => cb.value);

        const touteRegionCochee = document.querySelector('input[name="regions"][value="ALL"]').checked;
        const deptContainer = document.querySelector('input[name="departements"]').closest('.multi-select-container');

        if (regionsSelectionnees.length === 0 && !touteRegionCochee) {
            deptContainer.classList.add('bouton-inactif');
            
            departementCheckboxes.forEach(deptCb => {
                if (deptCb.checked) {
                    deptCb.checked = false;
                    deptCb.dispatchEvent(new Event('change'));
                }
                // CORRECTION : Utilisation de la classe CSS pour masquer, pas de style en ligne
                if (deptCb.value !== 'ALL') {
                    deptCb.parentElement.classList.add('masque');
                }
            });
            
            return; 
        } else {
            deptContainer.classList.remove('bouton-inactif');
        }

        const afficherTout = touteRegionCochee;

        departementCheckboxes.forEach(deptCb => {
            const deptLabel = deptCb.parentElement;
            const deptRegionId = deptCb.getAttribute('data-region');

            if (deptCb.value === 'ALL') return;

            if (afficherTout || regionsSelectionnees.includes(deptRegionId)) {
                deptLabel.classList.remove('masque'); 
            } else {
                deptLabel.classList.add('masque');
                
                if (deptCb.checked) {
                    deptCb.checked = false;
                    deptCb.dispatchEvent(new Event('change')); 
                }
            }
        });
    }

    regionCheckboxes.forEach(cb => {
        cb.addEventListener('change', filtrerDepartements);
    });
    
    // Initialisation au chargement de la page
    filtrerDepartements();

    const ligneMaxRadios = document.querySelectorAll('input[name="ligne_max"]');
    const formulairePrincipal = document.getElementById('form-filtres');

    ligneMaxRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            // Dès qu'une nouvelle limite est choisie, on envoie le formulaire au serveur Python
            if (formulairePrincipal) {
                formulairePrincipal.submit();
            }
        });
    });

    // ---------------------------------------------------------
    // RESTAURATION DE L'ONGLET ET DÉFILEMENT (Mémoire de session)
    // ---------------------------------------------------------
    const ongletSauvegarde = sessionStorage.getItem('ongletActif');
    
    // Si une sauvegarde existe ET que ce n'est pas le graphique (qui est là par défaut)
    if (ongletSauvegarde && ongletSauvegarde !== 'tab-graphique') {
        // On trouve le bouton qui correspond à cet onglet
        const boutonCorrespondant = document.querySelector(`button[onclick*="${ongletSauvegarde}"]`);
        
        if (boutonCorrespondant) {
            // 1. On simule virtuellement un clic sur ce bouton
            boutonCorrespondant.click();
            
            // 2. On fait défiler la page automatiquement et en douceur vers la zone de données
            // Pour éviter un saut brutal, on laisse un petit délai pour que le HTML se place bien
            setTimeout(() => {
                document.getElementById(ongletSauvegarde).scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' // Aligne le haut de l'onglet avec le haut de l'écran
                });
            }, 100);
        }
    }
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

    // 5. NOUVEAU : Sauvegarder le choix dans la mémoire du navigateur !
    sessionStorage.setItem('ongletActif', tabId);
}
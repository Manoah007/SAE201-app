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

        // ---------------------------------------------------------
        // NOUVEAU : INITIALISATION AU CHARGEMENT (Juste après la boucle)
        // ---------------------------------------------------------
        const casesCochees = dropdown.querySelectorAll('input:checked');
        if (casesCochees.length > 0) {
            // On simule un événement "change" sur la première case trouvée
            casesCochees[0].dispatchEvent(new Event('change'));
        }
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

    // ---------------------------------------------------------
    // EXCLUSIVITÉ MUTUELLE DES CASES "ALL" (Régions et Départements)
    // ---------------------------------------------------------
    function configurerExclusiviteTout(nomFormulaire) {
        const checkboxes = document.querySelectorAll(`input[name="${nomFormulaire}"]`);
        const caseTout = Array.from(checkboxes).find(cb => cb.value === 'ALL');
        const casesSpecifiques = Array.from(checkboxes).filter(cb => cb.value !== 'ALL');

        if (!caseTout) return;

        // Cas 1 : Si on coche "TOUT", on décoche toutes les options spécifiques
        caseTout.addEventListener('change', () => {
            if (caseTout.checked) {
                casesSpecifiques.forEach(cb => {
                    if (cb.checked) {
                        cb.checked = false;
                        // Crucial : on déclenche l'événement pour mettre à jour les compteurs et la cascade
                        cb.dispatchEvent(new Event('change')); 
                    }
                });
            }
        });

        // Cas 2 : Si on coche une option spécifique, on décoche obligatoirement "TOUT"
        casesSpecifiques.forEach(cb => {
            cb.addEventListener('change', () => {
                if (cb.checked && caseTout.checked) {
                    caseTout.checked = false;
                    // On déclenche l'événement pour que le compteur du bouton se mette à jour
                    caseTout.dispatchEvent(new Event('change')); 
                }
            });
        });
    }

    // On active cette logique pour les deux menus distincts
    configurerExclusiviteTout('regions');
    configurerExclusiviteTout('departements');
    
    // ---------------------------------------------------------
    // SOUMISSION AUTOMATIQUE CORRIGÉE (Filtre Ligne Max)
    // ---------------------------------------------------------
    const ligneMaxRadios = document.querySelectorAll('input[name="ligne_max"]');
    const formulairePrincipal = document.getElementById('form-filtres');

    ligneMaxRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            if (formulairePrincipal) {
                // STRATÉGIE : On cherche le bouton de soumission du formulaire
                const boutonSoumettre = formulairePrincipal.querySelector('button[type="submit"]') || document.getElementById('btn-rechercher');
                
                if (boutonSoumettre) {
                    // On simule un clic : cela déclenche TOUTE la logique des filtres sans rien oublier
                    boutonSoumettre.click(); 
                } else {
                    // Si le bouton n'est pas trouvé, on utilise la méthode moderne qui respecte les événements
                    formulairePrincipal.requestSubmit(); 
                }
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
    
    // ---------------------------------------------------------
    // EXPORTATION DES DONNÉES EN CSV (Bouton Exporter)
    // ---------------------------------------------------------
    const btnExport = document.querySelector('.export-btn');

    if (btnExport) {
        btnExport.addEventListener('click', () => {
            // 1. On cible le tableau HTML
            const table = document.querySelector('.prescriptions-table-box table');
            if (!table) {
                alert("Aucune donnée à exporter.");
                return;
            }

            // 2. On prépare le fichier CSV (\uFEFF force l'UTF-8 pour que Excel lise bien les accents)
            let csvContent = "data:text/csv;charset=utf-8,\uFEFF";

            // 3. On lit toutes les lignes du tableau (titres + données)
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                const cols = row.querySelectorAll('th, td');
                const rowData = Array.from(cols).map(col => {
                    // On récupère le texte en enlevant les espaces inutiles
                    let text = col.innerText.trim();
                    
                    // Nettoyage pour Excel : on enlève le symbole "€" pour avoir de vrais nombres
                    text = text.replace('€', '').trim();
                    
                    // Optionnel pour la France : remplacer le point par une virgule pour les décimales
                    // text = text.replace('.', ','); 

                    // On met chaque cellule entre guillemets pour éviter les bugs si un nom contient une virgule
                    return `"${text}"`;
                });
                
                // On assemble la ligne avec un point-virgule (le standard d'Excel en France)
                csvContent += rowData.join(";") + "\r\n";
            });

            // 4. On simule un clic sur un lien invisible pour lancer le téléchargement
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "export_prescriptions_ameli.csv");
            
            document.body.appendChild(link); // Requis pour Firefox
            link.click();
            document.body.removeChild(link); // On nettoie après le téléchargement
        });
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

/*********************************************/
/** SCRIPT EN JS POUR GÉRÉ LES HISTOGRAMMES **/
/*********************************************/
document.addEventListener('DOMContentLoaded', () => {
    
    // ---------------------------------------------------------
    // 1. RÉCUPÉRATION DES DONNÉES (La Passerelle)
    // ---------------------------------------------------------
    const passerelle = document.getElementById('data-passerelle');
    
    if (passerelle) {
        window.chartData = {
            labels: JSON.parse(passerelle.dataset.labels),
            totaux: JSON.parse(passerelle.dataset.totaux),
            moyennes: JSON.parse(passerelle.dataset.moyennes)
        };
    }

    // ---------------------------------------------------------
    // 2. CRÉATION DES GRAPHIQUES CHART.JS
    // ---------------------------------------------------------
    // On s'assure que les données existent ET que l'on est bien sur la page avec les canvas
    const canvasTotal = document.getElementById('histogram-total');
    const canvasMoyenne = document.getElementById('histogram-moyenne');

    if (window.chartData && canvasTotal && canvasMoyenne) {

        // --- Histogramme 1 : Coût Global ---
        new Chart(canvasTotal, {
            type: 'bar', // Type histogramme (barres)
            data: {
                labels: window.chartData.labels, // Axe X (ex: IDF, Bretagne)
                datasets: [{
                    label: 'Coût total (€)',
                    data: window.chartData.totaux, // Axe Y
                    backgroundColor: '#3b82f6', // Un beau bleu moderne
                    borderRadius: 4 // Arrondit légèrement le haut des barres
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Permet au graphique de s'adapter à la hauteur de ta div
                plugins: {
                    legend: { display: false }, // Cache la légende si tu n'as qu'une seule couleur
                    title: {
                        display: true,
                        text: 'Coût total des prescriptions',
                        font: { size: 16 }
                    }
                }
            }
        });

        // --- Histogramme 2 : Coût Moyen ---
        new Chart(canvasMoyenne, {
            type: 'bar',
            data: {
                labels: window.chartData.labels,
                datasets: [{
                    label: 'Coût moyen par professionnel (€)',
                    data: window.chartData.moyennes,
                    backgroundColor: '#10b981', // Un beau vert
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Coût moyen de prescription par professionnel',
                        font: { size: 16 }
                    }
                }
            }
        });
    }

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
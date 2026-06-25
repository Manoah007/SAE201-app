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
        
        const inputs = dropdown.querySelectorAll('input[type="checkbox"], input[type="radio"]');

        btn.addEventListener('click', (event) => {
            containers.forEach(c => {
                if (c !== container) c.querySelector('.dropdown-content').classList.remove('show');
            });
            dropdown.classList.toggle('show');
            event.stopPropagation();
        });

        dropdown.addEventListener('click', (event) => {
            event.stopPropagation(); 
        });

        inputs.forEach(input => {
            input.addEventListener('change', () => {
                
                if (input.type === 'radio') {
                    if (input.checked) {
                        btnText.textContent = input.parentElement.textContent.trim();
                        dropdown.classList.remove('show'); 
                    }
                } else {
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
            casesCochees[0].dispatchEvent(new Event('change'));
        }
    });

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
    
    filtrerDepartements();

    // ---------------------------------------------------------
    // EXCLUSIVITÉ MUTUELLE DES CASES "ALL" (Régions et Départements)
    // ---------------------------------------------------------
    function configurerExclusiviteTout(nomFormulaire) {
        const checkboxes = document.querySelectorAll(`input[name="${nomFormulaire}"]`);
        const caseTout = Array.from(checkboxes).find(cb => cb.value === 'ALL');
        const casesSpecifiques = Array.from(checkboxes).filter(cb => cb.value !== 'ALL');

        if (!caseTout) return;

        caseTout.addEventListener('change', () => {
            if (caseTout.checked) {
                casesSpecifiques.forEach(cb => {
                    if (cb.checked) {
                        cb.checked = false;
                        cb.dispatchEvent(new Event('change')); 
                    }
                });
            }
        });

        casesSpecifiques.forEach(cb => {
            cb.addEventListener('change', () => {
                if (cb.checked && caseTout.checked) {
                    caseTout.checked = false;
                    caseTout.dispatchEvent(new Event('change')); 
                }
            });
        });
    }

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
                const boutonSoumettre = formulairePrincipal.querySelector('button[type="submit"]') || document.getElementById('btn-rechercher');
                
                if (boutonSoumettre) {
                    boutonSoumettre.click(); 
                } else {
                    formulairePrincipal.requestSubmit(); 
                }
            }
        });
    });

    // ---------------------------------------------------------
    // RESTAURATION DE L'ONGLET ET DÉFILEMENT (Mémoire de session)
    // ---------------------------------------------------------
    const ongletSauvegarde = sessionStorage.getItem('ongletActif');
    
    if (ongletSauvegarde && ongletSauvegarde !== 'tab-graphique') {
        const boutonCorrespondant = document.querySelector(`button[onclick*="${ongletSauvegarde}"]`);
        
        if (boutonCorrespondant) {
            boutonCorrespondant.click();
            
            setTimeout(() => {
                document.getElementById(ongletSauvegarde).scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
        }
    }
});



/*************************************************************/
/** SCRIPT EN JS POUR GÉRÉ LES ONGLETS GRAPHIQUE ET TABLEAU **/
/*************************************************************/

function switchTab(event, tabId) {
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
    });

    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    event.currentTarget.classList.add('active');

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
    const canvasTotal = document.getElementById('histogram-total');
    const canvasMoyenne = document.getElementById('histogram-moyenne');

    if (window.chartData && canvasTotal && canvasMoyenne) {

        new Chart(canvasTotal, {
            type: 'bar', 
            data: {
                labels: window.chartData.labels, 
                datasets: [{
                    label: 'Coût total (€)',
                    data: window.chartData.totaux, 
                    backgroundColor: '#3b82f6', 
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
                        text: 'Coût total des prescriptions',
                        font: { size: 16 }
                    }
                }
            }
        });

        new Chart(canvasMoyenne, {
            type: 'bar',
            data: {
                labels: window.chartData.labels,
                datasets: [{
                    label: 'Coût moyen par professionnel (€)',
                    data: window.chartData.moyennes,
                    backgroundColor: '#ff9800', 
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
    
    if (ongletSauvegarde && ongletSauvegarde !== 'tab-graphique') {
        const boutonCorrespondant = document.querySelector(`button[onclick*="${ongletSauvegarde}"]`);
        
        if (boutonCorrespondant) {
            boutonCorrespondant.click();
            
            setTimeout(() => {
                document.getElementById(ongletSauvegarde).scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
        }
    }
});
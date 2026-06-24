/**********************************************************************/
/** 1. GESTION DE L'INTERFACE UTILISATEUR & FILTRES                  */
/**********************************************************************/

document.addEventListener('DOMContentLoaded', () => {
    const containers = document.querySelectorAll('.multi-select-container');
    const form = document.getElementById('form-filtres');

    containers.forEach(container => {
        const btn = container.querySelector('.select-btn');
        const dropdown = container.querySelector('.dropdown-content');
        const btnText = container.querySelector('.btnText');
        
        // Configuration de la liste déroulante
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

        // Comportement des boutons radio
        const radios = dropdown.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    btnText.textContent = radio.parentElement.textContent.trim();
                    dropdown.classList.remove('show');
                    
                    // Si on change de département ou d'année, on applique directement le filtre
                    if (radio.name === 'departement' || radio.name === 'annee') {
                        form.submit();
                    }
                }
            });
        });

        // Initialisation du texte au chargement
        const checkedRadio = dropdown.querySelector('input:checked');
        if (checkedRadio) {
            btnText.textContent = checkedRadio.parentElement.textContent.trim();
        }
    });

    document.addEventListener('click', () => {
        containers.forEach(container => {
            container.querySelector('.dropdown-content').classList.remove('show');
        });
    });

    /**********************************************************************/
    /** 2. SÉCURISATION & PASSERELLE DE DONNÉES                           */
    /**********************************************************************/
    const passerelle = document.getElementById('data-passerelle');
    if (!passerelle) return;

    const donneesGlobales = JSON.parse(passerelle.dataset.globales || '[]');
    const donneesPyramide = JSON.parse(passerelle.dataset.pyramide || '[]');

    /**********************************************************************/
    /** 3. CONSTRUIRE LE NUAGE DE POINTS (CHART.JS - SCATTER CHIPS)       */
    /**********************************************************************/
    const canvasScatter = document.getElementById('scatter-correlation');
    if (canvasScatter && donneesGlobales.length > 0) {
        
        // Extraction des coordonnées (X: % Seniors, Y: Coût Moyen)
        const scatterPoints = donneesGlobales.map(dept => ({
            x: dept.pourcentage_seniors,
            y: dept.cout_moyen,
            label: dept.departement_code
        }));

        new Chart(canvasScatter, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Départements français',
                    data: scatterPoints,
                    backgroundColor: '#3b82f6',
                    borderColor: '#1d4ed8',
                    pointRadius: 6,
                    pointHoverRadius: 9
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: 'Taux de praticiens seniors (+60 ans) en %', font: { weight: 'bold' } }
                    },
                    y: {
                        title: { display: true, text: 'Montant moyen des prescriptions (€)', font: { weight: 'bold' } }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const pt = context.raw;
                                return `Dép. ${pt.label} : ${pt.x}% Seniors | Moy : ${pt.y} €`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**********************************************************************/
    /** 4. CONSTRUIRE LA PYRAMIDE DES ÂGES (CHART.JS - HORIZONTAL BAR)    */
    /**********************************************************************/
    const canvasPyramide = document.getElementById('pyramide-ages');
    if (canvasPyramide && donneesPyramide.length > 0) {
        
        const labelsAges = donneesPyramide.map(d => d.age);
        // Inversion mathématique des données Hommes pour les projeter à gauche de la pyramide
        const valeursHommes = donneesPyramide.map(d => -Math.abs(d.hommes));
        const valeursFemmes = donneesPyramide.map(d => Math.abs(d.femmes));

        new Chart(canvasPyramide, {
            type: 'bar',
            data: {
                labels: labelsAges,
                datasets: [
                    {
                        label: 'Hommes',
                        data: valeursHommes,
                        backgroundColor: '#2563eb',
                        borderRadius: 4
                    },
                    {
                        label: 'Femmes',
                        data: valeursFemmes,
                        backgroundColor: '#ec4899',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                indexAxis: 'y', // Rotation des barres à l'horizontale
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        ticks: {
                            callback: function(value) {
                                return Math.abs(value); // On masque le signe "-" mathématique à l'affichage
                            }
                        }
                    },
                    y: { stacked: true }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label} : ${Math.abs(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**********************************************************************/
    /** 5. CARTOGRAPHIE CHOROPLÈTHE DYNAMIQUE (LEAFLET.JS)                */
    /**********************************************************************/
    const mapDiv = document.getElementById('map-deserts');
    if (mapDiv && donneesGlobales.length > 0) {
        
        // Échelle relative : Détermination des extrêmes réels
        const valeursPourcentages = donneesGlobales.map(d => d.pourcentage_seniors);
        const minPct = Math.min(...valeursPourcentages);
        const maxPct = Math.max(...valeursPourcentages);
        const amplitude = maxPct - minPct;

        // Fonction du thermomètre d'échelle relative adaptative
        function associerCouleurRelative(pourcentage) {
            if (pourcentage >= maxPct - (amplitude * 0.2)) return '#d73027'; // Risque Critique (Top 20%)
            if (pourcentage >= maxPct - (amplitude * 0.4)) return '#fc8d59'; // Alerte Orange
            if (pourcentage >= maxPct - (amplitude * 0.6)) return '#fee08b'; // Zone Modérée (Jaune)
            if (pourcentage >= maxPct - (amplitude * 0.8)) return '#d9ef8b'; // Tranche Saine
            return '#1a9850'; // Renouvellement optimal (Vert foncé)
        }

        // Initialisation géographique de la carte centrée sur la France
        const map = L.map('map-deserts').setView([46.2276, 2.2137], 5.5);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Intégration du GeoJSON des départements français
        // (En supposant que le fichier GeoJSON standard est hébergé localement)
        fetch('/static/data/departements.geojson')
            .then(response => response.json())
            .then(geojsonData => {
                L.geoJson(geojsonData, {
                    style: function(feature) {
                        const codeDeptGeo = feature.properties.code;
                        // Recherche de la correspondance de données
                        const matchDemo = donneesGlobales.find(d => d.departement_code === codeDeptGeo);
                        const pct = matchDemo ? matchDemo.pourcentage_seniors : minPct;

                        return {
                            fillColor: associerCouleurRelative(pct),
                            weight: 1,
                            opacity: 1,
                            color: '#ffffff',
                            fillOpacity: 0.75
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        const codeDeptGeo = feature.properties.code;
                        const nomDeptGeo = feature.properties.nom;
                        const matchDemo = donneesGlobales.find(d => d.departement_code === codeDeptGeo);
                        
                        let popupText = `<strong>${codeDeptGeo} - ${nomDeptGeo}</strong><br/>`;
                        if (matchDemo) {
                            popupText += `Taux de +60 ans : ${matchDemo.pourcentage_seniors}%<br/>`;
                            popupText += `Médecins actifs : ${matchDemo.total_medecins}`;
                        } else {
                            popupText += `Aucune donnée répertoriée`;
                        }
                        layer.bindPopup(popupText);
                    }
                }).addTo(map);
            }).catch(err => console.error("Impossible de tracer le GeoJSON : ", err));
    }

    /**********************************************************************/
    /** 6. EXPORT DES DONNÉES EN CSV                                      */
    /**********************************************************************/
    const btnExport = document.querySelector('.export-btn');
    if (btnExport) {
        btnExport.addEventListener('click', () => {
            const table = document.querySelector('.prescriptions-table-box table');
            if (!table) return alert("Aucun jeu de données disponible pour l'export.");

            let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
            const rows = table.querySelectorAll('tr');

            rows.forEach(row => {
                const cols = row.querySelectorAll('th, td');
                const rowData = Array.from(cols).map(col => `"${col.innerText.trim().replace('%', '')}"`);
                csvContent += rowData.join(";") + "\r\n";
            });

            const link = document.createElement("a");
            link.setAttribute("href", encodeURI(csvContent));
            link.setAttribute("download", `analye_correlation_demographie.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    /**********************************************************************/
    /** 7. MÉMOIRE DE L'ONGLET ACTIF AU RECHARGEMENT                      */
    /**********************************************************************/
    const ongletSauvegarde = sessionStorage.getItem('ongletActif');
    if (ongletSauvegarde && ongletSauvegarde !== 'tab-analyse') {
        const boutonCorrespondant = document.querySelector(`button[onclick*="${ongletSauvegarde}"]`);
        if (boutonCorrespondant) boutonCorrespondant.click();
    }
});

/**********************************************************************/
/** 8. FONCTION COMMUTATRICE DES ONGLET (ACCESSIBLE DEPUIS L'HTML)     */
/**********************************************************************/
function switchTab(event, tabId) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    const targetTab = document.getElementById(tabId);
    if (targetTab) targetTab.classList.add('active');
    event.currentTarget.classList.add('active');

    sessionStorage.setItem('ongletActif', tabId);
}
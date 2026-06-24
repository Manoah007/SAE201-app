function switchTab(event, tabId) {
    const parent = event.target.closest(".prescriptions-results");

    if (!parent) return;

    parent.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    parent.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    event.target.classList.add("active");

    const target = document.getElementById(tabId);
    if (target) target.classList.add("active");

    setTimeout(() => {
        window.dispatchEvent(new Event("resize"));
    }, 100);
}

document.addEventListener("DOMContentLoaded", () => {
    // Menus déroulants custom
    document.querySelectorAll(".multi-select-container .select-btn").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            event.stopPropagation();

            const container = btn.closest(".multi-select-container");
            const menu = container.querySelector(".dropdown-content");

            document.querySelectorAll(".dropdown-content.show").forEach((openMenu) => {
                if (openMenu !== menu) openMenu.classList.remove("show");
            });

            if (menu) menu.classList.toggle("show");
        });
    });

    document.addEventListener("click", () => {
        document.querySelectorAll(".dropdown-content.show").forEach((menu) => {
            menu.classList.remove("show");
        });
    });

    const passerelle = document.getElementById("data-passerelle");
    if (!passerelle) return;

    const donneesGlobales = JSON.parse(passerelle.dataset.globales || "[]");
    const donneesPyramide = JSON.parse(passerelle.dataset.pyramide || "[]");

    // Nuage de points
    const scatterCanvas = document.getElementById("scatter-correlation");

    if (scatterCanvas && donneesGlobales.length > 0) {
        new Chart(scatterCanvas, {
            type: "scatter",
            data: {
                datasets: [{
                    label: "Départements",
                    data: donneesGlobales.map(d => ({
                        x: Number(d.pourcentage_seniors) || 0,
                        y: Number(d.cout_moyen) || 0,
                        nom: d.nom_dept || d.departement_code
                    })),
                    backgroundColor: "#41e46a"
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const p = context.raw;
                                return `${p.nom} : ${p.x}% seniors · ${p.y} € moyen`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: "Part des praticiens de 60 ans et plus (%)" },
                        beginAtZero: true
                    },
                    y: {
                        title: { display: true, text: "Coût moyen de prescription (€)" },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Pyramide des âges
    const pyramideCanvas = document.getElementById("pyramide-ages");

    if (pyramideCanvas && donneesPyramide.length > 0) {
        new Chart(pyramideCanvas, {
            type: "bar",
            data: {
                labels: donneesPyramide.map(d => d.age),
                datasets: [
                    {
                        label: "Hommes",
                        data: donneesPyramide.map(d => -(Number(d.hommes) || 0)),
                        backgroundColor: "#2E74B5",
                        borderRadius: 6
                    },
                    {
                        label: "Femmes",
                        data: donneesPyramide.map(d => Number(d.femmes) || 0),
                        backgroundColor: "#41e46a",
                        borderRadius: 6
                    }
                ]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                scales: {
                    x: {
                        ticks: {
                            callback: value => Math.abs(value)
                        }
                    }
                }
            }
        });
    }

    // Carte Leaflet des départements à risque
    const mapElement = document.getElementById("map-deserts");

    if (mapElement && donneesGlobales.length > 0 && typeof L !== "undefined") {
        const map = L.map("map-deserts").setView([46.5, 2.5], 6);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap"
        }).addTo(map);

        const dataParDept = {};
        donneesGlobales.forEach(d => {
            dataParDept[d.departement_code] = d;
        });

        function couleur(pourcentage) {
            if (pourcentage >= 50) return "#dc2626";
            if (pourcentage >= 40) return "#f59e0b";
            if (pourcentage >= 30) return "#41e46a";
            return "#dfffe8";
        }

        fetch("https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson")
            .then(r => r.json())
            .then(geojson => {
                const layer = L.geoJSON(geojson, {
                    style: feature => {
                        const code = feature.properties.code;
                        const ligne = dataParDept[code];
                        const taux = ligne ? ligne.pourcentage_seniors : 0;

                        return {
                            fillColor: ligne ? couleur(taux) : "#e5e7eb",
                            fillOpacity: 0.85,
                            color: "#ffffff",
                            weight: 1
                        };
                    },
                    onEachFeature: (feature, layer) => {
                        const code = feature.properties.code;
                        const ligne = dataParDept[code];

                        layer.bindPopup(
                            ligne
                                ? `<strong>${feature.properties.nom}</strong><br>
                                   Seniors : ${ligne.pourcentage_seniors}%<br>
                                   Coût moyen : ${ligne.cout_moyen} €`
                                : `<strong>${feature.properties.nom}</strong><br>Aucune donnée`
                        );
                    }
                }).addTo(map);

                const metropole = L.geoJSON({
                    type: "FeatureCollection",
                    features: geojson.features.filter(f => !f.properties.code.startsWith("97"))
                });

                map.fitBounds(metropole.getBounds(), { padding: [10, 10] });

                setTimeout(() => {
                    map.invalidateSize();
                }, 300);
            });
    }
});
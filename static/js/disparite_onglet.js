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

    // Graphiques
    const passerelle = document.getElementById("data-passerelle");
    if (!passerelle) return;

    const labels = JSON.parse(passerelle.dataset.labels || "[]");
    const totaux = JSON.parse(passerelle.dataset.totaux || "[]");
    const moyennes = JSON.parse(passerelle.dataset.moyennes || "[]");

    const ctxTotal = document.getElementById("histogram-total");
    const ctxMoyenne = document.getElementById("histogram-moyenne");

    if (ctxTotal && labels.length > 0) {
        new Chart(ctxTotal, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Montant total (€)",
                    data: totaux,
                    backgroundColor: "#41e46a",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    if (ctxMoyenne && labels.length > 0) {
        new Chart(ctxMoyenne, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Montant moyen (€)",
                    data: moyennes,
                    backgroundColor: "#2E74B5",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
});
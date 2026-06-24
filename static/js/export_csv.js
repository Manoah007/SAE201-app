document.addEventListener("DOMContentLoaded", () => {
    const boutonsExport = document.querySelectorAll(".export-btn");

    boutonsExport.forEach((bouton) => {
        bouton.setAttribute("type", "button");

        bouton.addEventListener("click", (event) => {
            event.preventDefault();

            const table = trouverTableauLePlusProche(bouton);

            if (!table) {
                alert("Aucun tableau à exporter pour le moment. Lance d'abord une recherche.");
                return;
            }

            const csv = convertirTableauEnCSV(table);
            const nomFichier = creerNomFichier();

            telechargerCSV(csv, nomFichier);
        });
    });
});


function trouverTableauLePlusProche(bouton) {
    const section = bouton.closest("section");

    if (section) {
        const tableDansSection = section.querySelector("table");
        if (tableDansSection) {
            return tableDansSection;
        }
    }

    return document.querySelector("main table");
}


function convertirTableauEnCSV(table) {
    const lignes = table.querySelectorAll("tr");
    const contenuCSV = [];

    lignes.forEach((ligne) => {
        const cellules = ligne.querySelectorAll("th, td");
        const ligneCSV = [];

        cellules.forEach((cellule) => {
            let texte = cellule.innerText.trim();

            texte = texte.replace(/\s+/g, " ");
            texte = texte.replace(/"/g, '""');

            ligneCSV.push(`"${texte}"`);
        });

        contenuCSV.push(ligneCSV.join(";"));
    });

    return "\uFEFF" + contenuCSV.join("\n");
}


function creerNomFichier() {
    const titrePage = document.querySelector("h1");

    let nom = "export_sante_data";

    if (titrePage) {
        nom = titrePage.innerText
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "_")
            .replace(/^_+|_+$/g, "");
    }

    const date = new Date().toISOString().slice(0, 10);

    return `${nom}_${date}.csv`;
}


function telechargerCSV(contenu, nomFichier) {
    const blob = new Blob([contenu], {
        type: "text/csv;charset=utf-8;"
    });

    const lien = document.createElement("a");
    const url = URL.createObjectURL(blob);

    lien.href = url;
    lien.download = nomFichier;
    lien.style.display = "none";

    document.body.appendChild(lien);
    lien.click();

    document.body.removeChild(lien);
    URL.revokeObjectURL(url);
}
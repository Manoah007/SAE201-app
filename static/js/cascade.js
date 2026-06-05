document.getElementById("region").addEventListener("change", async (e) => {
    const regionId = e.target.value;
    const selectDept = document.getElementById("departement");

    // Vider la liste
    selectDept.innerHTML = '<option value="">-- Choisir --</option>';

    if (!regionId) return;

    // Appel AJAX (BASE_URL gère le préfixe en déploiement sous-dossier ; vide en local)
    const response = await fetch(`${BASE_URL}/api/departements/${regionId}`);
    const depts = await response.json();

    // Remplir la liste
    for (const dept of depts) {
        const opt = document.createElement("option");
        opt.value = dept.id;
        opt.textContent = `${dept.code} – ${dept.libelle}`;
        selectDept.appendChild(opt);
    }
});
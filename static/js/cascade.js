document.addEventListener("DOMContentLoaded", () => {
    const regionSelect = document.getElementById("region");
    const deptSelect = document.getElementById("departement");

    if (!regionSelect || !deptSelect) return;

    regionSelect.addEventListener("change", async () => {
        const regionId = regionSelect.value;
        const baseUrl = (typeof BASE_URL !== "undefined") ? BASE_URL : "";

        deptSelect.innerHTML = '<option value="">Département</option>';

        if (!regionId) return;

        try {
            const response = await fetch(`${baseUrl}/api/departements/${regionId}`);

            if (!response.ok) {
                throw new Error("Erreur lors du chargement des départements");
            }

            const departements = await response.json();

            departements.forEach((dept) => {
                const option = document.createElement("option");
                option.value = dept.id;
                option.textContent = `${dept.code} - ${dept.libelle}`;
                deptSelect.appendChild(option);
            });
        } catch (error) {
            console.error(error);
            deptSelect.innerHTML = '<option value="">Erreur de chargement</option>';
        }
    });
});
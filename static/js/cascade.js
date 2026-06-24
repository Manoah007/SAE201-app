/* 
    Script Json pour le fichier disparite_geo.html 
    Gère la mise à jour dynamique de la liste déroulante 
    des départements en fonction de la région sélectionnée.
*/

document.getElementById('region_select').addEventListener('change', function() {
    const regionId = this.value;
    const deptSelect = document.getElementById('departement_select');
    
    // On vide la deuxième liste
    deptSelect.innerHTML = '<option value="">Sélectionnez un département</option>';
    
    if (!regionId) {
        deptSelect.disabled = true;
        return;
    }

    // Appel en arrière-plan à notre route Flask
    fetch(`/api/departements/${regionId}`)
        .then(response => response.json())
        .then(data => {
            // On réactive la liste et on injecte les nouvelles options
            deptSelect.disabled = false;
            data.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.libelle;
                deptSelect.appendChild(option);
            });
        });
});
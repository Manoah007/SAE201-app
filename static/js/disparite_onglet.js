document.addEventListener("DOMContentLoaded", function () {
    const regionTout = document.getElementById('region_tout');
    const regionCheckboxes = document.querySelectorAll('.region-checkbox');
    const deptFilterGroup = document.getElementById('dept_filter_group');
    
    const departementTout = document.getElementById('departement_tout');
    const departementCheckboxes = document.querySelectorAll('.departement-checkbox');
    const formFiltres = document.getElementById('form-filtres');

    // --- LOGIQUE DES CHECKBOXES DE RÉGION ---
    if (regionTout) {
        regionTout.addEventListener('change', function () {
            if (this.checked) {
                // Si on coche TOUT, on décoche les autres régions
                regionCheckboxes.forEach(cb => cb.checked = false);
                if (deptFilterGroup) deptFilterGroup.style.display = 'none';
                if (departementTout) departementTout.checked = true;
                departementCheckboxes.forEach(cb => cb.checked = false);
            }
        });

        regionCheckboxes.forEach(cb => {
            cb.addEventListener('change', function () {
                if (this.checked) {
                    // Si on coche une région, on décoche obligatoirement le "TOUT"
                    regionTout.checked = false;
                    if (deptFilterGroup) deptFilterGroup.style.style.display = 'block';
                }
            });
        });
    }

    // --- LOGIQUE DES CHECKBOXES DE DÉPARTEMENT ---
    if (departementTout) {
        departementTout.addEventListener('change', function () {
            if (this.checked) {
                departementCheckboxes.forEach(cb => cb.checked = false);
            }
        });

        departementCheckboxes.forEach(cb => {
            cb.addEventListener('change', function () {
                if (this.checked) {
                    departementTout.checked = false;
                } else {
                    const unDeptEstCoche = Array.from(departementCheckboxes).some(c => c.checked);
                    if (!unDeptEstCoche) departementTout.checked = true;
                }
            });
        });
    }

    // --- SÉCURITÉ AU SUBMIT (CONTRAINTE STRICTE MIN 2 DEPARTEMENTS) ---
    if (formFiltres) {
        formFiltres.addEventListener('submit', function (e) {
            const deptsCoches = Array.from(departementCheckboxes).filter(cb => cb.checked);
            
            // Si on filtre une région spécifique mais qu'on choisit des départements précis, il en faut min 2
            if (!regionTout.checked && !departementTout.checked && deptsCoches.length < 2) {
                e.preventDefault();
                alert("⚠️ Contrainte de comparaison : Veuillez cocher au minimum 2 départements pour générer les graphiques.");
            }
        });
    }
});
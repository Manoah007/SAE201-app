document.addEventListener('DOMContentLoaded', () => {
    // On récupère tous les blocs de filtres à choix multiple
    const containers = document.querySelectorAll('.multi-select-container');
    const form = document.getElementById('form-filtres');

    containers.forEach(container => {
        // Pour chaque bloc, on cherche ses éléments internes spécifiques
        const btn = container.querySelector('.select-btn');
        const dropdown = container.querySelector('.dropdown-content');
        const btnText = container.querySelector('.btnText');
        const defaultText = btnText.textContent; // Sauvegarde le texte d'origine ("RÉGIONS" ou "DÉPARTEMENT")
        const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');

        // OUVERTURE / FERMETURE au clic sur le bouton
        btn.addEventListener('click', (event) => {
            // Ferme les autres menus déroulants s'ils sont ouverts
            containers.forEach(c => {
                if (c !== container) c.querySelector('.dropdown-content').classList.remove('show');
            });
            // Alterne l'affichage du menu actuel
            dropdown.classList.toggle('show');
            event.stopPropagation(); // Empêche le clic de se propager au document
        });

        // MISE À JOUR DU TEXTE DU BOUTON au changement des cases à cocher
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const checkedBoxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');
                const checkedCount = checkedBoxes.length;

                if (checkedCount === 0) {
                    btnText.textContent = defaultText; // Revenir à "RÉGIONS"
                } else if (checkedCount === 1) {
                    // S'il n'y a qu'un choix, on affiche son nom exact (ex: "Bretagne")
                    btnText.textContent = checkedBoxes[0].parentElement.textContent.trim();
                } else {
                    // S'il y a plusieurs choix, on affiche le nombre (ex: "3 sélectionnés")
                    btnText.textContent = `${checkedCount} sélectionnés`;
                }

                // SOUUMISSION AUTOMATIQUE (Optionnel)
                // Si tu veux que la page se recharge dès qu'on coche une case, décommente la ligne suivante :
                // form.submit();
            });
        });
    });

    // FERMETURE DU MENU si on clique n'importe où à l'extérieur sur la page
    document.addEventListener('click', () => {
        containers.forEach(container => {
            container.querySelector('.dropdown-content').classList.remove('show');
        });
    });
});
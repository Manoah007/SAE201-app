import unittest
from unittest.mock import MagicMock
# Remplacez 'votre_module' par le nom du fichier Python contenant votre classe
from ameli_api import AmeliAPI 

class TestGetRegionPrescription(unittest.TestCase):

    def setUp(self):
        """Configuration initiale exécutée avant chaque test."""
        self.service = AmeliAPI()
        # On remplace la méthode interne _requete par un "Mock" (un faux)
        self.service._requete = MagicMock()

    def test_get_region_prescription_avec_annee_uniquement(self):
        """Cas 1 : L'utilisateur filtre uniquement par année (sans région)."""
        # Appel de la fonction
        self.service.get_region_prescription(annee='2024', region_list_id=None, limite_ligne=10)

        # Vérification : _requete doit avoir été appelée avec la bonne clause WHERE
        self.service._requete.assert_called_once_with(
            "prescription",
            {
                "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
                "where": "annee=2024",
                "limit": 10
            }
        )

    def test_get_region_prescription_avec_regions(self):
        """Cas 2 : L'utilisateur filtre par année ET sélectionne plusieurs régions."""
        # Appel de la fonction avec une liste de régions
        self.service.get_region_prescription(annee='2023', region_list_id=['11', '24'])

        # Vérification de la construction dynamique du "WHERE" avec l'opérateur "IN"
        self.service._requete.assert_called_once_with(
            "prescription",
            {
                "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
                "where": "annee=2023 AND region_id IN (11,24)",
                "limit": 25 # Limite par défaut
            }
        )

    def test_get_region_prescription_avec_liste_vide(self):
        """Cas 3 : Sécurité si region_list_id est une liste vide []."""
        self.service.get_region_prescription(annee='2024', region_list_id=[])

        # Vérification : La liste vide ne doit pas ajouter le "IN" pour éviter un crash SQL
        self.service._requete.assert_called_once_with(
            "prescription",
            {
                "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
                "where": "annee=2024",
                "limit": 25
            }
        )

if __name__ == '__main__':
    unittest.main()
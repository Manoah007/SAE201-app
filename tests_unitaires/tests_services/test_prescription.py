import pytest
from unittest.mock import MagicMock
from services.ameli_api import AmeliAPI

@pytest.fixture
def api_service():
    """Fixture qui crée une instance de l'API avec une méthode _requete mockée."""
    service = AmeliAPI()
    service._requete = MagicMock()
    return service


def test_get_prescription_default(api_service):
    "Renvoie le toutes les régions ainsi que montant (total et moyen) selon 2024"
    api_service.get_prescription_default() 

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2024",
            "limit": 25
        }
    )

def test_get_region_prescription_avec_annee_uniquement(api_service):
    """Filtre uniquement par année (sans région)."""
    # Appel de la fonction
    api_service.get_region_prescription(annee='2024', region_list_id=None, limite_ligne=10)

    # Vérification
    api_service._requete.assert_called_once_with(
        "prescription",
        {
            "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2024",
            "limit": 10
        }
    )


def test_get_region_prescription_avec_regions(api_service):
    """Filtre par année ET pour plusieurs régions."""
    # Appel de la fonction
    api_service.get_region_prescription(annee='2023', region_list_id=['11', '24'])

    # Vérification
    api_service._requete.assert_called_once_with(
        "prescription",
        {
            "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2023 AND region_id IN (11,24)",
            "limit": 25  # Limite par défaut
        }
    )


def test_get_region_prescription_avec_liste_vide(api_service):
    """Sécurité si region_list_id est une liste vide []."""
    # Appel de la fonction
    api_service.get_region_prescription(annee='2024', region_list_id=[])

    # Vérification : La liste vide ne doit pas ajouter le "IN"
    api_service._requete.assert_called_once_with(
        "prescription",
        {
            "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2024",
            "limit": 25
        }
    )
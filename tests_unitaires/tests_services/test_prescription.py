import pytest
from unittest.mock import MagicMock
from services.ameli_api import AmeliAPI


##============================================================##
## Test des fonctions de requêtes SQL de la page améli_api.py ##
##============================================================##

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
            "limit": 30
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



def test_cross_filter_cas_1_tout_selectionne(api_service):
    """Cas 1 : Vérifie le maillage régional brut lorsque le filtre TOUT est appliqué (département et région)."""

    # Appel avec les paramètres par défaut / vides
    api_service.get_prescriptions_cross_filter(region_list_id=None, departement_list_id=None, annee='2024')

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2024",
            "limit": 100
        }
    )

    


def test_cross_filter_cas_2_departements_specifiques(api_service):
    """Cas 2 : Vérifie le filtrage par identifiants de départements."""
    
    # Appel en simulant la sélection des départements 75 et 94 (Paris et Val-de-Marne)
    api_service.get_prescriptions_cross_filter(region_list_id=['11'], departement_list_id=['75', '94'], annee='2024')

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "departement,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2024 AND departement_id IN (75,94)",
            "limit": 100
        }
    )




def test_cross_filter_cas_3_selection_rapide_region(api_service):
    """Cas 3 : Vérifie l'affichage de tous les départements d'une région donnée."""

    # L'utilisateur choisit la région 11 mais laisse les départements vides
    api_service.get_prescriptions_cross_filter(region_list_id=['11'], departement_list_id=None, annee='2024')

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "departement,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
            "where": "annee=2024 AND region_id IN (11)",
            "limit": 100
        }
    )


##===============================================================##
## Test de la fonction page_disparite() de la page prescriptions ##
##===============================================================##
from unittest.mock import patch
from flask import Flask


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test'
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client() if hasattr(app, 'test_client') else app.test_client()

@pytest.fixture
def mock_dependencies():
    """Fixture pour cloner (ou imiter) la base de données, l'API externe et render_template."""
    with patch('prescriptions.Session') as mock_session_cls, \
         patch('prescriptions.api') as mock_api, \
         patch('prescriptions.render_template') as mock_render:
        
        # Simulation du comportement de la base de données SQLAlchemy
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        
        # Données factices pour les listes déroulantes
        mock_session.query.return_value.order_by.return_value.all.return_value = ['item1', 'item2']
        
        yield {
            'session': mock_session,
            'api': mock_api,
            'render': mock_render
        }



def test_page_disparite_cas_1_maillage_regional(app, mock_dependencies):
    """
    Vérifie que le Cas 1 (Premier chargement ou "TOUT" sélectionné) 
    appelle le cross-filter sans filtres géographiques (Maillage Régional)
    """

    with app.test_request_context('/?annee=2024'):
        # On simule l'import ou l'exécution de ta fonction
        from controllers.prescriptions import page_disparite
        page_disparite()

        # On vérifie l'appel API attendu
        mock_dependencies['api'].get_prescriptions_cross_filter.assert_called_once_with(
            region_list_id=None,
            departement_list_id=None,
            annee='2024'
        )
        
        # On valide les variables transmises à Jinja2
        mock_dependencies['render'].assert_called_once()
        kwargs = mock_dependencies['render'].call_args[1]
        assert kwargs['mode_maillage_regional'] is True
        assert kwargs['error_message'] is None


def test_page_disparite_cas_2_selection_rapide(app, mock_dependencies):
    """
    Vérifie que le Cas 2 (Région sélectionnée ET Option "TOUT" pour les Départements)
    appelle le cross-filter pour extraire les départements d'une région
    """

    # Simulation d'une URL contenant une région, mais l'option TOUT pour le département
    with app.test_request_context('/?region_id=11&departement_id=TOUT&annee=2024'):
        from controllers.prescriptions import page_disparite
        page_disparite()

        mock_dependencies['api'].get_prescriptions_cross_filter.assert_called_once_with(
            region_list_id=['11'],
            departement_list_id=None,
            annee='2024'
        )
        
        kwargs = mock_dependencies['render'].call_args[1]
        assert kwargs['mode_maillage_regional'] is False


def test_page_disparite_cas_3_infraction_contrainte(app, mock_dependencies):
    """
    Vérifie que la sélection d'un seul département 
    lève l'erreur métier et bascule sur le message d'erreur
    """

    # L'utilisateur tente de valider un seul département
    with app.test_request_context('/?region_id=11&departement_id=75&annee=2024'):
        from controllers.prescriptions import page_disparite
        page_disparite()

        # L'application doit ignorer le cross-filter et charger le secours par défaut
        mock_dependencies['api'].get_prescription_default.assert_called_once_with(annee='2024')
        
        kwargs = mock_dependencies['render'].call_args[1]
        assert kwargs['error_message'] is not None
        assert "Au moins 2 départements" in kwargs['error_message']
        assert kwargs['mode_maillage_regional'] is True



def test_page_disparite_cas_3_conforme(app, mock_dependencies):
    """Vérifie que la sélection de 2 départements ou plus exécute le filtrage ciblé."""


    # L'utilisateur sélectionne 2 départements valides
    with app.test_request_context('/?region_id=11&departement_id=75&departement_id=94&annee=2024'):
        from controllers.prescriptions import page_disparite
        page_disparite()

        mock_dependencies['api'].get_prescriptions_cross_filter.assert_called_once_with(
            region_list_id=['11'],
            departement_list_id=['75', '94'],
            annee='2024'
        )
        
        kwargs = mock_dependencies['render'].call_args[1]
        assert kwargs['error_message'] is None
        assert kwargs['mode_maillage_regional'] is False
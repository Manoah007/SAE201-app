###########################========#############################
## Test des fonctions de requêtes SQL de la page améli_api.py ##
###########################========#############################
import pytest
from unittest.mock import MagicMock
from services.ameli_api import AmeliAPI



###########################==========#############################
## TESTS DES FONCTIONS DE PRESCRIPTIONS DE LA PAGE ameli_api.py ##
###########################==========#############################
@pytest.fixture
def api_service():
    """Fixture qui crée une instance de l'API avec une méthode _requete mockée."""
    service = AmeliAPI()
    service._requete = MagicMock()
    return service


##==============================================================##
##      Test de la fonction get_prescription_toutes_zones()     ##
##==============================================================##

def test_get_prescription_toutes_zones_departements(api_service):
    """Vérifie le filtrage quand toutes_regions=True et tous_départ=True."""
    api_service.get_prescription_toutes_zones(
        toutes_regions=True, 
        tous_départ=True, 
        annee="2024", 
        limite_ligne=30
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2024",
            "group_by": "libelle_departement",
            "limit": 30
        }
    )


def test_get_prescription_toutes_zones_regions_uniquement(api_service):
    """Vérifie le filtrage quand toutes_regions=True et tous_départ=False."""
    api_service.get_prescription_toutes_zones(
        toutes_regions=True, 
        tous_départ=False, 
        annee="2023", 
        limite_ligne=15
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2023",
            "group_by": "libelle_region",
            "limit": 15
        }
    )


def test_get_prescription_toutes_zones_aucune_zone(api_service):
    """Vérifie le comportement de sécurité si toutes_regions est à False."""
    # Aucun bloc if/elif n'étant validé, la fonction ne doit pas appeler l'API
    resultat = api_service.get_prescription_toutes_zones(
        toutes_regions=False, 
        tous_départ=False
    )

    assert resultat is None
    api_service._requete.assert_not_called()



##==============================================================##
##        Test de la fonction get_region_prescription           ##
##==============================================================##

def test_get_region_prescription_avec_annee_uniquement(api_service):
    """Vérifie la construction SQL sans aucune région (liste vide ou None)."""
    api_service.get_region_prescription(
        region_list_id=None, 
        annee="2024", 
        limite_ligne=30
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2024",
            "group_by": "libelle_region",
            "limit": 30
        }
    )


def test_get_region_prescription_avec_plusieurs_regions(api_service):
    """Vérifie la construction SQL avec une liste contenant plusieurs IDs de régions."""
    api_service.get_region_prescription(
        region_list_id=["11", "24", "53"], 
        annee="2023", 
        limite_ligne=10
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2023 AND region IN ('11','24','53')",
            "group_by": "libelle_region",
            "limit": 10
        }
    )


def test_get_region_prescription_avec_une_seule_region(api_service):
    """Vérifie que l'opérateur IN fonctionne correctement même avec un seul élément dans la liste."""
    api_service.get_region_prescription(
        region_list_id=["84"], 
        annee="2022", 
        limite_ligne=30
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2022 AND region IN ('84')",
            "group_by": "libelle_region",
            "limit": 30
        }
    )



##==============================================================##
##     Test de la fonction get_departement_prescriptions        ##
##==============================================================##
def test_get_departement_prescriptions_annee_uniquement(api_service):
    """Vérifie la construction SQL avec l'année seule (sans filtre de zone)."""
    api_service.get_departement_prescriptions(
        region_list_id=None,
        departement_list_id=None,
        annee="2024",
        limite_ligne=100
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2024",
            "group_by": "libelle_departement",
            "limit": 100
        }
    )


def test_get_departement_prescriptions_avec_departements_uniquement(api_service):
    """Vérifie la construction SQL avec un filtre sur les départements uniquement."""
    api_service.get_departement_prescriptions(
        region_list_id=None,
        departement_list_id=["29", "35"],
        annee="2024",
        limite_ligne=50
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2024 AND departement IN ('29','35')",
            "group_by": "libelle_departement",
            "limit": 50
        }
    )


def test_get_departement_prescriptions_avec_regions_uniquement(api_service):
    """Vérifie la construction SQL avec un filtre sur les régions uniquement."""
    api_service.get_departement_prescriptions(
        region_list_id=["53"],
        departement_list_id=None,
        annee="2023",
        limite_ligne=100
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2023 AND region IN ('53')",
            "group_by": "libelle_departement",
            "limit": 100
        }
    )


def test_get_departement_prescriptions_avec_regions_et_departements(api_service):
    """Vérifie l'accumulation des clauses quand les deux filtres de zones sont fournis."""
    api_service.get_departement_prescriptions(
        region_list_id=["11", "24"],
        departement_list_id=["75", "92"],
        annee="2022",
        limite_ligne=200
    )

    api_service._requete.assert_called_once_with(
        "prescriptions",
        {
            "select": "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
            "where": "year(annee)=2022 AND departement IN ('75','92') AND region IN ('11','24')",
            "group_by": "libelle_departement",
            "limit": 200
        }
    )









#########################==========###########################
## TESTS DE LA page_disparite() DE LA PAGE prescriptions.py ##
#########################==========###########################
from unittest.mock import patch
from flask import Flask
from controllers.prescriptions import page_disparite


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
    with patch('controllers.prescriptions.Session') as mock_session_cls, \
         patch('controllers.prescriptions.api') as mock_api, \
         patch('controllers.prescriptions.render_template') as mock_render:
        
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



def test_page_disparite_scenario_0_premier_chargement(app, mock_dependencies):
    """Vérifie le comportement lors du premier chargement sans paramètres URL."""
    ctx = mock_dependencies
    
    ctx['api'].get_prescription_toutes_zones.return_value = [
        {"libelle_region": "Bretagne", "cout_total": 5000, "cout_moyen": 120.556}
    ]

    with app.test_request_context('/page_disparite'):
        page_disparite()

    ctx['api'].get_prescription_toutes_zones.assert_called_once_with(
        toutes_regions=True,
        tous_départ=False,
        annee="2024",
        limite_ligne=110
    )
    
    ctx['render'].assert_called_once()
    kwargs_template = ctx['render'].call_args[1]
    assert kwargs_template["mode_maillage_regional"] is True
    assert kwargs_template["labels_zones"] == ["Bretagne"]
    assert kwargs_template["valeurs_totales"] == [5000]
    assert kwargs_template["valeurs_moyennes"] == [120.56]
    ctx['session'].close.assert_called_once()


def test_page_disparite_scenario_1_maillage_departemental_filtre(app, mock_dependencies):
    """Vérifie le filtrage ciblé par départements ou par régions."""
    ctx = mock_dependencies
    
    ctx['api'].get_departement_prescriptions.return_value = [
        {"libelle_departement": "Paris", "cout_total": 10000, "cout_moyen": 250.00}
    ]

    url = '/page_disparite?regions=11&departements=75&annee=2024&ligne_max=110'
    with app.test_request_context(url):
        page_disparite()

    ctx['api'].get_departement_prescriptions.assert_called_once_with(
        region_list_id=["11"],
        departement_list_id=["75"],
        annee="2024",
        limite_ligne=110
    )
    
    kwargs_template = ctx['render'].call_args[1]
    assert kwargs_template["mode_maillage_regional"] is False
    assert kwargs_template["labels_zones"] == ["Paris"]


def test_page_disparite_scenario_2_tous_les_departements(app, mock_dependencies):
    """Vérifie la sélection de tous les départements via l'option ALL."""
    ctx = mock_dependencies
    ctx['api'].get_prescription_toutes_zones.return_value = []

    with app.test_request_context('/page_disparite?regions=ALL&departements=ALL'):
        page_disparite()

    ctx['api'].get_prescription_toutes_zones.assert_called_once_with(
        toutes_regions=True,
        tous_départ=True,
        annee="2024",
        limite_ligne=110
    )



def test_page_disparite_gestion_erreur_serveur(app, mock_dependencies):
    """Vérifie l'interception des anomalies SQL et le renvoi du statut 500."""
    ctx = mock_dependencies
    ctx['session'].query.side_effect = Exception("Erreur fatale base de données")

    with app.test_request_context('/page_disparite'):
        response, status_code = page_disparite()

    assert status_code == 500
    assert response == "Une erreur serveur est survenue."
    ctx['session'].close.assert_called_once()
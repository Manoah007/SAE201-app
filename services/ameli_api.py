import requests

class AmeliAPI:
    """Service d'accès à l'API data.ameli.fr."""

    BASE_URL = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets"

    def __init__(self, timeout=10):
        self._timeout = timeout
        self._session = requests.Session()

    def get_effectifs(self, profession, departement_code, annee):
        """Effectifs pour une profession, un département et une année."""

        where = (
            f'profession_sante="{profession}" AND '
            f'departement="{departement_code}" AND '
            f'year(annee)={annee} AND '
            f'libelle_classe_age="Tout âge" AND '
            f'libelle_sexe="tout sexe"'
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "annee,effectif,densite",
                "where": where,
                "limit": 100
            }
        )

    def get_evolution_effectifs(self, profession, departement_code):
        """Effectifs sur toutes les années disponibles."""

        where = (
            f'profession_sante="{profession}" AND '
            f'departement="{departement_code}" AND '
            f'libelle_classe_age="Tout âge" AND '
            f'libelle_sexe="tout sexe"'
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "annee,effectif,densite",
                "where": where,
                "order_by": "annee",
                "limit": 100
            }
        )

    def _requete(self, dataset, params):
        """Effectue une requête GET vers l'API."""

        url = f"{self.BASE_URL}/{dataset}/records"

        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json().get("results", [])

        except requests.RequestException as e:
            print(f"[AmeliAPI] Erreur : {e}")
            return []
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

    def get_honoraires(self, profession, departement_code, annee):
        """Récupère les honoraires pour une profession, un département et une année."""

        print("Profession envoyée :", profession, flush=True)
        print("Département envoyé :", departement_code, flush=True)
        print("Année envoyée :", annee, flush=True)

        where = (
            f'profession_sante="{profession}" AND '
            f'departement="{departement_code}" AND '
            f'year(annee)={annee}'
        )

        return self._requete(
            "honoraires",
            {
                "where": where,
                "limit": 100
            }
        )

# REQUËTES DE DONNÉES POUR LES PRESCRIPTIONS

    def get_prescript_test(self):
        """Récupère uniquement les professions selon la régions et l'année dans l'API"""

        return self._requete(
            "prescriptions",
            { 
                "select" : "profession_sante,region,annee",
                "limite" : 10
            }
        )

    def get_prescriptions(self, profession_name, departement_code, annee, type_prescription):
        """Récupère les prescriptions pour une profession, un département, une année et un poste."""

        where = (
            f'profession_sante="{profession_name}" AND '
            f'departement="{departement_code}" AND '
            f'year(annee)={annee} AND '
            f'libelle_poste_prescription="{type_prescription}"'
        )

        return self._requete(
            "prescriptions", # nom de la table
            {
                "select": "annee,prescriptions",    # colonne que l'on veut récupéré
                "where": where,                     # filtre
                "limit": 100                        # limite de lignes que l'on souhaite
            }
        )

    def get_evolution_prescriptions(self, profession, departement_code, poste_prescription):
        """Récupère l'évolution des prescriptions sur toutes les années disponibles."""

        where = (
            f'profession_sante="{profession}" AND '
            f'departement="{departement_code}" AND '
            f'libelle_poste_prescription="{poste_prescription}"'
        )

        return self._requete(
            "prescriptions",
            {
                "where": where,
                "order_by": "annee",
                "limit": 100
            }
        )

    def get_patientele(self, profession, departement_code, annee):
        """Récupère les données de patientèle pour une profession, un département et une année."""

        where = (
            f'profession_sante="{profession}" AND '
            f'departement="{departement_code}" AND '
            f'year(annee)={annee}'
        )

        return self._requete(
            "patientele",
            {
                "select": "annee,patientele",
                "where": where,
                "limit": 100
            }
        )

    def _requete(self, dataset, params):
        """Effectue une requête GET vers l'API."""

        url = f"{self.BASE_URL}/{dataset}/records"

        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)

            print("URL appelée :", resp.url, flush=True)
            print("Statut API :", resp.status_code, flush=True)

            if resp.status_code != 200:
                print("Erreur API :", resp.text, flush=True)

            resp.raise_for_status()

            data = resp.json().get("results", [])
            print("Nombre de résultats :", len(data), flush=True)

            return data

        except requests.RequestException as e:
            print(f"[AmeliAPI] Erreur : {e}", flush=True)
            return []
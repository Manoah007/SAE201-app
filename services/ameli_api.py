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

    def get_prescriptions(self, profession, departement_code, annee, poste_prescription):
        """Récupère les prescriptions pour une profession, un département, une année et un poste."""

        where = (
            f'profession_sante="{profession}" AND '
            f'departement="{departement_code}" AND '
            f'year(annee)={annee} AND '
            f'libelle_poste_prescription="{poste_prescription}"'
        )

        return self._requete(
            "prescriptions",
            {
                "select": "annee,prescriptions",
                "where": where,
                "limit": 100
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

    def get_repartition_departements(self, profession, annee, libelle_sexe="tout sexe", libelle_classe_age="Tout âge"):
        """Effectifs agrégés par département (sum), pour une profession et une année données.

        On filtre sur `departement is not null` pour ne garder que les lignes
        de granularité "département" et éviter de compter en double les lignes
        de granularité région/France entière qui pourraient exister dans le jeu de données.
        """

        where = (
            f'profession_sante="{profession}" AND '
            f'year(annee)={annee} AND '
            f'libelle_sexe="{libelle_sexe}" AND '
            f'libelle_classe_age="{libelle_classe_age}" AND '
            f'departement is not null'
        )

        return self._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, sum(effectif) as effectif",
                "where": where,
                "group_by": "departement",
                "limit": 100
            }
        )

    def get_repartition_sexe(self, profession, annee, libelle_classe_age="Tout âge"):
        """Effectifs agrégés par sexe (hors la ligne récapitulative 'tout sexe'), France entière."""

        where = (
            f'profession_sante="{profession}" AND '
            f'year(annee)={annee} AND '
            f'libelle_classe_age="{libelle_classe_age}" AND '
            f'libelle_sexe!="tout sexe" AND '
            f'departement is not null'
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "libelle_sexe, sum(effectif) as effectif",
                "where": where,
                "group_by": "libelle_sexe",
                "limit": 10
            }
        )

    def get_repartition_age(self, profession, annee, libelle_sexe="tout sexe"):
        """Effectifs agrégés par tranche d'âge (hors la ligne récapitulative 'Tout âge'), France entière."""

        where = (
            f'profession_sante="{profession}" AND '
            f'year(annee)={annee} AND '
            f'libelle_sexe="{libelle_sexe}" AND '
            f'libelle_classe_age!="Tout âge" AND '
            f'departement is not null'
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "libelle_classe_age, sum(effectif) as effectif",
                "where": where,
                "group_by": "libelle_classe_age",
                "limit": 20
            }
        )

    def get_repartition_professions(self, annee, libelle_sexe="tout sexe", libelle_classe_age="Tout âge"):
        """Effectifs agrégés par profession de santé, France entière."""

        where = (
            f'year(annee)={annee} AND '
            f'libelle_sexe="{libelle_sexe}" AND '
            f'libelle_classe_age="{libelle_classe_age}" AND '
            f'departement is not null'
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "profession_sante, sum(effectif) as effectif",
                "where": where,
                "group_by": "profession_sante",
                "limit": 100
            }
        )

    def _requete_paginee(self, dataset, params, limite_max=1000):
        """Enchaîne les appels avec offset pour récupérer tous les résultats
        quand on s'attend à plus de `limit` lignes (ex : ~100 départements)."""

        resultats = []
        offset = 0
        taille_page = params.get("limit", 100)

        while True:
            page_params = dict(params)
            page_params["limit"] = taille_page
            page_params["offset"] = offset

            lot = self._requete(dataset, page_params)
            resultats.extend(lot)

            if len(lot) < taille_page or len(resultats) >= limite_max:
                break

            offset += taille_page

        return resultats

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
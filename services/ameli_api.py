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
#=====================================================================#
# REQUËTES SQL DE RÉCUPÉRATION DE DONNÉES RELATIVES AUX PRESCRIPTIONS #
#=====================================================================#

    def get_prescription_toutes_zones(self, toutes_regions=True, tous_départ=False, annee="2024", limite_ligne=30):
        """Affiche soit tous les départements, soit toutes les régions"""

        print("\nameli_api.py | get_prescription_toutes_zones()")

        if toutes_regions and tous_départ:
            print(f"Retourne tous les départements : toutes_regions={toutes_regions} et tous_départ={tous_départ}")
            return self._requete("prescriptions",
                                {
                                "select" : "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                                "where" : f'year(annee)={annee}',
                                "group_by" : "libelle_departement",
                                "limit" : limite_ligne
                                }
                                )
        
        elif toutes_regions:
            print(f"Retourne toutes les régions: toutes_regions={toutes_regions}")
            return self._requete("prescriptions",
                                {
                                "select" : "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                                "where" : f'year(annee)={annee}',
                                "group_by" : "libelle_region",
                                "limit" : limite_ligne
                                }
                                )
        


    def get_region_prescription(self, region_list_id=None, annee="2024", limite_ligne=30):
        """Filtre les montants totales et moyens selon la (ou les) région(s) pour une année donnée"""

        print("\nameli_api.py | get_region_prescription()")

        where_clauses = [f"year(annee)={annee}"]

        if region_list_id:
            ids_reg = ",".join([f"'{r_id}'" for r_id in region_list_id]) # On s'assure que tous les IDs sont des chaînes ou des entiers propres
            where_clauses.append(f"region IN ({ids_reg})") # Utilisation de l'opérateur IN pour gérer la liste

        where = " AND ".join(where_clauses)

        print(f"Création du filtre SQL : WHERE {where}")

        return self._requete(
            "prescriptions",
            {
                "select" : "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                "where" : where,
                "group_by" : "libelle_region",
                "limit" : limite_ligne
            }
        )


    def get_departement_prescriptions(self, region_list_id=None, departement_list_id=None, annee="2024", limite_ligne=100):
        """Filtre les montants totales et moyens selon le (ou les) département(s) pour une année donnée"""
        
        print("\nameli_api.py | get_departement_prescriptionsr()")

        where_clauses = [f"year(annee)={annee}"]
        select_fields = "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen"
        
        if departement_list_id:
            ids_dep = ",".join([f"'{d_id}'" for d_id in departement_list_id])
            where_clauses.append(f"departement IN ({ids_dep})")
            
        if region_list_id:
            ids_reg = ",".join([f"'{r_id}'" for r_id in region_list_id])
            where_clauses.append(f"region IN ({ids_reg})")
        
        else:
            print(f"Les listes sont vides | region_list_id={region_list_id}, departement_list_id={departement_list_id}")


        where_final = " AND ".join(where_clauses)
        print(f"Filtre WHERE : {where_final}")


        return self._requete(
            "prescriptions",
            {
                "select": select_fields,
                "where": where_final,
                "group_by" : "libelle_departement",
                "limit": limite_ligne
            }
        )

#====================================================================================================#


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
        """Effectifs par (département, sexe), hors la ligne récapitulative 'tout sexe'.

        On groupe aussi par département (comme get_repartition_departements) car
        filtrer uniquement sur 'departement is not null' ne suffit pas à exclure les
        lignes de niveau régional/national : elles ont aussi une valeur dans ce champ,
        ce qui provoquait un triple comptage (national + régions + départements).
        Le tri par département connu se fait ensuite côté Python (dashboard_service.py).
        """

        where = (
            f'profession_sante="{profession}" AND '
            f'year(annee)={annee} AND '
            f'libelle_classe_age="{libelle_classe_age}" AND '
            f'libelle_sexe!="tout sexe" AND '
            f'departement is not null'
        )

        return self._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, libelle_sexe, sum(effectif) as effectif",
                "where": where,
                "group_by": "departement, libelle_sexe",
                "limit": 100
            }
        )

    def get_repartition_age(self, profession, annee, libelle_sexe="tout sexe"):
        """Effectifs par (département, tranche d'âge), hors la ligne récapitulative 'Tout âge'.

        Même logique que get_repartition_sexe : on groupe par département pour pouvoir
        ne garder, côté Python, que les vraies lignes départementales.
        """

        where = (
            f'profession_sante="{profession}" AND '
            f'year(annee)={annee} AND '
            f'libelle_sexe="{libelle_sexe}" AND '
            f'libelle_classe_age!="Tout âge" AND '
            f'departement is not null'
        )

        return self._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, libelle_classe_age, sum(effectif) as effectif",
                "where": where,
                "group_by": "departement, libelle_classe_age",
                "limit": 100
            }
        )

    def get_repartition_professions(self, annee, libelle_sexe="tout sexe", libelle_classe_age="Tout âge"):
        """Effectifs par (département, profession de santé).

        Même logique : on groupe par département pour exclure le bruit régional/national,
        le tri par code connu se fait ensuite côté Python.
        """

        where = (
            f'year(annee)={annee} AND '
            f'libelle_sexe="{libelle_sexe}" AND '
            f'libelle_classe_age="{libelle_classe_age}" AND '
            f'departement is not null'
        )

        return self._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, profession_sante, sum(effectif) as effectif",
                "where": where,
                "group_by": "departement, profession_sante",
                "limit": 100
            }
        )

    def _requete_paginee(self, dataset, params, limite_max=5000):
        """Enchaîne les appels avec offset pour récupérer tous les résultats
        quand on s'attend à plus de `limit` lignes (ex : département x profession
        peut monter jusqu'à ~3800 combinaisons)."""

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
        

    def get_pathologies(self, departement_code, annee):
        """Récupère la pathologie la plus fréquente pour un département et une année."""
        
        # On filtre sur le département et l'année. 
        where = (
            f'departement="{departement_code}" AND '
            f'year(annee)={annee}'
        )

        # "cartographie-des-pathologies" est le nom classique du dataset sur data.ameli.fr
        # S'il n'est pas disponible, l'API renverra une liste vide sans faire planter ton site.
        return self._requete(
            "cartographie-des-pathologies",
            {
                # On demande le nom de la maladie, le nombre de patients et le coût
                "select": "libelle_pathologie, effectif_patients, depenses",
                "where": where,
                "order_by": "effectif_patients DESC", # Trie pour avoir la plus fréquente en premier
                "limit": 1 # On ne prend que la N°1 pour l'afficher sur ta carte
            }
        )
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
        """Retourne les données par défaut quand rien n'est sélectionner par l"utilisateur"""

        print("\nameli_api.py | get_prescription_default()")

        if toutes_regions and tous_départ:
            return self._requete("prescriptions",
                                {
                                "select" : "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                                "where" : f'year(annee)={annee}',
                                "group_by" : "libelle_departement",
                                "limit" : limite_ligne
                                }
                                )
        
        elif toutes_regions:
            return self._requete("prescriptions",
                                {
                                "select" : "libelle_region,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                                "where" : f'year(annee)={annee}',
                                "group_by" : "libelle_region",
                                "limit" : limite_ligne
                                }
                                )
        


    def get_region_prescription(self, region_list_id=None, annee="2024", limite_ligne=30):
        """
        Filtre les montants totales et moyens selon la (ou les) région(s) pour une année
        On affiche toutes les régions si 'region_list_id=None'
        """

        print("\nameli_api.py | get_region_prescription()")

        conditions_de_filtres = [f"year(annee)={annee}"]

        if region_list_id:
            ids_formates = ",".join([f"'{r_id}'" for r_id in region_list_id]) # On s'assure que tous les IDs sont des chaînes ou des entiers propres
            conditions_de_filtres.append(f"region IN ({ids_formates})") # Utilisation de l'opérateur IN pour gérer la liste

        where = " AND ".join(conditions_de_filtres)

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


    def get_departement_prescriptions(self, departement_list_id=None, annee="2024", limite_ligne=100):
        """
        Croise les filtres du montant (total et moyen) selon la région et le département sur une annéee
        """
        print("\nameli_api.py | get_prescriptions_cross_filter()")

        where_clauses = [f"year(annee)={annee}"]
        select_fields = ""

        # Si l'utilisateur a coché une (ou plusieurs) région(s) et des départements (min 2)
        if departement_list_id:
            ids_dep = ",".join([f"'{d_id}'" for d_id in departement_list_id])
            where_clauses.append(f"departement IN ({ids_dep})")
            
            select_fields = "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen"
            print(f"Sélections de (ou plusieurs) région(s) et min=2 départements | select_fields : {select_fields}")


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
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

    def get_prescription_default(self, annee="2024", limite_ligne=30):
        """Retourne les données par défaut quand rien n'est sélectionner par l"utilisateur"""

        return self._requete("prescriptions",
                             {
                              "select" : "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
                              "where" : f'annee={annee}',
                              "limit" : limite_ligne
                             }
                            )


    def get_region_prescription(self, region_list_id=None, annee='2024', limite_ligne=25):
        """
        Filtre les montants totales et moyens selon la (ou les) région(s) pour une année
        On affiche toutes les régions si 'region_list_id=None'
        """

        conditions_de_filtres = [f"annee={annee}"]

        if region_list_id:
            ids_formates = ",".join([str(r_id) for r_id in region_list_id]) # On s'assure que tous les IDs sont des chaînes ou des entiers propres
            conditions_de_filtres.append(f"region_id IN ({ids_formates})") # Utilisation de l'opérateur IN pour gérer la liste

        where = " AND ".join(conditions_de_filtres)

        print(f"Création du filtre SQL : WHERE {where}")

        return self._requete(
            "prescription",
            {
                "select" : "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee",
                "where" : where,
                "limit" : limite_ligne
            }
        )


    def get_prescriptions_cross_filter(self, region_list_id=None, departement_list_id=None, annee='2024', limite_ligne=100):
        """
        Croise les filtres du montant (total et moyen) selon la région et le département sur une annéee
        Cas 1 : TOUT est séléctionner (régions et départements)
        Cas 2 : Un (ou plusieurs) régions sont séléctionnées, on filtre selon les départements associés
        Cas 3 : Un (ou plusieurs) régions séléctionnées, on filtres selon TOUT les départements associés
        """

        where_clauses = [f"annee={annee}"]


        # Si TOUTES les régions et TOUS les départements sont sélectionnés
        if not region_list_id and not departement_list_id:
            print(f"Toutes les options ont été séléctionnées | select_fields : {select_fields}")
            select_fields = "region,montant_total_prescription_integer,montant_moyen_prescription_integer,annee"
 

        # Si l'utilisateur a coché une (ou plusieurs) région(s) et des départements (min 2)
        elif departement_list_id:
            ids_dep = ",".join([str(d_id) for d_id in departement_list_id])
            where_clauses.append(f"departement_id IN ({ids_dep})")
            
            select_fields = "departement,montant_total_prescription_integer,montant_moyen_prescription_integer,annee"
            print(f"Sélections de (ou plusieurs) région(s) et min=2 départements | select_fields : {select_fields}")
        
        # Si l'utilisateur a sélectionné une (ou plusieurs) région(s) mais veut TOUS ses départements (Sélection rapide)
        elif region_list_id:
            ids_reg = ",".join([str(r_id) for r_id in region_list_id])
            where_clauses.append(f"region_id IN ({ids_reg})")

            select_fields = "departement,montant_total_prescription_integer,montant_moyen_prescription_integer,annee"
            print(f"Sélections de (ou plusieurs) région(s) et TOUS les départements | select_fields : {select_fields}")


        where_final = " AND ".join(where_clauses)
        print(f"Filtre WHERE : {where_final}")


        return self._requete(
            "prescriptions",
            {
                "select": select_fields,
                "where": where_final,
                "limit": limite_ligne
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
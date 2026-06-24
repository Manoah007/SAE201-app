# Ce fichier se sert du module ameli_api.py
# Il ne contient que les fonctions de requêtes SQL pour les différetes pages en lien avec les prescriptions

class PrescriptionService:
    """Service gérant la logique métier et les requêtes des prescriptions."""

    def __init__(self, ameli_api):
        # On injecte l'API pour pouvoir utiliser son moteur de requête
        self.api = ameli_api


#===============================================================================#
#   FONCTIONS DE REQUËTES SQL POUR LA DISPARITÉ GÉOGRAPHIQUE (page_disparite()) #
#===============================================================================#


    def get_prescription_toutes_zones(self, toutes_regions=True, tous_depart=False, annee="2024", limite_ligne=30):
        """Affiche soit tous les départements, soit toutes les régions"""

        print("\nameli_api.py | get_prescription_toutes_zones()")

        if toutes_regions and tous_depart:
            print(f"Retourne tous les départements : toutes_regions={toutes_regions} et tous_départ={tous_depart}")
            return self.api._requete("prescriptions",
                                {
                                "select" : "libelle_departement,SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                                "where" : f'year(annee)={annee}',
                                "group_by" : "libelle_departement",
                                "limit" : limite_ligne
                                }
                                )
        
        elif toutes_regions:
            print(f"Retourne toutes les régions: toutes_regions={toutes_regions}")
            return self.api._requete("prescriptions",
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

        return self.api._requete(
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


        return self.api._requete(
            "prescriptions",
            {
                "select": select_fields,
                "where": where_final,
                "group_by" : "libelle_departement",
                "limit": limite_ligne
            }
        )

#====================================================================================================#

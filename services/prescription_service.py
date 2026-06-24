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

#========================================================================================================#
#   FONCTIONS DE REQUËTES SQL POUR LA CORRÉLATION DÉMOGRAPHIQUES DES PROFESSIONNELS (page_correlation5°) #
#========================================================================================================#

    def get_donnees_pyramide_ages(self, profession, departement_code=None, annee="2024", limit_ligne=100):
        """Retourne les effectifs groupés par sexe et par tranche d'âge"""

        print("\nprescription_service.py | get_donnees_pyramide_ages()")


        where_clauses = [
            f"year(annee)={annee}", 
            "libelle_sexe != 'tout sexe'",
            "libelle_classe_age != 'Tout âge'"
        ]


        if profession:
            where_clauses.append(f"profession_sante = '{profession}'")

        if departement_code:
            where_clauses.append(f"departement = '{departement_code}'")


        where_final = " AND ".join(where_clauses)
        print(f"Filtre WHERE Pyramide : {where_final}")


        donnees_brutes = self.api._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "libelle_sexe, libelle_classe_age, SUM(effectif) as total",
                "where": where_final,
                "group_by": "libelle_sexe, libelle_classe_age",
                "limit": limit_ligne
            }
        )

        # On groupe par Tranche d'Âge
        pyramide_formatee = {}

        for ligne in donnees_brutes:
            age = ligne.get('libelle_classe_age', '')
            sexe = ligne.get('libelle_sexe', '').lower()
            total = ligne.get('total', 0)

            # Si la tranche d'âge n'existe pas encore, on la crée
            if age not in pyramide_formatee:
                pyramide_formatee[age] = {
                    "age": age, 
                    "hommes": 0, 
                    "femmes": 0, 
                    "total_tranche": 0
                }

            # On range les effectifs dans la bonne case
            if "hommes" in sexe:
                pyramide_formatee[age]["hommes"] += total
            elif "femmes" in sexe:
                pyramide_formatee[age]["femmes"] += total

            # On calcule le total de la ligne au passage
            pyramide_formatee[age]["total_tranche"] += total


        resultats_finaux = list(pyramide_formatee.values())
        resultats_finaux.sort(key=lambda x: x["age"])

        return resultats_finaux
    


    def get_tableau_top_deserts_medicaux(self, profession, annee="2024"):
        """
        Pivote les tranches d'âge en colonnes pour chaque département.
        """

        print("\nprescription_service.py | get_tableau_top_deserts_medicaux()")

        where_clauses = [
            f"year(annee)={annee}",
            f"profession_sante='{profession}'",
            "libelle_sexe = 'tout sexe'",
            "libelle_classe_age != 'Tout âge'",
            "departement IS NOT NULL"
        ]
        
        where_final = " AND ".join(where_clauses)
        
        donnees_brutes = self.api._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, libelle_departement, libelle_classe_age, SUM(effectif) as effectif",
                "where": where_final,
                "group_by": "departement, libelle_departement, libelle_classe_age"
            }
        )

        tableau_depts = {}

        for ligne in donnees_brutes:
            code_dept = ligne.get('departement')
            nom_dept = ligne.get('libelle_departement', '')
            age = ligne.get('libelle_classe_age', "")
            effectif = ligne.get('effectif', 0)
            
            # Initialisation de la ligne du département
            if code_dept not in tableau_depts:
                tableau_depts[code_dept] = {
                    "code": code_dept,
                    "nom": nom_dept,
                    "total": 0,
                    "tranches": {}
                }
                
            tableau_depts[code_dept]["total"] += effectif
            tableau_depts[code_dept]["tranches"][age] = effectif

        
        resultats_finaux = list(tableau_depts.values()) # Formatage pour le frontend
        resultats_finaux.sort(key=lambda x: x["nom"]) # Tri alphabétique par nom de département

        return resultats_finaux
    

    def get_graphique_top_deserts_medicaux(self, profession, annee="2024", limite=15):
        """Calcule la proportion de médecins de +60 ans par département"""

        print("\nprescription_service.py | get_graphique_top_deserts_medicaux()")

        # LA REQUÊTE API : On récupère tous les âges pour tous les départements
        where_clauses = [
            f"year(annee)={annee}",
            f"profession_sante='{profession}'",
            "libelle_sexe = 'tout sexe'",       # On regroupe hommes et femmes ici !
            "libelle_classe_age != 'Tout âge'", # Mais on garde le détail des tranches d'âge
            "departement IS NOT NULL"           # On exclut les lignes de totaux nationaux
        ]
        
        where_final = " AND ".join(where_clauses)
        

        donnees_brutes = self.api._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, libelle_classe_age, SUM(effectif) as effectif",
                "where": where_final,
                "group_by": "departement, libelle_classe_age"
            }
        )

        # LE CALCUL PYTHON

        # Les libellés Ameli pour les seniors  :
        mots_cles_seniors = ["de 60 à 64", "de 65 à 69", "70 ans et plus"] 
        
        stats_depts = {} # Dictionnaire qui va stocker nos calculs

        for ligne in donnees_brutes:
            dept = ligne.get('departement')
            age = ligne.get('libelle_classe_age', "")
            effectif = ligne.get('effectif', 0)
            
            # Initialisation du département s'il n'existe pas encore dans le dictionnaire
            if dept not in stats_depts:
                stats_depts[dept] = {"total": 0, "seniors": 0}
                
            # On ajoute à la population totale du département
            stats_depts[dept]["total"] += effectif
            
            # Si le libellé de l'âge contient l'un de nos mots clés, on l'ajoute aux seniors !
            if any(mot in age for mot in mots_cles_seniors):
                stats_depts[dept]["seniors"] += effectif

        # LE CLASSEMENT : Calcul du % et création du Top
        resultats_finaux = []
        for dept, stats in stats_depts.items():
            if stats["total"] > 0: # Évite la division par zéro
                pourcentage = (stats["seniors"] / stats["total"]) * 100
                resultats_finaux.append({
                    "departement": dept,
                    "total_praticiens": stats["total"],
                    "praticiens_seniors": stats["seniors"],
                    "pourcentage_seniors": round(pourcentage, 2) # Arrondi à 2 décimales
                })

        # On trie la liste du plus grand risque (plus fort %) au plus petit
        resultats_finaux.sort(key=lambda x: x["pourcentage_seniors"], reverse=True)

        if limite:
            return resultats_finaux[:limite] # Renvoie le Top 15

        return resultats_finaux


    




    def get_correlation_age_depense(self, profession, annee="2024"):
        """
        Prépare les données pour le GRAPHIQUE 3 (Nuage) ET LE TABLEAU RÉCAPITULATIF.
        Fusionne la démographie et les finances départementales.
        """

        print("\nprescription_service.py | get_correlation_age_depense()")


        donnees_demo = self.get_graphique_top_deserts_medicaux(profession, annee=annee, limite=None)
        if not donnees_demo:
            return []


        donnees_finance = self.get_finance(
            annee=annee,
            limite_ligne=150
        )


        dict_finance = {}
        for ligne in donnees_finance:
            # CORRECTION A : On utilise le CODE du département, pas son nom !
            code_dept = ligne.get('departement', '').strip() 
            print(f"\n--- [DEBUG CORRÉLATION] ---")
            print(f"Détection | code_dept={repr(code_dept)} | Type: {type(code_dept)}")
            print("-----------------------------\n")
            if code_dept:
                # CORRECTION B : On utilise les vrais noms de colonnes "integer" !
                dict_finance[code_dept] = {
                    "cout_moyen": ligne.get('montant_moyen_prescription_integer', 0),
                    "cout_total": ligne.get('montant_total_prescription_integer', 0)
                }


        resultats_fusionnes = []
        print(f"\n--- [DEBUG CORRÉLATION] ---")
        print(f"Exemple ligne démo : {donnees_demo[0]}")
        print(f"Clés disponibles dans la démo : {list(donnees_demo[0].keys())}")
        print("-----------------------------\n")
        print(f"Exemple ligne finance : {donnees_finance[0]}")
        print(f"Exemple de clés dans le dictionnaire dict_finance : {list(dict_finance.keys())[:5]}")
        print("-----------------------------\n")
        for dept_demo in donnees_demo:
           
            cle_commune = dept_demo.get('departement') or dept_demo.get('code_dept')
            
            if not cle_commune:
                continue
                
            cle_commune = str(cle_commune).strip() # Nettoyage des espaces
            
            finances = dict_finance.get(cle_commune, {})
            cout_moyen = finances.get("cout_moyen", 0)
            cout_total = finances.get("cout_total", 0)
            
            if cout_moyen > 0: 
                resultats_fusionnes.append({
                    "departement_code": cle_commune, # On précise que c'est le code
                    "total_medecins": dept_demo['total_praticiens'],
                    "praticiens_seniors": dept_demo['praticiens_seniors'],
                    "pourcentage_seniors": dept_demo['pourcentage_seniors'],
                    "cout_total": cout_total,
                    "cout_moyen": cout_moyen
                })

        return resultats_fusionnes
    

    def get_finance(self, annee="2024", limite_ligne=30):
        """Affiche soit tous les départements, soit toutes les régions"""

        print("\nameli_api.py | get_finance()")


        return self.api._requete("prescriptions",
                            {
                            "select" : "departement,libelle_departement, SUM(montant_total_prescription_integer) as cout_total, AVG(montant_moyen_prescription_integer) as cout_moyen",
                            "where" : f'year(annee)={annee}',
                            "group_by" : "departement, libelle_departement",
                            "limit" : limite_ligne
                            }
                            )
from flask import Blueprint, jsonify, render_template, request
from models.db import Session
from models.dimensions import Region, Departement
from services.ameli_api import AmeliAPI

bp_prescriptions = Blueprint("prescriptions", __name__)
api = AmeliAPI()
    


@bp_prescriptions.route("/prescriptions")
def accueil_prescription():
    """Cette fonction ne sert qu'à rediriger vers la page des postes de prescription et les cartes des sous thème disponibles"""
    return render_template("prescriptions/accueil_prescription.html")


@bp_prescriptions.route("/prescriptions/disparite")
def page_disparite():

    session = Session()
    print("\nprescription.py | page_disparite()")


    try:
        # Récupère les tables pour charger les listes déroulantes
        regions = session.query(Region).order_by(Region.libelle).all()
        departements = session.query(Departement).order_by(Departement.libelle).all()

        # RÉCUPÉRATION DES CHOIX (Noms corrigés pour matcher le HTML)
        region_list = request.args.getlist("regions") 
        departement_list = request.args.getlist("departements")
        
        annee_str = str(request.args.get("annee", default="2024"))
        limit_ligne = request.args.get("ligne_max", default=19, type=int)

        # ANALYSE DES CHOIX
        is_region_tout = not region_list or "ALL" in region_list or "" in region_list
        is_dept_tout = not departement_list or "ALL" in departement_list or "" in departement_list

        # Nettoyage
        regions_ids = [r for r in region_list if r != "ALL"]
        departments_ids = [d for d in departement_list if d != "ALL"]

        resultats = []
        mode_maillage_regional = False



        # APPELS API - Géstion des Scénarios
        if not request.args.get('regions') and not request.args.get('departements'):
            print("0 - Premier chargement de page, aucune sélection")
            mode_maillage_regional = True
            resultats = api.get_prescription_toutes_zones(
                toutes_regions=True,
                tous_départ=False,
                annee=annee_str,
                limite_ligne=limit_ligne
            )

        elif departments_ids or (is_dept_tout and regions_ids):
            print("I - Affichage maillage Départemental (Filtré)")
            resultats = api.get_departement_prescriptions(
                region_list_id=regions_ids,
                departement_list_id=departments_ids, 
                annee=annee_str,
                limite_ligne=limit_ligne
            )

        elif is_dept_tout and is_region_tout:
            print("II - Sélection de tous les départements de France")
            resultats = api.get_prescription_toutes_zones(
                toutes_regions=True,
                tous_départ=True,
                annee=annee_str,
                limite_ligne=limit_ligne
            )  

        elif regions_ids and not departments_ids:
            print("III - Sélection de régions spécifiques")
            mode_maillage_regional = True
            resultats = api.get_region_prescription(
                region_list_id=regions_ids, 
                annee=annee_str,
                limite_ligne=limit_ligne
            )
        
        else:
            print("IV - Maillage Régional National")
            mode_maillage_regional = True
            resultats = api.get_prescription_toutes_zones(
                toutes_regions=True,
                tous_départ=False,
                annee=annee_str,
                limite_ligne=limit_ligne
            )


        # PRÉPARATION DES DONNÉES POUR CHART.JS
        labels_zones = []
        valeurs_totales = []
        valeurs_moyennes = []

        if resultats:
            for ligne in resultats:
                nom_zone = ligne.get('libelle_departement') or ligne.get('libelle_region') or "Inconnu"
                labels_zones.append(nom_zone) 
                
                # On utilise les noms exacts de tes colonnes 'select'
                valeurs_totales.append(ligne.get('cout_total', 0))

                moyenne_brute = ligne.get('cout_moyen', 0)
                # S'il y a un chiffre, on l'arrondit à 2 décimales. Sinon, on met 0.
                moyenne_arrondie = round(moyenne_brute, 2) if moyenne_brute else 0
                valeurs_moyennes.append(moyenne_arrondie)



        return render_template(
            "prescriptions/page_disparite.html",
            regions=regions,
            departements=departements,
            annee=annee_str,
            limite_ligne=limit_ligne,
            region_id=region_list,    
            departement_id=departement_list,
            resultats=resultats,
            mode_maillage_regional=mode_maillage_regional,
            labels_zones=labels_zones,
            valeurs_totales=valeurs_totales,
            valeurs_moyennes=valeurs_moyennes
        )
    
    except Exception as e:
        print(f"Erreur lors de la génération de la page disparité : {e}")
        return "Une erreur serveur est survenue.", 500
    
    finally:
        session.close()
        


@bp_prescriptions.route("/prescriptions/correlation_demographique")
def page_correlation():
    return render_template("prescriptions/page_correlation.html")


@bp_prescriptions.route("/prescriptions/prescriptions_majeurs")
def page_prescript_majeur():
    return render_template("prescriptions/page_prescript_majeur.html")
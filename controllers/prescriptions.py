from flask import Blueprint, jsonify, render_template, request
from models.db import Session
from models.dimensions import Region, Departement, ProfessionSante
from services.ameli_api import AmeliAPI
from services.prescription_service import PrescriptionService

bp_prescriptions = Blueprint("prescriptions", __name__)
api = AmeliAPI()
prescription_service = PrescriptionService(api) 


@bp_prescriptions.route("/prescriptions")
def accueil_prescription():
    """Cette fonction ne sert qu'à rediriger vers la page des postes de prescription et les cartes des sous thème disponibles"""
    return render_template("prescriptions/accueil_prescription.html")


@bp_prescriptions.route("/prescriptions/disparite")
def page_disparite():

    session = Session()
    print("\nprescription.py | page_disparite() | ROUTE : /prescriptions/disparite")


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
            resultats = prescription_service.get_prescription_toutes_zones(
                toutes_regions=True,
                tous_depart=False,
                annee=annee_str,
                limite_ligne=limit_ligne
            )

        elif departments_ids or (is_dept_tout and regions_ids):
            print("I - Affichage maillage Départemental (Filtré)")
            resultats = prescription_service.get_departement_prescriptions(
                region_list_id=regions_ids,
                departement_list_id=departments_ids, 
                annee=annee_str,
                limite_ligne=limit_ligne
            )

        elif is_dept_tout and is_region_tout:
            print("II - Sélection de tous les départements de France")
            resultats = prescription_service.get_prescription_toutes_zones(
                toutes_regions=True,
                tous_depart=True,
                annee=annee_str,
                limite_ligne=limit_ligne
            )  

        elif regions_ids and not departments_ids:
            print("III - Sélection de régions spécifiques")
            mode_maillage_regional = True
            resultats = prescription_service.get_region_prescription(
                region_list_id=regions_ids, 
                annee=annee_str,
                limite_ligne=limit_ligne
            )
        
        else:
            print("IV - Maillage Régional National")
            mode_maillage_regional = True
            resultats = prescription_service.get_prescription_toutes_zones(
                toutes_regions=True,
                tous_depart=False,
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
    
    session = Session()
    print("\nprescription.py | page_correlation() | ROUTE : /prescriptions/correlation_demographique")

    try:
        departements = session.query(Departement).order_by(Departement.libelle).all()
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()

        profession = request.args.get("profession", "Ensemble des médecins") 
        annee_str = str(request.args.get("annee", default="2024"))
        departement_code = request.args.get("departement")


        donnees_globales = prescription_service.get_correlation_age_depense(
            profession=profession, 
            annee=annee_str
        )
        
        donnees_pyramide = prescription_service.get_donnees_pyramide_ages(
            profession=profession, 
            departement_code=departement_code, 
            annee=annee_str
        )
        
        donnees_tableau_deserts = prescription_service.get_tableau_top_deserts_medicaux(
            profession=profession, 
            annee=annee_str
        )

        return render_template(
            "prescriptions/page_correlation.html",
            # Listes pour construire les <select>
            departements=departements,
            professions=professions,
            
            # Choix actuels pour garder les options sélectionnées après rafraîchissement
            profession_selectionnee=profession,
            annee_selectionnee=annee_str,
            departement_selectionne=departement_code,
            
            # Données JSON pour l'affichage (Graphiques et Tableaux)
            donnees_globales=donnees_globales,
            donnees_pyramide=donnees_pyramide,
            donnees_tableau_deserts=donnees_tableau_deserts
        )

    except Exception as e:
        print(f"Erreur lors de la génération de la page corrélation : {e}")
        return "Une erreur serveur est survenue lors de la récupération des données.", 500
        
    finally:
        session.close()


@bp_prescriptions.route("/prescriptions/prescriptions_majeurs")
def page_prescript_majeur():
    return render_template("prescriptions/page_prescript_majeur.html")
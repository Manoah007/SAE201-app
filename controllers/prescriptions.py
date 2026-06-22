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
 
    try:
        # Récupère les tables pour charger les listes déroulantes
        regions = session.query(Region).order_by(Region.libelle).all()
        departements = session.query(Departement).order_by(Departement.libelle).all()

        # Récupération des choix de l'utilisateur (via l'URL en GET)
        region_list_id = request.args.getlist("region_id")
        departement_list_id = request.args.getlist("departement_id")
        
        # On passe l'année en string pour correspondre à la signature de l'API ('2024')
        annee = request.args.get("annee", default="2024")
        annee_str = str(annee) if annee else "2024"



        # Si l'utilisateur choisit "TOUT", la valeur soumise est souvent une chaîne "TOUT" ou vide
        is_region_tout = not region_list_id or "TOUT" in region_list_id or "" in region_list_id
        is_dept_tout = not departement_list_id or "TOUT" in departement_list_id or "" in departement_list_id

        # Nettoyage des listes pour l'API (on ne garde que les vrais IDs numériques)
        clean_regions = [r for r in region_list_id if str(r).isdigit()]
        clean_departments = [d for d in departement_list_id if str(d).isdigit()]

        resultats = None
        error_message = None
        mode_maillage_regional = False


        
        # CAS 1 : Premier chargement ou Option "TOUT" active sur les Régions (Maillage Régional)
        if is_region_tout:
            print("Maillage Régional National")
            mode_maillage_regional = True
            # On appelle l'API sans filtres géographiques (Cas 1 de ton cross_filter)
            resultats = api.get_prescriptions_cross_filter(
                region_list_id=None, 
                departement_list_id=None, 
                annee=annee_str
            )

        # Région spécifique ET option "TOUT" sélectionnée au sein de cette région
        elif not is_region_tout and is_dept_tout:
            print("Sélection rapide de tous les départements d'une région")
            resultats = api.get_prescriptions_cross_filter(
                region_list_id=clean_regions, 
                departement_list_id=None, 
                annee=annee_str
            )

        # Région spécifique ET départements spécifiques cochés
        else:
            # CONTRAINTE : Au moins 2 départements
            if len(clean_departments) < 2:
                print("Infraction règle : Moins de 2 départements sélectionnés")
                error_message = "Contrainte de comparaison : Veuillez sélectionner au minimum 2 départements pour générer les graphiques."
                
                # Comportement de secours pour éviter un écran blanc : on affiche le maillage régional par défaut
                mode_maillage_regional = True
                resultats = api.get_prescription_default(annee=annee_str)
            else:
                print("Comparaison ciblée de départements")
                resultats = api.get_prescriptions_cross_filter(
                    region_list_id=clean_regions, 
                    departement_list_id=clean_departments, 
                    annee=annee_str
                )

        return render_template(
            "prescriptions/page_disparite.html",
            regions=regions,
            departements=departements,
            annee=annee_str,
            region_id=region_list_id,                  # Renvoie la sélection brute pour garder le focus HTML
            departement_id=departement_list_id,          # Renvoie la sélection brute pour garder le focus HTML
            resultats=resultats,
            error_message=error_message,               # Contient le message d'erreur si < 2 départements
            mode_maillage_regional=mode_maillage_regional # Variable utilisable en Jinja2 pour masquer/afficher des blocs
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
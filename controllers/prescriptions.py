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
    resultats = None

    try:
        # Chargement des données depuis la BD pour alimenter les listes déroualntes
        regions = session.query(Region).order_by(Region.libelle).all()
        departements = session.query(Departement).order_by(Departement.libelle).all()

        
        # Récupération des choix de l'utilisateur (via l'URL en GET)
        # Renvoie l'ID de chaque choix pour les identifiés 
        region_ids = request.args.getlist("region_id") # On récupère une liste d'ID pour des choix mutliple
        departement_ids = request.args.getlist("departement_id")
        annee = request.args.get("annee", type=int)


        if not region_ids and not departement_ids and not annee:
            resultats = api.get_prescription_default()

        # Envoi de TOUTES les variables nécessaires au template Jinja2
        return render_template(
            "prescriptions/pages_disparite/page_disparite.html",
            # Pour charger les listes
            regions=regions,
            departements=departements,
            #Pour filtrer les données
            annee=annee,
            region_ids=region_ids,
            departement_ids=departement_ids,
            resultats=resultats,
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
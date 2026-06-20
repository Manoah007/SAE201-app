from flask import Blueprint, jsonify, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement, TypePrescription, TrancheAge
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
        # Chargement des données depuis la BD pour alimenter les listes déroualntes
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        prescription = session.query(TypePrescription).order_by(TypePrescription.libelle).all()
        
        # Récupération des choix de l'utilisateur (via l'URL en GET)
        # Renvoie l'ID de chaque choix pour les identifiés 
        profession_id = request.args.get("profession_id", type=int)
        region_id = request.args.get("region_id", type=int)
        annee = request.args.get("annee", type=int)

        resultats = api.get_prescript_test()

        # Envoi de TOUTES les variables nécessaires au template Jinja2
        return render_template(
            "prescriptions/page_disparite.html",
            # Pour charger les listes
            professions=professions,
            regions=regions,
            annee=annee,
            profession_id=profession_id, # Ajouté pour garder les options "selected"
            region_id=region_id,         # Ajouté pour garder les options "selected"
            resultats=resultats,
        )
    
    finally:
        session.close() 
        

@bp_prescriptions.route("/prescriptions/correlation_demographique")
def page_correlation():
    return render_template("prescriptions/page_correlation.html")


@bp_prescriptions.route("/prescriptions/prescriptions_majeurs")
def page_prescript_majeur():
    return render_template("prescriptions/page_prescript_majeur.html")
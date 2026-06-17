from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement, TypePrescription
from services.ameli_api import AmeliAPI

bp_prescriptions = Blueprint("prescriptions", __name__)
api = AmeliAPI()
    


@bp_prescriptions.route("/prescriptions")
def page_prescriptions():
    """Cette fonction ne sert qu'à rediriger vers la page des postes de prescription et les cartes des sous thème disponibles"""
    return render_template("prescriptions/prescriptions_maquette.html")


@bp_prescriptions.route("/prescriptions/poste")
def page_postes():
    session = Session()
    try:
        # 1. Chargement des données pour alimenter les listes déroulantes
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        postes = session.query(TypePrescription).order_by(TypePrescription.libelle).all()
        
        # Récupération des choix de l'utilisateur (via l'URL en GET)
        profession_id = request.args.get("profession_id", type=int)
        departement_id = request.args.get("departement_id", type=int)
        annee = request.args.get("annee", type=int)
        prescription_id = request.args.get("prescription_id", type=int)
        
        resultats = None
        evolution = None
        prof = None
        dept = None
        poste = None

        # 3. Si le formulaire a été soumis avec tous les champs
        if profession_id and departement_id and annee and prescription_id:
            prof = session.get(ProfessionSante, profession_id)
            dept = session.get(Departement, departement_id)
            poste = session.get(TypePrescription, prescription_id)
            
            if prof and dept and poste:
                # Appels à l'API Ameli
                resultats = api.get_prescriptions(prof.libelle, dept.code, annee, poste.libelle)
                evolution = api.get_evolution_prescriptions(prof.libelle, dept.code, poste.libelle)
        
        return render_template(
            "prescriptions/poste_prescription.html",
            professions=professions,
            regions=regions,
            postes=postes,
            prof=prof,
            dept=dept,
            poste=poste,
            annee=annee,
            resultats=resultats,
            evolution=evolution
        )
    finally:
        session.close()


@bp_prescriptions.route("/prescriptions/finance")
def page_finances():
    return render_template("prescriptions/finance_prescription.html")


@bp_prescriptions.route("/prescriptions/volume")
def page_volumes():
    return render_template("prescriptions/volume_prescription.html")
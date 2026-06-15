from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement, TypePrescription
from services.ameli_api import AmeliAPI

bp_prescriptions = Blueprint("prescriptions", __name__)
api = AmeliAPI()

@bp_prescriptions.route("/prescriptions")
def afficher():
    session = Session()
    try:
        # 1. Chargement des données pour alimenter les listes déroulantes
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        postes = session.query(TypePrescription).order_by(TypePrescription.libelle).all()
        
        # 2. Récupération des choix de l'utilisateur (via l'URL en GET)
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
            "prescriptions/prescriptions.html",
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
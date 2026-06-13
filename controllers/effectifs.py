from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region ,Departement
from services.ameli_api import AmeliAPI

bp_effectifs = Blueprint("effectifs", __name__)

api = AmeliAPI()

@bp_effectifs.route("/effectifs")
def afficher():
    """Affiche les effectifs pour la sélection de l'utilisateur."""

    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)
    annee = request.args.get("annee", type=int)

    session = Session()

    try:
        
        professions = session.query(ProfessionSante).all()
        regions = session.query(Region).all()

        if not profession_id or not departement_id or not annee:
            return render_template(
                "effectifs.html",
                professions=professions,
                regions=regions,
                prof=None,
                dept=None,
                annee=None,
                resultats=None,
                evolution=None
            )

        prof = session.get(ProfessionSante, profession_id)
        dept = session.get(Departement, departement_id)

        if not prof or not dept:
            return render_template(
                "erreur.html",
                message="Paramètres manquants."
            ), 400

        resultats = api.get_effectifs(prof.libelle, dept.code, annee)
        evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

        return render_template(
            "effectifs.html",
            professions=professions,
            regions=regions,
            prof=prof,
            dept=dept,
            annee=annee,
            resultats=resultats,
            evolution=evolution
        )

    finally:
        session.close()
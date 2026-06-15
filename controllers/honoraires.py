from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI

bp_honoraires = Blueprint("honoraires", __name__)

api = AmeliAPI()


@bp_honoraires.route("/honoraires")
def afficher():
    session = Session()

    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)
    annee = request.args.get("annee", type=int)

    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()

        prof = None
        dept = None
        resultats = None

        if profession_id and departement_id and annee:
            prof = session.get(ProfessionSante, profession_id)
            dept = session.get(Departement, departement_id)

            if prof and dept:
                resultats = api.get_honoraires(prof.libelle, dept.code, annee)

        return render_template(
            "honoraires.html",
            professions=professions,
            regions=regions,
            prof=prof,
            dept=dept,
            annee=annee,
            resultats=resultats
        )

    finally:
        session.close()
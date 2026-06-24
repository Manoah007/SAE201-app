from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Departement
from services.ameli_api import AmeliAPI

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()


@bp_comparaison.route("/comparaison")
def afficher():
    session = Session()

    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        departements = session.query(Departement).order_by(Departement.code).all()

        dept_a = request.args.get("dept_a", type=str)
        prof_a_id = request.args.get("prof_a", type=int)
        annee_a = request.args.get("annee_a", type=int)

        dept_b = request.args.get("dept_b", type=str)
        prof_b_id = request.args.get("prof_b", type=int)
        annee_b = request.args.get("annee_b", type=int)

        resultats = None

        if dept_a and prof_a_id and annee_a and dept_b and prof_b_id and annee_b:
            prof_a = session.get(ProfessionSante, prof_a_id)
            prof_b = session.get(ProfessionSante, prof_b_id)

            dept_obj_a = session.query(Departement).filter_by(code=dept_a).first()
            dept_obj_b = session.query(Departement).filter_by(code=dept_b).first()

            dept_nom_a = dept_obj_a.libelle if dept_obj_a else dept_a
            dept_nom_b = dept_obj_b.libelle if dept_obj_b else dept_b

            if prof_a and prof_b:
                data_a = api.get_effectifs(prof_a.libelle, dept_a, annee_a)
                data_b = api.get_effectifs(prof_b.libelle, dept_b, annee_b)

                valeur_a = data_a[0].get("effectif", 0) if data_a else 0
                valeur_b = data_b[0].get("effectif", 0) if data_b else 0

                resultats = [
                    {
                        "libelle": f"{prof_a.libelle} ({dept_nom_a})",
                        "annee": annee_a,
                        "valeur": valeur_a
                    },
                    {
                        "libelle": f"{prof_b.libelle} ({dept_nom_b})",
                        "annee": annee_b,
                        "valeur": valeur_b
                    }
                ]

        return render_template(
            "comparaison.html",
            professions=professions,
            departements=departements,
            resultats=resultats
        )

    finally:
        session.close()
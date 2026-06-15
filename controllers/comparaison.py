from flask import Blueprint, render_template, request
from models.db import Session

# AJOUT DE 'Departement' ICI
from models.dimensions import ProfessionSante, Departement 
from services.ameli_api import AmeliAPI 

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()

@bp_comparaison.route("/comparaison")
def afficher():
    session = Session()
    try:
        # On charge les listes pour les menus déroulants
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        departements = session.query(Departement).order_by(Departement.code).all() # NOUVEAU
        
        # Récupération des choix
        dept_code = request.args.get("dept_code", type=str) # NOUVEAU
        prof_a_id = request.args.get("prof_a", type=int)
        annee_a = request.args.get("annee_a", type=int)
        prof_b_id = request.args.get("prof_b", type=int)
        annee_b = request.args.get("annee_b", type=int)
        
        resultats = None

        # Si tout le formulaire est rempli
        if dept_code and prof_a_id and annee_a and prof_b_id and annee_b:
            prof_a = session.get(ProfessionSante, prof_a_id)
            prof_b = session.get(ProfessionSante, prof_b_id)
            
            if prof_a and prof_b:
                # 🚀 On utilise le vrai département choisi par l'utilisateur !
                data_a = api.get_effectifs(prof_a.libelle, dept_code, annee_a)
                data_b = api.get_effectifs(prof_b.libelle, dept_code, annee_b)
                
                valeur_a = data_a[0].get("effectif", 0) if (data_a and len(data_a) > 0) else 0
                valeur_b = data_b[0].get("effectif", 0) if (data_b and len(data_b) > 0) else 0
                
                # Pour faire joli, on récupère le nom du département pour l'afficher dans le tableau
                dept_obj = session.query(Departement).filter_by(code=dept_code).first()
                dept_nom = dept_obj.libelle if dept_obj else dept_code

                resultats = [
                    {
                        "libelle": f"{prof_a.libelle} ({dept_nom})",
                        "annee": annee_a,
                        "valeur": valeur_a
                    },
                    {
                        "libelle": f"{prof_b.libelle} ({dept_nom})",
                        "annee": annee_b,
                        "valeur": valeur_b
                    }
                ]
        
        return render_template(
            "comparaison.html", 
            professions=professions,
            departements=departements, # NOUVEAU
            resultats=resultats
        )
        
    finally:
        session.close()
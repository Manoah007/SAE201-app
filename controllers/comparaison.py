from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Departement 
from services.ameli_api import AmeliAPI 

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()

# Fonction utilitaire pour espacer les grands chiffres (ex: 12500 -> 12 500)
def formater_nombre(valeur):
    if isinstance(valeur, (int, float)):
        return f"{valeur:,}".replace(",", " ")
    return valeur

@bp_comparaison.route("/comparaison")
def afficher():
    session = Session()
    try:
        # On charge les listes complètes pour alimenter les menus déroulants
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        departements = session.query(Departement).order_by(Departement.code).all()
        
        # 🟢 Récupération des filtres pour le Bloc A
        dept_a = request.args.get("dept_a", type=str)
        prof_a_id = request.args.get("prof_a", type=int)
        annee_a = request.args.get("annee_a", type=int)
        
        # 🔵 Récupération des filtres pour le Bloc B
        dept_b = request.args.get("dept_b", type=str)
        prof_b_id = request.args.get("prof_b", type=int)
        annee_b = request.args.get("annee_b", type=int)
        
        resultats = None

        # Si le formulaire a été soumis et est complet
        if dept_a and prof_a_id and annee_a and dept_b and prof_b_id and annee_b:
            prof_a = session.get(ProfessionSante, prof_a_id)
            prof_b = session.get(ProfessionSante, prof_b_id)
            
            if prof_a and prof_b:
                # 🚀 Appels API indépendants pour le Bloc A et le Bloc B
                data_a = api.get_effectifs(prof_a.libelle, dept_a, annee_a)
                data_b = api.get_effectifs(prof_b.libelle, dept_b, annee_b)
                
                valeur_a = data_a[0].get("effectif", 0) if (data_a and len(data_a) > 0) else 0
                valeur_b = data_b[0].get("effectif", 0) if (data_b and len(data_b) > 0) else 0
                
                # Récupération des libellés réels des départements A et B pour le graphique et le tableau
                dept_a_obj = session.query(Departement).filter_by(code=dept_a).first()
                dept_a_nom = dept_a_obj.libelle if dept_a_obj else dept_a

                dept_b_obj = session.query(Departement).filter_by(code=dept_b).first()
                dept_b_nom = dept_b_obj.libelle if dept_b_obj else dept_b

                # On assemble les résultats pour Chart.js et la table HTML
                resultats = [
                    {
                        "libelle": f"{prof_a.libelle} ({dept_a_nom})",
                        "annee": annee_a,
                        "valeur": formater_nombre(valeur_a)
                    },
                    {
                        "libelle": f"{prof_b.libelle} ({dept_b_nom})",
                        "annee": annee_b,
                        "valeur": formater_nombre(valeur_b)
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
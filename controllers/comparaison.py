from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante
from services.ameli_api import AmeliAPI 

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()

@bp_comparaison.route("/comparaison")
def afficher():
    session = Session()
    try:
        # 1. On charge les professions de santé pour les menus déroulants
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        
        # 2. Récupération des choix de l'utilisateur
        prof_a_id = request.args.get("prof_a", type=int)
        annee_a = request.args.get("annee_a", type=int)
        
        prof_b_id = request.args.get("prof_b", type=int)
        annee_b = request.args.get("annee_b", type=int)
        
        resultats = None

        # 3. Si le formulaire est validé
        if prof_a_id and annee_a and prof_b_id and annee_b:
            prof_a = session.get(ProfessionSante, prof_a_id)
            prof_b = session.get(ProfessionSante, prof_b_id)
            
            if prof_a and prof_b:
                # Code département par défaut (ex: "94" pour Créteil / Val-de-Marne)
                # Tu pourras ajouter un champ département dans le HTML plus tard si tu veux
                dept_code = "94" 
                
                # 🚀 APPEL À TON VRAI SERVICE AMELI
                data_a = api.get_effectifs(prof_a.libelle, dept_code, annee_a)
                data_b = api.get_effectifs(prof_b.libelle, dept_code, annee_b)
                
                # L'API renvoie une liste de résultats [ {annee, effectif, densite} ]
                # On extrait la valeur de la clé 'effectif' du premier élément s'il existe
                valeur_a = data_a[0].get("effectif", 0) if (data_a and len(data_a) > 0) else 0
                valeur_b = data_b[0].get("effectif", 0) if (data_b and len(data_b) > 0) else 0
                
                # Formatage propre pour ton tableau HTML et Chart.js
                resultats = [
                    {
                        "libelle": prof_a.libelle,
                        "annee": annee_a,
                        "valeur": valeur_a
                    },
                    {
                        "libelle": prof_b.libelle,
                        "annee": annee_b,
                        "valeur": valeur_b
                    }
                ]
        
        return render_template(
            "comparaison.html", 
            professions=professions,
            resultats=resultats
        )
        
    finally:
        session.close()
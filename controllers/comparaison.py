from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante

# N'oublie pas d'importer ton API !
from services.ameli_api import AmeliAPI 

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()

@bp_comparaison.route("/comparaison")
def afficher():
    session = Session()
    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        
        # On récupère les choix (nouveaux noms de variables du HTML)
        prof_a_id = request.args.get("prof_a", type=int)
        annee_a = request.args.get("annee_a", type=int)
        
        prof_b_id = request.args.get("prof_b", type=int)
        annee_b = request.args.get("annee_b", type=int)
        
        resultats = None

        if prof_a_id and annee_a and prof_b_id and annee_b:
            prof_a = session.get(ProfessionSante, prof_a_id)
            prof_b = session.get(ProfessionSante, prof_b_id)
            
            if prof_a and prof_b:
                # 🚀 L'APPEL À TON API (À vérifier selon ton fichier ameli_api.py)
                # On suppose que get_effectifs a besoin du libellé et de l'année. 
                # (Si tu dois aussi lui passer un code département ou région, adapte-le !)
                data_a = api.get_effectifs(prof_a.libelle, annee_a)
                data_b = api.get_effectifs(prof_b.libelle, annee_b)
                
                # Formatage du résultat pour le tableau et le graphique
                resultats = [
                    {
                        "libelle": prof_a.libelle,
                        "annee": annee_a,
                        # Adapte ".get('effectif_total', 0)" en fonction de ce que te renvoie ton API (dictionnaire ou chiffre brut)
                        "valeur": data_a.get("effectif_total", 0) if isinstance(data_a, dict) else (data_a or 0)
                    },
                    {
                        "libelle": prof_b.libelle,
                        "annee": annee_b,
                        "valeur": data_b.get("effectif_total", 0) if isinstance(data_b, dict) else (data_b or 0)
                    }
                ]
        
        return render_template(
            "comparaison.html", 
            professions=professions,
            resultats=resultats
        )
        
    finally:
        session.close()
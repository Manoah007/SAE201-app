from flask import Blueprint, render_template, request
from models.db import Session
from services.ameli_api import AmeliAPI

# ATTENTION: Remplace "Pathologie" par le vrai nom de ta classe dans models.dimensions
from models.dimensions import Pathologie 

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()

@bp_comparaison.route("/comparaison")
def afficher():
    session = Session()
    try:
        # 1. Chargement de toutes les pathologies pour remplir les 2 menus déroulants
        pathologies = session.query(Pathologie).order_by(Pathologie.libelle).all()
        
        # 2. Récupération des choix du formulaire (identifiants et années A et B)
        pathologie_a_id = request.args.get("pathologie_a", type=int)
        annee_a = request.args.get("annee_a", type=int)
        
        pathologie_b_id = request.args.get("pathologie_b", type=int)
        annee_b = request.args.get("annee_b", type=int)
        
        resultats = None

        # 3. Si l'utilisateur a rempli les 4 champs et cliqué sur "Comparer"
        if pathologie_a_id and annee_a and pathologie_b_id and annee_b:
            # On récupère les vrais objets en base de données pour avoir leurs libellés
            patho_a = session.get(Pathologie, pathologie_a_id)
            patho_b = session.get(Pathologie, pathologie_b_id)
            
            if patho_a and patho_b:
                # --- APPEL À L'API AMELI ---
                # ATTENTION: Remplace "get_pathologie_data" par la vraie méthode de ton AmeliAPI !
                data_a = api.get_pathologie_data(patho_a.libelle, annee_a)
                data_b = api.get_pathologie_data(patho_b.libelle, annee_b)
                
                # 4. Formatage des résultats pour qu'ils soient lus par le tableau HTML et le graphique JS
                resultats = [
                    {
                        "libelle_pathologie": patho_a.libelle,
                        "annee": annee_a,
                        "valeur": data_a.get("montant", 0) if data_a else 0 # Adapte la clé selon l'API
                    },
                    {
                        "libelle_pathologie": patho_b.libelle,
                        "annee": annee_b,
                        "valeur": data_b.get("montant", 0) if data_b else 0 # Adapte la clé selon l'API
                    }
                ]
        
        # 5. On renvoie tout à notre fichier HTML
        return render_template(
            "comparaison.html", # Ou le nom de ton dossier : "comparaison/comparaison.html"
            pathologies=pathologies,
            resultats=resultats
        )
        
    finally:
        session.close()
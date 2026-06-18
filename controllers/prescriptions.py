from flask import Blueprint, jsonify, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement, TypePrescription, TrancheAge
from services.ameli_api import AmeliAPI

bp_prescriptions = Blueprint("prescriptions", __name__)
api = AmeliAPI()
    


@bp_prescriptions.route("/prescriptions")
def page_prescriptions():
    """Cette fonction ne sert qu'à rediriger vers la page des postes de prescription et les cartes des sous thème disponibles"""
    return render_template("prescriptions/prescriptions_maquette.html")


@bp_prescriptions.route("/prescriptions/poste")
@bp_prescriptions.route("/prescriptions/poste")
def page_postes():
    session = Session()

    try:
        # Chargement des données depuis la BD pour alimenter les listes déroualntes
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        tranches_age = session.query(TrancheAge).order_by(TrancheAge.libelle).all()
        types_prescriptions = session.query(TypePrescription).order_by(TypePrescription.libelle).all()
        

        # Récupération des choix de l'utilisateur (via l'URL en GET)
        # Renvoie l'ID de chaque choix pour les identifiés
        profession_id = request.args.get("profession_id", type=int)
        region_id = request.args.get("region_id", type=int)
        departement_id = request.args.get("departement_id", type=int)
        prescription_id = request.args.get("prescription_id", type=int)
        tranche_age_id = request.args.get("tranche_age_id", type=int)
        montant_id = request.args.get("montant_id", type=int)
        annee = request.args.get("annee", type=int)

        # On charge les départements uniquement si une région est sélectionnée
        departements = []
        if region_id:
            departements = session.query(Departement).filter_by(region_id=region_id).order_by(Departement.libelle).all()
        
        # Initialisation des variables pour la vue
        resultats = None
        evolution = None

        poste = None
        prescript = None
        reg = None # Sera récupéré via la base de données


        # Traitement des filtres et appels API (Si le formulaire complet est soumis)
        if profession_id and region_id and annee and prescription_id and tranche_age_id and montant_id:
            poste = session.get(ProfessionSante, profession_id)
            prescript = session.get(TypePrescription, prescription_id)
            reg = session.get(Region, region_id)

            if poste and prescript and reg: # CORRECTION 3 : Maintenant 'dept' existe bien, la condition fonctionne
                # Appels à ton service API Ameli externe
                resultats = api.get_prescriptions(poste.libelle, reg.code, annee, prescript.libelle)
                evolution = api.get_evolution_prescriptions(poste.libelle, reg.code, prescript.libelle)
        
        # 5. Envoi de TOUTES les variables nécessaires au template Jinja2
        return render_template(
            "prescriptions/poste_prescription.html",
            # Pour charger les listes
            professions=professions,
            regions=regions,
            departements=departements, # Ajouté pour que Jinja2 puisse réafficher les départements au rechargement
            types_prescriptions=types_prescriptions,
            tranches_age=tranches_age,
            profession_id=profession_id, # Ajouté pour garder les options "selected"
            region_id=region_id,         # Ajouté pour garder les options "selected"
            departement_id=departement_id, # Ajouté pour garder les options "selected"
            prescription_id=prescription_id, # Ajouté pour garder les options "selected"
            poste=poste,
            annee=annee,
            resultats=resultats,
            evolution=evolution
        )
    finally:
        session.close()

@bp_prescriptions.route("/api/departements/<int:region_id>")
def api_departements(region_id):
    """
    Cette route (dynamique car elle change constamment selon la région sélectionnée) 
    permet de récupérer les départements d'une région donnée
    """

    session = Session()

    # SELECT * FROM departement WHERE region_id = <region_id>
    departement = session.query(Departement).filter_by(region_id=region_id).all()
    
    # On transforme le résultat en liste de dictionnaires pour le JSON
    # Sans JSON, les listes retournées ne serait pas comprises par JavaScript
    return jsonify([{"id": depart.id, "libelle": depart.libelle} for depart in departement])


@bp_prescriptions.route("/prescriptions/finance")
def page_finances():
    return render_template("prescriptions/finance_prescription.html")


@bp_prescriptions.route("/prescriptions/volume")
def page_volumes():
    return render_template("prescriptions/volume_prescription.html")
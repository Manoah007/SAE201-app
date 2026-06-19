"""Carte interactive des effectifs par département (Leaflet)."""

from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante
from services.ameli_api import AmeliAPI

bp_carte = Blueprint("carte", __name__)
ameli = AmeliAPI()

PROFESSION_DEFAUT = "Ensemble des médecins"
ANNEE_DEFAUT = 2024


@bp_carte.route("/carte")
def afficher():
    """Carte choroplèthe des effectifs par département."""
    session = Session()
    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()

        profession_id = request.args.get("profession_id", type=int)
        annee = request.args.get("annee", ANNEE_DEFAUT, type=int)

        # Si une profession est choisie dans le formulaire, on l'utilise ;
        # sinon on affiche d'emblée "Ensemble des médecins" pour que la carte
        # soit visible dès le premier chargement, sans avoir à valider un filtre.
        prof = None
        prof_libelle = PROFESSION_DEFAUT

        if profession_id:
            prof = session.query(ProfessionSante).filter_by(id=profession_id).first()
            if prof:
                prof_libelle = prof.libelle

        lignes = ameli.get_repartition_departements(prof_libelle, annee)

        # On construit un dict { code_dept: effectif } passé en JSON au template.
        donnees_carte = {}
        for ligne in lignes:
            code = ligne.get("departement")
            effectif = ligne.get("effectif") or 0
            if code:
                donnees_carte[code] = effectif

        return render_template(
            "carte.html",
            professions=professions,
            prof=prof,
            annee=annee,
            profession_id=profession_id,
            donnees_carte=donnees_carte,
            titre_carte=f"{prof_libelle} — {annee}",
        )
    finally:
        session.close()
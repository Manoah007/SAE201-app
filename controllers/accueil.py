from flask import Blueprint, render_template
from models.db import Session
from models.dimensions import Region, ProfessionSante

bp_accueil = Blueprint("accueil", __name__)

@bp_accueil.route("/")
@bp_accueil.route("/accueil")
def index():
    """Page d'accueil : affiche les régions et professions."""
    session = Session()
    try:
        regions = session.query(Region).order_by(Region.libelle).all()
        professions = (session.query(ProfessionSante).order_by(ProfessionSante.libelle).all())
        return render_template("accueil.html",
                                regions=regions,
                                professions=professions)
    finally:
        session.close()

@bp_accueil.route("/api-ameli")
def api_ameli():
    """Page API Ameli : formulaire de consultation des effectifs."""
    session = Session()
    try:
        regions = session.query(Region).order_by(Region.libelle).all()
        professions = (
            session.query(ProfessionSante)
            .order_by(ProfessionSante.libelle)
            .all()
        )

        return render_template(
            "api_ameli.html",
            regions=regions,
            professions=professions
        )
    finally:
        session.close()

from flask import Blueprint, jsonify
from models.db import Session
from models.dimensions import Departement

bp_api = Blueprint("api", __name__, url_prefix="/api")


@bp_api.route("/departements/<int:region_id>")
def departements(region_id):
    """Retourne les départements d'une région au format JSON."""
    session = Session()

    try:
        depts = (
            session.query(Departement)
            .filter_by(region_id=region_id)
            .order_by(Departement.code)
            .all()
        )

        return jsonify([
            {
                "id": d.id,
                "code": d.code,
                "libelle": d.libelle
            }
            for d in depts
        ])

    finally:
        session.close()
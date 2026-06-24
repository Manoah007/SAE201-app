from flask import Blueprint, render_template

bp_documentation = Blueprint("documentation", __name__)


@bp_documentation.route("/documentation")
def afficher():
    """Affiche la page documentation du site."""
    return render_template("documentation.html")
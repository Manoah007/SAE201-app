from flask import Blueprint, render_template

bp_apropos = Blueprint("apropos", __name__)


@bp_apropos.route("/a-propos")
def afficher():
    """Affiche la page À propos du projet."""
    return render_template("apropos.html")
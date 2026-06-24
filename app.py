import os
from flask import Flask
from config import Config
from controllers.accueil import bp_accueil
from controllers.effectifs import bp_effectifs
from controllers.prescriptions import bp_prescriptions
from controllers.honoraires import bp_honoraires
from controllers.comparaison import bp_comparaison
from controllers.carte import bp_carte
from flask import Flask, render_template
from controllers.indicateurs import bp_indicateurs
from controllers.documentation import bp_documentation

app = Flask(__name__)
app.config.from_object(Config)

# Préfixe d'URL pour un futur déploiement en sous-dossier (vide en local).
app.config["BASE_URL"] = os.getenv("APP_BASE_URL", "")

@app.context_processor
def inject_base_url():
    """Rend BASE_URL disponible dans tous les templates."""
    return {"BASE_URL": app.config["BASE_URL"]}

# Enregistrement des contrôleurs (blueprints)
app.register_blueprint(bp_accueil)
app.register_blueprint(bp_effectifs)
app.register_blueprint(bp_prescriptions)
app.register_blueprint(bp_honoraires)
app.register_blueprint(bp_comparaison)
app.register_blueprint(bp_carte)
app.register_blueprint(bp_indicateurs)
app.register_blueprint(bp_documentation)

@app.errorhandler(404)
def page_non_trouvee(e):
    return render_template(
        "erreur.html",
        message="Page non trouvée."
    ), 404

@app.errorhandler(500)
def erreur_serveur(e):
    return render_template(
        "erreur.html",
        message="Erreur interne. Réessayez plus tard."
    ), 500

@app.route('/faq')
def faq():
    return render_template('faq.html')


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, use_reloader=False)
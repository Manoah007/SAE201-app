import os
from flask import Flask
from config import Config
from controllers.accueil import bp_accueil
from controllers.api import bp_api
from controllers.effectifs import bp_effectifs

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
app.register_blueprint(bp_api)
app.register_blueprint(bp_effectifs)

if __name__ == "__main__":
 app.run(debug=True)